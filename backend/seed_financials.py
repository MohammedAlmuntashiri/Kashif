# seed_financials.py — Fetches annual financial statements from Yahoo Finance for all seeded stocks
# Usage: python seed_financials.py
#
# For each stock in the `stocks` table, the script:
#   1. Pulls 3 annual statements from yfinance: income statement, balance sheet, cash flow
#   2. Extracts the last 4 annual periods (newest first)
#   3. Maps yfinance fields to our 10 FinancialData columns
#   4. Inserts new rows or updates existing ones (keyed by stock_id + period)
#
# Column mapping (yfinance → FinancialData):
#   income.Total Revenue                  → revenue
#   income.Net Income                     → net_income
#   income.Basic EPS (or Diluted EPS)     → eps
#   balance.Total Assets                  → total_assets
#   balance.Total Debt                    → total_borrowings  (loans/debt only, not all liabilities)
#   balance.Stockholders Equity           → shareholders_equity
#   balance.Cash And Cash Equivalents     → cash_and_equivalents
#   balance.Ordinary Shares Number        → shares_outstanding
#   cashflow.Free Cash Flow               → free_cash_flow
#   dividends (sum per year)              → dividends_per_share

import os
import yfinance as yf
from dotenv import load_dotenv

# Load .env from project root (one level up from backend/)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app import create_app
from app.extensions import db
from app.models.stock import Stock
from app.models.financial_data import FinancialData

app = create_app()


def safe_get(df, row_name, col):
    """Safely extract a value from a yfinance dataframe. Returns None if missing or NaN."""
    try:
        if row_name in df.index:
            val = df.loc[row_name, col]
            if val is None:
                return None
            fval = float(val)
            # Filter NaN (NaN != NaN is the canonical check)
            if fval != fval:
                return None
            return fval
    except Exception:
        pass
    return None


def fetch_financials(symbol):
    """Fetch annual financials from Yahoo Finance for a given Tadawul symbol.

    Returns a list of dicts (one per year, up to 4, newest first), or [] if unavailable.
    """
    try:
        yf_ticker = yf.Ticker(f"{symbol}.SR")

        income = yf_ticker.financials          # Annual income statement (cols=dates, rows=metrics)
        balance = yf_ticker.balance_sheet      # Annual balance sheet
        cashflow = yf_ticker.cashflow          # Annual cash flow statement
        dividends = yf_ticker.dividends        # Per-share dividend payment history (Series)

        if income is None or income.empty or balance is None or balance.empty:
            return []

        # Columns are period end dates (datetime). Take the last 4 annual periods, newest first.
        periods = list(income.columns[:4])
        results = []

        for col in periods:
            year = col.year
            period_label = f"{year}-annual"

            # Income statement fields
            revenue = safe_get(income, "Total Revenue", col)
            net_income = safe_get(income, "Net Income", col)
            eps = safe_get(income, "Basic EPS", col)
            if eps is None:
                eps = safe_get(income, "Diluted EPS", col)

            # Balance sheet fields
            total_assets = safe_get(balance, "Total Assets", col)
            total_borrowings = safe_get(balance, "Total Debt", col)
            shareholders_equity = safe_get(balance, "Stockholders Equity", col)
            if shareholders_equity is None:
                shareholders_equity = safe_get(balance, "Total Equity Gross Minority Interest", col)
            cash_and_equivalents = safe_get(balance, "Cash And Cash Equivalents", col)
            shares_outstanding = safe_get(balance, "Ordinary Shares Number", col)
            if shares_outstanding is None:
                shares_outstanding = safe_get(balance, "Share Issued", col)

            # Cash flow fields
            free_cash_flow = safe_get(cashflow, "Free Cash Flow", col)

            # Dividends per share — sum all ex-dividend payments that fell in this calendar year.
            # yfinance's `.dividends` is already per-share, so summing gives annual DPS.
            dps = None
            if dividends is not None and not dividends.empty:
                year_divs = dividends[dividends.index.year == year]
                if not year_divs.empty:
                    dps = float(year_divs.sum())

            results.append({
                "period": period_label,
                "revenue": revenue,
                "net_income": net_income,
                "eps": eps,
                "total_assets": total_assets,
                "total_borrowings": total_borrowings,
                "shareholders_equity": shareholders_equity,
                "cash_and_equivalents": cash_and_equivalents,
                "free_cash_flow": free_cash_flow,
                "dividends_per_share": dps,
                "shares_outstanding": shares_outstanding,
            })

        return results
    except Exception as e:
        print(f"  Error: {type(e).__name__}: {e}")
        return []


# ──────────────────────────────────────────────
# Insert/update financial_data rows for every stock
# ──────────────────────────────────────────────

with app.app_context():
    stocks = Stock.query.order_by(Stock.symbol).all()
    total_inserted = 0
    total_updated = 0
    stocks_skipped = 0

    for stock in stocks:
        print(f"Fetching {stock.symbol} ({stock.name_en})...", end=" ")
        periods_data = fetch_financials(stock.symbol)

        if not periods_data:
            print("NO DATA, skipping.")
            stocks_skipped += 1
            continue

        inserted_here = 0
        updated_here = 0

        for pd_row in periods_data:
            # Upsert keyed on (stock_id, period)
            existing = FinancialData.query.filter_by(
                stock_id=stock.id, period=pd_row["period"]
            ).first()

            if existing:
                for key, val in pd_row.items():
                    if key != "period":
                        setattr(existing, key, val)
                updated_here += 1
            else:
                fd = FinancialData(stock_id=stock.id, **pd_row)
                db.session.add(fd)
                inserted_here += 1

        total_inserted += inserted_here
        total_updated += updated_here
        print(f"{inserted_here} new, {updated_here} updated ({len(periods_data)} periods)")

    db.session.commit()
    print(f"\nDone. Inserted: {total_inserted}, Updated: {total_updated}, Stocks skipped: {stocks_skipped}")
