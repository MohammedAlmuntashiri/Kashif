# valuation_engine.py — Blends DCF, P/E, P/B into one fair value per stock
#
# This is the orchestrator that finally brings everything together.
# Pure function (no DB writes) — the runner script in backend/run_valuations.py
# is what actually persists results to the valuations table.
#
# Pipeline per stock:
#   1. Fetch latest financial_data row + historical FCF (last 4 annual periods)
#   2. Run advanced_dcf (fallback to simple_dcf if <2 years of FCF)
#      using a company-specific WACC from calculate_wacc(equity, debt)
#   3. Run pe_fair_value(eps, sector_pe)  with sector_pe cached per-sector
#   4. Run pb_fair_value(equity, shares, sector_pb) with sector_pb cached per-sector
#   5. Blend with the stock's sector weights:
#        fair_value = (dcf × dcf_w) + (pe × pe_w) + (pb × pb_w)
#      If a model returns None, its weight is redistributed proportionally
#      across the remaining models. So a REIT with no balance sheet still gets
#      a fair value from DCF + P/E alone.
#   6. Compute status from market_price vs fair_value (10% threshold)

from app.models.financial_data import FinancialData
from app.services.dcf_service import simple_dcf, advanced_dcf
from app.services.wacc_service import calculate_wacc
from app.services.pe_service import pe_fair_value, get_sector_average_pe
from app.services.pb_service import pb_fair_value, get_sector_average_pb

# Status thresholds: how far market_price must deviate from fair_value
# before we call it under/overvalued. ±10% is the industry default for MVP.
UNDERVALUED_THRESHOLD = 0.10   # fair_value > market_price × 1.10  → undervalued
OVERVALUED_THRESHOLD = 0.10    # fair_value < market_price × 0.90  → overvalued

# Symmetric sanity cap applied to DCF, P/E, and P/B outputs.
# Any single-method result > 3× market is dropped (returned as None) so the
# remaining methods carry the blend via weight redistribution.
# Why: extreme ratios come from broken inputs — tiny EPS inflates P/E,
# near-zero book value inflates sector P/B, small FCF base × CAGR inflates DCF.
# A 3× market ceiling preserves legitimate 2-3× undervaluation signals while
# rejecting obvious garbage (we saw 15× and 4× ratios in the unclamped run).
MAX_VALUE_TO_MARKET_RATIO = 3.0


def compute_status(market_price, fair_value):
    """Classify a stock as undervalued / fair / overvalued.

    Returns one of: "undervalued", "fair", "overvalued", or None if either
    input is missing or non-positive.
    """
    if market_price is None or fair_value is None:
        return None
    if market_price <= 0 or fair_value <= 0:
        return None

    upper_band = market_price * (1 + OVERVALUED_THRESHOLD)
    lower_band = market_price * (1 - UNDERVALUED_THRESHOLD)

    if fair_value > upper_band:
        return "undervalued"
    if fair_value < lower_band:
        return "overvalued"
    return "fair"


def _blend(values_and_weights):
    """Weighted average that skips None values and renormalizes weights.

    Args:
        values_and_weights: list of (value, weight) tuples

    Returns:
        Blended value, or None if every input is None.

    Example:
        >>> _blend([(100, 0.4), (None, 0.4), (50, 0.2)])
        # Available weights sum to 0.6, renormalize → pe=0.667, pb=0.333
        # Result: 100 × 0.667 + 50 × 0.333 ≈ 83.33
    """
    available = [(v, w) for v, w in values_and_weights if v is not None and w > 0]
    if not available:
        return None

    total_weight = sum(w for _, w in available)
    if total_weight <= 0:
        return None

    return sum(v * w for v, w in available) / total_weight


def _historical_fcf(stock_id, n_years=4):
    """Return historical FCF as a list, oldest → newest.

    Pulls the last n_years annual periods, drops Nones at the edges.
    advanced_dcf needs at least 2 positive values to compute CAGR.
    """
    rows = (
        FinancialData.query
        .filter_by(stock_id=stock_id)
        .order_by(FinancialData.period.desc())
        .limit(n_years)
        .all()
    )
    # rows are newest → oldest; reverse so oldest is first (CAGR convention)
    rows = list(reversed(rows))
    return [row.free_cash_flow for row in rows]


def _sanitize_value(value, market_price):
    """Drop a single-method fair value that's unrealistically far from market.

    Applied symmetrically to DCF, P/E, and P/B results. Returning None
    lets the blend redistribute weight to the remaining methods.
    """
    if value is None or market_price is None or market_price <= 0:
        return value
    if value > market_price * MAX_VALUE_TO_MARKET_RATIO:
        return None
    return value


def value_stock(stock, sector_pe_cache=None, sector_pb_cache=None):
    """Compute blended fair value for one stock.

    Args:
        stock: Stock ORM object (with .sector relationship loaded)
        sector_pe_cache: optional dict {sector_id: avg_pe_excluding_self} —
            cache lives per-stock since each stock excludes itself from its
            sector's average. Pass {} or omit; the engine will populate it
            but it won't deduplicate across stocks.
        sector_pb_cache: same shape as sector_pe_cache

    Returns:
        dict with keys: stock_id, dcf_value, pe_value, pb_value,
                        fair_value, market_price, status
        Individual model values may be None; fair_value is None only if
        all three models failed.
    """
    if sector_pe_cache is None:
        sector_pe_cache = {}
    if sector_pb_cache is None:
        sector_pb_cache = {}

    result = {
        "stock_id": stock.id,
        "dcf_value": None,
        "pe_value": None,
        "pb_value": None,
        "fair_value": None,
        "market_price": stock.market_price,
        "status": None,
    }

    # Latest financial snapshot — needed for all three models
    latest_fd = (
        FinancialData.query
        .filter_by(stock_id=stock.id)
        .order_by(FinancialData.period.desc())
        .first()
    )
    if latest_fd is None:
        return result

    # ── DCF ──
    # Use company-specific WACC from current equity + debt
    wacc = calculate_wacc(latest_fd.shareholders_equity, latest_fd.total_borrowings)

    # Try advanced first (uses historical FCF growth), fall back to simple
    fcf_history = _historical_fcf(stock.id)
    dcf = advanced_dcf(fcf_history, latest_fd.shares_outstanding, wacc=wacc)
    if dcf is None:
        dcf = simple_dcf(latest_fd.free_cash_flow, latest_fd.shares_outstanding, wacc=wacc)
    result["dcf_value"] = _sanitize_value(dcf, stock.market_price)

    # ── P/E ──
    # Exclude self from the sector average so we don't compare a stock to itself
    # (single-stock sectors would otherwise return mp × (mp/eps)/eps = mp).
    # Cache key includes stock.id since each stock excludes a different peer.
    sector_id = stock.sector_id
    pe_cache_key = (sector_id, stock.id)
    if pe_cache_key not in sector_pe_cache:
        sector_pe_cache[pe_cache_key] = get_sector_average_pe(sector_id, exclude_stock_id=stock.id)
    sector_pe = sector_pe_cache[pe_cache_key]
    result["pe_value"] = _sanitize_value(
        pe_fair_value(latest_fd.eps, sector_pe),
        stock.market_price,
    )

    # ── P/B ──
    pb_cache_key = (sector_id, stock.id)
    if pb_cache_key not in sector_pb_cache:
        sector_pb_cache[pb_cache_key] = get_sector_average_pb(sector_id, exclude_stock_id=stock.id)
    sector_pb = sector_pb_cache[pb_cache_key]
    result["pb_value"] = _sanitize_value(
        pb_fair_value(
            latest_fd.shareholders_equity,
            latest_fd.shares_outstanding,
            sector_pb,
        ),
        stock.market_price,
    )

    # ── Blend ──
    sector = stock.sector
    fair_value = _blend([
        (result["dcf_value"], sector.dcf_weight),
        (result["pe_value"], sector.pe_weight),
        (result["pb_value"], sector.pb_weight),
    ])
    result["fair_value"] = fair_value
    result["status"] = compute_status(stock.market_price, fair_value)

    return result
