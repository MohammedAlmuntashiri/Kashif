# pdf.py — API endpoint for uploading and processing financial-statement PDFs
#
# URL prefix (registered in api/__init__.py): /api/pdf
#
# Endpoints:
#   POST /api/pdf/upload?ticker=<symbol>
#     — Accepts a PDF file (annual or quarterly financial report from Tadawul)
#     — Runs the full extraction pipeline (extract_all) on it
#     — Upserts the extracted values into the financial_data table
#     — Returns extracted values + a field-by-field comparison vs the existing DB row
#
# How to call this endpoint (example using curl):
#   curl -X POST "http://localhost:5000/api/pdf/upload?ticker=2222" \
#        -F "pdf=@/path/to/aramco_2024_annual.pdf"
#
# Period naming convention (must match what's already in the DB):
#   Annual reports  → "{year}-annual"   e.g. "2024-annual"
#   Quarterly (Phase 6, not yet implemented):
#     Q1 → "{year}-Q1", Q2 → "{year}-Q2", Q3 → "{year}-Q3", Q4 → "{year}-Q4"
#
# The fiscal year is auto-detected from the PDF text by extract_all()
# (which internally calls _detect_fiscal_year). The detected year is returned
# inside the result dict under the key "_fiscal_year".

import os
import tempfile
from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.stock import Stock
from app.models.financial_data import FinancialData
from app.services.pdf_extractor import extract_all

pdf_bp = Blueprint('pdf', __name__)

# The 10 financial fields that extract_all() populates.
# These map 1-to-1 to FinancialData column names.
_FINANCIAL_FIELDS = [
    "revenue",
    "net_income",
    "eps",
    "total_assets",
    "total_borrowings",
    "shareholders_equity",
    "cash_and_equivalents",
    "free_cash_flow",
    "dividends_per_share",
    "shares_outstanding",
]


def _values_match(db_val, extracted_val, tolerance=0.01):
    """Check whether a DB value and an extracted value are close enough to call a match.

    Rules:
      - Both None  → match (neither side has data, no disagreement)
      - One None   → no match (one side has data the other doesn't)
      - Both numbers → match if they are within `tolerance` (default 1%) of each other.
        The denominator uses max(|db_val|, 1) to avoid division by zero for
        values that are legitimately 0 or very small.

    1% tolerance accounts for rounding differences between the PDF text and
    the DB seed values (e.g. 1,234,567,000 vs 1,234,568,000 from different sources).
    """
    if db_val is None and extracted_val is None:
        return True
    if db_val is None or extracted_val is None:
        return False
    return abs(db_val - extracted_val) / max(abs(db_val), 1) <= tolerance


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/pdf/upload?ticker=<symbol>
#
# Request format:
#   Content-Type: multipart/form-data
#   Query param:  ticker  (required) — Tadawul symbol e.g. "2222"
#   Form file:    pdf     (required) — the PDF file
#
# Response (200 OK):
#   {
#     "ticker":   "2222",
#     "period":   "2024-annual",
#     "extracted": { "revenue": 1.23e12, "net_income": ..., ... },
#     "db_comparison": {
#       "revenue": { "db": 1.23e12, "extracted": 1.23e12, "match": true },
#       "net_income": { ... },
#       ...
#     },
#     "updated": true
#   }
#
# "updated": true means the financial_data row was saved (insert or update).
# ─────────────────────────────────────────────────────────────────────────────
@pdf_bp.route('/upload', methods=['POST'])
def upload_pdf():

    # ── Validate the ticker query parameter ───────────────────────────────
    ticker = request.args.get('ticker', '').strip()
    if not ticker:
        return jsonify({"error": "ticker query parameter is required (e.g. ?ticker=2222)"}), 400

    # Dry-run mode: when ?dry_run=true, we run the full extraction and return
    # the DB comparison but do NOT write anything to the database. This lets
    # the user preview extraction quality before committing — protects the DB
    # from bad extractions on untested company layouts (Alinma 2022/2024
    # showed how easily a wrong upload can overwrite good seeded values).
    # Accepted truthy values: "true", "1", "yes" (case-insensitive).
    dry_run = request.args.get('dry_run', '').strip().lower() in ('true', '1', 'yes')

    stock = Stock.query.filter_by(symbol=ticker).first()
    if stock is None:
        return jsonify({"error": f"Stock {ticker} not found. Add it first via POST /api/stocks/"}), 404

    # ── Validate the uploaded file ─────────────────────────────────────────
    # Flask puts uploaded files in request.files. The field name must be "pdf".
    if 'pdf' not in request.files:
        return jsonify({"error": "No file found. Send the PDF in a form field named 'pdf'"}), 400

    pdf_file = request.files['pdf']
    if pdf_file.filename == '':
        return jsonify({"error": "Empty filename — please select a PDF file"}), 400

    # ── Save PDF to a temporary file and run the extractor ─────────────────
    # We can't pass a Flask file stream directly to pdfplumber — it needs a
    # real file path on disk. NamedTemporaryFile gives us a path; delete=False
    # means the OS won't auto-delete it before we finish using it.
    tmp = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    try:
        pdf_file.save(tmp.name)  # Write the uploaded bytes to disk
        tmp.close()              # Close our handle before pdfplumber opens it

        # Run the full 10-value extraction pipeline.
        # extract_all() internally:
        #   1. Does a standard text pass with pdfplumber + OCR fallback
        #   2. Does a rowwise pass (word-coordinate clustering) for column layouts
        #   3. Picks the best result per field (rowwise vs standard)
        #   4. Runs EPS × shares cross-validation to catch unit misdetection
        #   5. Auto-detects the fiscal year and appends it as "_fiscal_year"
        extracted = extract_all(tmp.name)

    except Exception as exc:
        # Extraction can fail on corrupted PDFs, password-protected files, etc.
        return jsonify({"error": f"PDF extraction failed: {str(exc)}"}), 422

    finally:
        # Always clean up the temp file — even if extraction raised an exception.
        try:
            os.unlink(tmp.name)
        except OSError:
            pass  # Already gone or permission issue — not critical

    # ── Determine the period string ─────────────────────────────────────────
    # extract_all() appends the auto-detected fiscal year under "_fiscal_year".
    # We pop it out of the dict so it doesn't get confused with a financial field.
    fiscal_year = extracted.pop("_fiscal_year", None)

    if fiscal_year:
        # Phase 5: all uploads are assumed to be annual reports.
        # Phase 6 (quarterly) will detect Q1/Q2/Q3/Q4 here and set e.g. "2024-Q1".
        period = f"{fiscal_year}-annual"
    else:
        # Fallback if year detection failed (very unusual — most PDFs have a year header).
        # We still proceed rather than reject the upload, so the user gets the extracted data.
        period = "unknown-annual"

    # ── Look up existing financial_data row for this stock + period ──────
    # In dry-run mode we only READ this row to build the comparison.
    # In normal mode we INSERT a new row if missing, then UPDATE it below.
    fd = (
        FinancialData.query
        .filter_by(stock_id=stock.id, period=period)
        .first()
    )

    if fd is None:
        # No existing row for this period.
        # In dry-run we use a transient unsaved object so getattr() returns
        # None for every field (clean comparison output without DB writes).
        # In normal mode we add it to the session for insertion.
        fd = FinancialData(stock_id=stock.id, period=period)
        if not dry_run:
            db.session.add(fd)
        is_new_row = True
    else:
        is_new_row = False

    # ── Build the field-by-field DB comparison ─────────────────────────────
    # For each of the 10 fields:
    #   - Read the current DB value (before any potential overwrite)
    #   - Compare against the extracted value
    #   - In normal mode, also write the extracted value back to the row
    #     (skipping None — preserves existing good DB values when the
    #     extractor couldn't find something)
    db_comparison = {}

    for field in _FINANCIAL_FIELDS:
        db_val  = getattr(fd, field)          # Current value in DB (None for new rows)
        ext_val = extracted.get(field)        # What the extractor found (may be None)

        db_comparison[field] = {
            "db":        db_val,              # Value in DB before this request
            "extracted": ext_val,             # Value the extractor just found in the PDF
            "match":     _values_match(db_val, ext_val),  # True = within 1% or both None
        }

        # Only write in non-dry-run mode AND only when extraction succeeded.
        if not dry_run and ext_val is not None:
            setattr(fd, field, ext_val)

    if dry_run:
        # No DB writes at all — also rollback any session-level state in case
        # SQLAlchemy attached the new (unsaved) FinancialData implicitly.
        db.session.rollback()
    else:
        db.session.commit()  # Persist the updated or newly created row

    return jsonify({
        "ticker":        ticker,
        "period":        period,
        "is_new_row":    is_new_row,      # True = no existing DB row for this period
        "extracted":     extracted,        # The 10 extracted values (None where not found)
        "db_comparison": db_comparison,    # Per-field: {db, extracted, match}
        "updated":       not dry_run,     # False in dry-run mode — DB was not written
        "dry_run":       dry_run,         # Echo the flag so the caller can confirm
    })
