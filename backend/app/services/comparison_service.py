# comparison_service.py — Computes 7 fundamental ratios and ranks each stock
# against its sector peers. The runner script in backend/run_comparisons.py
# persists the results to the comparisons table.
#
# The 7 ratios:
#   pe_ratio       = market_price / eps
#   pb_ratio       = market_price / (shareholders_equity / shares_outstanding)
#   roe            = net_income / shareholders_equity * 100
#   roa            = net_income / total_assets * 100
#   debt_to_equity = total_borrowings / shareholders_equity
#   profit_margin  = net_income / revenue * 100
#   dividend_yield = dividends_per_share / market_price * 100
#
# Ranking convention: rank=1 always means "best" within the sector.
# A stock with a None ratio is excluded from that metric's ranking only
# (other metrics still rank normally). Stocks without any financial_data
# are skipped entirely and produce no comparison row.
#
# No outlier filtering is applied to sector averages here — unlike
# pe_service/pb_service which cap P/E at 50 and P/B at 20 for valuation
# inputs. This is deliberate: comparisons are descriptive statistics where
# every valid peer belongs in the ranking, even if its ratio is extreme.

from app.models.stock import Stock
from app.models.financial_data import FinancialData


# (column_name, short_name, direction)
#   column_name — column on the Comparison model holding the stock's own value
#   short_name  — used to derive sector_avg_<short> and <short>_rank column names
#   direction   — "asc" = lower is better, "desc" = higher is better
METRICS = [
    ("pe_ratio",       "pe",              "asc"),
    ("pb_ratio",       "pb",              "asc"),
    ("roe",            "roe",             "desc"),
    ("roa",            "roa",             "desc"),
    ("debt_to_equity", "debt_to_equity",  "asc"),
    ("profit_margin",  "profit_margin",   "desc"),
    ("dividend_yield", "dividend_yield",  "desc"),
]


# ── Pure-math ratio calculators ─────────────────────────────────────
# Each returns None if inputs are missing or would cause division-by-zero /
# nonsensical math (negative shares, zero equity, etc.). Negative results
# are allowed where they carry meaning — e.g. ROE of a loss-making year.

def compute_pe(market_price, eps):
    if market_price is None or eps is None:
        return None
    if market_price <= 0 or eps <= 0:
        return None
    return market_price / eps


def compute_pb(market_price, equity, shares_outstanding):
    if market_price is None or equity is None or shares_outstanding is None:
        return None
    if market_price <= 0 or equity <= 0 or shares_outstanding <= 0:
        return None
    book_value_per_share = equity / shares_outstanding
    if book_value_per_share <= 0:
        return None
    return market_price / book_value_per_share


def compute_roe(net_income, equity):
    if net_income is None or equity is None:
        return None
    if equity <= 0:
        return None
    return net_income / equity * 100


def compute_roa(net_income, total_assets):
    if net_income is None or total_assets is None:
        return None
    if total_assets <= 0:
        return None
    return net_income / total_assets * 100


def compute_debt_to_equity(debt, equity):
    if debt is None or equity is None:
        return None
    if equity <= 0 or debt < 0:
        return None
    return debt / equity


def compute_profit_margin(net_income, revenue):
    if net_income is None or revenue is None:
        return None
    if revenue <= 0:
        return None
    return net_income / revenue * 100


def compute_dividend_yield(dividends_per_share, market_price):
    if dividends_per_share is None or market_price is None:
        return None
    if market_price <= 0 or dividends_per_share < 0:
        return None
    return dividends_per_share / market_price * 100


# ── Orchestration ───────────────────────────────────────────────────

def _latest_financial_data(stock_id):
    return (
        FinancialData.query
        .filter_by(stock_id=stock_id)
        .order_by(FinancialData.period.desc())
        .first()
    )


def _ratios_for_stock(stock, latest_fd):
    """Compute all 7 ratios for one stock from its latest financial snapshot."""
    return {
        "pe_ratio":       compute_pe(stock.market_price, latest_fd.eps),
        "pb_ratio":       compute_pb(stock.market_price, latest_fd.shareholders_equity, latest_fd.shares_outstanding),
        "roe":            compute_roe(latest_fd.net_income, latest_fd.shareholders_equity),
        "roa":            compute_roa(latest_fd.net_income, latest_fd.total_assets),
        "debt_to_equity": compute_debt_to_equity(latest_fd.total_borrowings, latest_fd.shareholders_equity),
        "profit_margin":  compute_profit_margin(latest_fd.net_income, latest_fd.revenue),
        "dividend_yield": compute_dividend_yield(latest_fd.dividends_per_share, stock.market_price),
    }


def build_sector_comparisons(sector_id):
    """Compute ratios + ranks for every stock in one sector.

    Returns a list of dicts ready to pass as kwargs to Comparison(**record).
    Stocks with no financial_data are skipped and produce no record.

    peer_count is the number of stocks with financial_data in the sector
    (not the number of valid values for a specific metric). For any one
    metric, a stock's rank may be None if the stock lacks that ratio —
    e.g. a non-dividend-paying stock will have dividend_yield_rank = None.
    """
    stocks = Stock.query.filter_by(sector_id=sector_id).all()

    # Step 1 — gather ratios per stock with financial_data
    stock_ratios = {}
    for stock in stocks:
        latest_fd = _latest_financial_data(stock.id)
        if latest_fd is None:
            continue
        stock_ratios[stock.id] = _ratios_for_stock(stock, latest_fd)

    if not stock_ratios:
        return []

    # Step 2 — per-metric sector average + rank
    sector_avg = {}
    ranks = {sid: {} for sid in stock_ratios}

    for value_col, short, direction in METRICS:
        valid = [(sid, stock_ratios[sid][value_col])
                 for sid in stock_ratios
                 if stock_ratios[sid][value_col] is not None]
        if not valid:
            sector_avg[short] = None
            continue

        values = [v for _, v in valid]
        sector_avg[short] = sum(values) / len(values)

        ordered = sorted(valid, key=lambda t: t[1], reverse=(direction == "desc"))
        for rank_idx, (sid, _) in enumerate(ordered, start=1):
            ranks[sid][short] = rank_idx

    # Step 3 — assemble one record per stock
    peer_count = len(stock_ratios)
    records = []
    for sid, ratios in stock_ratios.items():
        record = {"stock_id": sid, "peer_count": peer_count}
        for value_col, short, _ in METRICS:
            record[value_col] = ratios[value_col]
            record[f"sector_avg_{short}"] = sector_avg[short]
            record[f"{short}_rank"] = ranks[sid].get(short)
        records.append(record)
    return records
