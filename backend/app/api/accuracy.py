# accuracy.py — Accuracy tracking for the PDF extractor
#
# URL prefix (registered in api/__init__.py): /api/accuracy
#
# This module maintains a CSV file that records every PDF extraction and
# every manual correction, so we can answer questions like:
#   - "How accurate is the extractor across all the companies I've tested?"
#   - "Which field fails most often?"
#   - "Which companies need the most manual corrections?"
#
# The CSV file lives at: backend/accuracy_log.csv (gitignored).
# Each row has these columns:
#   timestamp           ISO 8601 e.g. 2026-05-12T14:23:01
#   action              "extract" (from /upload) or "correct" (from PATCH) or "verify" (from /accuracy/log)
#   ticker              e.g. "2222"
#   period              e.g. "2024-annual"
#   filename            e.g. "aramco_2024.pdf" (empty for "correct"/"verify" rows)
#   field               which of the 10 financial fields
#   extracted           value returned by the PDF extractor (may be empty for non-"extract" rows)
#   db_before           DB value before this action
#   db_after            DB value after this action (same as db_before if not committed)
#   gemini              ground-truth value from Gemini (empty unless action=="verify")
#   extractor_correct   "yes"/"no"/"" — whether extracted matches gemini (only when action=="verify")
#   db_correct          "yes"/"no"/"" — whether db_before matches gemini (only when action=="verify")
#   committed           "yes"/"no" — whether DB was actually written
#   notes               free-text reason / commit_reason
#
# Endpoints exposed:
#   POST /api/accuracy/log    — record Gemini verification for one company+period
#   GET  /api/accuracy/report — aggregated stats across all logged rows

import csv
import os
import threading
from datetime import datetime
from flask import Blueprint, jsonify, request
from app.models.stock import Stock
from app.models.financial_data import FinancialData

accuracy_bp = Blueprint('accuracy', __name__)

# CSV path — sits inside /app inside the container (which maps to backend/
# on the host). Gitignored via the *.csv pattern in .gitignore (or we'll
# add it explicitly).
_LOG_PATH = '/app/accuracy_log.csv'

# A simple lock to serialize writes across requests. Flask's dev server
# uses threads to handle requests, so two simultaneous uploads could
# interleave their writes and corrupt the CSV. The lock keeps it sane.
_log_lock = threading.Lock()

# CSV column order — fixed for the lifetime of the file. If you add a
# new column, append it at the END and bump _CSV_VERSION (not currently
# tracked, but worth knowing).
_CSV_COLUMNS = [
    "timestamp",
    "action",
    "ticker",
    "period",
    "filename",
    "field",
    "extracted",
    "db_before",
    "db_after",
    "gemini",
    "extractor_correct",
    "db_correct",
    "committed",
    "notes",
]

# Same 10 fields as the extractor knows about. Duplicated here so this
# module has no import dependency on pdf.py (avoids circular imports).
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


def _ensure_log_file():
    """Create the CSV with header row if it doesn't exist yet.

    Called by every logging function before writing. Idempotent — no-op
    if the file already exists.
    """
    if not os.path.exists(_LOG_PATH):
        with open(_LOG_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(_CSV_COLUMNS)


def _append_rows(rows):
    """Append a list of row-dicts to the CSV. Thread-safe via _log_lock."""
    with _log_lock:
        _ensure_log_file()
        with open(_LOG_PATH, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=_CSV_COLUMNS)
            for row in rows:
                # Fill missing keys with empty string so DictWriter doesn't crash.
                writer.writerow({col: row.get(col, "") for col in _CSV_COLUMNS})


# ─────────────────────────────────────────────────────────────────────────────
# Public function — log_extraction
#
# Called by pdf.py after each PDF is processed (single or batch).
# Writes ONE row per financial field (10 rows per PDF).
#
# Parameters:
#   ticker         Tadawul symbol
#   period         e.g. "2024-annual"
#   filename       Original PDF filename
#   db_comparison  Dict from _apply_extraction_to_db — per-field {db, extracted, match}
#   committed      bool — whether the extraction was actually written to DB
# ─────────────────────────────────────────────────────────────────────────────
def log_extraction(ticker, period, filename, db_comparison, committed):
    timestamp = datetime.utcnow().isoformat()
    committed_str = "yes" if committed else "no"

    rows = []
    for field in _FINANCIAL_FIELDS:
        cell = db_comparison.get(field, {})
        db_val  = cell.get("db")
        ext_val = cell.get("extracted")
        match   = cell.get("match", False)

        # db_after = the value now in the DB. If committed and extracted is
        # not None, the new value is ext_val. Otherwise it stayed as db_val.
        db_after = ext_val if (committed and ext_val is not None) else db_val

        rows.append({
            "timestamp":         timestamp,
            "action":            "extract",
            "ticker":            ticker,
            "period":            period,
            "filename":          filename,
            "field":             field,
            "extracted":         "" if ext_val is None else str(ext_val),
            "db_before":         "" if db_val is None else str(db_val),
            "db_after":          "" if db_after is None else str(db_after),
            "gemini":            "",
            "extractor_correct": "",       # unknown without Gemini
            "db_correct":        "",       # unknown without Gemini
            "committed":         committed_str,
            "notes":             "match" if match else "mismatch",
        })

    _append_rows(rows)


# ─────────────────────────────────────────────────────────────────────────────
# Public function — log_correction
#
# Called by financial_data.py's PATCH endpoint after manual fixes. Writes
# ONE row per field that was corrected.
# ─────────────────────────────────────────────────────────────────────────────
def log_correction(ticker, period, field_changes, source="manual"):
    """field_changes: dict of {field_name: {"before": x, "after": y}} """
    timestamp = datetime.utcnow().isoformat()
    rows = []
    for field, change in field_changes.items():
        rows.append({
            "timestamp":         timestamp,
            "action":            "correct",
            "ticker":            ticker,
            "period":            period,
            "filename":          "",
            "field":             field,
            "extracted":         "",
            "db_before":         "" if change.get("before") is None else str(change["before"]),
            "db_after":          "" if change.get("after")  is None else str(change["after"]),
            "gemini":            "",
            "extractor_correct": "",
            "db_correct":        "",
            "committed":         "yes",
            "notes":             f"patched from {source}",
        })
    _append_rows(rows)


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/accuracy/log?ticker=<symbol>&period=<period>
#
# Record a Gemini verification for one company+period. The caller (you)
# sends the ground-truth values you got from Gemini in the request body.
# The endpoint reads the current DB values, compares against the Gemini
# values, and writes 10 rows to the CSV — one per field.
#
# Request:
#   POST /api/accuracy/log?ticker=2222&period=2024-annual
#   Content-Type: application/json
#   Body: {
#     "revenue":      2520000000000,
#     "net_income":   454000000000,
#     "eps":          1.87,
#     "total_assets": null,        ← null = Gemini couldn't find this field
#     ...
#   }
#
# Response:
#   {
#     "ticker":          "2222",
#     "period":          "2024-annual",
#     "rows_logged":     10,
#     "summary": {
#       "db_correct_count":      8,
#       "db_incorrect_count":    2,
#       "fields_with_mismatch":  ["revenue", "net_income"]
#     }
#   }
# ─────────────────────────────────────────────────────────────────────────────
@accuracy_bp.route('/log', methods=['POST'])
def log_verification():
    ticker = request.args.get('ticker', '').strip()
    period = request.args.get('period', '').strip()
    if not ticker or not period:
        return jsonify({"error": "ticker and period query parameters are required"}), 400

    stock = Stock.query.filter_by(symbol=ticker).first()
    if stock is None:
        return jsonify({"error": f"Stock {ticker} not found"}), 404

    fd = FinancialData.query.filter_by(stock_id=stock.id, period=period).first()
    # If no row exists for this period, we still want to log against Gemini
    # — just treat all db values as None.

    gemini_values = request.get_json(silent=True) or {}

    timestamp = datetime.utcnow().isoformat()
    rows = []
    db_correct_count = 0
    db_incorrect_count = 0
    fields_with_mismatch = []

    for field in _FINANCIAL_FIELDS:
        gemini_val = gemini_values.get(field)
        db_val     = getattr(fd, field) if fd else None

        # Compute db_correct flag — only meaningful if Gemini provided a value.
        db_correct = ""
        if gemini_val is not None:
            if db_val is None:
                db_correct = "no"  # DB has no data but Gemini does
            else:
                try:
                    diff_ratio = abs(db_val - float(gemini_val)) / max(abs(db_val), 1)
                    db_correct = "yes" if diff_ratio <= 0.01 else "no"
                except (TypeError, ValueError):
                    db_correct = "no"

            if db_correct == "yes":
                db_correct_count += 1
            else:
                db_incorrect_count += 1
                fields_with_mismatch.append(field)

        rows.append({
            "timestamp":         timestamp,
            "action":            "verify",
            "ticker":            ticker,
            "period":            period,
            "filename":          "",
            "field":             field,
            "extracted":         "",
            "db_before":         "" if db_val is None else str(db_val),
            "db_after":          "" if db_val is None else str(db_val),
            "gemini":            "" if gemini_val is None else str(gemini_val),
            "extractor_correct": "",
            "db_correct":        db_correct,
            "committed":         "no",
            "notes":             "gemini_verification",
        })

    _append_rows(rows)

    return jsonify({
        "ticker":      ticker,
        "period":      period,
        "rows_logged": len(rows),
        "summary": {
            "db_correct_count":     db_correct_count,
            "db_incorrect_count":   db_incorrect_count,
            "fields_with_mismatch": fields_with_mismatch,
        }
    })


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/accuracy/report
#
# Read the CSV and return aggregated stats.
#
# Response:
#   {
#     "total_rows":            420,
#     "total_extractions":     30,    ← unique (ticker, period) extracts
#     "total_corrections":     8,
#     "total_verifications":   12,
#     "by_field": {
#       "revenue":     { "checked": 30, "matched": 24, "match_rate": "80%" },
#       ...
#     },
#     "by_ticker": {
#       "1150": { "extract_rows": 30, "match_count": 21, "match_rate": "70%" },
#       ...
#     },
#     "worst_fields":     [ "net_income (60%)", "revenue (70%)", ... ],
#     "worst_companies":  [ "1150 (70%)", "5110 (60%)", ... ]
#   }
# ─────────────────────────────────────────────────────────────────────────────
@accuracy_bp.route('/report', methods=['GET'])
def report():
    if not os.path.exists(_LOG_PATH):
        return jsonify({
            "total_rows":           0,
            "total_extractions":    0,
            "total_corrections":    0,
            "total_verifications":  0,
            "message":              "No accuracy log yet. Run an upload to start collecting data."
        })

    # Read every row. CSV size grows slowly (10 rows per PDF), so even after
    # 1000 PDF uploads the file is ~10K rows — trivially readable in memory.
    rows = []
    with _log_lock:
        with open(_LOG_PATH, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

    # Counters.
    extract_rows = [r for r in rows if r["action"] == "extract"]
    correct_rows = [r for r in rows if r["action"] == "correct"]
    verify_rows  = [r for r in rows if r["action"] == "verify"]

    # ── Per-field stats (based on "match"/"mismatch" notes in extract rows) ──
    by_field = {}
    for field in _FINANCIAL_FIELDS:
        field_rows = [r for r in extract_rows if r["field"] == field]
        if not field_rows:
            by_field[field] = {"checked": 0, "matched": 0, "match_rate": "n/a"}
            continue
        matched = sum(1 for r in field_rows if r["notes"] == "match")
        rate = 100.0 * matched / len(field_rows)
        by_field[field] = {
            "checked":    len(field_rows),
            "matched":    matched,
            "match_rate": f"{rate:.0f}%",
        }

    # ── Per-ticker stats ────────────────────────────────────────────────────
    by_ticker = {}
    for r in extract_rows:
        t = r["ticker"]
        if t not in by_ticker:
            by_ticker[t] = {"extract_rows": 0, "match_count": 0}
        by_ticker[t]["extract_rows"] += 1
        if r["notes"] == "match":
            by_ticker[t]["match_count"] += 1
    for t, stats in by_ticker.items():
        rate = 100.0 * stats["match_count"] / stats["extract_rows"]
        stats["match_rate"] = f"{rate:.0f}%"

    # ── Worst-X rankings ───────────────────────────────────────────────────
    # Sort fields by match rate ascending. Skip "n/a" entries.
    field_ranked = sorted(
        [(f, by_field[f]["match_rate"]) for f in by_field if by_field[f]["match_rate"] != "n/a"],
        key=lambda x: int(x[1].rstrip('%')),
    )
    worst_fields = [f"{f} ({r})" for f, r in field_ranked[:5]]

    ticker_ranked = sorted(
        [(t, by_ticker[t]["match_rate"]) for t in by_ticker],
        key=lambda x: int(x[1].rstrip('%')),
    )
    worst_companies = [f"{t} ({r})" for t, r in ticker_ranked[:5]]

    # ── Unique extract events (counted by ticker+period+filename) ───────────
    unique_extracts = len({(r["ticker"], r["period"], r["filename"]) for r in extract_rows})

    # Overall match rate across all extract rows.
    overall_matched = sum(1 for r in extract_rows if r["notes"] == "match")
    overall_rate = (100.0 * overall_matched / len(extract_rows)) if extract_rows else 0.0

    return jsonify({
        "total_rows":            len(rows),
        "total_extractions":     unique_extracts,
        "total_corrections":     len(correct_rows),
        "total_verifications":   len(verify_rows),
        "overall_match_rate":    f"{overall_rate:.0f}%",
        "by_field":              by_field,
        "by_ticker":             by_ticker,
        "worst_fields":          worst_fields,
        "worst_companies":       worst_companies,
    })
