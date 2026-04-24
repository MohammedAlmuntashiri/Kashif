# pe_service.py — Price-to-Earnings valuation
#
# Formula: fair_value = EPS × sector_average_PE
#
# Two public functions:
#   get_sector_average_pe(sector_id) — queries DB, returns avg P/E across sector
#   pe_fair_value(eps, sector_pe)    — pure math, returns fair value per share
#
# Why P/E works where DCF fails:
#   - Banks like Al Rajhi have negative FCF in some years → DCF returns None
#   - But they still have positive EPS → P/E gives a valuation

from app.models.stock import Stock
from app.models.financial_data import FinancialData

# Outlier cap: reject P/E ratios above this when building the sector average.
# Near-zero EPS can produce P/E=500+ which would destroy the average. Typical
# Saudi market P/E ranges from 10 to 40; anything above 50 is suspect.
MAX_REASONABLE_PE = 50


def pe_fair_value(eps, sector_pe):
    """Compute fair value per share using P/E multiple.

    Args:
        eps: Earnings per share (SAR)
        sector_pe: Sector-average P/E ratio

    Returns:
        Fair value per share (SAR), or None if inputs are invalid.
    """
    if eps is None or sector_pe is None:
        return None
    if eps <= 0 or sector_pe <= 0:
        return None
    return eps * sector_pe


def get_sector_average_pe(sector_id, max_pe=MAX_REASONABLE_PE, exclude_stock_id=None):
    """Calculate average P/E for a sector using latest annual EPS from DB.

    Steps:
        1. Fetch all stocks in the sector (optionally excluding one)
        2. For each stock, get its most recent financial_data row
        3. Compute P/E = market_price / eps
        4. Filter: EPS must be positive AND P/E ≤ max_pe (outlier protection)
        5. Return the arithmetic mean of valid ratios

    Args:
        sector_id: ID from the sectors table
        max_pe: Upper cap for individual P/E inclusion (default 50)
        exclude_stock_id: If set, skip this stock when averaging. Pass the
            stock's own ID during valuation to avoid self-comparison
            (otherwise eps × (mp/eps) = mp — fair value trivially = market price).

    Returns:
        Average P/E (float), or None if no valid peer stocks remain.
    """
    stocks = Stock.query.filter_by(sector_id=sector_id).all()
    if not stocks:
        return None

    ratios = []
    for stock in stocks:
        if exclude_stock_id is not None and stock.id == exclude_stock_id:
            continue
        if not stock.market_price or stock.market_price <= 0:
            continue

        # Latest annual period (period strings sort lexically — "2025-annual" > "2024-annual")
        latest_fd = (
            FinancialData.query
            .filter_by(stock_id=stock.id)
            .order_by(FinancialData.period.desc())
            .first()
        )
        if not latest_fd or not latest_fd.eps or latest_fd.eps <= 0:
            continue

        pe = stock.market_price / latest_fd.eps
        if 0 < pe <= max_pe:
            ratios.append(pe)

    if not ratios:
        return None
    return sum(ratios) / len(ratios)
