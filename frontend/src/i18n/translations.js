// Translation dictionary for English + Arabic.
//
// Conventions:
//   - Keys are dot-separated, grouped by area (nav, home, stock, etc.).
//   - Interpolation uses {placeholder} syntax — see the t() helper in
//     LanguageContext.jsx.
//   - When adding a string, add BOTH languages at the same time; missing
//     keys fall back to the key itself, which is obvious in the UI.

export const translations = {
  en: {
    // ── Navbar ─────────────────────────────────────────────
    'nav.home':         'Home',
    'nav.compare':      'Compare',

    // ── Search ─────────────────────────────────────────────
    'search.placeholder': 'Search ticker, e.g. 2222',
    'search.go':          'Go',

    // ── Toggles (tooltips) ─────────────────────────────────
    'toggle.theme.toDark':  'Switch to dark mode',
    'toggle.theme.toLight': 'Switch to light mode',
    'toggle.lang.toAr':     'Switch to Arabic',
    'toggle.lang.toEn':     'Switch to English',

    // ── Common ─────────────────────────────────────────────
    'common.loading':    'Loading…',
    'common.error':      'Error',
    'common.home':       'Home',

    // ── Home page ──────────────────────────────────────────
    'home.title':        'Stocks',
    'home.subtitle':     '{count} stocks across {sectors} sectors',
    'home.empty':        'No stocks in the database yet.',

    // ── Stock detail ───────────────────────────────────────
    'stock.marketPrice': 'Market price',
    'stock.sector':      'Sector',

    // ── Valuation section ──────────────────────────────────
    'val.title':         'Valuation',
    'val.fairValue':     'Fair value',
    'val.none':          'No valuation computed yet for this stock.',
    'val.calculated':    'Calculated',
    'val.source':        'source',

    // ── Gauge ──────────────────────────────────────────────
    'gauge.market':      'Market',
    'gauge.fair':        'Fair',
    'gauge.diff':        'Diff',
    'gauge.fairValue':   'Fair value',
    'gauge.insufficient': 'Insufficient data for valuation gauge.',

    // ── Valuation badge ────────────────────────────────────
    'badge.undervalued': 'UNDERVALUED',
    'badge.fair':        'FAIR',
    'badge.overvalued':  'OVERVALUED',
    'badge.unknown':     'UNKNOWN',

    // ── Financials section ─────────────────────────────────
    'fin.title':                  'Financials',
    'fin.metric':                 'Metric',
    'fin.empty':                  'No financial data available for this stock.',
    'fin.revenue':                'Revenue',
    'fin.net_income':             'Net Income',
    'fin.eps':                    'EPS',
    'fin.total_assets':           'Total Assets',
    'fin.total_borrowings':       'Total Borrowings',
    'fin.shareholders_equity':    'Shareholders Equity',
    'fin.cash_and_equivalents':   'Cash & Equivalents',
    'fin.free_cash_flow':         'Free Cash Flow',
    'fin.dividends_per_share':    'Dividends Per Share',
    'fin.shares_outstanding':     'Shares Outstanding',

    // ── Upload section ─────────────────────────────────────
    'up.title':            'Upload PDF',
    'up.previewOnly':      'PREVIEW ONLY',
    'up.description':      'Upload a financial-statement PDF for {ticker} to see what the extractor pulls out and how it compares to the current database row. Nothing is saved.',
    'up.extract':          'Extract',
    'up.extracting':       'Extracting…',
    'up.failed':           'Upload failed',
    'up.extractedValues':  'Extracted values',
    'up.period':           'Period',
    'up.noDbRow':          'no DB row for this period',
    'up.col.field':        'Field',
    'up.col.dbValue':      'DB value',
    'up.col.extracted':    'Extracted',
    'up.col.match':        'Match',

    // ── Compare page ───────────────────────────────────────
    'cmp.title':           'Comparisons',
    'cmp.subtitle':        '{count} of {total} stocks shown',
    'cmp.inSector':        'in',
    'cmp.all':             'All',
    'cmp.col.ticker':      'Ticker',
    'cmp.col.name':        'Name',
    'cmp.col.sector':      'Sector',
    'cmp.legend.best':     'Best in sector',
    'cmp.legend.worst':    'Worst in sector',
    'cmp.legend.hint':     'Hover any ratio cell to see the sector average + rank.',
    'cmp.tooltip':         'Rank {rank}/{peers} in {sector}  |  Sector avg: {avg}',
    'cmp.empty':           'No comparisons available.',

    // ── Sector page ────────────────────────────────────────
    'sec.breadcrumb':      'Sector',
    'sec.count.one':       '{count} stock in this sector',
    'sec.count.many':      '{count} stocks in this sector',
    'sec.empty':           'No stocks found in the {sector} sector.',

    // ── Stock card ─────────────────────────────────────────
    'card.period':         'Period',
    'card.eps':            'EPS',
    'card.revenue':        'Revenue',
  },

  ar: {
    // ── Navbar ─────────────────────────────────────────────
    'nav.home':         'الرئيسية',
    'nav.compare':      'المقارنات',

    // ── Search ─────────────────────────────────────────────
    'search.placeholder': 'ابحث برمز السهم، مثال 2222',
    'search.go':          'بحث',

    // ── Toggles (tooltips) ─────────────────────────────────
    'toggle.theme.toDark':  'التبديل إلى الوضع الداكن',
    'toggle.theme.toLight': 'التبديل إلى الوضع الفاتح',
    'toggle.lang.toAr':     'التبديل إلى العربية',
    'toggle.lang.toEn':     'التبديل إلى الإنجليزية',

    // ── Common ─────────────────────────────────────────────
    'common.loading':    'جارٍ التحميل…',
    'common.error':      'خطأ',
    'common.home':       'الرئيسية',

    // ── Home page ──────────────────────────────────────────
    'home.title':        'الأسهم',
    'home.subtitle':     '{count} سهم في {sectors} قطاع',
    'home.empty':        'لا توجد أسهم في قاعدة البيانات بعد.',

    // ── Stock detail ───────────────────────────────────────
    'stock.marketPrice': 'سعر السوق',
    'stock.sector':      'القطاع',

    // ── Valuation section ──────────────────────────────────
    'val.title':         'التقييم',
    'val.fairValue':     'القيمة العادلة',
    'val.none':          'لم يتم احتساب تقييم لهذا السهم بعد.',
    'val.calculated':    'تاريخ الاحتساب',
    'val.source':        'المصدر',

    // ── Gauge ──────────────────────────────────────────────
    'gauge.market':      'السوق',
    'gauge.fair':        'العادلة',
    'gauge.diff':        'الفرق',
    'gauge.fairValue':   'القيمة العادلة',
    'gauge.insufficient': 'بيانات غير كافية لعرض مقياس التقييم.',

    // ── Valuation badge ────────────────────────────────────
    'badge.undervalued': 'مقومة بأقل',
    'badge.fair':        'عادلة',
    'badge.overvalued':  'مقومة بأكثر',
    'badge.unknown':     'غير معروف',

    // ── Financials section ─────────────────────────────────
    'fin.title':                  'البيانات المالية',
    'fin.metric':                 'المقياس',
    'fin.empty':                  'لا تتوفر بيانات مالية لهذا السهم.',
    'fin.revenue':                'الإيرادات',
    'fin.net_income':             'صافي الدخل',
    'fin.eps':                    'ربحية السهم',
    'fin.total_assets':           'إجمالي الأصول',
    'fin.total_borrowings':       'إجمالي القروض',
    'fin.shareholders_equity':    'حقوق المساهمين',
    'fin.cash_and_equivalents':   'النقد وما يعادله',
    'fin.free_cash_flow':         'التدفقات النقدية الحرة',
    'fin.dividends_per_share':    'توزيعات السهم',
    'fin.shares_outstanding':     'الأسهم القائمة',

    // ── Upload section ─────────────────────────────────────
    'up.title':            'تحميل ملف PDF',
    'up.previewOnly':      'للمعاينة فقط',
    'up.description':      'قم بتحميل ملف PDF للقوائم المالية للسهم {ticker} لمعرفة القيم التي يستخرجها النظام ومقارنتها بالبيانات الحالية. لن يتم حفظ أي شيء.',
    'up.extract':          'استخراج',
    'up.extracting':       'جارٍ الاستخراج…',
    'up.failed':           'فشل التحميل',
    'up.extractedValues':  'القيم المستخرجة',
    'up.period':           'الفترة',
    'up.noDbRow':          'لا توجد بيانات في قاعدة البيانات لهذه الفترة',
    'up.col.field':        'الحقل',
    'up.col.dbValue':      'القيمة في القاعدة',
    'up.col.extracted':    'المستخرج',
    'up.col.match':        'التطابق',

    // ── Compare page ───────────────────────────────────────
    'cmp.title':           'المقارنات',
    'cmp.subtitle':        '{count} من أصل {total} سهم',
    'cmp.inSector':        'في',
    'cmp.all':             'الكل',
    'cmp.col.ticker':      'الرمز',
    'cmp.col.name':        'الاسم',
    'cmp.col.sector':      'القطاع',
    'cmp.legend.best':     'الأفضل في القطاع',
    'cmp.legend.worst':    'الأسوأ في القطاع',
    'cmp.legend.hint':     'مرر الفأرة فوق أي خلية لعرض المتوسط والترتيب.',
    'cmp.tooltip':         'الترتيب {rank}/{peers} في {sector}  |  المتوسط: {avg}',
    'cmp.empty':           'لا توجد مقارنات متاحة.',

    // ── Sector page ────────────────────────────────────────
    'sec.breadcrumb':      'القطاع',
    'sec.count.one':       'سهم واحد في هذا القطاع',
    'sec.count.many':      '{count} أسهم في هذا القطاع',
    'sec.empty':           'لا توجد أسهم في قطاع {sector}.',

    // ── Stock card ─────────────────────────────────────────
    'card.period':         'الفترة',
    'card.eps':            'ربحية السهم',
    'card.revenue':        'الإيرادات',
  },
};

// Sector-name translations — kept separate because sector names arrive
// from the backend as English strings, not translation keys.
// If a sector isn't in the map, it falls back to the English name.
export const sectorAr = {
  'Banks':          'البنوك',
  'Energy':         'الطاقة',
  'Materials':      'المواد الأساسية',
  'Telecom':        'الاتصالات',
  'Food':           'الغذاء',
  'Transportation': 'النقل',
  'Real Estate':    'العقارات',
};
