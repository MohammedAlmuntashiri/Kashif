# financial_data.py — Endpoints for manually correcting financial_data rows
#
# URL prefix (registered in api/__init__.py): /api/financial_data
#
# Endpoint:
#   PATCH /api/financial_data/<ticker>/<period>
#     — Manually update one or more financial fields for a specific
#       (ticker, period) row. Used after Gemini verification reveals the
#       extractor and/or DB seed are wrong and you have the correct value.
#     — Only the fields you include in the body are updated; other fields
#       are left untouched. Pass null to clear a field.
#     — Every changed field is logged to accuracy_log.csv via log_correction.
#
# Why a separate endpoint instead of just updating via /pdf/upload?
#   - You may not have the PDF anymore, but you have Gemini's table.
#   - The extractor might be wrong AND the DB might be wrong — neither
#     /pdf/upload nor a re-run helps. You just need to write the correct
#     value directly.
#
# Request example:
#   PATCH /api/financial_data/2222/2024-annual
#   Content-Type: application/json
#   Body: {
#     "revenue":    2520000000000,
#     "net_income": 454000000000
#   }
#
# Response:
#   {
#     "ticker":          "2222",
#     "period":          "2024-annual",
#     "updated_fields":  ["revenue", "net_income"],
#     "ignored_fields":  [],          ← fields the request had but aren't real columns
#     "changes": {
#       "revenue":    { "before": 2400000000000, "after": 2520000000000 },
#       "net_income": { "before": 454000000000, "after": 454000000000 }
#     },
#     "is_new_row":      false
#   }

from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.stock import Stock
from app.models.financial_data import FinancialData
from app.api.accuracy import log_correction

financial_data_bp = Blueprint('financial_data', __name__)

# Same 10 fields as pdf.py. Duplicated to avoid circular imports.
_FINANCIAL_FIELDS = {
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
}


@financial_data_bp.route('/<ticker>/<period>', methods=['PATCH'])
def patch_financial_data(ticker, period):
    # ── Resolve the stock ──────────────────────────────────────────────────
    stock = Stock.query.filter_by(symbol=ticker).first()
    if stock is None:
        return jsonify({"error": f"Stock {ticker} not found"}), 404

    # ── Parse the JSON body ────────────────────────────────────────────────
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not payload:
        return jsonify({
            "error": "Request body must be a non-empty JSON object of {field: value}"
        }), 400

    # Separate valid fields from unknown ones — be forgiving and report
    # ignored keys in the response so the caller can see typos.
    updates = {}
    ignored = []
    for key, value in payload.items():
        if key in _FINANCIAL_FIELDS:
            updates[key] = value
        else:
            ignored.append(key)

    if not updates:
        return jsonify({
            "error":           "No valid financial fields in body",
            "valid_fields":    sorted(_FINANCIAL_FIELDS),
            "ignored_fields":  ignored,
        }), 400

    # ── Coerce values to float (or None) ────────────────────────────────────
    # Postman JSON might send numbers as strings sometimes. Be tolerant.
    coerced = {}
    for field, raw in updates.items():
        if raw is None:
            coerced[field] = None
            continue
        try:
            coerced[field] = float(raw)
        except (TypeError, ValueError):
            return jsonify({
                "error": f"Field {field}: cannot convert {raw!r} to a number"
            }), 400

    # ── Find or create the row ─────────────────────────────────────────────
    fd = FinancialData.query.filter_by(stock_id=stock.id, period=period).first()
    if fd is None:
        fd = FinancialData(stock_id=stock.id, period=period)
        db.session.add(fd)
        is_new_row = True
    else:
        is_new_row = False

    # ── Apply the updates, recording before→after for the accuracy log ─────
    changes = {}
    for field, new_val in coerced.items():
        before = getattr(fd, field)
        setattr(fd, field, new_val)
        changes[field] = {"before": before, "after": new_val}

    db.session.commit()

    # ── Log to accuracy CSV ────────────────────────────────────────────────
    # Best-effort — don't fail the request if logging crashes.
    try:
        log_correction(ticker=ticker, period=period, field_changes=changes, source="manual_patch")
    except Exception:
        pass

    return jsonify({
        "ticker":          ticker,
        "period":          period,
        "updated_fields":  list(coerced.keys()),
        "ignored_fields":  ignored,
        "changes":         changes,
        "is_new_row":      is_new_row,
    })
