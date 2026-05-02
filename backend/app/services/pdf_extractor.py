# pdf_extractor.py — Extract 10 financial values from Saudi Tadawul annual reports.
#
# Strategy: bilingual keyword matching (English + Arabic) over text-extracted
# pages. All 10 known test PDFs are text-based — no OCR fallback in the MVP.
# If a scanned PDF appears later, add a pytesseract fallback inside _extract_text.
#
# Public interface:
#     extract_all(pdf_path) -> dict mapping each of the 10 value names to
#                              float or None.
#
# Per-value functions follow this shape:
#     extract_<name>(pages) -> float or None
# where `pages` is the list of (page_num, text) tuples from _extract_text.
# Splitting them out keeps each extractor independently testable and lets
# us iterate one value at a time without re-extracting PDF text.
#
# Build progress (each is None until its part lands):
#   Part 2  revenue
#   Part 3  net_income
#   Part 4  eps
#   Part 5  total_assets
#   Part 6  shareholders_equity
#   Part 7  total_borrowings
#   Part 8  cash_and_equivalents
#   Part 9  free_cash_flow
#   Part 10 shares_outstanding
#   Part 11 dividends_per_share

import re
import pdfplumber


# ── Keyword lists per value (English + Arabic) ──────────────────
# Each list is searched in order; first hit wins. Add variations as we
# encounter them in real PDFs. Match is case-insensitive.
KEYWORDS = {
    "revenue": [
        "Total revenue", "Revenue", "Net sales", "Total sales",
        "إجمالي الإيرادات", "الإيرادات", "صافي المبيعات",
    ],
    "net_income": [
        "Net income", "Net profit", "Profit for the year", "Net earnings",
        "صافي الدخل", "صافي الربح", "ربح السنة",
    ],
    "eps": [
        "Basic earnings per share", "Earnings per share", "EPS", "Basic EPS",
        "ربحية السهم الأساسية", "ربحية السهم", "العائد على السهم",
    ],
    "total_assets": [
        "Total assets", "إجمالي الأصول", "إجمالي الموجودات", "مجموع الموجودات",
    ],
    "shareholders_equity": [
        "Total shareholders' equity", "Total shareholders equity",
        "Shareholders' equity", "Total equity",
        "إجمالي حقوق المساهمين", "حقوق المساهمين", "إجمالي حقوق الملكية",
    ],
    "total_borrowings": [
        "Total borrowings", "Total debt", "Long-term debt", "Borrowings",
        "إجمالي القروض", "مجموع القروض", "القروض",
    ],
    "cash_and_equivalents": [
        "Cash and cash equivalents", "Cash and equivalents",
        "النقد وما يماثله", "النقد ومعادلاته", "النقد ومايعادله",
    ],
    "free_cash_flow": [
        "Free cash flow", "FCF",
        "التدفق النقدي الحر", "التدفقات النقدية الحرة",
    ],
    "shares_outstanding": [
        "Shares outstanding", "Number of shares", "Issued shares",
        "Weighted average number of shares",
        "عدد الأسهم", "الأسهم المصدرة", "المتوسط المرجح لعدد الأسهم",
    ],
    "dividends_per_share": [
        "Dividends per share", "DPS", "Dividend per share",
        "توزيعات الأرباح للسهم", "توزيعات أرباح السهم",
    ],
}


# ── Unit detection ──────────────────────────────────────────────
# Many Saudi annual reports state values in millions or thousands of SAR.
# Patterns are checked in order; first match wins. If none match, return 1.
UNIT_PATTERNS = [
    (re.compile(r"in\s+millions|بالملايين|ملايين\s+الريالات", re.I), 1_000_000),
    (re.compile(r"in\s+thousands|بالآلاف|آلاف\s+الريالات", re.I), 1_000),
]


def _detect_unit(text):
    """Scan text for unit hints; return multiplier (1, 1_000, or 1_000_000)."""
    for pattern, mult in UNIT_PATTERNS:
        if pattern.search(text):
            return mult
    return 1


# ── Number parsing ──────────────────────────────────────────────
# Handles: "1,234,567.89", "(1,234)" (negative), "12.5%", whitespace.
# Does NOT handle: scientific notation, Eastern Arabic digits (٠١٢…).
# We can extend later if real PDFs use Arabic digits — a quick test will tell us.
NUMBER_RE = re.compile(r"\(?-?[\d,]+(?:\.\d+)?\)?")


def _parse_number(s):
    """Convert a matched number string to float, handling commas and parentheses.
    Returns None if the string can't be parsed."""
    if not s:
        return None
    s = s.strip()
    negative = s.startswith("(") and s.endswith(")")
    s = s.strip("()").replace(",", "").replace("%", "").strip()
    try:
        v = float(s)
        return -v if negative else v
    except ValueError:
        return None


# ── Page extraction ─────────────────────────────────────────────

def _extract_text(pdf_path):
    """Return [(page_num, text), ...] with 1-based page numbers."""
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            pages.append((i, page.extract_text() or ""))
    return pages


# ── Per-value extractors (stubs until each part lands) ──────────

def extract_revenue(pages):              return None
def extract_net_income(pages):           return None
def extract_eps(pages):                  return None
def extract_total_assets(pages):         return None
def extract_shareholders_equity(pages):  return None
def extract_total_borrowings(pages):     return None
def extract_cash_and_equivalents(pages): return None
def extract_free_cash_flow(pages):       return None
def extract_shares_outstanding(pages):   return None
def extract_dividends_per_share(pages):  return None


# ── Orchestrator ────────────────────────────────────────────────

def extract_all(pdf_path):
    """Extract all 10 financial values from one PDF.

    Returns dict with keys matching FinancialData column names. A value of
    None means extraction returned nothing — either the field is not
    implemented yet, or the extractor couldn't find a match.
    """
    pages = _extract_text(pdf_path)
    return {
        "revenue":              extract_revenue(pages),
        "net_income":           extract_net_income(pages),
        "eps":                  extract_eps(pages),
        "total_assets":         extract_total_assets(pages),
        "shareholders_equity":  extract_shareholders_equity(pages),
        "total_borrowings":     extract_total_borrowings(pages),
        "cash_and_equivalents": extract_cash_and_equivalents(pages),
        "free_cash_flow":       extract_free_cash_flow(pages),
        "shares_outstanding":   extract_shares_outstanding(pages),
        "dividends_per_share":  extract_dividends_per_share(pages),
    }
