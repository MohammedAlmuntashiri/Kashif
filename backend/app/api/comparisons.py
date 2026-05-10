# comparisons.py — API endpoint for sector peer-comparison data
#
# URL prefix (registered in api/__init__.py): /api/comparisons
#
# Endpoints:
#   GET /api/comparisons/              — all stocks with their 7 ratios + sector ranks
#   GET /api/comparisons/?sector=Banks — same, filtered to one sector
#
# The comparisons table is populated by the offline runner (run_comparisons.py).
# Each stock gets one row per runner execution. This endpoint always returns
# the LATEST row per stock (deduplicated by stock_id).
#
# The 7 ratios returned per stock:
#   pe_ratio        — Price / EPS                  (lower = cheaper, rank 1 = best)
#   pb_ratio        — Price / Book Value per Share  (lower = cheaper, rank 1 = best)
#   roe             — Net Income / Equity × 100     (higher = more profitable)
#   roa             — Net Income / Assets × 100     (higher = more efficient)
#   debt_to_equity  — Total Borrowings / Equity     (lower = less leveraged)
#   profit_margin   — Net Income / Revenue × 100    (higher = more profitable)
#   dividend_yield  — DPS / Market Price × 100      (higher = more income)
#
# For each ratio the response includes:
#   <ratio>              — the stock's own value
#   sector_avg_<short>   — average across all peers in the same sector
#   <short>_rank         — rank within the sector (1 = best, peer_count = worst)

from flask import Blueprint, jsonify, request
from app.models.comparison import Comparison
from app.models.stock import Stock

comparisons_bp = Blueprint('comparisons', __name__)


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/comparisons/
# GET /api/comparisons/?sector=Energy
#
# Returns one comparison record per stock (the most recently computed one).
# Optional query param ?sector= filters by sector name (case-insensitive).
# ─────────────────────────────────────────────────────────────────────────────
@comparisons_bp.route('/', methods=['GET'])
def list_comparisons():
    # Optional sector filter — e.g. ?sector=Banks or ?sector=banks
    sector_filter = request.args.get('sector', '').strip().lower()

    # Load all stocks into a dict keyed by stock_id so we can join in Python
    # without a complex SQL join. 48–200 stocks fits comfortably in memory.
    stocks = {s.id: s for s in Stock.query.all()}

    # Fetch all comparison rows ordered by most recent first.
    # We'll deduplicate in Python, keeping only the first (=latest) row per stock.
    all_comps = (
        Comparison.query
        .order_by(Comparison.calculated_at.desc())
        .all()
    )

    seen_stock_ids = set()  # Tracks which stocks we've already included
    result = []

    for comp in all_comps:
        # Skip if we've already included a (more recent) row for this stock
        if comp.stock_id in seen_stock_ids:
            continue
        seen_stock_ids.add(comp.stock_id)

        stock = stocks.get(comp.stock_id)
        if stock is None:
            # Orphaned comparison row (stock was deleted) — skip silently
            continue

        # Apply sector filter if provided
        if sector_filter and stock.sector.name_en.lower() != sector_filter:
            continue

        result.append({
            # ── Stock identity ────────────────────────────────────────────
            "symbol":   stock.symbol,
            "name_en":  stock.name_en,
            "sector":   stock.sector.name_en,
            "peer_count": comp.peer_count,  # How many stocks were in the sector at calc time

            # ── P/E ratio (lower = cheaper relative to earnings) ──────────
            "pe_ratio":             comp.pe_ratio,
            "sector_avg_pe":        comp.sector_avg_pe,
            "pe_rank":              comp.pe_rank,        # 1 = cheapest P/E in sector

            # ── P/B ratio (lower = cheaper relative to book value) ────────
            "pb_ratio":             comp.pb_ratio,
            "sector_avg_pb":        comp.sector_avg_pb,
            "pb_rank":              comp.pb_rank,        # 1 = cheapest P/B in sector

            # ── ROE % (higher = more return generated from equity) ─────────
            "roe":                  comp.roe,
            "sector_avg_roe":       comp.sector_avg_roe,
            "roe_rank":             comp.roe_rank,       # 1 = highest ROE in sector

            # ── ROA % (higher = more efficient use of assets) ─────────────
            "roa":                  comp.roa,
            "sector_avg_roa":       comp.sector_avg_roa,
            "roa_rank":             comp.roa_rank,       # 1 = highest ROA in sector

            # ── Debt-to-Equity (lower = less financial leverage) ──────────
            "debt_to_equity":            comp.debt_to_equity,
            "sector_avg_debt_to_equity": comp.sector_avg_debt_to_equity,
            "debt_to_equity_rank":       comp.debt_to_equity_rank,  # 1 = least leveraged

            # ── Profit Margin % (higher = more profit per SAR of revenue) ─
            "profit_margin":             comp.profit_margin,
            "sector_avg_profit_margin":  comp.sector_avg_profit_margin,
            "profit_margin_rank":        comp.profit_margin_rank,   # 1 = highest margin

            # ── Dividend Yield % (higher = more income per SAR invested) ──
            "dividend_yield":            comp.dividend_yield,
            "sector_avg_dividend_yield": comp.sector_avg_dividend_yield,
            "dividend_yield_rank":       comp.dividend_yield_rank,  # 1 = highest yield

            "calculated_at": comp.calculated_at.isoformat() if comp.calculated_at else None,
        })

    return jsonify(result)
