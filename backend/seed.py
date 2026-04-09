# seed.py — Populates the database with initial data (sectors, stocks, financial data)
# Run this script once to fill the database, then comment out or skip what's already inserted.
# Usage: python seed.py

from dotenv import load_dotenv
import os

# Load .env from project root (one level up from backend/)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app import create_app
from app.extensions import db
from app.models.sector import Sector

# Create the Flask app so we have access to the database connection
app = create_app()

# ──────────────────────────────────────────────
# Part 1: Seed Sectors (22 official Tadawul sectors)
# ──────────────────────────────────────────────
# Each sector has:
#   - name_en: English name
#   - name_ar: Arabic name
#   - dcf_weight, pe_weight, pb_weight: how much to trust each valuation model (must sum to 1.0)
#
# Weight profiles:
#   Most sectors:                          dcf=0.40, pe=0.40, pb=0.20
#   Banks, Financial Services, Insurance:  dcf=0.20, pe=0.40, pb=0.40  (asset-heavy, P/B matters more)
#   REITs, Real Estate Mgmt & Dev't:       dcf=0.20, pe=0.30, pb=0.50  (real estate valued by assets)

sectors = [
    # ── Energy & Industrial ──
    {"name_en": "Energy", "name_ar": "الطاقة", "dcf_weight": 0.40, "pe_weight": 0.40, "pb_weight": 0.20},
    {"name_en": "Materials", "name_ar": "المواد الأساسية", "dcf_weight": 0.40, "pe_weight": 0.40, "pb_weight": 0.20},
    {"name_en": "Capital Goods", "name_ar": "السلع الرأسمالية", "dcf_weight": 0.40, "pe_weight": 0.40, "pb_weight": 0.20},
    {"name_en": "Commercial & Professional Svc", "name_ar": "الخدمات التجارية والمهنية", "dcf_weight": 0.40, "pe_weight": 0.40, "pb_weight": 0.20},
    {"name_en": "Transportation", "name_ar": "النقل", "dcf_weight": 0.40, "pe_weight": 0.40, "pb_weight": 0.20},

    # ── Consumer ──
    {"name_en": "Consumer Durables & Apparel", "name_ar": "السلع طويلة الاجل", "dcf_weight": 0.40, "pe_weight": 0.40, "pb_weight": 0.20},
    {"name_en": "Consumer Services", "name_ar": "الخدمات الإستهلاكية", "dcf_weight": 0.40, "pe_weight": 0.40, "pb_weight": 0.20},
    {"name_en": "Media and Entertainment", "name_ar": "الإعلام والترفيه", "dcf_weight": 0.40, "pe_weight": 0.40, "pb_weight": 0.20},
    {"name_en": "Consumer Discretionary Distribution & Retail", "name_ar": "توزيع السلع الكمالية وتجزئتها", "dcf_weight": 0.40, "pe_weight": 0.40, "pb_weight": 0.20},
    {"name_en": "Consumer Staples Distribution & Retail", "name_ar": "توزيع السلع الاستهلاكية وتجزئتها", "dcf_weight": 0.40, "pe_weight": 0.40, "pb_weight": 0.20},
    {"name_en": "Food & Beverages", "name_ar": "الأغذية والمشروبات", "dcf_weight": 0.40, "pe_weight": 0.40, "pb_weight": 0.20},
    {"name_en": "Household & Personal Products", "name_ar": "المنتجات المنزلية والشخصية", "dcf_weight": 0.40, "pe_weight": 0.40, "pb_weight": 0.20},

    # ── Healthcare ──
    {"name_en": "Health Care Equipment & Svc", "name_ar": "المعدات والخدمات الصحية", "dcf_weight": 0.40, "pe_weight": 0.40, "pb_weight": 0.20},
    {"name_en": "Pharma, Biotech & Life Science", "name_ar": "الأدوية والتكنولوجيا الحيوية وعلوم الحياة", "dcf_weight": 0.40, "pe_weight": 0.40, "pb_weight": 0.20},

    # ── Financials (asset-heavy — P/B matters more) ──
    {"name_en": "Banks", "name_ar": "البنوك", "dcf_weight": 0.20, "pe_weight": 0.40, "pb_weight": 0.40},
    {"name_en": "Financial Services", "name_ar": "الخدمات المالية", "dcf_weight": 0.20, "pe_weight": 0.40, "pb_weight": 0.40},
    {"name_en": "Insurance", "name_ar": "التأمين", "dcf_weight": 0.20, "pe_weight": 0.40, "pb_weight": 0.40},

    # ── Technology & Telecom ──
    {"name_en": "Software & Services", "name_ar": "البرمجيات والخدمات", "dcf_weight": 0.40, "pe_weight": 0.40, "pb_weight": 0.20},
    {"name_en": "Telecommunication Services", "name_ar": "الإتصالات", "dcf_weight": 0.40, "pe_weight": 0.40, "pb_weight": 0.20},

    # ── Utilities ──
    {"name_en": "Utilities", "name_ar": "المرافق العامة", "dcf_weight": 0.40, "pe_weight": 0.40, "pb_weight": 0.20},

    # ── Real Estate (valued heavily by assets — P/B dominates) ──
    {"name_en": "REITs", "name_ar": "صناديق الاستثمار العقارية المتداولة", "dcf_weight": 0.20, "pe_weight": 0.30, "pb_weight": 0.50},
    {"name_en": "Real Estate Mgmt & Dev't", "name_ar": "إدارة وتطوير العقارات", "dcf_weight": 0.20, "pe_weight": 0.30, "pb_weight": 0.50},
]

# ──────────────────────────────────────────────
# Insert into database
# ──────────────────────────────────────────────

with app.app_context():
    # Check if sectors already exist to avoid duplicates
    existing = Sector.query.count()
    if existing > 0:
        print(f"Sectors already seeded ({existing} found). Skipping.")
    else:
        # Loop through each sector dict and create a Sector object
        for s in sectors:
            sector = Sector(
                name_en=s["name_en"],
                name_ar=s["name_ar"],
                dcf_weight=s["dcf_weight"],
                pe_weight=s["pe_weight"],
                pb_weight=s["pb_weight"],
            )
            db.session.add(sector)

        # Commit all 22 sectors to the database in one transaction
        db.session.commit()
        print(f"Seeded {len(sectors)} sectors successfully.")
