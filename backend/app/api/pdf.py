# pdf.py — API endpoint for uploading and processing financial-statement PDFs
#
# URL prefix (registered in api/__init__.py): /api/pdf
#
# Endpoints:
#   POST /api/pdf/upload?ticker=<symbol>
#     — Single-file upload. Accepts ONE PDF, runs extract_all, upserts financial_data,
#       returns extracted values + per-field DB comparison.
#
#   POST /api/pdf/upload_batch?ticker=<symbol>
#     — Multi-file upload (Part 14.1). Accepts MULTIPLE PDFs under the same field
#       name 'pdf'. Same ticker for all files (typical use: upload several years
#       of the same company's annual reports in one call). Each PDF is processed
#       independently — if one fails, the others still run. Returns a per-file
#       results array.
#
# How to call these endpoints (curl examples):
#   Single file:
#     curl -X POST "http://localhost:5000/api/pdf/upload?ticker=2222" \
#          -F "pdf=@/path/to/aramco_2024_annual.pdf"
#
#   Multiple files (note the repeated -F "pdf=..." for each file):
#     curl -X POST "http://localhost:5000/api/pdf/upload_batch?ticker=2222" \
#          -F "pdf=@/path/to/aramco_2022.pdf" \
#          -F "pdf=@/path/to/aramco_2023.pdf" \
#          -F "pdf=@/path/to/aramco_2024.pdf"
#
#   In Postman: under Body → form-data, add MULTIPLE rows all with key "pdf"
#   (type File) — Postman will send them as a repeated multipart field.
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
# Internal helper — process ONE uploaded PDF and return a result dict.
#
# Used by both /upload (single file) and /upload_batch (multiple files).
# Keeping this in a helper means both endpoints share the exact same
# extraction + DB-comparison + upsert logic, so /upload behaviour is
# unchanged after the refactor.
#
# Parameters:
#   stock     — already-resolved Stock ORM object for the ticker
#   pdf_file  — a werkzeug FileStorage from request.files (one uploaded PDF)
#   dry_run   — bool. When True, no DB writes occur (rollback at end).
#
# Returns a dict with the per-file result. On success:
#   { "status": "success", "filename": ..., "period": ..., "is_new_row": ...,
#     "extracted": {...}, "db_comparison": {...}, "updated": bool }
# On failure:
#   { "status": "error", "filename": ..., "error": "..." }
#
# Does NOT commit or rollback the DB session — the caller controls that
# so batch uploads can commit all successful files in a single transaction.
# ─────────────────────────────────────────────────────────────────────────────
def _process_single_pdf(stock, pdf_file, dry_run):
    filename = pdf_file.filename or "<unnamed>"

    # Validate filename — empty means the form field was sent without a file.
    if filename == '':
        return {
            "status":   "error",
            "filename": filename,
            "error":    "Empty filename — please select a PDF file",
        }

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
        # In batch mode we don't raise — we return an error dict so the
        # batch caller can include this file in its per-file results array
        # and continue processing the remaining files.
        return {
            "status":   "error",
            "filename": filename,
            "error":    f"PDF extraction failed: {str(exc)}",
        }

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

    # NOTE: this helper does NOT commit or rollback. The caller decides:
    #   - /upload commits/rollbacks after this single call
    #   - /upload_batch commits ONCE after the whole loop, so all files
    #     in the batch either land together or get rolled back together.
    return {
        "status":        "success",
        "filename":      filename,
        "period":        period,
        "is_new_row":    is_new_row,      # True = no existing DB row for this period
        "extracted":     extracted,        # The 10 extracted values (None where not found)
        "db_comparison": db_comparison,    # Per-field: {db, extracted, match}
        "updated":       not dry_run,     # False in dry-run mode — DB was not written
    }


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/pdf/upload?ticker=<symbol>
#
# Single-file upload. See _process_single_pdf for the per-file logic.
#
# Request format:
#   Content-Type: multipart/form-data
#   Query param:  ticker  (required) — Tadawul symbol e.g. "2222"
#   Query param:  dry_run (optional) — "true"/"1"/"yes" to skip DB writes
#   Form file:    pdf     (required) — the PDF file
#
# Response (200 OK):
#   {
#     "ticker":        "2222",
#     "period":        "2024-annual",
#     "extracted":     { "revenue": 1.23e12, "net_income": ..., ... },
#     "db_comparison": { "revenue": { "db":..., "extracted":..., "match":... }, ... },
#     "is_new_row":    false,
#     "updated":       true,
#     "dry_run":       false
#   }
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

    # ── Delegate to the shared helper ──────────────────────────────────────
    result = _process_single_pdf(stock, pdf_file, dry_run)

    # If the helper returned an error (extraction failure, empty filename),
    # surface it with a 4xx/5xx-style envelope but keep 200 + status=error
    # in the body — matches how /upload_batch reports per-file errors.
    # For backwards-compat with the previous /upload response shape, we still
    # return 422 on extraction failures and 400 on validation failures.
    if result["status"] == "error":
        # Empty filename → 400; everything else (extraction crash) → 422.
        # The previous /upload behaviour returned these same codes, so this
        # keeps Postman / curl callers seeing the same error semantics.
        status_code = 400 if result["error"].startswith("Empty filename") else 422
        return jsonify({"error": result["error"]}), status_code

    # ── Commit or rollback ─────────────────────────────────────────────────
    # In single-file mode, the helper has staged any DB changes on the
    # session but hasn't committed. We commit here so /upload remains
    # exactly equivalent to its pre-refactor behaviour.
    if dry_run:
        db.session.rollback()
    else:
        db.session.commit()

    # ── Build the response (same shape as before the refactor) ─────────────
    return jsonify({
        "ticker":        ticker,
        "period":        result["period"],
        "is_new_row":    result["is_new_row"],
        "extracted":     result["extracted"],
        "db_comparison": result["db_comparison"],
        "updated":       result["updated"],
        "dry_run":       dry_run,
    })


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/pdf/upload_batch?ticker=<symbol>
#
# Multi-file upload. Accepts MULTIPLE PDFs under the form field name 'pdf'
# (all for the same ticker). Each PDF is processed independently — if one
# fails extraction, the rest still run.
#
# Typical use:
#   - Upload several years of annual reports for the same company in one call.
#   - Each PDF's fiscal year is auto-detected, so they land in different
#     period rows (e.g. 2022-annual, 2023-annual, 2024-annual).
#
# Request format:
#   Content-Type: multipart/form-data
#   Query param:  ticker  (required) — Tadawul symbol e.g. "2222"
#   Query param:  dry_run (optional) — "true"/"1"/"yes" to skip DB writes
#                                       for the WHOLE batch
#   Form file:    pdf     (required, repeatable) — one or more PDF files
#
# Response (200 OK):
#   {
#     "ticker":       "2222",
#     "total_files":  3,
#     "successful":   2,
#     "failed":       1,
#     "dry_run":      false,
#     "results": [
#       {
#         "status":        "success",
#         "filename":      "aramco_2024.pdf",
#         "period":        "2024-annual",
#         "is_new_row":    false,
#         "extracted":     { ... },
#         "db_comparison": { ... },
#         "updated":       true
#       },
#       {
#         "status":   "error",
#         "filename": "broken.pdf",
#         "error":    "PDF extraction failed: ..."
#       },
#       ...
#     ]
#   }
#
# Transaction semantics:
#   - All successful files commit together at the end (one db.session.commit).
#   - If dry_run=true, the session is rolled back instead.
#   - A failing file does NOT roll back successful files in the same batch —
#     the failure is reported in its per-file result and the rest still commit.
# ─────────────────────────────────────────────────────────────────────────────
@pdf_bp.route('/upload_batch', methods=['POST'])
def upload_pdf_batch():

    # ── Validate the ticker query parameter ───────────────────────────────
    ticker = request.args.get('ticker', '').strip()
    if not ticker:
        return jsonify({"error": "ticker query parameter is required (e.g. ?ticker=2222)"}), 400

    # Same dry_run semantics as /upload — applies to the whole batch.
    dry_run = request.args.get('dry_run', '').strip().lower() in ('true', '1', 'yes')

    stock = Stock.query.filter_by(symbol=ticker).first()
    if stock is None:
        return jsonify({"error": f"Stock {ticker} not found. Add it first via POST /api/stocks/"}), 404

    # ── Validate that at least one PDF was uploaded ────────────────────────
    # request.files.getlist('pdf') returns a list of FileStorage objects —
    # one per form field repetition. Empty list = no files attached.
    pdf_files = request.files.getlist('pdf')
    if not pdf_files:
        return jsonify({
            "error": "No files found. Send one or more PDFs in form field(s) named 'pdf'"
        }), 400

    # ── Process each PDF independently ─────────────────────────────────────
    # The helper does NOT commit/rollback the session — it only stages
    # changes. We commit ONCE at the end for the whole batch so that either
    # all successful files land together or (in dry_run) none of them do.
    results = []
    successful_count = 0
    failed_count = 0

    for pdf_file in pdf_files:
        result = _process_single_pdf(stock, pdf_file, dry_run)
        results.append(result)
        if result["status"] == "success":
            successful_count += 1
        else:
            failed_count += 1

    # ── Commit / rollback the whole batch ──────────────────────────────────
    # If dry_run is on, throw away every staged change.
    # Otherwise commit all successful files' upserts in one transaction.
    # Note: failed files never wrote to the session in the first place
    # (the helper returned early before reaching setattr), so they don't
    # contaminate the commit.
    if dry_run:
        db.session.rollback()
    else:
        db.session.commit()

    return jsonify({
        "ticker":      ticker,
        "total_files": len(pdf_files),
        "successful":  successful_count,
        "failed":      failed_count,
        "dry_run":     dry_run,
        "results":     results,
    })
