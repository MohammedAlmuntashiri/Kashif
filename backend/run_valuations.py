# run_valuations.py — Compute and persist fair values for every stock
#
# Run this whenever financial_data or market_price changes:
#   python run_valuations.py
#
# Behavior: wipes the valuations table, recomputes all stocks, writes fresh rows.
# The wipe keeps things simple — for MVP we don't need historical valuation tracking.
# (When we want history later, switch to "insert new row each run" and let the UI
#  pick the latest by calculated_at.)

from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app import create_app
from app.extensions import db
from app.models.stock import Stock
from app.models.valuation import Valuation
from app.services.valuation_engine import value_stock

app = create_app()


def run():
    stocks = Stock.query.order_by(Stock.symbol).all()
    print(f"Computing valuations for {len(stocks)} stocks...\n")

    # Wipe previous valuations — full recompute, not incremental
    Valuation.query.delete()
    db.session.commit()

    # Caches so we compute each sector's avg P/E and P/B only once
    sector_pe_cache = {}
    sector_pb_cache = {}

    inserted = 0
    skipped = 0

    for stock in stocks:
        result = value_stock(stock, sector_pe_cache, sector_pb_cache)

        if result["fair_value"] is None:
            print(f"  {stock.symbol} {stock.name_en[:30]:30s}  SKIP (no fair value)")
            skipped += 1
            continue

        valuation = Valuation(
            stock_id=result["stock_id"],
            dcf_value=result["dcf_value"],
            pe_value=result["pe_value"],
            pb_value=result["pb_value"],
            fair_value=result["fair_value"],
            market_price=result["market_price"],
            status=result["status"],
        )
        db.session.add(valuation)
        inserted += 1

        gap_pct = ""
        if result["market_price"] and result["fair_value"]:
            gap = (result["fair_value"] - result["market_price"]) / result["market_price"] * 100
            gap_pct = f"{gap:+.1f}%"

        print(
            f"  {stock.symbol} {stock.name_en[:30]:30s}  "
            f"market={result['market_price'] or 0:>7.2f}  "
            f"fair={result['fair_value']:>7.2f}  "
            f"{gap_pct:>7s}  {result['status']}"
        )

    db.session.commit()
    print(f"\nDone. Inserted {inserted}, skipped {skipped}.")


if __name__ == "__main__":
    with app.app_context():
        run()
