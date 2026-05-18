# pdf.py — API endpoints for uploading and processing financial-statement PDFs
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
#       independently — if one fails, the others still run.
#     — Part 14.2: parallel extraction via ThreadPoolExecutor (default 4 workers).
#       4-8× speed-up when uploading multiple PDFs.
#
# Shared query params (work on BOTH endpoints):
#   ticker                  REQUIRED  Tadawul symbol (e.g. "2222")
#   dry_run=true            optional  Don't write anything to DB. Useful for previewing.
#   auto_commit_if_match    optional  "Smart save" mode — only commits to DB when
#                                     all extracted (non-null) values match the existing
#                                     DB row within 1% tolerance. If ANY field mismatches,
#                                     this file is left as dry-run and the response flags
#                                     it for manual review. Safer than dry_run=false
#                                     because bad extractions never silently overwrite
#                                     good DB data.
#   workers=<N>             optional  /upload_batch only. Number of parallel workers
#                                     (default 4, clamped to 1-8). Tune per machine.
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
from concurrent.futures import ThreadPoolExecutor
from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.stock import Stock
from app.models.financial_data import FinancialData
from app.services.pdf_extractor import extract_all
# Accuracy log — every PDF upload appends a row per field so we can track
# extractor accuracy over time. Imported lazily inside the function in case
# the accuracy module fails to load (don't break extraction over logging).
from app.api.accuracy import log_extraction

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
# Phase 1 helper — pure PDF extraction (thread-safe, no DB access)
#
# This runs the slow extract_all() pipeline against the uploaded PDF.
# Designed to be called from worker threads in a ThreadPoolExecutor so
# multiple PDFs can extract in parallel. CRITICAL: this function MUST NOT
# touch the SQLAlchemy session (sessions aren't thread-safe).
#
# Steps performed:
#   1. Save the uploaded FileStorage to a temp file on disk (pdfplumber
#      needs a real path, not a Flask stream).
#   2. Call extract_all() — this is the expensive part (~1-3 min per PDF,
#      including OCR for image-heavy reports).
#   3. Pop "_fiscal_year" out of the result and build the period string.
#   4. Always delete the temp file in a finally block.
#
# Returns a dict shaped like:
#   On success:
#     {"status": "extracted", "filename": ..., "period": ..., "extracted": {...10 fields...}}
#   On error:
#     {"status": "error", "filename": ..., "error": "..."}
#
# The caller is responsible for the DB upsert (Phase 2 helper below).
# ─────────────────────────────────────────────────────────────────────────────
def _extract_pdf_only(pdf_file):
    filename = pdf_file.filename or "<unnamed>"

    # Empty filename means the form field was sent without an actual file
    # attached. Treat as a validation error — no point running extraction.
    if filename == '':
        return {
            "status":   "error",
            "filename": filename,
            "error":    "Empty filename — please select a PDF file",
        }

    # NamedTemporaryFile gives us a path on disk; delete=False stops the OS
    # from removing it before pdfplumber opens it. We unlink it ourselves in
    # the finally block below.
    tmp = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    try:
        pdf_file.save(tmp.name)  # Write the uploaded bytes to disk
        tmp.close()              # Close our handle before pdfplumber opens it

        # The expensive call. extract_all() runs:
        #   1. Standard text pass with pdfplumber + OCR fallback
        #   2. Rowwise pass (word-coordinate clustering) for column layouts
        #   3. Picks the best result per field
        #   4. EPS × shares cross-validation
        #   5. Fiscal-year auto-detection
        extracted = extract_all(tmp.name)

    except Exception as exc:
        # In batch mode we don't raise — return an error dict so the caller
        # can include this file in its per-file results array and continue
        # processing the remaining files.
        return {
            "status":   "error",
            "filename": filename,
            "error":    f"PDF extraction failed: {str(exc)}",
        }

    finally:
        # Always clean up the temp file — even if extraction raised.
        try:
            os.unlink(tmp.name)
        except OSError:
            pass  # Already gone or permission issue — not critical

    # Extract the fiscal year (added by extract_all) and build the period string.
    fiscal_year = extracted.pop("_fiscal_year", None)
    period = f"{fiscal_year}-annual" if fiscal_year else "unknown-annual"

    return {
        "status":    "extracted",
        "filename":  filename,
        "period":    period,
        "extracted": extracted,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Phase 2 helper — apply extracted values to the DB (main thread ONLY)
#
# Takes the result from _extract_pdf_only and:
#   1. Looks up the existing FinancialData row for (stock, period)
#   2. Builds the per-field DB comparison
#   3. Decides whether to write the extracted values to the row, based on
#      dry_run + auto_commit_if_match modes:
#        - dry_run=True              → never writes, never commits
#        - auto_commit_if_match=True → writes only if ALL non-null extracted
#                                       values match existing DB values
#        - both false                → always writes (legacy behaviour)
#   4. Logs the extraction to the accuracy CSV (one row per field).
#
# Does NOT commit the SQLAlchemy session — the caller does that once at the
# end (allows batch endpoint to commit all files in a single transaction).
#
# Returns a result dict containing the full per-file response shape.
# ─────────────────────────────────────────────────────────────────────────────
def _apply_extraction_to_db(stock, ticker, extraction_result, dry_run, auto_commit_if_match):
    # Errors from _extract_pdf_only pass through unchanged.
    if extraction_result["status"] == "error":
        return extraction_result

    period    = extraction_result["period"]
    extracted = extraction_result["extracted"]
    filename  = extraction_result["filename"]

    # Look up existing financial_data row. If missing, build a new one.
    fd = (
        FinancialData.query
        .filter_by(stock_id=stock.id, period=period)
        .first()
    )

    if fd is None:
        # No existing row. Build a transient instance — we may or may not
        # add it to the session depending on whether we end up writing.
        fd = FinancialData(stock_id=stock.id, period=period)
        is_new_row = True
    else:
        is_new_row = False

    # Build the per-field DB comparison FIRST, before any writes, so the
    # "db" field in the response shows the BEFORE state.
    db_comparison = {}
    all_match = True  # Tracks whether every non-null extracted value matches DB

    for field in _FINANCIAL_FIELDS:
        db_val  = getattr(fd, field)
        ext_val = extracted.get(field)

        match = _values_match(db_val, ext_val)
        db_comparison[field] = {
            "db":        db_val,
            "extracted": ext_val,
            "match":     match,
        }

        # For auto_commit_if_match logic: ignore fields where extractor
        # returned None (those don't overwrite anyway). Only count fields
        # where extractor has a value but it doesn't match DB.
        if ext_val is not None and not match:
            all_match = False

    # ── Decide whether to write to DB ──────────────────────────────────────
    # Three modes:
    #   1. dry_run=true                 → never write
    #   2. auto_commit_if_match=true    → write only if all_match is True
    #   3. neither flag                 → always write (legacy)
    if dry_run:
        will_write = False
        write_reason = "dry_run"
    elif auto_commit_if_match:
        if all_match:
            will_write = True
            write_reason = "auto_commit_match"
        else:
            # Mismatch detected — refuse to overwrite good DB data.
            will_write = False
            write_reason = "flagged_mismatch"
    else:
        will_write = True
        write_reason = "normal_write"

    # ── Apply writes (or not) ──────────────────────────────────────────────
    if will_write:
        if is_new_row:
            db.session.add(fd)
        for field in _FINANCIAL_FIELDS:
            ext_val = extracted.get(field)
            # Skip None — preserves existing good DB values when extractor
            # couldn't find something.
            if ext_val is not None:
                setattr(fd, field, ext_val)

    # ── Log this extraction to the accuracy CSV ────────────────────────────
    # One row per field. Don't crash extraction if logging fails.
    try:
        log_extraction(
            ticker=ticker,
            period=period,
            filename=filename,
            db_comparison=db_comparison,
            committed=will_write,
        )
    except Exception:
        # Logging is best-effort — if the CSV file is locked or the disk is
        # full, we still return a valid extraction response.
        pass

    return {
        "status":         "success",
        "filename":       filename,
        "period":         period,
        "is_new_row":     is_new_row,
        "extracted":      extracted,
        "db_comparison":  db_comparison,
        "all_match":      all_match,
        "committed":      will_write,
        "commit_reason":  write_reason,
    }


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/pdf/upload?ticker=<symbol>
#
# Single-file upload. See _extract_pdf_only + _apply_extraction_to_db for
# the per-file logic.
#
# Query params: ticker (required), dry_run, auto_commit_if_match.
#
# Response (200 OK):
#   {
#     "ticker":        "2222",
#     "period":        "2024-annual",
#     "extracted":     { "revenue": 1.23e12, ... },
#     "db_comparison": { "revenue": { "db":..., "extracted":..., "match":... }, ... },
#     "is_new_row":    false,
#     "all_match":     true,
#     "committed":     true,
#     "commit_reason": "auto_commit_match",
#     "dry_run":       false
#   }
# ─────────────────────────────────────────────────────────────────────────────
@pdf_bp.route('/upload', methods=['POST'])
def upload_pdf():

    ticker = request.args.get('ticker', '').strip()
    if not ticker:
        return jsonify({"error": "ticker query parameter is required (e.g. ?ticker=2222)"}), 400

    dry_run = request.args.get('dry_run', '').strip().lower() in ('true', '1', 'yes')
    auto_commit_if_match = request.args.get('auto_commit_if_match', '').strip().lower() in ('true', '1', 'yes')

    stock = Stock.query.filter_by(symbol=ticker).first()
    if stock is None:
        return jsonify({"error": f"Stock {ticker} not found. Add it first via POST /api/stocks/"}), 404

    if 'pdf' not in request.files:
        return jsonify({"error": "No file found. Send the PDF in a form field named 'pdf'"}), 400

    pdf_file = request.files['pdf']

    # Phase 1: extract (slow). For single-file uploads we just call directly
    # — no thread pool needed.
    extraction_result = _extract_pdf_only(pdf_file)

    # Phase 2: apply to DB (fast, main thread).
    result = _apply_extraction_to_db(stock, ticker, extraction_result, dry_run, auto_commit_if_match)

    # If extraction errored, surface a 4xx/5xx — matches pre-refactor behaviour.
    if result["status"] == "error":
        status_code = 400 if result["error"].startswith("Empty filename") else 422
        return jsonify({"error": result["error"]}), status_code

    # ── Commit or rollback the staged changes ──────────────────────────────
    # If we wrote anything in Phase 2, commit. Otherwise rollback to drop
    # any transient SQLAlchemy state.
    if result["committed"]:
        db.session.commit()
    else:
        db.session.rollback()

    return jsonify({
        "ticker":         ticker,
        "period":         result["period"],
        "is_new_row":     result["is_new_row"],
        "extracted":      result["extracted"],
        "db_comparison":  result["db_comparison"],
        "all_match":      result["all_match"],
        "committed":      result["committed"],
        "commit_reason":  result["commit_reason"],
        "dry_run":        dry_run,
    })


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/pdf/upload_batch?ticker=<symbol>
#
# Multi-file upload. Accepts multiple PDFs under repeated form field 'pdf'.
# Phase 1 (extraction) runs in parallel via ThreadPoolExecutor.
# Phase 2 (DB upsert) runs sequentially on the main thread.
#
# Query params: ticker (required), dry_run, auto_commit_if_match, workers (1-8).
#
# Response (200 OK):
#   {
#     "ticker":       "2222",
#     "total_files":  3,
#     "successful":   2,
#     "failed":       1,
#     "committed":    2,           # how many files actually wrote to DB
#     "flagged":      0,           # files with mismatches in auto_commit_if_match mode
#     "workers":      4,
#     "dry_run":      false,
#     "results":      [ ... per-file result dicts ... ]
#   }
# ─────────────────────────────────────────────────────────────────────────────
@pdf_bp.route('/upload_batch', methods=['POST'])
def upload_pdf_batch():

    ticker = request.args.get('ticker', '').strip()
    if not ticker:
        return jsonify({"error": "ticker query parameter is required (e.g. ?ticker=2222)"}), 400

    dry_run = request.args.get('dry_run', '').strip().lower() in ('true', '1', 'yes')
    auto_commit_if_match = request.args.get('auto_commit_if_match', '').strip().lower() in ('true', '1', 'yes')

    # Worker count — default 4, clamped to [1, 8]. 8 is the upper bound
    # because pdfplumber + pytesseract are CPU-bound and most dev machines
    # are 4-8 cores. Higher than 8 = context switching overhead with no gain.
    try:
        workers = int(request.args.get('workers', 4))
    except ValueError:
        workers = 4
    workers = max(1, min(workers, 8))

    stock = Stock.query.filter_by(symbol=ticker).first()
    if stock is None:
        return jsonify({"error": f"Stock {ticker} not found. Add it first via POST /api/stocks/"}), 404

    pdf_files = request.files.getlist('pdf')
    if not pdf_files:
        return jsonify({
            "error": "No files found. Send one or more PDFs in form field(s) named 'pdf'"
        }), 400

    # ── Phase 1: extract all PDFs in PARALLEL ──────────────────────────────
    # Workers run _extract_pdf_only which has no DB access — safe to thread.
    # We use list(executor.map(...)) instead of submit() so results come back
    # in the SAME ORDER as the input files (important for predictable response).
    #
    # CPU note: pdfplumber + pytesseract release the GIL during the heavy
    # operations (file I/O, subprocess for tesseract OCR), so threads —
    # not processes — give real parallelism here without the overhead of
    # multiprocessing.
    with ThreadPoolExecutor(max_workers=workers) as executor:
        extraction_results = list(executor.map(_extract_pdf_only, pdf_files))

    # ── Phase 2: apply each extraction to DB (sequential, main thread) ─────
    # SQLAlchemy session lives on the main thread. Each call stages writes
    # on the same session — we commit ONCE at the end so all successful
    # files land together (or all roll back in dry_run mode).
    results = []
    successful_count = 0
    failed_count = 0
    committed_count = 0
    flagged_count = 0

    for ext_result in extraction_results:
        result = _apply_extraction_to_db(stock, ticker, ext_result, dry_run, auto_commit_if_match)
        results.append(result)

        if result["status"] == "success":
            successful_count += 1
            if result["committed"]:
                committed_count += 1
            elif result.get("commit_reason") == "flagged_mismatch":
                flagged_count += 1
        else:
            failed_count += 1

    # ── Commit / rollback once for the whole batch ─────────────────────────
    # If ANY file ended up writing (committed=True), commit the session.
    # In dry_run mode (or if every file was flagged), rollback.
    if committed_count > 0:
        db.session.commit()
    else:
        db.session.rollback()

    return jsonify({
        "ticker":      ticker,
        "total_files": len(pdf_files),
        "successful":  successful_count,
        "failed":      failed_count,
        "committed":   committed_count,
        "flagged":     flagged_count,
        "workers":     workers,
        "dry_run":     dry_run,
        "results":     results,
    })
