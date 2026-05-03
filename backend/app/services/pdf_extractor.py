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

# OCR fallback for image-based pages. Many Tadawul annual reports embed the
# financial statements section as images while the rest of the document is
# real text. Detect "empty" pages and OCR them with Tesseract (eng + ara).
import pytesseract
from pdf2image import convert_from_path

# Pages with fewer than this many extracted characters are treated as
# image-only and routed through OCR. Tuned from observation: real text
# pages had 1000+ chars, image pages returned 0–50.
TEXT_THRESHOLD_CHARS = 50

# pdf2image uses Poppler to rasterize. Higher DPI = better OCR but slower.
# 200 is a common sweet spot for printed financial statements.
OCR_DPI = 200

# tesseract languages: English + Arabic. The "+" tells Tesseract to load both.
OCR_LANGS = "eng+ara"


# ── Keyword lists per value (English + Arabic) ──────────────────
# Each list is searched in order; first hit wins. Add variations as we
# encounter them in real PDFs. Match is case-insensitive.
#
# Arabic note: pdfplumber returns Arabic text in *visual* (RTL-reversed)
# order, while Tesseract OCR returns it in *logical* order. The keywords
# below are written in logical order; _expand_arabic() generates a
# character-reversed twin for each so we match either source.
ARABIC_RANGE = ("؀", "ۿ")  # Arabic Unicode block


def _is_arabic(s):
    return any(ARABIC_RANGE[0] <= c <= ARABIC_RANGE[1] for c in s)


def _expand_arabic(keywords):
    """Return original list plus a character-reversed copy of each Arabic
    entry (for matching against pdfplumber's visual-order extraction)."""
    out = list(keywords)
    for kw in keywords:
        if _is_arabic(kw):
            rev = kw[::-1]
            if rev not in out:
                out.append(rev)
    return out


KEYWORDS = {
    "revenue": [
        # Aramco-style: matches the broader yfinance "Total Revenue" definition
        # (must come BEFORE "Revenue" since both lines appear and substring matches "Revenue").
        "Revenue and other income related to sales",
        # Industrial / consumer / telecom / energy
        "Total revenue", "Revenue", "Revenues", "Net sales", "Total sales",
        "إجمالي الإيرادات", "الإيرادات", "إيرادات", "الايرادات", "ايرادات",
        "صافي المبيعات", "المبيعات",
        # Banks (no "revenue" line — total operating income is the analog)
        "Total operating income", "Net financing income",
        "إجمالي الدخل التشغيلي", "صافي دخل التمويل", "الدخل التشغيلي",
    ],
    # net_income is split into attribution + total constants below the
    # KEYWORDS dict (extract_net_income runs them in stages). Leaving an
    # empty placeholder here so the dict still has the key for callers
    # that introspect KEYWORDS.
    "net_income": [],
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

# Auto-add reversed-form Arabic variants so we match either pdfplumber's
# visual-order extraction or Tesseract's logical-order output.
KEYWORDS = {k: _expand_arabic(v) for k, v in KEYWORDS.items()}


# ── Net income: attribution vs consolidated total ───────────────
# yfinance reports parent-attributable net income (excluding minority
# interests). Most Saudi annual reports show two values:
#   1. Consolidated total                       e.g. "Net income"
#   2. Attributable to equity holders of parent e.g. "• Equity holders ..."
# We try (1) attribution-with-anchor, (2) attribution-without-anchor (for
# multi-column layouts pdfplumber flattens), then (3) the consolidated
# total as a fallback. See extract_net_income for the orchestration.
#
# Each company labels the parent differently — Saudi banks say "of the
# Bank", others "of the Parent", "of the Parent Company", or "of the
# Company". STC + SABIC's 2024 statements show *two* attribution lines
# (continuing-ops attribution first, total attribution second), so the
# matcher uses last-match semantics for these keywords.
NET_INCOME_ATTRIBUTION_KEYWORDS = _expand_arabic([
    "Net income attributable to equity holders of the parent",
    "Net income attributable to shareholders of the parent",
    "Net profit attributable to equity holders of the parent",
    "Net profit attributable to shareholders of the parent",
    "Profit attributable to equity holders of the parent",
    "Profit attributable to shareholders of the parent",
    "Equity holders of the Parent Company",
    "Equity holders of the parent",
    "Equity holders of the Bank",
    "Equity holders of the Company",
    "Shareholders of the Parent Company",
    "Shareholders of the parent",
    "Shareholders of the Bank",
    "Shareholders of the Company",
    # Arabic
    "العائد إلى مساهمي الشركة الأم",
    "العائد لمساهمي الشركة الأم",
    "العائد لمساهمي البنك",
    "صافي الدخل العائد إلى مساهمي الشركة الأم",
    "صافي الربح العائد إلى مساهمي الشركة الأم",
    "حصة مساهمي الشركة الأم",
    "حصة مساهمي البنك",
    "مساهمي الشركة الأم",
])
NET_INCOME_TOTAL_KEYWORDS = _expand_arabic([
    "Profit for the year", "Net profit", "Net income", "Net earnings",
    "صافي الدخل", "صافي الربح", "ربح السنة", "ربح العام",
])
# Lines mentioning these qualifiers are NOT the consolidated total —
# Al Rajhi's "Net income for the year before Zakat" is 21.97B vs the
# real 19.73B post-zakat figure on the next line.
NET_INCOME_TOTAL_DISQUALIFIERS = [
    re.compile(r"before\s+zakat", re.I),
    re.compile(r"before\s+(?:income\s+)?tax", re.I),
    re.compile(r"قبل\s+الزكاة"),
    re.compile(r"قبل\s+الضريبة"),
]


# ── Unit detection ──────────────────────────────────────────────
# Match a unit hint only when it appears in a recognisable declaration
# context, not in narrative prose ("impairment of SR 1,387 million" should
# NOT pull millions for the whole page).
#
# Variants we've seen across the 5 test companies:
#   SABIC:    "All amounts in thousands of Saudi Riyals"
#   Aramco:   "All amounts in millions of Saudi Riyals"
#   STC:      "All Amounts in Saudi Riyals Thousands"
#   Al Rajhi: "(SAR'000)"
#
# Each pattern requires a currency anchor (Saudi Riyals / SAR / SR /
# الريالات / ريال) close to the unit word, except for the apostrophe form.
UNIT_PATTERNS = [
    # SAR'000  /  SR ' 000  (apostrophe = thousands, "Mn" = millions)
    (re.compile(r"(?:SAR|SR)\s*['’‘′ʼ`]\s*000", re.I), 1_000),
    (re.compile(r"(?:SAR|SR)\s*['’‘′ʼ`]\s*0{6}", re.I), 1_000_000),
    (re.compile(r"(?:SAR|SR)\s*['’‘′ʼ`]\s*[Mm]n?\b", re.I), 1_000_000),
    # "in millions/thousands of Saudi Riyals|SAR|SR"
    (re.compile(r"\bin\s+millions?\s+of\s+(?:Saudi\s+Riyals?|SAR|SR)\b", re.I), 1_000_000),
    (re.compile(r"\bin\s+thousands?\s+of\s+(?:Saudi\s+Riyals?|SAR|SR)\b", re.I), 1_000),
    # "Saudi Riyals millions/thousands" (STC's reversed phrasing)
    (re.compile(r"\b(?:Saudi\s+Riyals?|SAR|SR)\s+millions?\b", re.I), 1_000_000),
    (re.compile(r"\b(?:Saudi\s+Riyals?|SAR|SR)\s+thousands?\b", re.I), 1_000),
    # Parenthesised "(in millions)" or "(in thousands)" — last-resort English
    (re.compile(r"\(\s*in\s+millions?\s*\)", re.I), 1_000_000),
    (re.compile(r"\(\s*in\s+thousands?\s*\)", re.I), 1_000),
    # Arabic: standalone unit words are typically declarative on a header line
    (re.compile(r"بالملايين|ملايين\s+الريالات|ملايين\s+ريال"), 1_000_000),
    (re.compile(r"بالآلاف|آلاف\s+الريالات|آلاف\s+ريال"), 1_000),
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


# ── Income statement detection ──────────────────────────────────
# The income statement (a.k.a. statement of profit or loss) is the
# authoritative place for revenue and net income. Searching here first
# avoids the highlights/summary tables which sometimes restate or round.
#
# Patterns are regexes (not literals) because OCR introduces missing or
# extra whitespace — e.g. "PROFIT OR LOSS" came back as "PROFIT ORLOSS"
# from Tesseract. \s* tolerates that. Arabic patterns are matched in both
# logical and reversed (visual) form via _expand_arabic.
_HEADER_PATTERN_STRINGS = [
    r"statement\s+of\s+profit\s*or\s*loss",
    r"statement\s+of\s+income",
    r"income\s+statement",
    r"statement\s+of\s+comprehensive\s+income",
    "قائمة الدخل",
    "قائمة الأرباح والخسائر",
    "قائمة الربح أو الخسارة",
    "قائمة الربح والخسارة",
    "قائمة الدخل الشامل",
    "قائمة الدخل الموحدة",
]
_HEADER_PATTERN_STRINGS = _expand_arabic(_HEADER_PATTERN_STRINGS)
INCOME_STATEMENT_PATTERNS = [re.compile(p, re.I) for p in _HEADER_PATTERN_STRINGS]


def _pages_matching_patterns(pages, patterns):
    """Return the subset of pages whose text matches any of the given regexes."""
    matches = []
    for page in pages:
        _, text = page
        for pat in patterns:
            if pat.search(text):
                matches.append(page)
                break
    return matches


# ── Keyword-based value lookup ──────────────────────────────────

def _value_near_keyword(text, keywords, *, anchor_start=True, last=False, exclude=()):
    """Find a plausible number on a line where the keyword appears.

    "Near the start" (anchor_start=True) = within the first 6 chars of the
    stripped line. Filters narrative mentions ("applied to revenue
    recognition...") while allowing leading note numbers / bullets.

    anchor_start=False drops that constraint — needed when pdfplumber
    flattens multi-column layouts and a tabular row ends up mid-line.
    Use only with phrases specific enough that mid-line matches are safe
    (e.g. "Equity holders of the parent").

    last=True returns the LAST plausible match per keyword instead of the
    first. Used for net-income attribution where statements with both
    continuing-ops and total sub-lines list them in that order; yfinance
    reports the second.

    exclude is a list of compiled regexes; matching lines are skipped.

    Plausible number = not a year (2010-2099), not tiny (|n| < 100, which
    rules out page references and footnote markers). Negatives "(1,234)"
    and "-1,234" are parsed as signed by NUMBER_RE + _parse_number.
    """
    for kw in keywords:
        kw_lower = kw.lower()
        candidate = None
        for line in text.splitlines():
            stripped = line.strip()
            if exclude and any(p.search(stripped) for p in exclude):
                continue
            stripped_lower = stripped.lower()
            pos = stripped_lower.find(kw_lower)
            if pos < 0:
                continue
            if anchor_start and pos > 6:
                continue
            after = stripped[pos + len(kw):]
            for m in NUMBER_RE.finditer(after):
                n = _parse_number(m.group(0))
                if n is None:
                    continue
                if 2010 <= n <= 2099 and n == int(n):
                    continue  # year column header
                if abs(n) < 100:
                    continue  # page ref / footnote
                if not last:
                    return n
                candidate = n
                break  # first plausible number on this line is the row's value
        if candidate is not None:
            return candidate
    return None


def _extract_in_pages(pages_subset, keywords, **kwargs):
    """Run _value_near_keyword across a list of pages; first hit wins.
    Applies unit detection on the page where the match was found.
    kwargs (anchor_start, last, exclude) are forwarded to _value_near_keyword."""
    for _, text in pages_subset:
        n = _value_near_keyword(text, keywords, **kwargs)
        if n is not None:
            return n * _detect_unit(text)
    return None


# ── Page extraction (text first, OCR fallback) ──────────────────

def _ocr_pages(pdf_path, page_numbers):
    """OCR the specified 1-based page numbers, returns dict {page_num: text}.

    pdf2image rasterizes each requested page individually (first_page/last_page)
    so we don't pay the cost for pages that already had real text.
    """
    out = {}
    for pn in page_numbers:
        images = convert_from_path(pdf_path, dpi=OCR_DPI, first_page=pn, last_page=pn)
        if not images:
            out[pn] = ""
            continue
        out[pn] = pytesseract.image_to_string(images[0], lang=OCR_LANGS)
    return out


def _extract_text(pdf_path):
    """Return [(page_num, text), ...] with 1-based page numbers.

    Pages where pdfplumber finds < TEXT_THRESHOLD_CHARS are OCR'd, since
    most "empty" pages in our test set are the image-rendered financial
    statements (which is exactly what we need to read).
    """
    pages = []
    image_page_nums = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if len(text.strip()) < TEXT_THRESHOLD_CHARS:
                image_page_nums.append(i)
                pages.append((i, ""))  # placeholder — filled by OCR below
            else:
                pages.append((i, text))

    if image_page_nums:
        ocr_results = _ocr_pages(pdf_path, image_page_nums)
        pages = [(pn, ocr_results[pn]) if pn in ocr_results else (pn, t)
                 for pn, t in pages]

    return pages


# ── Per-value extractors (stubs until each part lands) ──────────

def extract_revenue(pages):
    """Find revenue (or, for banks, total operating income).

    Strategy:
      1. Search inside the income statement (authoritative).
      2. If nothing found there, fall back to scanning the whole document
         (catches highlights/summary tables when income-statement parsing
         fails — e.g. multi-line headers, RTL Arabic table quirks).
    """
    keywords = KEYWORDS["revenue"]
    income_pages = _pages_matching_patterns(pages, INCOME_STATEMENT_PATTERNS)
    return (_extract_in_pages(income_pages, keywords)
            or _extract_in_pages(pages, keywords))
def extract_net_income(pages):
    """Find net income, preferring parent-attributable when reported.

    Per subset (income-statement pages first, then whole doc), run three
    stages and return the first hit:
      1. Attribution keywords with start-of-line anchor + LAST match.
         Last-match handles 2024 statements (STC, SABIC) that show both
         continuing-ops attribution and total attribution; yfinance reports
         the latter, which appears later in the statement.
      2. Same attribution keywords WITHOUT the start-of-line anchor.
         pdfplumber flattens SABIC's two-column income statement so the
         attribution row ends up mid-line.
      3. Fallback to consolidated-total keywords with disqualifiers for
         "before zakat / before tax" pseudo-totals (Al Rajhi shows the
         pre-zakat line first; we want the post-zakat one).

    Negatives are handled implicitly by NUMBER_RE + _parse_number — a
    full-year loss in "(1,234)" parens is returned as -1,234.
    """
    income_pages = _pages_matching_patterns(pages, INCOME_STATEMENT_PATTERNS)
    stages = [
        (NET_INCOME_ATTRIBUTION_KEYWORDS, dict(last=True, anchor_start=True)),
        (NET_INCOME_ATTRIBUTION_KEYWORDS, dict(last=True, anchor_start=False)),
        (NET_INCOME_TOTAL_KEYWORDS,
         dict(last=False, anchor_start=True, exclude=NET_INCOME_TOTAL_DISQUALIFIERS)),
    ]
    for subset in (income_pages, pages):
        for keywords, kwargs in stages:
            n = _extract_in_pages(subset, keywords, **kwargs)
            if n is not None:
                return n
    return None
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
