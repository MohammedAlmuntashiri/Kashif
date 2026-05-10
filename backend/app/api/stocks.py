# stocks.py — API endpoints for browsing and creating stocks
#
# URL prefix (registered in api/__init__.py): /api/stocks
#
# Endpoints:
#   GET  /api/stocks/           — list all stocks with basic summary data
#   GET  /api/stocks/<ticker>   — full detail for one stock (financials + valuation)
#   POST /api/stocks/           — add a new stock to the database

from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.stock import Stock
from app.models.sector import Sector
from app.models.financial_data import FinancialData
from app.models.valuation import Valuation

stocks_bp = Blueprint('stocks', __name__)

# The 10 financial values we store per period.
# Used to serialize FinancialData rows consistently in both endpoints.
_FINANCIAL_FIELDS = [
    "revenue", "net_income", "eps", "total_assets",
    "total_borrowings", "shareholders_equity", "cash_and_equivalents",
    "free_cash_flow", "dividends_per_share", "shares_outstanding",
]


def _fd_to_dict(fd):
    """Convert a FinancialData ORM row to a plain dict for JSON output.

    Includes the period string (e.g. "2024-annual", "2024-Q1") plus all
    10 financial values. None is preserved for fields that were never
    extracted or seeded — the frontend should display these as "N/A".
    """
    return {
        "period": fd.period,
        # Unpack all 10 financial fields dynamically so we never miss one
        # if new columns are added to the model in future phases.
        **{field: getattr(fd, field) for field in _FINANCIAL_FIELDS},
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/stocks/
# Returns a lightweight list of all stocks — enough for a stock-list page.
# Includes only the most recent period's revenue/net_income/EPS so the
# frontend can show a quick snapshot without loading all historical rows.
# ─────────────────────────────────────────────────────────────────────────────
@stocks_bp.route('/', methods=['GET'])
def list_stocks():
    # Load every stock in the database.
    # Currently 48 seeded stocks; grows as users add more via POST.
    stocks = Stock.query.all()

    result = []
    for stock in stocks:
        # Fetch only the single latest financial_data row per stock.
        # We order by period descending — "2024-annual" sorts after "2023-annual"
        # because the string comparison works correctly for our naming convention.
        latest_fd = (
            FinancialData.query
            .filter_by(stock_id=stock.id)
            .order_by(FinancialData.period.desc())
            .first()
        )

        entry = {
            "symbol":        stock.symbol,       # Tadawul ticker e.g. "2222"
            "name_en":       stock.name_en,       # English name e.g. "Saudi Aramco"
            "name_ar":       stock.name_ar,       # Arabic name
            "sector":        stock.sector.name_en,# Sector name via lazy-loaded relationship
            "market_price":  stock.market_price,  # Current price in SAR (None if not set)

            # Latest period snapshot — None for stocks with no financial data yet
            "latest_period": latest_fd.period      if latest_fd else None,
            "revenue":       latest_fd.revenue     if latest_fd else None,
            "net_income":    latest_fd.net_income  if latest_fd else None,
            "eps":           latest_fd.eps         if latest_fd else None,
        }
        result.append(entry)

    return jsonify(result)


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/stocks/<ticker>
# Full detail for one stock: all historical financial periods + latest valuation.
# Used by the stock-detail page.
# ─────────────────────────────────────────────────────────────────────────────
@stocks_bp.route('/<ticker>', methods=['GET'])
def stock_detail(ticker):
    # Look up the stock by its Tadawul symbol (e.g. "2222" for Aramco).
    stock = Stock.query.filter_by(symbol=ticker).first()
    if stock is None:
        return jsonify({"error": f"Stock {ticker} not found"}), 404

    # Build the full financial history — all periods, newest first.
    # stock.financial_data is a lazy-loaded list of all FinancialData rows
    # for this stock. We sort in Python rather than SQL because the list is
    # already loaded by the relationship and is typically small (4–5 rows).
    financials = [
        _fd_to_dict(fd)
        for fd in sorted(stock.financial_data, key=lambda f: f.period, reverse=True)
    ]

    # Fetch the most recently computed valuation row from the valuations table.
    # The runner script (run_valuations.py) populates this table; the valuation
    # API endpoint (/api/valuations/<ticker>) can also compute on-demand and save.
    latest_val = (
        Valuation.query
        .filter_by(stock_id=stock.id)
        .order_by(Valuation.calculated_at.desc())
        .first()
    )

    # Serialize valuation — None if the runner hasn't been executed yet.
    valuation = None
    if latest_val:
        valuation = {
            "dcf_value":     latest_val.dcf_value,   # Discounted Cash Flow fair value
            "pe_value":      latest_val.pe_value,     # Price-to-Earnings fair value
            "pb_value":      latest_val.pb_value,     # Price-to-Book fair value
            "fair_value":    latest_val.fair_value,   # Blended fair value (sector-weighted)
            "market_price":  latest_val.market_price, # Snapshot of market price at calc time
            "status":        latest_val.status,       # "undervalued" / "fair" / "overvalued"
            "calculated_at": latest_val.calculated_at.isoformat() if latest_val.calculated_at else None,
        }

    return jsonify({
        "symbol":      stock.symbol,
        "name_en":     stock.name_en,
        "name_ar":     stock.name_ar,
        "sector":      stock.sector.name_en,
        "sector_id":   stock.sector_id,   # Included so the frontend can link to sector data
        "market_price": stock.market_price,
        "financials":  financials,        # List of dicts, newest period first
        "valuation":   valuation,         # None if not yet computed
    })


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/stocks/
# Add a new stock to the database.
# Required JSON body fields: symbol, name_en, name_ar, + sector_id OR sector
# Optional: market_price
#
# Example body:
#   {
#     "symbol":       "4200",
#     "name_en":      "Al Babtain Power",
#     "name_ar":      "البابطين للطاقة",
#     "sector":       "Energy",
#     "market_price": 45.20
#   }
# ─────────────────────────────────────────────────────────────────────────────
@stocks_bp.route('/', methods=['POST'])
def create_stock():
    # Parse JSON body — return empty dict on malformed JSON so we give a clean error.
    data = request.get_json(silent=True) or {}

    # Validate required string fields
    symbol  = (data.get('symbol')  or '').strip()
    name_en = (data.get('name_en') or '').strip()
    name_ar = (data.get('name_ar') or '').strip()

    if not symbol:
        return jsonify({"error": "symbol is required"}), 400
    if not name_en:
        return jsonify({"error": "name_en is required"}), 400
    if not name_ar:
        return jsonify({"error": "name_ar is required"}), 400

    # Prevent duplicate tickers — symbol must be unique across all stocks.
    if Stock.query.filter_by(symbol=symbol).first():
        return jsonify({"error": f"Stock {symbol} already exists"}), 409

    # Resolve sector: accept either sector_id (integer) or sector (name string).
    # This makes the endpoint friendly for both programmatic callers (who know IDs)
    # and manual usage via tools like Postman (who know names).
    sector = None
    sector_id   = data.get('sector_id')
    sector_name = (data.get('sector') or '').strip()

    if sector_id is not None:
        # Caller provided a numeric ID — look up directly
        sector = Sector.query.get(int(sector_id))
        if sector is None:
            return jsonify({"error": f"Sector id {sector_id} not found"}), 404
    elif sector_name:
        # Caller provided a name — case-insensitive match (ilike = SQL ILIKE)
        sector = Sector.query.filter(Sector.name_en.ilike(sector_name)).first()
        if sector is None:
            return jsonify({"error": f"Sector '{sector_name}' not found"}), 404
    else:
        return jsonify({"error": "sector_id or sector (name) is required"}), 400

    # market_price is optional — new listings may not have a price yet.
    market_price = data.get('market_price')
    if market_price is not None:
        try:
            market_price = float(market_price)
        except (ValueError, TypeError):
            return jsonify({"error": "market_price must be a number"}), 400

    # Create and persist the new stock row
    stock = Stock(
        symbol=symbol,
        name_en=name_en,
        name_ar=name_ar,
        sector_id=sector.id,
        market_price=market_price,
    )
    db.session.add(stock)
    db.session.commit()

    # Return the created stock with HTTP 201 Created
    return jsonify({
        "symbol":      stock.symbol,
        "name_en":     stock.name_en,
        "name_ar":     stock.name_ar,
        "sector":      sector.name_en,
        "sector_id":   sector.id,
        "market_price": stock.market_price,
    }), 201
