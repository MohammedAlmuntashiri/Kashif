"""
update_prices.py — Refresh market_price for every stock from Yahoo Finance.

Only touches stocks.market_price; names/sectors/financials are left alone.
Run this before run_valuations.py + run_comparisons.py so derived ratios
reflect the latest prices.

Usage (inside the backend container):
    docker exec kashif-backend-1 python update_prices.py
"""
import sys
import time
import yfinance as yf

from app import create_app, db
from app.models.stock import Stock


def fetch_price(symbol):
    """Return latest price for a Tadawul ticker, or None on failure."""
    try:
        return yf.Ticker(f"{symbol}.SR").fast_info.get("lastPrice")
    except Exception as e:
        print(f"  ! {symbol}: {type(e).__name__}: {e}")
        return None


def main():
    app = create_app()
    started = time.time()
    updated = unchanged = failed = 0

    with app.app_context():
        stocks = Stock.query.order_by(Stock.symbol).all()
        print(f"Refreshing prices for {len(stocks)} stocks...\n")

        for s in stocks:
            old = s.market_price
            new = fetch_price(s.symbol)

            if new is None:
                print(f"  {s.symbol}  FAILED  (kept {old})")
                failed += 1
                continue

            new = float(new)
            if old and abs(new - old) / max(abs(old), 1e-9) < 1e-6:
                print(f"  {s.symbol}  {old:>8.2f}  →  {new:>8.2f}  (no change)")
                unchanged += 1
                continue

            delta_pct = ((new - old) / old * 100) if old else 0.0
            sign = "+" if delta_pct >= 0 else ""
            print(f"  {s.symbol}  {old:>8.2f}  →  {new:>8.2f}  ({sign}{delta_pct:.2f}%)")
            s.market_price = new
            updated += 1

        db.session.commit()

    elapsed = time.time() - started
    print(f"\nDone in {elapsed:.1f}s. updated={updated}  unchanged={unchanged}  failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
