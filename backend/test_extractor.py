# test_extractor.py — Three-state accuracy harness for pdf_extractor
#
# For each (PDF, value) cell, classify the extraction:
#     MATCH    — extracted, within tolerance of DB value
#     DISAGREE — extracted, but outside tolerance
#     FAIL     — extractor returned None
#     N/A      — DB has no expected value (excluded from accuracy)
#
# DB ground truth comes from financial_data rows where period='2024-annual'
# (the PDFs are 2024 annual reports). Latest periods like 2025-annual are
# ignored here because the PDF can't agree with a year it doesn't cover.
#
# Usage:
#     python test_extractor.py                 # tests all 10 values, EN only
#     python test_extractor.py revenue         # tests only revenue
#     python test_extractor.py revenue eps     # tests revenue + eps
#     python test_extractor.py --with-ar       # also extract Arabic PDFs
#
# Arabic is skipped by default since the OCR pipeline can't reliably read
# image-rendered Arabic financial-statement pages — those are deferred to
# the Mistral fallback in Phase 5 Part 13. Skipping AR halves runtime.
#
# Tolerances:
#     Currency-like values  ±5%   (revenue, net_income, total_assets, etc.)
#     EPS, DPS, shares      ±0.1% (effectively exact)

from dotenv import load_dotenv
import os
import sys

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app import create_app
from app.models.stock import Stock
from app.models.financial_data import FinancialData
from app.services.pdf_extractor import extract_all


PDF_DIR = os.path.join(os.path.dirname(__file__), 'test_pdfs')
TEST_PERIOD = "2024-annual"

# 6 companies × 2 languages → 12 PDFs.
# 2280 (Almarai) is the out-of-sample anchor — kept here so every regression
# run validates against a company we did NOT use to tune keyword lists.
TEST_FILES = {
    "2222": ("2222_aramco_2024_annual_en.pdf",   "2222_aramco_2024_annual_ar.pdf"),
    "1120": ("1120_alrajhi_2024_annual_en.pdf",  "1120_alrajhi_2024_annual_ar.pdf"),
    "2010": ("2010_sabic_2024_annual_en.pdf",    "2010_sabic_2024_annual_ar.pdf"),
    "4190": ("4190_jarir_2024_annual_en.pdf",    "4190_jarir_2024_annual_ar.pdf"),
    "7010": ("7010_stc_2024_annual_en.pdf",      "7010_stc_2024_annual_ar.pdf"),
    "2280": ("2280_almarai_2024_annual_en.pdf",  "2280_almarai_2024_annual_ar.pdf"),
    "7030": ("7030_zain_2024_annual_en.pdf",     "7030_zain_2024_annual_ar.pdf"),
}

# Per-value tolerance as a relative fraction (0.05 = 5%).
TOLERANCES = {
    "revenue":              0.05,
    "net_income":           0.05,
    "total_assets":         0.05,
    "shareholders_equity":  0.05,
    "total_borrowings":     0.05,
    "cash_and_equivalents": 0.05,
    "free_cash_flow":       0.05,
    "eps":                  0.001,
    "shares_outstanding":   0.001,
    "dividends_per_share":  0.001,
}

ALL_VALUES = list(TOLERANCES.keys())


def _classify(extracted, expected, tolerance):
    if expected is None or expected == 0:
        return "N/A"
    if extracted is None:
        return "FAIL"
    rel = abs(extracted - expected) / abs(expected)
    return "MATCH" if rel <= tolerance else "DISAGREE"


def _fmt(v):
    if v is None:
        return f"{'None':>15}"
    if abs(v) >= 1_000:
        return f"{v:>15,.0f}"
    return f"{v:>15,.4f}"


def run_tests(values_to_test, *, with_ar=False):
    """Extract test PDFs and report accuracy for the requested values only.
    By default only English PDFs are extracted; pass with_ar=True to include
    Arabic (slow due to OCR and currently unreliable — see module docstring)."""
    app = create_app()
    with app.app_context():
        # Pull 2024 financial_data row for each test company
        db_values = {}
        for sym in TEST_FILES:
            stock = Stock.query.filter_by(symbol=sym).first()
            if stock is None:
                print(f"WARN: stock {sym} missing from DB")
                db_values[sym] = None
                continue
            fd = FinancialData.query.filter_by(stock_id=stock.id, period=TEST_PERIOD).first()
            if fd is None:
                print(f"WARN: no {TEST_PERIOD} financial_data for {sym}")
            db_values[sym] = fd

        # Extract each PDF once, then evaluate each requested value.
        # Shape: results[value][pdf_filename] = (extracted, expected, status)
        results = {v: {} for v in values_to_test}

        for sym, (en, ar) in TEST_FILES.items():
            files = (en, ar) if with_ar else (en,)
            for fname in files:
                path = os.path.join(PDF_DIR, fname)
                print(f"  extracting {fname} ...", flush=True)
                extracted = extract_all(path)
                fd = db_values[sym]
                for v in values_to_test:
                    expected = getattr(fd, v) if fd else None
                    status = _classify(extracted[v], expected, TOLERANCES[v])
                    results[v][fname] = (extracted[v], expected, status)

        # ── Per-value summary ──
        print()
        print("=" * 92)
        print(f"  {'value':<22}  {'match':>5}  {'disagree':>8}  {'fail':>4}  {'n/a':>3}  {'accuracy':>9}")
        print("-" * 92)
        all_evaluable = 0
        all_match = 0
        for v in values_to_test:
            cells = list(results[v].values())
            m  = sum(1 for c in cells if c[2] == "MATCH")
            d  = sum(1 for c in cells if c[2] == "DISAGREE")
            f  = sum(1 for c in cells if c[2] == "FAIL")
            na = sum(1 for c in cells if c[2] == "N/A")
            evaluable = m + d + f
            acc = (m / evaluable * 100) if evaluable else 0.0
            all_evaluable += evaluable
            all_match += m
            print(f"  {v:<22}  {m:>5}  {d:>8}  {f:>4}  {na:>3}  {acc:>8.1f}%")

        print("-" * 92)
        overall = (all_match / all_evaluable * 100) if all_evaluable else 0.0
        print(f"  {'OVERALL':<22}  {all_match:>5}  {'':>8}  {'':>4}  {'':>3}  {overall:>8.1f}%")
        print("=" * 92)

        # ── Per-PDF detail (only for the values being tested) ──
        for v in values_to_test:
            print(f"\n── {v} ──")
            for fname in sorted(results[v].keys()):
                extracted, expected, status = results[v][fname]
                print(f"  {fname:<40}  ext={_fmt(extracted)}  exp={_fmt(expected)}  {status}")


if __name__ == "__main__":
    args = sys.argv[1:]
    with_ar = "--with-ar" in args
    args = [a for a in args if a != "--with-ar"]
    values = args if args else ALL_VALUES
    invalid = [v for v in values if v not in ALL_VALUES]
    if invalid:
        print(f"Unknown value name(s): {invalid}")
        print(f"Valid: {ALL_VALUES}")
        sys.exit(1)
    run_tests(values, with_ar=with_ar)
