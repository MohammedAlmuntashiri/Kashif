# run_comparisons.py — Compute and persist peer-comparison rows for every stock
#
# Run after seeding financial_data or whenever market_price changes:
#   python run_comparisons.py
#
# Behavior: wipes the comparisons table and rebuilds one row per stock with
# financial_data. Same wipe-and-rebuild pattern as run_valuations.py —
# no historical comparison tracking for MVP.

from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app import create_app
from app.extensions import db
from app.models.sector import Sector
from app.models.comparison import Comparison
from app.services.comparison_service import build_sector_comparisons

app = create_app()


def run():
    sectors = Sector.query.order_by(Sector.name_en).all()
    print(f"Computing comparisons across {len(sectors)} sectors...\n")

    Comparison.query.delete()
    db.session.commit()

    inserted = 0
    for sector in sectors:
        records = build_sector_comparisons(sector.id)
        if not records:
            print(f"  {sector.name_en[:40]:40s}  (no stocks with financial_data)")
            continue

        for rec in records:
            db.session.add(Comparison(**rec))
            inserted += 1
        print(f"  {sector.name_en[:40]:40s}  {len(records)} stocks ranked")

    db.session.commit()
    print(f"\nDone. Inserted {inserted} comparison rows.")


if __name__ == "__main__":
    with app.app_context():
        run()
