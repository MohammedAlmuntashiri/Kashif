"""
report_service.py — Bilingual PDF "Extraction Report" for an upload.

Called from POST /api/pdf/report/<ticker>?lang=en|ar with the dry-run
extraction result the frontend already has. Returns a single-stream PDF
laid out in the requested language (English LTR or Arabic RTL).

Layout (mirrored for Arabic):
    1. Page frame + branded header band + footer rule (canvas-drawn)
    2. Stock identity card
    3. Source file metadata
    4. Summary chips
    5. Field-by-field comparison table (Field | DB | Extracted | Diff% | Match)
    6. Mini bar chart of diff % per field (or "all matched" message)
    7. Historical context table (10 fields × last 4 DB periods)
    8. Verified valuation block (DCF / PE / PB / Fair, conflicts default to DB)
    9. Inputs used (collapses to one line when 100% verified)
   10. Methodology & notes (closing block)
"""
import os
from datetime import datetime, timezone
from io import BytesIO

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    KeepTogether,
)

from app.extensions import db  # noqa: F401
from app.models.stock import Stock
from app.models.financial_data import FinancialData
from app.services.dcf_service import advanced_dcf, simple_dcf
from app.services.wacc_service import calculate_wacc
from app.services.pe_service import pe_fair_value, get_sector_average_pe
from app.services.pb_service import pb_fair_value, get_sector_average_pb


# ── Font registration ────────────────────────────────────────────────
# Noto Sans Arabic is installed by `apt-get install fonts-noto-core` in the
# Dockerfile. The list of candidate paths exists so the same code also works
# on machines where a different Arabic font is installed (Tajawal, Amiri, etc.).
# Registration runs once at import time. Falls back silently if no Arabic
# font is present — English reports still render with Helvetica; Arabic ones
# would show squares.
_FONT_CANDIDATES = [
    # (registration_name, regular_ttf_path, bold_ttf_path)
    ("NotoArabic",
     "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
     "/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf"),
    ("Tajawal",
     "/usr/share/fonts/truetype/tajawal/Tajawal-Regular.ttf",
     "/usr/share/fonts/truetype/tajawal/Tajawal-Bold.ttf"),
    ("Amiri",
     "/usr/share/fonts/truetype/amiri/amiri-regular.ttf",
     "/usr/share/fonts/truetype/amiri/amiri-bold.ttf"),
]
_ARABIC_FONT = "Helvetica"
_ARABIC_FONT_BOLD = "Helvetica-Bold"
for name, regular_path, bold_path in _FONT_CANDIDATES:
    if os.path.exists(regular_path):
        try:
            pdfmetrics.registerFont(TTFont(name, regular_path))
            _ARABIC_FONT = name
            if os.path.exists(bold_path):
                pdfmetrics.registerFont(TTFont(f"{name}-Bold", bold_path))
                _ARABIC_FONT_BOLD = f"{name}-Bold"
            else:
                _ARABIC_FONT_BOLD = name
            # Register the family so <b> inside a Paragraph styled with this
            # font picks up the bold variant. Without this, <b> renders nothing
            # (or falls back silently) when the base font isn't Helvetica/Times.
            registerFontFamily(name, normal=name, bold=_ARABIC_FONT_BOLD,
                               italic=name, boldItalic=_ARABIC_FONT_BOLD)
            break  # first available font wins
        except Exception:
            continue


# ── Label dictionary ─────────────────────────────────────────────────
# Every UI string in the report. Anything new must land here in both
# languages — never hard-code English strings into the layout code.
LABELS = {
    "extraction_report":         {"en": "Extraction Report",                                         "ar": "تقرير الاستخراج"},
    "sector":                    {"en": "Sector",                                                    "ar": "القطاع"},
    "market_price":              {"en": "Market price",                                              "ar": "سعر السوق"},
    "source_file":               {"en": "Source file",                                               "ar": "الملف المصدر"},
    "detected_period":           {"en": "Detected period",                                           "ar": "الفترة المكتشفة"},
    "generated":                 {"en": "Generated",                                                 "ar": "تاريخ التوليد"},
    "no_db_row":                 {"en": "no DB row for this period",                                 "ar": "لا يوجد سجل في قاعدة البيانات لهذه الفترة"},
    "summary":                   {"en": "Summary",                                                   "ar": "الملخص"},
    "match_word":                {"en": "match",                                                     "ar": "مطابقة"},
    "mismatch_word":             {"en": "mismatch",                                                  "ar": "اختلاف"},
    "missing_word":              {"en": "missing",                                                   "ar": "مفقود"},
    "accuracy":                  {"en": "Accuracy",                                                  "ar": "الدقة"},
    "field_by_field":            {"en": "Field-by-field comparison",                                 "ar": "مقارنة حقل بحقل"},
    "col_field":                 {"en": "Field",                                                     "ar": "الحقل"},
    "col_db":                    {"en": "DB value",                                                  "ar": "قيمة القاعدة"},
    "col_extracted":             {"en": "Extracted",                                                 "ar": "المستخرج"},
    "col_diff":                  {"en": "Diff",                                                      "ar": "الفرق"},
    "col_match":                 {"en": "Match",                                                     "ar": "التطابق"},
    "field_accuracy":            {"en": "Field accuracy",                                            "ar": "دقة الحقول"},
    "all_matched_msg":           {"en": "All fields matched the database within 1%. No diffs to chart.",
                                  "ar": "جميع الحقول مطابقة لقاعدة البيانات ضمن واحد بالمئة. لا توجد فروقات لعرضها."},
    "field_accuracy_chart":      {"en": "Field accuracy (diff % from DB, capped at 25% for display)",
                                  "ar": "دقة الحقول (نسبة الفرق عن قاعدة البيانات، بحد أقصى 25% للعرض)"},
    "historical_context":        {"en": "Historical context (DB values, last 4 periods)",
                                  "ar": "السياق التاريخي (قيم قاعدة البيانات، آخر 4 فترات)"},
    "verified_valuation":        {"en": "Verified valuation (recomputed for {period})",
                                  "ar": "التقييم المُتحقَّق منه (مُعاد حسابه للفترة {period})"},
    "dcf":                       {"en": "DCF",          "ar": "التدفقات المخصومة"},
    "pe":                        {"en": "P/E",          "ar": "مكرر الربحية"},
    "pb":                        {"en": "P/B",          "ar": "مكرر القيمة الدفترية"},
    "fair_value":                {"en": "Fair value",   "ar": "القيمة العادلة"},
    "status_vs_mp":              {"en": "Status vs market price",
                                  "ar": "الحالة مقابل سعر السوق"},
    "status_undervalued":        {"en": "undervalued",   "ar": "مقومة بأقل من قيمتها"},
    "status_overvalued":         {"en": "overvalued",    "ar": "مقومة بأعلى من قيمتها"},
    "status_fair":               {"en": "fair",          "ar": "عادلة"},
    "inputs_used":               {"en": "Inputs used",   "ar": "المدخلات المستخدمة"},
    "inputs_all_verified":       {"en": "All 10 fields verified from the uploaded PDF (extracted values matched the database within 1%).",
                                  "ar": "تم التحقق من جميع الحقول العشرة من الملف المرفوع، وطابقت القيم المستخرجة قاعدة البيانات ضمن واحد بالمئة."},
    "src_from_pdf_verified":     {"en": "from PDF (verified)",          "ar": "من PDF (مُتحقَّق منه)"},
    "src_from_pdf_no_db":        {"en": "from PDF (no DB row)",         "ar": "من PDF (لا يوجد سجل في القاعدة)"},
    "src_from_db_conflict":      {"en": "from DB (PDF said {pdf_val})", "ar": "من قاعدة البيانات (PDF قال {pdf_val})"},
    "src_from_db_missing":       {"en": "from DB (PDF missing)",        "ar": "من قاعدة البيانات (PDF مفقود)"},
    "src_unavailable":           {"en": "unavailable",                  "ar": "غير متاح"},
    "methodology_notes":         {"en": "Methodology & notes",          "ar": "المنهجية والملاحظات"},
    "methodology_body":          {"en": "DCF uses a 4-year FCF history (oldest 3 years pulled from the DB). P/E and P/B use the current sector averages (excluding this stock from its own peer set), so this recomputed fair value may differ slightly from the value stored in the main app — the stored value was calculated when its sector averages were last refreshed. When the extractor and the DB disagreed on a field, the DB value was used since Tadawul filings (loaded into the DB) are treated as the source of truth. This is a preview-only extraction report — no values were written to the database. Numbers are rounded for display; the underlying calculations use full precision.",
                                  "ar": "تستخدم طريقة التدفقات النقدية المخصومة تاريخ التدفقات النقدية الحرة لأربع سنوات (أقدم 3 سنوات من قاعدة البيانات). تستخدم مكررات الربحية والقيمة الدفترية متوسطات القطاع الحالية (مع استثناء هذا السهم من مجموعة نظرائه)، لذا قد تختلف القيمة العادلة المعاد حسابها قليلاً عن القيمة المخزنة في التطبيق الرئيسي — تم حساب القيمة المخزنة عند آخر تحديث لمتوسطات قطاعها. عند اختلاف المستخرج وقاعدة البيانات في حقل ما، تم استخدام قيمة قاعدة البيانات لأن إفصاحات تداول (المحملة في قاعدة البيانات) تُعتبر مصدر الحقيقة. هذا تقرير استخراج للمعاينة فقط — لم تتم كتابة أي قيم في قاعدة البيانات. الأرقام مقربة للعرض؛ تستخدم الحسابات الأساسية الدقة الكاملة."},

    "field_revenue":              {"en": "Revenue",              "ar": "الإيرادات"},
    "field_net_income":           {"en": "Net Income",           "ar": "صافي الدخل"},
    "field_eps":                  {"en": "EPS",                  "ar": "ربحية السهم"},
    "field_total_assets":         {"en": "Total Assets",         "ar": "إجمالي الأصول"},
    "field_total_borrowings":     {"en": "Total Borrowings",     "ar": "إجمالي القروض"},
    "field_shareholders_equity":  {"en": "Shareholders Equity",  "ar": "حقوق المساهمين"},
    "field_cash_and_equivalents": {"en": "Cash & Equivalents",   "ar": "النقد وما يعادله"},
    "field_free_cash_flow":       {"en": "Free Cash Flow",       "ar": "التدفقات النقدية الحرة"},
    "field_dividends_per_share":  {"en": "Dividends Per Share",  "ar": "توزيعات السهم"},
    "field_shares_outstanding":   {"en": "Shares Outstanding",   "ar": "الأسهم القائمة"},
}

# Stock-data fields the report iterates over.
FIELD_KEYS = [
    "revenue", "net_income", "eps", "total_assets", "total_borrowings",
    "shareholders_equity", "cash_and_equivalents", "free_cash_flow",
    "dividends_per_share", "shares_outstanding",
]
PER_SHARE_FIELDS = {"eps", "dividends_per_share"}


def _shape_ar(text):
    """Reshape isolated Arabic letters into connected forms + apply BiDi.
    Safe to call on mixed Arabic/Latin strings — non-Arabic chars pass through."""
    if not text:
        return text
    return get_display(arabic_reshaper.reshape(text))


def _shape_ar_paragraph(text, wrap_chars=80):
    """Shape long Arabic body text for use inside a Paragraph.

    ReportLab wraps text at the VISUAL level, so a single pre-bidi'd line
    longer than the column gets wrapped at arbitrary positions, scrambling
    reading order. Workaround: chunk the source into ~wrap_chars segments
    on word boundaries, shape each segment individually, then join with
    explicit <br/> so ReportLab doesn't have to reflow.
    """
    if not text:
        return text
    words = text.split()
    lines, current = [], ""
    for w in words:
        if len(current) + 1 + len(w) > wrap_chars and current:
            lines.append(current)
            current = w
        else:
            current = f"{current} {w}".strip()
    if current:
        lines.append(current)
    shaped_lines = [_shape_ar(line) for line in lines]
    return "<br/>".join(shaped_lines)


def L(key, lang, **fmt):
    """Look up a label, optionally interpolate {placeholders}, and reshape if Arabic."""
    entry = LABELS.get(key, {})
    text = entry.get(lang) or entry.get("en") or key
    if fmt:
        text = text.format(**fmt)
    if lang == "ar":
        text = _shape_ar(text)
    return text


def _lat(text, lang, bold=False):
    """Wrap Latin text in an explicit Helvetica font tag so it renders even
    when the surrounding paragraph uses an Arabic-only font (NotoSansArabic
    in Debian's fonts-noto-core has only Arabic glyphs + digits — Latin
    letters render as missing glyphs without this wrap)."""
    if text is None:
        return ""
    if lang != "ar":
        # In English mode the body font (Helvetica) already covers Latin —
        # but we still respect the bold flag.
        return f"<b>{text}</b>" if bold else f"{text}"
    font = "Helvetica-Bold" if bold else "Helvetica"
    return f"<font name='{font}'>{text}</font>"


# ── Number formatting ────────────────────────────────────────────────

def _fmt_money(v):
    if v is None:
        return "—"
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "—"
    if v == 0:
        return "0"
    sign = "-" if v < 0 else ""
    a = abs(v)
    if a >= 1e12: return f"{sign}{a/1e12:,.2f}T"
    if a >= 1e9:  return f"{sign}{a/1e9:,.2f}B"
    if a >= 1e6:  return f"{sign}{a/1e6:,.2f}M"
    if a >= 1e3:  return f"{sign}{a/1e3:,.2f}K"
    return f"{sign}{a:,.2f}"


def _fmt_per_share(v):
    if v is None:
        return "—"
    try:
        return f"{float(v):,.2f}"
    except (TypeError, ValueError):
        return "—"


def _fmt_field(field, v):
    return _fmt_per_share(v) if field in PER_SHARE_FIELDS else _fmt_money(v)


def _classify_diff(extracted, db_val):
    if extracted is None or db_val is None:
        return ("missing", None)
    try:
        a, b = float(extracted), float(db_val)
    except (TypeError, ValueError):
        return ("missing", None)
    if abs(b) < 1e-9:
        return (("match" if a == 0 else "bad"), None)
    pct = abs(a - b) / abs(b) * 100
    if pct <= 1:  return ("match", pct)
    if pct <= 10: return ("warn",  pct)
    return ("bad", pct)


def _diff_color(kind):
    return {
        "match":   colors.HexColor("#059669"),
        "warn":    colors.HexColor("#d97706"),
        "bad":     colors.HexColor("#dc2626"),
        "missing": colors.HexColor("#94a3b8"),
    }[kind]


# ── Valuation helpers ────────────────────────────────────────────────

def _merge_verified(db_comparison, lang):
    """Merge extracted vs DB into one verified snapshot. Source labels are
    already localized so the inputs-used table can print them as-is."""
    values, sources = {}, {}
    for field in FIELD_KEYS:
        info = (db_comparison or {}).get(field) or {}
        ext = info.get("extracted")
        dbv = info.get("db")
        if dbv is None and ext is not None:
            values[field] = ext
            sources[field] = L("src_from_pdf_no_db", lang)
        elif info.get("match"):
            values[field] = ext
            sources[field] = L("src_from_pdf_verified", lang)
        elif ext is not None and dbv is not None:
            values[field] = dbv
            sources[field] = L("src_from_db_conflict", lang, pdf_val=_fmt_field(field, ext))
        elif dbv is not None:
            values[field] = dbv
            sources[field] = L("src_from_db_missing", lang)
        else:
            values[field] = None
            sources[field] = L("src_unavailable", lang)
    return values, sources


def _verified_valuation(stock, period, verified):
    history_rows = (
        FinancialData.query
        .filter_by(stock_id=stock.id)
        .filter(FinancialData.period < period)
        .order_by(FinancialData.period.desc())
        .limit(3)
        .all()
    )
    fcf_history = list(reversed([r.free_cash_flow for r in history_rows])) + [verified.get("free_cash_flow")]
    wacc = calculate_wacc(verified.get("shareholders_equity"), verified.get("total_borrowings"))
    dcf = advanced_dcf(fcf_history, verified.get("shares_outstanding"), wacc=wacc)
    if dcf is None:
        dcf = simple_dcf(verified.get("free_cash_flow"), verified.get("shares_outstanding"), wacc=wacc)
    sector_pe = get_sector_average_pe(stock.sector_id, exclude_stock_id=stock.id)
    pe = pe_fair_value(verified.get("eps"), sector_pe)
    sector_pb = get_sector_average_pb(stock.sector_id, exclude_stock_id=stock.id)
    pb = pb_fair_value(verified.get("shareholders_equity"), verified.get("shares_outstanding"), sector_pb)
    sector = stock.sector
    parts = [(dcf, sector.dcf_weight), (pe, sector.pe_weight), (pb, sector.pb_weight)]
    available = [(v, w) for v, w in parts if v is not None and w > 0]
    fair = None
    if available:
        total_w = sum(w for _, w in available)
        if total_w > 0:
            fair = sum(v * w for v, w in available) / total_w
    return {"dcf": dcf, "pe": pe, "pb": pb, "fair": fair, "market_price": stock.market_price}


def _status_parts(market, fair, lang):
    if market is None or fair is None or market <= 0 or fair <= 0:
        return ("—", None, "#64748b")
    pct = (fair - market) / market * 100
    if fair > market * 1.10:
        return (L("status_undervalued", lang), pct, "#059669")
    if fair < market * 0.90:
        return (L("status_overvalued", lang), pct, "#dc2626")
    return (L("status_fair", lang), pct, "#d97706")


# ── PDF builder ──────────────────────────────────────────────────────

def build_report(ticker, result, source_filename=None, lang="en"):
    """Generate the PDF bytes for one extraction result.

    Args:
        ticker: Tadawul ticker string (e.g. "2222").
        result: dict from /api/pdf/upload dry-run.
        source_filename: optional original PDF filename to cite.
        lang: "en" or "ar". Arabic flips alignment + uses Tajawal font.
    """
    if lang not in ("en", "ar"):
        lang = "en"

    stock = Stock.query.filter_by(symbol=ticker).first()
    if stock is None:
        raise ValueError(f"Stock {ticker} not found")

    period = result.get("period") or "—"
    db_comparison = result.get("db_comparison") or {}
    fd_db = FinancialData.query.filter_by(stock_id=stock.id, period=period).first()

    # Direction-aware constants. In Arabic the section accent bar lives on
    # the right, text aligns right, table column order flips.
    is_rtl = (lang == "ar")
    text_align = TA_RIGHT if is_rtl else TA_LEFT
    base_font  = _ARABIC_FONT if is_rtl else "Helvetica"
    bold_font  = _ARABIC_FONT_BOLD if is_rtl else "Helvetica-Bold"

    # ── styles ──
    body = ParagraphStyle("body", fontName=base_font, fontSize=9, leading=13,
                          textColor=colors.HexColor("#334155"),
                          alignment=text_align)
    small_muted = ParagraphStyle("muted", parent=body, fontSize=8,
                                  textColor=colors.HexColor("#64748b"))
    h_section_p = ParagraphStyle("section_p", fontName=bold_font, fontSize=12, leading=16,
                                  textColor=colors.HexColor("#0f172a"),
                                  alignment=text_align,
                                  leftIndent=0 if is_rtl else 6,
                                  rightIndent=6 if is_rtl else 0)

    BRAND       = colors.HexColor("#059669")
    BRAND_RULE  = colors.HexColor("#a7f3d0")
    CARD_BG     = colors.HexColor("#f8fafc")
    CARD_BORDER = colors.HexColor("#e2e8f0")

    def section(text):
        """Section header with a 2pt accent bar — on the left for LTR,
        on the right for RTL — so it always points away from the page edge."""
        accent = Table([[Paragraph(f"<b>{text}</b>", h_section_p)]],
                       colWidths=[180*mm], rowHeights=[16])
        line_cmd = ("LINEAFTER", (0, 0), (0, 0), 2, BRAND) if is_rtl \
                   else ("LINEBEFORE", (0, 0), (0, 0), 2, BRAND)
        pad_left, pad_right = (0, 6) if is_rtl else (6, 0)
        accent.setStyle(TableStyle([
            line_cmd,
            ("LEFTPADDING",  (0, 0), (-1, -1), pad_left),
            ("RIGHTPADDING", (0, 0), (-1, -1), pad_right),
            ("TOPPADDING",   (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ]))
        return accent

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                             leftMargin=15*mm, rightMargin=15*mm,
                             topMargin=28*mm, bottomMargin=18*mm,
                             title=f"Kashif Extraction Report — {ticker}")
    story = []

    # ── 2. Stock identity card ──
    mp = f"SAR {stock.market_price:,.2f}" if stock.market_price else "—"
    name_para = Paragraph(
        f"<font size=11 name='Helvetica-Bold'>{ticker}</font> &nbsp; "
        f"<font size=10 name='Helvetica'>{stock.name_en}</font>",
        body,
    )
    detail_para = Paragraph(
        f"{L('sector', lang)}: {_lat(stock.sector.name_en, lang, bold=True)} "
        f"&nbsp;&nbsp;&middot;&nbsp;&nbsp; "
        f"{L('market_price', lang)}: {_lat(mp, lang, bold=True)}",
        small_muted,
    )
    identity = Table([[name_para], [detail_para]], colWidths=[180*mm])
    identity.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), CARD_BG),
        ("BOX",          (0, 0), (-1, -1), 0.5, CARD_BORDER),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
    ]))
    story.append(identity)
    story.append(Spacer(1, 6))

    # ── 3. Source metadata ──
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    src = source_filename or "(uploaded PDF)"
    new_tag = f" &nbsp;<font color='#059669'><b>({L('no_db_row', lang)})</b></font>" if result.get("is_new_row") else ""
    story.append(Paragraph(
        f"{L('source_file', lang)}: <font name='Helvetica' color='#475569'>{src}</font>",
        small_muted,
    ))
    story.append(Paragraph(
        f"{L('detected_period', lang)}: {_lat(period, lang, bold=True)}{new_tag}",
        small_muted,
    ))
    story.append(Paragraph(
        f"{L('generated', lang)}: {_lat(now, lang)}",
        small_muted,
    ))

    # ── 4. Summary ──
    match = mismatch = missing = 0
    for field in FIELD_KEYS:
        info = db_comparison.get(field) or {}
        kind, _ = _classify_diff(info.get("extracted"), info.get("db"))
        if kind == "missing": missing += 1
        elif kind == "match": match += 1
        else: mismatch += 1
    total = match + mismatch + missing
    accuracy = (match / total * 100) if total else 0
    story.append(section(L("summary", lang)))
    story.append(Spacer(1, 2))
    story.append(Paragraph(
        f"<font color='#059669'><b>{match}</b> {L('match_word', lang)}</font> &nbsp;&middot;&nbsp; "
        f"<font color='#dc2626'><b>{mismatch}</b> {L('mismatch_word', lang)}</font> &nbsp;&middot;&nbsp; "
        f"<font color='#64748b'><b>{missing}</b> {L('missing_word', lang)}</font> &nbsp;&nbsp; "
        f"{L('accuracy', lang)}: <b>{accuracy:.0f}%</b>",
        body,
    ))

    # ── 5. Field-by-field comparison ──
    story.append(section(L("field_by_field", lang)))
    story.append(Spacer(1, 2))
    # Column order: in RTL, the textual Field column should appear on the
    # right (visually first) → header row read left-to-right inside the table
    # but the table itself is right-aligned. We keep the logical column order
    # and rely on text-right alignment within each cell to feel native.
    cmp_rows = [[
        L("col_field", lang),
        L("col_db", lang),
        L("col_extracted", lang),
        L("col_diff", lang),
        L("col_match", lang),
    ]]
    cmp_style = [
        ("BACKGROUND",     (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ("TEXTCOLOR",      (0, 0), (-1, 0), colors.HexColor("#475569")),
        ("FONTNAME",       (0, 0), (-1, 0), bold_font),
        # Field-label column uses the Arabic font in AR mode; numeric columns
        # always use Helvetica so Latin digits and suffixes (T/B/M) render.
        ("FONTNAME",       (0, 1), (0, -1), base_font),
        ("FONTNAME",       (1, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",       (0, 0), (-1, -1), 8),
        ("ALIGN",          (0, 0), (0, -1),  "RIGHT" if is_rtl else "LEFT"),
        ("ALIGN",          (1, 0), (3, -1),  "RIGHT"),
        ("ALIGN",          (4, 0), (4, -1),  "CENTER"),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 4),
        ("TOPPADDING",     (0, 0), (-1, -1), 4),
        ("LINEBELOW",      (0, 0), (-1, 0), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ]
    for i, field in enumerate(FIELD_KEYS, start=1):
        info = db_comparison.get(field) or {}
        kind, pct = _classify_diff(info.get("extracted"), info.get("db"))
        cmp_rows.append([
            L(f"field_{field}", lang),
            _fmt_field(field, info.get("db")),
            _fmt_field(field, info.get("extracted")),
            "—" if pct is None else f"{pct:.2f}%",
            "✓" if info.get("match") else ("✗" if info.get("extracted") is not None or info.get("db") is not None else "—"),
        ])
        cmp_style.append(("TEXTCOLOR", (3, i), (3, i), _diff_color(kind)))
        match_color = colors.HexColor("#059669") if info.get("match") else colors.HexColor("#dc2626")
        cmp_style.append(("TEXTCOLOR", (4, i), (4, i), match_color))

    cmp_table = Table(cmp_rows, colWidths=[55*mm, 35*mm, 35*mm, 25*mm, 15*mm],
                       hAlign="RIGHT" if is_rtl else "LEFT")
    cmp_table.setStyle(TableStyle(cmp_style))
    story.append(cmp_table)

    # ── 6. Field accuracy chart ──
    has_any_diff = any(
        _classify_diff(info.get("extracted"), info.get("db"))[1] not in (None, 0)
        for info in (db_comparison.get(field) or {} for field in FIELD_KEYS)
    )
    if has_any_diff:
        story.append(section(L("field_accuracy_chart", lang)))
        story.append(Spacer(1, 2))
        BAR_MAX_W = 90 * mm
        bar_rows = []
        for field in FIELD_KEYS:
            info = db_comparison.get(field) or {}
            kind, pct = _classify_diff(info.get("extracted"), info.get("db"))
            display_pct = 0 if pct is None else min(pct, 25)
            bar_w = (display_pct / 25) * BAR_MAX_W
            bar = Table([[""]], colWidths=[max(bar_w, 0.1)], rowHeights=[6])
            bar.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), _diff_color(kind)),
                ("LEFTPADDING",   (0, 0), (-1, -1), 0),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
                ("TOPPADDING",    (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]))
            bar_rows.append([L(f"field_{field}", lang), bar,
                             "—" if pct is None else f"{pct:.2f}%"])
        bar_table = Table(bar_rows, colWidths=[55*mm, BAR_MAX_W + 2*mm, 18*mm],
                           hAlign="RIGHT" if is_rtl else "LEFT")
        bar_table.setStyle(TableStyle([
            ("FONTNAME",      (0, 0), (0, -1),  base_font),
            ("FONTNAME",      (2, 0), (2, -1),  "Helvetica"),
            ("FONTSIZE",      (0, 0), (-1, -1), 7),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("TOPPADDING",    (0, 0), (-1, -1), 2),
            ("ALIGN",         (0, 0), (0, -1),  "RIGHT" if is_rtl else "LEFT"),
            ("ALIGN",         (2, 0), (2, -1),  "RIGHT"),
        ]))
        story.append(bar_table)
    else:
        story.append(section(L("field_accuracy", lang)))
        story.append(Spacer(1, 2))
        msg = L("all_matched_msg", lang)
        # Add bold around the first sentence for emphasis (EN only — Arabic
        # already reshaped, can't easily nest tags after bidi).
        if lang == "en":
            msg = msg.replace(
                "All fields matched the database within 1%.",
                "<font color='#059669'><b>All fields matched the database within 1%.</b></font>",
            )
        story.append(Paragraph(msg, body))

    # ── 7. Historical context table ──
    history = (
        FinancialData.query
        .filter_by(stock_id=stock.id)
        .order_by(FinancialData.period.desc())
        .limit(4)
        .all()
    )
    history = list(reversed(history))
    if history:
        story.append(section(L("historical_context", lang)))
        story.append(Spacer(1, 2))
        head = [L("col_field", lang)] + [r.period for r in history]
        hist_rows = [head]
        for field in FIELD_KEYS:
            row = [L(f"field_{field}", lang)] + [_fmt_field(field, getattr(r, field)) for r in history]
            hist_rows.append(row)
        hist_table = Table(hist_rows,
                            colWidths=[55*mm] + [(105/len(history))*mm] * len(history),
                            hAlign="RIGHT" if is_rtl else "LEFT",
                            repeatRows=1)
        hist_table.setStyle(TableStyle([
            ("BACKGROUND",     (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ("TEXTCOLOR",      (0, 0), (-1, 0), colors.HexColor("#475569")),
            # First cell of header is the Arabic "Field" label; the rest of
            # the header row holds period strings like "2025-annual" (Latin).
            ("FONTNAME",       (0, 0), (0, 0), bold_font),
            ("FONTNAME",       (1, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME",       (0, 1), (0, -1), base_font),
            ("FONTNAME",       (1, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE",       (0, 0), (-1, -1), 8),
            ("ALIGN",          (0, 0), (0, -1),  "RIGHT" if is_rtl else "LEFT"),
            ("ALIGN",          (1, 0), (-1, -1), "RIGHT"),
            ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING",  (0, 0), (-1, -1), 3),
            ("TOPPADDING",     (0, 0), (-1, -1), 3),
            ("LINEBELOW",      (0, 0), (-1, 0), 0.5, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ]))
        story.append(hist_table)

    # ── 8. Verified valuation ──
    verified, sources = _merge_verified(db_comparison, lang)
    vals = _verified_valuation(stock, period, verified)

    val_block = []
    val_block.append(section(L("verified_valuation", lang, period=period)))
    val_block.append(Spacer(1, 2))
    val_rows = [
        [L("dcf", lang), L("pe", lang), L("pb", lang), L("fair_value", lang)],
        [
            "—" if vals["dcf"]  is None else f"SAR {vals['dcf']:,.2f}",
            "—" if vals["pe"]   is None else f"SAR {vals['pe']:,.2f}",
            "—" if vals["pb"]   is None else f"SAR {vals['pb']:,.2f}",
            "—" if vals["fair"] is None else f"SAR {vals['fair']:,.2f}",
        ],
    ]
    val_table = Table(val_rows, colWidths=[35*mm]*4,
                       hAlign="RIGHT" if is_rtl else "LEFT")
    val_table.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ("TEXTCOLOR",      (0, 0), (-1, 0), colors.HexColor("#475569")),
        ("FONTNAME",       (0, 0), (-1, 0), bold_font),
        # Value row holds "SAR 18.07" etc. — Latin, so use Helvetica.
        ("FONTNAME",       (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",       (0, 0), (-1, -1), 9),
        ("ALIGN",          (0, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 4),
        ("TOPPADDING",     (0, 0), (-1, -1), 4),
        ("LINEBELOW",      (0, 0), (-1, 0), 0.5, colors.HexColor("#cbd5e1")),
    ]))
    val_block.append(val_table)
    val_block.append(Spacer(1, 4))

    label, pct, color = _status_parts(stock.market_price, vals["fair"], lang)
    pct_str = "" if pct is None else f" ({'+' if pct >= 0 else ''}{pct:.1f}%)"
    mp_inline = (f" {_lat(f'(SAR {stock.market_price:,.2f})', lang)}"
                 if stock.market_price else "")
    val_block.append(Paragraph(
        f"{L('status_vs_mp', lang)}{mp_inline}: "
        f"<font color='{color}'><b>{label}</b></font>"
        f"<font color='{color}'>{_lat(pct_str, lang, bold=True)}</font>",
        body,
    ))
    story.append(KeepTogether(val_block))

    story.append(Spacer(1, 4))

    # ── Inputs used (collapsed when 100% verified) ──
    verified_marker = L("src_from_pdf_verified", lang)
    all_verified = all(s == verified_marker for s in sources.values()) \
                   and all(v is not None for v in verified.values())
    if all_verified:
        story.append(Paragraph(
            f"<b>{L('inputs_used', lang)}:</b> {L('inputs_all_verified', lang)}",
            body,
        ))
    else:
        story.append(Paragraph(f"<b>{L('inputs_used', lang)}:</b>", body))
        src_rows = []
        for field in FIELD_KEYS:
            src_rows.append([L(f"field_{field}", lang),
                             _fmt_field(field, verified.get(field)),
                             sources.get(field, "")])
        src_table = Table(src_rows, colWidths=[55*mm, 30*mm, 80*mm],
                           hAlign="RIGHT" if is_rtl else "LEFT")
        src_table.setStyle(TableStyle([
            # Field labels (col 0) use Arabic font; numeric values (col 1)
            # use Helvetica for Latin glyphs; source labels (col 2) may
            # contain Arabic so use the base font.
            ("FONTNAME",      (0, 0), (0, -1),  base_font),
            ("FONTNAME",      (1, 0), (1, -1),  "Helvetica"),
            ("FONTNAME",      (2, 0), (2, -1),  base_font),
            ("FONTSIZE",      (0, 0), (-1, -1), 7),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN",         (0, 0), (0, -1),  "RIGHT" if is_rtl else "LEFT"),
            ("ALIGN",         (1, 0), (1, -1),  "RIGHT"),
            ("ALIGN",         (2, 0), (2, -1),  "RIGHT" if is_rtl else "LEFT"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("TOPPADDING",    (0, 0), (-1, -1), 2),
            ("TEXTCOLOR",     (2, 0), (2, -1), colors.HexColor("#64748b")),
        ]))
        story.append(src_table)

    # ── 9. Methodology + Notes ──
    # For long Arabic body text we manually chunk-then-shape so ReportLab
    # doesn't reflow already-bidi'd text into scrambled visual order.
    story.append(Spacer(1, 6))
    story.append(section(L("methodology_notes", lang)))
    story.append(Spacer(1, 2))
    if lang == "ar":
        raw = LABELS["methodology_body"]["ar"]
        story.append(Paragraph(_shape_ar_paragraph(raw, wrap_chars=90), small_muted))
    else:
        story.append(Paragraph(L("methodology_body", lang), small_muted))

    # Pre-shape the strings the canvas will draw directly. The canvas's
    # drawString/drawRightString do NOT apply bidi or reshape, so we have
    # to do it ourselves for Arabic strings.
    title_text = L("extraction_report", lang)
    # "Page N of M" — pre-shape for RTL since the canvas won't.
    page_word  = _shape_ar("صفحة") if is_rtl else "Page"
    of_word    = _shape_ar("من")   if is_rtl else "of"
    gen_word   = L("generated", lang)
    today_str  = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # NumberedCanvas — collects per-page state during the first pass, then
    # draws the header/footer overlay on each page during save() with the
    # final total page count known. Avoids the two-pass-build issue with
    # KeepTogether/Spacer flowables.
    class NumberedCanvas(Canvas):
        def __init__(self, *args, **kwargs):
            Canvas.__init__(self, *args, **kwargs)
            self._saved_states = []

        def showPage(self):
            self._saved_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total = len(self._saved_states)
            for i, state in enumerate(self._saved_states, start=1):
                self.__dict__.update(state)
                self._page_number = i
                self._draw_overlay(total)
                Canvas.showPage(self)
            Canvas.save(self)

        def _draw_overlay(self, total):
            self.saveState()
            page_w, page_h = A4

            # Page frame.
            self.setStrokeColor(BRAND_RULE)
            self.setLineWidth(0.5)
            self.rect(8*mm, 8*mm, page_w - 16*mm, page_h - 16*mm, fill=0, stroke=1)

            # Branded header band.
            self.setFont("Helvetica-Bold", 14)
            self.setFillColor(BRAND)
            if is_rtl:
                self.drawRightString(page_w - 15*mm, page_h - 17*mm, "Kashif")
                self.setFont(_ARABIC_FONT, 10)
                self.setFillColor(colors.HexColor("#64748b"))
                self.drawRightString(page_w - 38*mm, page_h - 17*mm, title_text)
                self.setFont("Helvetica", 9)
                self.setFillColor(colors.HexColor("#475569"))
                self.drawString(15*mm, page_h - 17*mm, f"{ticker}  ·  {period}")
            else:
                self.drawString(15*mm, page_h - 17*mm, "Kashif")
                self.setFont("Helvetica", 10)
                self.setFillColor(colors.HexColor("#64748b"))
                self.drawString(38*mm, page_h - 17*mm, title_text)
                self.setFont("Helvetica", 9)
                self.setFillColor(colors.HexColor("#475569"))
                self.drawRightString(page_w - 15*mm, page_h - 17*mm, f"{ticker}  ·  {period}")

            self.setStrokeColor(BRAND_RULE)
            self.setLineWidth(0.7)
            self.line(15*mm, page_h - 22*mm, page_w - 15*mm, page_h - 22*mm)

            # Footer.
            self.setStrokeColor(BRAND_RULE)
            self.setLineWidth(0.5)
            self.line(15*mm, 14*mm, page_w - 15*mm, 14*mm)
            page_str = f"{page_word} {self._page_number} {of_word} {total}"
            gen_str = f"·  {gen_word} {today_str}"
            if is_rtl:
                self.setFont("Helvetica-Bold", 8)
                self.setFillColor(BRAND)
                self.drawRightString(page_w - 15*mm, 9*mm, "Kashif")
                self.setFont(_ARABIC_FONT, 7)
                self.setFillColor(colors.HexColor("#94a3b8"))
                self.drawRightString(page_w - 30*mm, 9*mm, gen_str)
                self.drawString(15*mm, 9*mm, page_str)
            else:
                self.setFont("Helvetica-Bold", 8)
                self.setFillColor(BRAND)
                self.drawString(15*mm, 9*mm, "Kashif")
                self.setFont("Helvetica", 7)
                self.setFillColor(colors.HexColor("#94a3b8"))
                self.drawString(30*mm, 9*mm, gen_str)
                self.drawRightString(page_w - 15*mm, 9*mm, page_str)
            self.restoreState()

    doc.build(story, canvasmaker=NumberedCanvas)
    return buf.getvalue()
