# sectors.py — API endpoint for sector metadata
#
# URL prefix (registered in api/__init__.py): /api/sectors
#
# Endpoints:
#   GET /api/sectors/   — list all Tadawul sectors with their valuation weights
#                         and how many stocks belong to each sector.
#
# Note: This endpoint returns sector *metadata* only (names, weights, counts).
#       For per-stock ratios and sector ranking tables, use /api/comparisons.

from flask import Blueprint, jsonify
from app.models.sector import Sector
from app.models.stock import Stock

sectors_bp = Blueprint('sectors', __name__)


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/sectors/
# Returns every sector in the database with:
#   - Arabic and English names
#   - Valuation model weights (DCF / P/E / P/B), which must sum to 1.0
#   - stock_count: how many stocks currently belong to this sector
#
# The weights differ by sector because different industries are valued
# differently. Example:
#   Banks       → dcf=0.20, pe=0.40, pb=0.40  (asset-heavy, P/B matters more)
#   Energy      → dcf=0.50, pe=0.30, pb=0.20  (cash-flow driven like Aramco)
#   Consumer    → dcf=0.40, pe=0.40, pb=0.20
# ─────────────────────────────────────────────────────────────────────────────
@sectors_bp.route('/', methods=['GET'])
def list_sectors():
    # Load all sectors — there are typically 10–15 Tadawul sector categories.
    sectors = Sector.query.all()

    result = []
    for sector in sectors:
        # Count how many stocks belong to this sector.
        # Using COUNT at the DB level is more efficient than loading all stock rows.
        stock_count = Stock.query.filter_by(sector_id=sector.id).count()

        result.append({
            "id":          sector.id,
            "name_en":     sector.name_en,   # e.g. "Banks"
            "name_ar":     sector.name_ar,   # e.g. "البنوك"

            # Valuation model weights — these are set at seed time per Tadawul
            # sector conventions and used by the valuation engine when blending
            # DCF + P/E + P/B into a single fair value.
            "dcf_weight":  sector.dcf_weight,
            "pe_weight":   sector.pe_weight,
            "pb_weight":   sector.pb_weight,

            # Number of stocks in this sector currently in the DB.
            # Grows as users add new stocks via POST /api/stocks/.
            "stock_count": stock_count,
        })

    return jsonify(result)
