# valuations.py — API endpoint for stock fair-value computations
#
# URL prefix (registered in api/__init__.py): /api/valuations
#
# Endpoints:
#   GET /api/valuations/<ticker>  — return DCF / P/E / P/B blend for one stock
#
# Strategy: DB-first, compute on demand if missing.
#   1. Check the valuations table for a pre-computed row (populated by
#      the offline runner script backend/run_valuations.py).
#   2. If no row exists, compute fresh via valuation_engine.value_stock(),
#      persist the result so future calls are instant, then return it.
#
# This means the first call for a newly-added stock is slightly slower
# (it runs the full DCF + P/E + P/B pipeline), but every subsequent call
# reads from the DB instantly.

from flask import Blueprint, jsonify
from app.extensions import db
from app.models.stock import Stock
from app.models.valuation import Valuation
from app.services.valuation_engine import value_stock

valuations_bp = Blueprint('valuations', __name__)


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/valuations/<ticker>
# Returns the blended fair value for one stock.
#
# Response fields:
#   symbol, name_en, market_price  — stock identity + current price
#   dcf_value    — Discounted Cash Flow fair value per share (SAR)
#   pe_value     — P/E-based fair value per share (SAR)
#   pb_value     — P/B-based fair value per share (SAR)
#   fair_value   — Sector-weighted blend of the three models (SAR)
#   status       — "undervalued" / "fair" / "overvalued" (±10% band)
#   calculated_at — ISO timestamp of when this valuation was computed
#   source       — "db" if read from pre-computed row, "computed" if fresh
#
# Any of dcf_value / pe_value / pb_value can be null when inputs are
# missing or produce unrealistic results (>3× market price cap applied
# by the valuation engine). fair_value is null only if all three fail.
# ─────────────────────────────────────────────────────────────────────────────
@valuations_bp.route('/<ticker>', methods=['GET'])
def get_valuation(ticker):
    # Look up stock by Tadawul symbol
    stock = Stock.query.filter_by(symbol=ticker).first()
    if stock is None:
        return jsonify({"error": f"Stock {ticker} not found"}), 404

    # ── Step 1: Try the pre-computed valuations table ──────────────────────
    # The offline runner (run_valuations.py) pre-computes all 48 stocks and
    # writes results here. We take the most recent row in case the runner
    # has been executed more than once (e.g. after a market price update).
    latest_val = (
        Valuation.query
        .filter_by(stock_id=stock.id)
        .order_by(Valuation.calculated_at.desc())
        .first()
    )

    source = "db"  # Track where the result came from for transparency

    if latest_val is None:
        # ── Step 2: Compute fresh and persist ─────────────────────────────
        # value_stock() runs DCF (advanced → simple fallback) + P/E + P/B,
        # blends them with the sector's weights, and classifies the result.
        # Returns a plain dict — no DB writes inside value_stock itself.
        computed = value_stock(stock)

        latest_val = Valuation(
            stock_id=     stock.id,
            dcf_value=    computed["dcf_value"],
            pe_value=     computed["pe_value"],
            pb_value=     computed["pb_value"],
            fair_value=   computed["fair_value"],
            market_price= computed["market_price"],
            status=       computed["status"],
            # calculated_at defaults to utcnow() via the model column definition
        )
        db.session.add(latest_val)
        db.session.commit()
        source = "computed"  # Let the caller know this was a fresh computation

    return jsonify({
        "symbol":        stock.symbol,
        "name_en":       stock.name_en,
        "name_ar":       stock.name_ar,
        "market_price":  stock.market_price,

        # Individual model outputs (any can be null)
        "dcf_value":     latest_val.dcf_value,
        "pe_value":      latest_val.pe_value,
        "pb_value":      latest_val.pb_value,

        # Final blended fair value and verdict
        "fair_value":    latest_val.fair_value,
        "status":        latest_val.status,

        "calculated_at": latest_val.calculated_at.isoformat() if latest_val.calculated_at else None,
        "source":        source,  # "db" = pre-computed, "computed" = just calculated now
    })
