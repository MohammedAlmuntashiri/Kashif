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
        # Specific phrases come first — generic "Revenue" / "Revenues" below
        # would otherwise match unrelated lines like "Other revenue" (Bupa)
        # or "Revenue from contracts" via substring search.
        #
        # Aramco-style: matches the broader yfinance "Total Revenue" definition.
        "Revenue and other income related to sales",
        # Insurance (IFRS 17): "Insurance revenue" is the standard line item
        # on the income statement (Bupa 2024 uses this exact phrase). Net
        # earned premiums / gross written premiums are pre-IFRS-17 fallbacks
        # for older filings. MUST come before generic "Revenue" — otherwise
        # "Revenue" matches "Other revenue 90,386" (pos=6, anchor-allowed)
        # and never reaches the real insurance line.
        "Insurance revenue", "Net earned premiums", "Gross written premiums",
        "إيرادات التأمين", "صافي الأقساط المكتسبة", "إجمالي الأقساط المكتتبة",
        # Banks (no "revenue" line — total operating income is the analog).
        # Net operating income is the after-impairment variant some banks use.
        "Total operating income", "Net operating income", "Net financing income",
        "إجمالي الدخل التشغيلي", "صافي الدخل التشغيلي", "صافي دخل العمليات",
        "صافي دخل التمويل", "الدخل التشغيلي",
        # Industrial / consumer / telecom / energy (generic — match last).
        "Total revenue", "Revenue", "Revenues", "Net sales", "Total sales",
        "إجمالي الإيرادات", "الإيرادات", "إيرادات", "الايرادات", "ايرادات",
        "صافي المبيعات", "المبيعات",
    ],
    # net_income is split into attribution + total constants below the
    # KEYWORDS dict (extract_net_income runs them in stages). Leaving an
    # empty placeholder here so the dict still has the key for callers
    # that introspect KEYWORDS.
    "net_income": [],
    # eps uses the EPS_KEYWORDS / EPS_DISQUALIFIERS module-level
    # constants below the KEYWORDS dict — extract_eps applies a different
    # numeric range and skips unit detection.
    "eps": [],
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
    # Insurance variants use passive verb "attributed" instead of the
    # adjective "attributable" — Bupa 2024 prints "Net income attributed
    # to the shareholders". The label/value are split across two lines, so
    # this won't capture the value directly; the canonical post-zakat row
    # is caught by the "After zakat and income tax" total-keyword above.
    "Net income attributed to the shareholders",
    "Income attributed to the shareholders",
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
    # Insurance bottom line — Bupa 2024 splits the label across two lines:
    #   "NET INCOME ATTRIBUTED TO THE SHAREHOLDERS"
    #   "AFTER ZAKAT AND INCOME TAX 1,166,002 940,163"
    # The second line carries the value, so we anchor on its leading phrase.
    # Safe vs the "before zakat" pseudo-total — that's filtered by
    # NET_INCOME_TOTAL_DISQUALIFIERS before we even see the line. MUST come
    # before generic "Net income" — that keyword would otherwise match a
    # random in-document mention with a small unrelated number on the same line.
    "After zakat and income tax",
    "بعد الزكاة وضريبة الدخل",
    "Profit for the year", "Net profit", "Net income", "Net earnings",
    "صافي الدخل", "صافي الربح", "ربح السنة", "ربح العام",
])
# Lines mentioning these qualifiers are NOT the consolidated total —
# Al Rajhi's "Net income for the year before Zakat" is 21.97B vs the
# real 19.73B post-zakat figure on the next line.
NET_INCOME_TOTAL_DISQUALIFIERS = [
    # Allow punctuation between "before" and "zakat/tax" — Bupa's page 69
    # supplementary table flattens to "...before, zakat and income tax..."
    # which strict \s+ would miss.
    re.compile(r"before[\W_]*zakat", re.I),
    re.compile(r"before[\W_]*(?:income[\W_]*)?tax", re.I),
    re.compile(r"قبل\s+الزكاة"),
    re.compile(r"قبل\s+الضريبة"),
]


# ── EPS: total (basic) earnings per share ───────────────────────
# yfinance reports basic EPS attributable to ordinary equity holders.
# Two complications shape the keyword + filter set:
#
#   1. Continuing-vs-total split (STC, SABIC) — same as net_income, the
#      total EPS sub-line comes AFTER the continuing-ops one. Last-match
#      semantics + a "continuing operations" disqualifier give us the
#      total figure.
#
#   2. Bullet-list sub-lines under an EPS-section header (SABIC) — labels
#      look like "• Net income (loss) 0.51 (0.92)", i.e. the same words
#      that appear on the actual income-statement totals (3.7M / -384K).
#      Adding "Net income" to EPS_KEYWORDS would normally collide with
#      the income line; max_abs=10_000 filters out the multi-million
#      currency value while leaving the genuine 0.51 EPS in scope.
EPS_KEYWORDS = _expand_arabic([
    # Singular "earning" first — Al Rajhi's notes section uses singular
    # ("Basic and diluted earning per share (in SAR) 4.67 3.95"), while
    # page 10's income statement says plural ("...earnings per share...
    # 4.81") which is the pre-Sukuk-adjustment figure. Tadawul/yfinance
    # report the post-adjustment 4.67, so the singular variant must win.
    "Basic and diluted earning per share",
    "Basic and diluted earnings per share",
    "Basic earning per share",
    "Basic earnings per share",
    "Diluted earnings per share",
    "Diluted earning per share",
    "Earnings per share",
    "Earning per share",
    # SABIC's bullet-list sub-lines under the EPS header reuse income
    # labels — these match alongside the EPS-specific phrases above.
    "Net income (loss)",
    "Net income",
    "Net profit",
    # STC + Almarai print the EPS values on rows whose ONLY label is
    # "Basic" / "Diluted" (the "Earnings per share" is a separate header
    # line above). Kept low-priority so the more-specific phrases above
    # win when present.
    "Basic",
    "Diluted",
    # Habib's EPS row spans two lines; the value-bearing second line is:
    #   "attributable to equity holders of the parent 26 6.62 5.85"
    # max_abs=10_000 + require_decimal=True keep this safe — the same phrase
    # in net-income context (Aramco/SABIC/etc.) carries large integer values
    # that get filtered out before this keyword has a chance to claim them.
    "attributable to equity holders of the parent",
    # Arabic
    "ربحية السهم الأساسية",
    "ربحية السهم المخففة",
    "ربحية السهم",
    "العائد على السهم",
    "أساسي",
    "مخفف",
])
EPS_DISQUALIFIERS = [
    re.compile(r"continuing\s+operations", re.I),
    re.compile(r"discontinued\s+operations", re.I),
    re.compile(r"before\s+zakat", re.I),
    re.compile(r"before\s+(?:income\s+)?tax", re.I),
    re.compile(r"العمليات\s+المستمرة"),
    re.compile(r"العمليات\s+المتوقفة"),
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
    # SAR'000  /  SR ' 000  /  SAR‘'000 (OCR-garbled with double quotes)
    # Allow whitespace + any combination of quote-like chars between the
    # currency and the zero block; image-rendered statements (SNB) often
    # come back with two stacked quotation marks.
    (re.compile(r"(?:SAR|SR)[\s'’‘′ʼ`]*0{3}\b", re.I), 1_000),
    (re.compile(r"(?:SAR|SR)[\s'’‘′ʼ`]*0{6}\b", re.I), 1_000_000),
    (re.compile(r"(?:SAR|SR)[\s'’‘′ʼ`]*[Mm]n?\b", re.I), 1_000_000),
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


# ── Balance-sheet detection ─────────────────────────────────────
# Balance sheet (statement of financial position) is the authoritative
# source for total_assets, shareholders_equity, total_borrowings, and
# cash_and_equivalents. Most Saudi 2024 filings use IFRS terminology
# ("Statement of Financial Position") rather than the older "Balance
# Sheet" — both included for older filings.
_BS_HEADER_PATTERN_STRINGS = [
    r"statement\s+of\s+financial\s+position",
    r"balance\s+sheet",
    "قائمة المركز المالي",
    "قائمة المركز المالي الموحدة",
    "الميزانية العمومية",
    "الميزانية",
]
_BS_HEADER_PATTERN_STRINGS = _expand_arabic(_BS_HEADER_PATTERN_STRINGS)
BALANCE_SHEET_PATTERNS = [re.compile(p, re.I) for p in _BS_HEADER_PATTERN_STRINGS]


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

def _value_near_keyword(text, keywords, *,
                        anchor_start=True, last=False, exclude=(),
                        min_abs=100, max_abs=float("inf"),
                        require_decimal=False,
                        next_line_fallback=False):
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

    min_abs / max_abs bound the plausible-value range. Defaults (100, inf)
    suit currency rows. EPS / DPS need min_abs ≈ 0.01, max_abs ≈ 10_000:
    EPS is typically 0.10–20 SAR/share, and the upper bound filters out
    income totals when an EPS keyword (e.g. SABIC's "• Net income (loss)"
    bullet) also matches the corresponding income-statement total line.

    require_decimal=True rejects integer matches — used for per-share
    values, which are always printed with at least one decimal place.
    This filters out the "Note 37" reference column that follows EPS row
    labels in many Saudi annual reports (NUMBER_RE would otherwise
    capture "37)" as a plausible signed integer).

    next_line_fallback=True: when the keyword line has no plausible number
    on it, peek at the next non-empty line and use its first plausible
    number. Required for column-layout balance sheets (Jarir, Habib) where
    "Total assets" sits on a label-only line and the value lives below.

    Plausible number = not a year (2010-2099), within [min_abs, max_abs].
    Negatives "(1,234)" and "-1,234" are parsed as signed.
    """
    def _first_plausible(s):
        s = re.sub(r"(\d)\s+\.(\d)", r"\1.\2", s)
        # Collect all parsed tokens first so the kerning heal below can
        # cross-check against the YoY comparative column.
        matches = []
        for m in NUMBER_RE.finditer(s):
            tok = m.group(0)
            if require_decimal and "." not in tok:
                continue
            n = _parse_number(tok)
            if n is None:
                continue
            if 2010 <= n <= 2099 and n == int(n):
                continue
            matches.append((tok, n))
        if not matches:
            return None
        # Kerning-split heal: pdfplumber sometimes inserts a stray space
        # between the leading digit and the rest of a comma-formatted number
        # (Almarai 2024 BS: "TOTAL ASSETS 3 5,567,960 36,194,015" — the 3
        # is the leading digit of 35,567,960, not a note ref). Distinguish
        # from a real note number (Aramco "Revenue 3 1,801,674 1,604,220")
        # by checking whether merging makes the YoY comparison plausible
        # AND treating the digit as a note leaves it implausible. Skipped
        # under require_decimal since per-share values don't follow this
        # 3-column layout.
        if len(matches) >= 3 and not require_decimal:
            tok1, n1 = matches[0]
            tok2, n2 = matches[1]
            tok3, n3 = matches[2]
            if (0 < n1 < 100 and "." not in tok1 and "." not in tok2
                    and abs(n3) >= 1000):
                digits1 = re.sub(r"\D", "", tok1)
                digits2 = re.sub(r"\D", "", tok2)
                if digits1 and digits2:
                    try:
                        merged = float(digits1 + digits2)
                    except ValueError:
                        merged = None
                    if merged is not None:
                        note_diff = abs(n2 - n3) / abs(n3)
                        merge_diff = abs(merged - n3) / abs(n3)
                        if merge_diff < 0.5 and note_diff > 0.5:
                            if min_abs <= abs(merged) <= max_abs:
                                return merged
        for tok, n in matches:
            if min_abs <= abs(n) <= max_abs:
                return n
        return None

    for kw in keywords:
        kw_lower = kw.lower()
        candidate = None
        lines = text.splitlines()
        for i, line in enumerate(lines):
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
            n = _first_plausible(after)
            if n is None and next_line_fallback:
                # Walk forward to the first non-empty, non-disqualified line
                # and try its first plausible number. Caps at +3 lines so we
                # don't stray into the next section.
                for j in range(1, 4):
                    if i + j >= len(lines):
                        break
                    nxt = lines[i + j].strip()
                    if not nxt:
                        continue
                    if exclude and any(p.search(nxt) for p in exclude):
                        break
                    n = _first_plausible(nxt)
                    break
            if n is None:
                continue
            if not last:
                return n
            candidate = n
        if candidate is not None:
            return candidate
    return None


def _extract_in_pages(pages_subset, keywords, *,
                      skip_unit=False, keyword_priority_over_page=False,
                      **kwargs):
    """Run _value_near_keyword across a list of pages; first hit wins.

    Applies unit detection on the page where the match was found, unless
    skip_unit=True (for per-share values like EPS / DPS, which are already
    in SAR-per-share and must not be multiplied by the page's currency
    unit hint).

    keyword_priority_over_page=False (default): page-major iteration —
    each page tries every keyword in order. The first page with any
    keyword hit returns that page's match.

    keyword_priority_over_page=True: keyword-major iteration — each
    keyword tries every page in order. A more-specific keyword on a
    later page wins over a less-specific keyword on an earlier page.
    Required for EPS, where Al Rajhi shows two values: a pre-Sukuk
    figure on the income-statement page (matched by the plural
    "earnings" keyword) and the canonical post-Sukuk figure deeper
    in the notes (matched by the singular "earning" keyword); the
    notes value is the one yfinance/Tadawul report.

    kwargs (anchor_start, last, exclude, min_abs, max_abs,
    require_decimal) are forwarded to _value_near_keyword.
    """
    if keyword_priority_over_page:
        for kw in keywords:
            for _, text in pages_subset:
                n = _value_near_keyword(text, [kw], **kwargs)
                if n is not None:
                    return n if skip_unit else n * _detect_unit(text)
        return None
    for _, text in pages_subset:
        n = _value_near_keyword(text, keywords, **kwargs)
        if n is not None:
            return n if skip_unit else n * _detect_unit(text)
    return None


# ── Page extraction (combined standard + rowwise pass) ──────────

# Words within this many points of each other on the y-axis are treated as
# being on the same visual row. Tuned for typical 11pt/12pt financial tables.
ROWWISE_Y_TOLERANCE = 3
# OCR's pixel scale at OCR_DPI=200 is ~3x pdfplumber's points; words on the
# same baseline land within ~10px even for 12-point fonts.
ROWWISE_Y_TOLERANCE_OCR = 10


def _cluster_rows(words, y_key, x_key, y_tol):
    """Cluster word dicts into visual rows by y-coord, then order each row by x."""
    if not words:
        return []
    words_sorted = sorted(words, key=lambda w: (w[y_key], w[x_key]))
    rows = [[words_sorted[0]]]
    for w in words_sorted[1:]:
        if abs(w[y_key] - rows[-1][0][y_key]) <= y_tol:
            rows[-1].append(w)
        else:
            rows.append([w])
    return [sorted(row, key=lambda w: w[x_key]) for row in rows]


def _ocr_pages_dual(pdf_path, page_numbers):
    """OCR each page once and derive both standard and rowwise text.

    pytesseract.image_to_data returns word-level data with bounding boxes
    AND tesseract's own line grouping. From a single OCR call we build:
      - standard text: words joined within tesseract's (block, par, line)
        groups — equivalent to the prior image_to_string output
      - rowwise text:  words clustered by 'top' y-coordinate (ignoring
        tesseract's blocks) so column-layout statements (SNB IS, Jarir/
        Habib BS) reconstruct visual rows with label and value adjacent

    Calling image_to_data once instead of image_to_string + image_to_data
    halves OCR time on image-heavy reports — the dominant cost in the
    pipeline.

    Returns {page_num: (standard_text, rowwise_text)}.
    """
    out = {}
    for pn in page_numbers:
        images = convert_from_path(pdf_path, dpi=OCR_DPI,
                                   first_page=pn, last_page=pn)
        if not images:
            out[pn] = ("", "")
            continue
        data = pytesseract.image_to_data(
            images[0], lang=OCR_LANGS,
            output_type=pytesseract.Output.DICT,
        )
        std_groups = {}
        for i, txt in enumerate(data["text"]):
            txt = txt.strip()
            if not txt:
                continue
            key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
            std_groups.setdefault(key, []).append((data["left"][i], txt))
        std_lines = []
        for key in sorted(std_groups):
            words = sorted(std_groups[key])
            std_lines.append(" ".join(w[1] for w in words))
        std_text = "\n".join(std_lines)

        row_words = []
        for i, txt in enumerate(data["text"]):
            txt = txt.strip()
            if not txt:
                continue
            row_words.append({"text": txt,
                              "top": data["top"][i],
                              "left": data["left"][i]})
        rows = _cluster_rows(row_words, y_key="top", x_key="left",
                             y_tol=ROWWISE_Y_TOLERANCE_OCR)
        rowwise_text = "\n".join(
            " ".join(w["text"] for w in row) for row in rows
        )
        out[pn] = (std_text, rowwise_text)
    return out


def _extract_text_dual(pdf_path):
    """Extract both standard and rowwise page text in one combined pass.

    Single pdfplumber.open() per PDF (was 2), single OCR per image page
    (was 2). For text pages, derives standard via extract_text() and
    rowwise via extract_words() + y-clustering. For image pages (where
    extract_words returns nothing AND extract_text returns less than
    TEXT_THRESHOLD_CHARS), defers to _ocr_pages_dual which OCRs once
    per page.

    Standard text serves the keyword extractors that work on most PDFs.
    Rowwise text serves the column-layout fix where pdfplumber's default
    reading separates labels from values into different blocks (Jarir BS,
    Habib BS, SNB IS).

    Returns (standard_pages, rowwise_pages) — both [(page_num, text), ...]
    with 1-based page numbers.
    """
    standard_pages = []
    rowwise_pages = []
    image_page_nums = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            try:
                words = page.extract_words(keep_blank_chars=False)
            except Exception:
                words = []
            std_text = page.extract_text() or ""
            if not words and len(std_text.strip()) < TEXT_THRESHOLD_CHARS:
                image_page_nums.append(i)
                standard_pages.append((i, ""))
                rowwise_pages.append((i, ""))
                continue
            standard_pages.append((i, std_text))
            if words:
                rows = _cluster_rows(words, y_key="top", x_key="x0",
                                     y_tol=ROWWISE_Y_TOLERANCE)
                rowwise_pages.append((i, "\n".join(
                    " ".join(w["text"] for w in row) for row in rows
                )))
            else:
                # Text page with no extractable words (rare) — reuse standard.
                rowwise_pages.append((i, std_text))

    if image_page_nums:
        ocr_dual = _ocr_pages_dual(pdf_path, image_page_nums)
        standard_pages = [(pn, ocr_dual[pn][0]) if pn in ocr_dual else (pn, t)
                          for pn, t in standard_pages]
        rowwise_pages = [(pn, ocr_dual[pn][1]) if pn in ocr_dual else (pn, t)
                         for pn, t in rowwise_pages]

    return standard_pages, rowwise_pages


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
    # DISQUALIFIERS apply to all stages: a "before zakat" / "before tax"
    # row is never the canonical net-income figure, regardless of which
    # keyword family matched it. Without this, the permissive Bupa
    # attribution keyword ("Income attributed to the shareholders") was
    # catching pre-zakat rows in supplementary tables.
    stages = [
        (NET_INCOME_ATTRIBUTION_KEYWORDS,
         dict(last=True, anchor_start=True, exclude=NET_INCOME_TOTAL_DISQUALIFIERS)),
        (NET_INCOME_ATTRIBUTION_KEYWORDS,
         dict(last=True, anchor_start=False, exclude=NET_INCOME_TOTAL_DISQUALIFIERS)),
        (NET_INCOME_TOTAL_KEYWORDS,
         dict(last=False, anchor_start=True, exclude=NET_INCOME_TOTAL_DISQUALIFIERS)),
    ]
    for subset in (income_pages, pages):
        for keywords, kwargs in stages:
            n = _extract_in_pages(subset, keywords, **kwargs)
            if n is not None:
                return n
    return None
def extract_eps(pages):
    """Find basic earnings per share (parent-attributable, total).

    Per subset (income-statement pages first, then whole doc), run two
    stages and return the first hit:
      1. EPS keywords with start-of-line anchor + LAST match. Last-match
         picks the total-EPS row over the continuing-ops one (STC, SABIC).
      2. Same keywords without the anchor, for pdfplumber-flattened
         multi-column layouts.

    Per-share tweaks:
      - skip_unit=True — EPS is already in SAR per share; the page's
        "in millions of SR" hint must NOT scale it.
      - min_abs=0.01 — EPS values are typically 0.10–20 SAR/share, well
        below the default currency threshold.
      - max_abs=10_000 — filters multi-million income totals when an EPS
        keyword (e.g. SABIC's "• Net income (loss)") also matches the
        consolidated income line.
      - EPS_DISQUALIFIERS skips "continuing operations" / "before zakat"
        rows so total-EPS wins over continuing-ops EPS.
    """
    income_pages = _pages_matching_patterns(pages, INCOME_STATEMENT_PATTERNS)
    eps_kwargs = dict(skip_unit=True, last=True, exclude=EPS_DISQUALIFIERS,
                      min_abs=0.01, max_abs=10_000, require_decimal=True,
                      keyword_priority_over_page=True)
    for subset in (income_pages, pages):
        for anchor_start in (True, False):
            n = _extract_in_pages(subset, EPS_KEYWORDS,
                                  anchor_start=anchor_start, **eps_kwargs)
            if n is not None:
                return n
    return None
def extract_total_assets(pages):
    """Find total assets from the balance sheet bottom-line.

    Strategy:
      1. Search inside the balance sheet (authoritative).
      2. Fall back to scanning the whole document.

    Last-match semantics: "Total assets" appears multiple times in any
    annual report — segment-level subtotals in the notes, comparative
    columns, etc. The consolidated bottom-line on the balance sheet is
    typically the LARGEST and the LAST occurrence within the BS page,
    so last=True picks it over earlier sub-totals on the same page.
    """
    keywords = KEYWORDS["total_assets"]
    bs_pages = _pages_matching_patterns(pages, BALANCE_SHEET_PATTERNS)
    # Restrict to BS pages whenever they're detected — falling back to the
    # whole document when BS pages exist but contain only label-column
    # text (Jarir, Habib) was landing on segment-subtable rows from the
    # notes section. Returning None here lets extract_all's rowwise
    # fallback re-extract the BS page with word-coordinate row
    # reconstruction. We only scan the whole doc when no BS-pattern page
    # was detected at all (older or unusual filings).
    if bs_pages:
        return _extract_in_pages(bs_pages, keywords, last=True, next_line_fallback=True)
    return _extract_in_pages(pages, keywords, last=True, next_line_fallback=True)
def extract_shareholders_equity(pages):  return None
def extract_total_borrowings(pages):     return None
def extract_cash_and_equivalents(pages): return None
def extract_free_cash_flow(pages):       return None
def extract_shares_outstanding(pages):   return None
def extract_dividends_per_share(pages):  return None


# ── Orchestrator ────────────────────────────────────────────────

# Currency-like values where the rowwise re-extraction often surfaces a
# materially larger consolidated figure than the standard pass — column-
# layout PDFs make the standard pass land on a wrong-row fragment.
# Per-share values (eps, dps) and counts (shares_outstanding) are excluded:
# magnitude isn't a quality signal there.
_PREFER_LARGER_FROM_ROWWISE = {
    "revenue", "net_income", "total_assets", "shareholders_equity",
    "total_borrowings", "cash_and_equivalents", "free_cash_flow",
}


def extract_all(pdf_path):
    """Extract all 10 financial values from one PDF.

    Two-pass extraction:
      1. Standard text — pdfplumber's default extract_text() with OCR
         fallback for image-only pages.
      2. Rowwise — words clustered by y-coordinate to reconstruct visual
         rows. Fixes column-layout PDFs (Jarir, Habib BS, SNB IS) where
         the default reading separates labels from values.

    Per-value selection rule:
      - If standard returned None, use rowwise (catches Jarir/Habib BS).
      - If rowwise returned None, use standard.
      - Otherwise, for currency-like values where rowwise > 2 × standard
        and the rowwise result is at least 1M, use rowwise — the size
        gap is a reliable signal that the standard pass landed on a
        column-layout fragment (catches SNB revenue/net_income).
      - In all other cases, prefer the standard pass.

    Returns dict with keys matching FinancialData column names. A value of
    None means extraction returned nothing — either the field is not
    implemented yet, or both passes couldn't find a match.
    """
    extractors = {
        "revenue":              extract_revenue,
        "net_income":           extract_net_income,
        "eps":                  extract_eps,
        "total_assets":         extract_total_assets,
        "shareholders_equity":  extract_shareholders_equity,
        "total_borrowings":     extract_total_borrowings,
        "cash_and_equivalents": extract_cash_and_equivalents,
        "free_cash_flow":       extract_free_cash_flow,
        "shares_outstanding":   extract_shares_outstanding,
        "dividends_per_share":  extract_dividends_per_share,
    }
    standard_pages, rowwise_pages = _extract_text_dual(pdf_path)
    standard = {name: fn(standard_pages) for name, fn in extractors.items()}
    rowwise = {name: fn(rowwise_pages) for name, fn in extractors.items()}

    result = {}
    for name in extractors:
        s, r = standard[name], rowwise[name]
        if s is None:
            result[name] = r
        elif r is None:
            result[name] = s
        elif (name in _PREFER_LARGER_FROM_ROWWISE
              and abs(r) > 2 * abs(s) and abs(r) >= 1_000_000):
            result[name] = r
        else:
            result[name] = s
    return result
