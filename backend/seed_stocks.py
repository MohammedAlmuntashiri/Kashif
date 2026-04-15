# seed_stocks.py — Fetches real Tadawul stock data from Yahoo Finance (yfinance) and inserts into the database
# Usage: python seed_stocks.py
#
# For each company below, the script:
#   1. Fetches quote from Yahoo Finance using ticker like "2222.SR"
#   2. Extracts name and market_price
#   3. Inserts into the `stocks` table (or updates market_price if already exists)
#   4. Skips companies Yahoo doesn't have (prints a warning)
#
# yfinance is free, no API key required.

import os
import yfinance as yf
from dotenv import load_dotenv

# Load .env from project root (one level up from backend/)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app import create_app
from app.extensions import db
from app.models.stock import Stock

# Create Flask app so we have database access
app = create_app()

# ──────────────────────────────────────────────
# Tadawul companies to seed (2-3 per sector)
# Format: (ticker, name_ar, sector_id)
# sector_id matches the IDs from seed.py (Energy=1, Materials=2, ... Real Estate=22)
# name_en and market_price are fetched from Yahoo Finance automatically
# ──────────────────────────────────────────────
companies = [
    # Energy (sector_id=1)
    ("2222", "أرامكو السعودية", 1),
    ("2381", "الحفر العربية", 1),
    ("2382", "أديس القابضة", 1),

    # Materials (sector_id=2)
    ("2010", "سابك", 2),
    ("2020", "سابك للمغذيات الزراعية", 2),
    ("2250", "المجموعة السعودية للاستثمار الصناعي", 2),

    # Capital Goods (sector_id=3)
    ("1210", "بي سي آي", 3),
    ("2320", "البابطين للطاقة والاتصالات", 3),

    # Commercial & Professional Svc (sector_id=4)
    ("6004", "كاتريون", 4),
    ("1831", "مهارة", 4),

    # Transportation (sector_id=5)
    ("4040", "سابتكو", 5),
    ("4260", "بدجت السعودية", 5),
    ("4030", "البحري", 5),

    # Consumer Durables & Apparel (sector_id=6)
    ("1212", "أسترا الصناعية", 6),

    # Consumer Services (sector_id=7)
    ("4170", "شمس", 7),
    ("1820", "البيلسان القابضة", 7),

    # Media and Entertainment (sector_id=8)
    ("4210", "المجموعة السعودية للأبحاث والإعلام", 8),
    ("4071", "الشركة العربية للتعهدات الفنية", 8),

    # Consumer Discretionary Distribution & Retail (sector_id=9)
    ("4190", "جرير", 9),
    ("4240", "سينومي ريتيل", 9),

    # Consumer Staples Distribution & Retail (sector_id=10)
    ("4001", "أسواق عبد الله العثيم", 10),
    ("4061", "إنعام القابضة الدولية", 10),

    # Food & Beverages (sector_id=11)
    ("2280", "المراعي", 11),
    ("6002", "هرفي للخدمات الغذائية", 11),
    ("2050", "صافولا", 11),

    # Household & Personal Products (sector_id=12)
    ("4011", "لازوردي", 12),

    # Health Care Equipment & Svc (sector_id=13)
    ("4005", "الرعاية الطبية الوطنية", 13),
    ("4004", "دله الصحية", 13),

    # Pharma, Biotech & Life Science (sector_id=14)
    ("2070", "الشركة السعودية للصناعات الدوائية والمستلزمات الطبية", 14),
    ("4002", "المواساة للخدمات الطبية", 14),

    # Banks (sector_id=15)
    ("1120", "مصرف الراجحي", 15),
    ("1180", "البنك الأهلي السعودي", 15),
    ("1150", "مصرف الإنماء", 15),
    ("1140", "بنك البلاد", 15),

    # Financial Services (sector_id=16)
    ("1111", "السوق المالية السعودية (تداول)", 16),

    # Insurance (sector_id=17)
    ("8010", "التعاونية للتأمين", 17),
    ("8210", "بوبا العربية", 17),

    # Software & Services (sector_id=18)
    ("7202", "الشركة العربية لخدمات الإنترنت والاتصالات (سولوشنز)", 18),

    # Telecommunication Services (sector_id=19)
    ("7010", "إس تي سي", 19),
    ("7020", "اتحاد اتصالات - موبايلي", 19),
    ("7030", "زين السعودية", 19),

    # Utilities (sector_id=20)
    ("5110", "الشركة السعودية للطاقة", 20),
    ("2081", "شركة الخريف لتقنية المياه والطاقة", 20),

    # REITs (sector_id=21)
    ("4338", "الأهلي ريت", 21),
    ("4330", "الرياض ريت", 21),

    # Real Estate Mgmt & Dev't (sector_id=22)
    ("4020", "الشركة السعودية العقارية", 22),
    ("4300", "دار الأركان للتطوير العقاري", 22),
    ("4250", "جبل عمر للتطوير", 22),
]


def fetch_stock(ticker):
    """Fetch stock info from Yahoo Finance. Returns dict with name and price, or None if not found."""
    try:
        # Yahoo Finance uses {ticker}.SR for Tadawul stocks
        yf_ticker = yf.Ticker(f"{ticker}.SR")

        # fast_info is lighter and quicker than .info (keys are camelCase)
        price = yf_ticker.fast_info.get("lastPrice")

        # Get the full info for the company name (long name preferred)
        info = yf_ticker.info
        name = info.get("longName") or info.get("shortName")

        if price is None or name is None:
            return None

        return {
            "name_en": name,
            "market_price": float(price),
        }
    except Exception as e:
        print(f"  Error for {ticker}: {type(e).__name__}")
        return None


# ──────────────────────────────────────────────
# Insert/update stocks in the database
# ──────────────────────────────────────────────

with app.app_context():
    inserted = 0
    updated = 0
    skipped = 0

    for ticker, name_ar, sector_id in companies:
        print(f"Fetching {ticker}...", end=" ")
        stock_data = fetch_stock(ticker)

        if stock_data is None:
            print("NOT FOUND, skipping.")
            skipped += 1
            continue

        # Check if stock already exists
        existing = Stock.query.filter_by(symbol=ticker).first()
        if existing:
            # Refresh price, English name (from Yahoo), Arabic name, and sector (from our list)
            existing.market_price = stock_data["market_price"]
            existing.name_en = stock_data["name_en"]
            existing.name_ar = name_ar
            existing.sector_id = sector_id
            updated += 1
            print(f"updated ({existing.name_en}, {stock_data['market_price']:.2f} SAR)")
        else:
            # Insert new stock
            stock = Stock(
                symbol=ticker,
                name_en=stock_data["name_en"],
                name_ar=name_ar,
                market_price=stock_data["market_price"],
                sector_id=sector_id,
            )
            db.session.add(stock)
            inserted += 1
            print(f"inserted ({stock_data['name_en']}, {stock_data['market_price']:.2f} SAR)")

    db.session.commit()
    print(f"\nDone. Inserted: {inserted}, Updated: {updated}, Skipped: {skipped}")
