# pb_service.py — Price-to-Book valuation
#
# Formula:
#   book_value_per_share = shareholders_equity / shares_outstanding
#   fair_value = book_value_per_share × sector_average_PB
#
# Two public functions:
#   get_sector_average_pb(sector_id)             — queries DB, returns avg P/B across sector
#   pb_fair_value(equity, shares, sector_pb)     — pure math, returns fair value per share
#
# Why P/B matters:
#   - Works when earnings AND cash flow are weak (distressed periods, REITs with heavy depreciation)
#   - Especially meaningful for asset-heavy sectors: banks, real estate, insurance, utilities
#   - Sector weight table gives P/B a heavier weight for those sectors

from app.models.stock import Stock
from app.models.financial_data import FinancialData

# Outlier cap: reject P/B ratios above this when building the sector average.
# Typical Saudi market P/B is 0.5 to 6. Anything above 20 is usually an accounting
# artifact (tiny equity with large market cap) and would distort the average.
MAX_REASONABLE_PB = 20


def pb_fair_value(equity, shares_outstanding, sector_pb):
    """Compute fair value per share using P/B multiple.

    Args:
        equity: Shareholders' equity (SAR)
        shares_outstanding: Total shares issued
        sector_pb: Sector-average P/B ratio

    Returns:
        Fair value per share (SAR), or None if inputs are invalid.
    """
    if equity is None or shares_outstanding is None or sector_pb is None:
        return None
    if equity <= 0 or shares_outstanding <= 0 or sector_pb <= 0:
        return None

    book_value_per_share = equity / shares_outstanding
    return book_value_per_share * sector_pb


def get_sector_average_pb(sector_id, max_pb=MAX_REASONABLE_PB):
    """Calculate average P/B for a sector using latest equity + shares from DB.

    Steps:
        1. Fetch all stocks in the sector
        2. For each stock, get its most recent financial_data row
        3. Compute P/B = market_price / (equity / shares)
        4. Filter: equity and shares must be positive AND P/B ≤ max_pb
        5. Return the arithmetic mean of valid ratios

    Args:
        sector_id: ID from the sectors table
        max_pb: Upper cap for individual P/B inclusion (default 20)

    Returns:
        Average P/B (float), or None if no valid stocks in sector.
    """
    stocks = Stock.query.filter_by(sector_id=sector_id).all()
    if not stocks:
        return None

    ratios = []
    for stock in stocks:
        if not stock.market_price or stock.market_price <= 0:
            continue

        latest_fd = (
            FinancialData.query
            .filter_by(stock_id=stock.id)
            .order_by(FinancialData.period.desc())
            .first()
        )
        if not latest_fd:
            continue
        if not latest_fd.shareholders_equity or latest_fd.shareholders_equity <= 0:
            continue
        if not latest_fd.shares_outstanding or latest_fd.shares_outstanding <= 0:
            continue

        book_value_per_share = latest_fd.shareholders_equity / latest_fd.shares_outstanding
        if book_value_per_share <= 0:
            continue

        pb = stock.market_price / book_value_per_share
        if 0 < pb <= max_pb:
            ratios.append(pb)

    if not ratios:
        return None
    return sum(ratios) / len(ratios)
