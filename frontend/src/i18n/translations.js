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
    'nav.watchlist':    'Watchlist',
    'nav.about':        'About',

    // ── Watchlist ──────────────────────────────────────────
    'watchlist.title':         'Your watchlist',
    'watchlist.count':         '{n} stocks',
    'watchlist.empty':         'No stocks starred yet',
    'watchlist.emptyHint':     'Tap the ⭐ on any stock card to add it here.',
    'watchlist.signinTitle':   'Sign in to use your watchlist',
    'watchlist.signinBody':    'Star stocks across the app and they’ll show up here, refreshed live alongside their valuations.',
    'watchlist.signinCta':     'Sign in',
    'watchlist.addTooltip':    'Add to watchlist',
    'watchlist.removeTooltip': 'Remove from watchlist',
    'watchlist.toggleFailed':  'Could not update watchlist',

    // ── Personal notes (per stock) ─────────────────────────
    'notes.title':       'Your notes',
    'notes.placeholder': 'Jot down your thesis, target price, or anything else you want to remember about this stock…',
    'notes.save':        'Save',
    'notes.saving':      'Saving…',
    'notes.saved':       'Saved',
    'notes.saveFailed':  'Could not save note',
    'notes.lastSaved':   'Last saved',

    // ── Recently viewed (browser-local) ────────────────────
    'recent.title':      'Recently viewed',

    // ── Pagination on HomePage ─────────────────────────────
    'home.loadMore':     'Load {n} more',
    'home.stocksShown':  'Showing {shown} of {total}',

    // ── Peers in same sector (stock detail page) ───────────
    'peers.title':       'Stocks in {sector}',
    'peers.count':       '{n} peers',
    'peers.empty':       'This stock is the only listed name in its sector.',

    // ── Search ─────────────────────────────────────────────
    'search.placeholder': 'Search ticker or name',
    'search.go':          'Go',
    'search.noMatches':   'No matches',

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

    // ── Home page hero ─────────────────────────────────────
    'home.hero.tagline':  'Tadawul intelligence',
    'home.hero.title':    'Saudi markets, decoded.',
    'home.hero.subtitle': 'Track Tadawul-listed companies with fair-value insights, side-by-side comparisons, and live market news.',
    'home.kpi.stocks':    'Stocks tracked',
    'home.kpi.sectors':   'Sectors',
    'home.kpi.revenue':   'Total revenue',
    'home.section.stocks':     'Stocks',
    'home.section.stocksSub':  'All {count} companies we follow.',
    'home.section.sectors':    'By sector',
    'home.section.sectorsSub': 'Pick a sector to compare its constituents.',

    // ── Stock detail ───────────────────────────────────────
    'stock.marketPrice': 'Market price',
    'stock.sector':      'Sector',

    // ── Valuation section ──────────────────────────────────
    'val.title':         'Valuation',
    'val.fairValue':     'Fair value',
    'val.none':          'No valuation computed yet for this stock.',
    'val.calculated':    'Calculated',
    'val.source':        'source',
    'val.model.dcf':     'DCF',
    'val.model.pe':      'P/E',
    'val.model.pb':      'P/B',

    // ── Why a fair value couldn't be computed ─────────────
    'val.unavailable.title':           'Fair value unavailable',
    'val.unavailable.loss_making':     'This company is currently loss-making (negative earnings or cash flow), so a fair value cannot be honestly computed. Valuation models like DCF and P/E require positive figures to work.',
    'val.unavailable.insolvent':       'This company has negative shareholders’ equity, meaning liabilities exceed assets. Standard valuation models cannot produce a meaningful fair value in this state.',
    'val.unavailable.incomplete_data': 'The latest financial statements are missing key values (EPS, equity, or shares outstanding). A fair value will appear once the next filing is processed.',
    'val.unavailable.no_peers':        'This company is the only listed stock in its sector, so peer-based valuation methods (P/E, P/B) cannot be calculated.',
    'val.unavailable.unknown':         'A fair value could not be computed for this stock at this time.',

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
    'up.toast.success':    'Extracted financials for {period}.',
    'up.extractedValues':  'Extracted values',
    'up.period':           'Period',
    'up.noDbRow':          'no DB row for this period',
    'up.col.field':        'Field',
    'up.col.dbValue':      'DB value',
    'up.col.extracted':    'Extracted',
    'up.col.diff':         'Diff',
    'up.col.match':        'Match',
    'up.summary.match':    '{n} match',
    'up.summary.mismatch': '{n} mismatch',
    'up.summary.missing':  '{n} missing',
    'up.download.csv':     'Download CSV',
    'up.download.json':    'Download JSON',
    'up.download.report':       'Download Report (PDF)',
    'up.download.reportEn':     'Download Report (EN)',
    'up.download.reportAr':     'Download Report (AR)',
    'up.download.reportBusy':   'Generating…',
    'up.download.reportFailed': 'Report generation failed',

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

    // ── News ───────────────────────────────────────────────
    'news.marketTitle': 'Market news',
    'news.subtitle':    'Latest headlines from Tadawul and global wires.',
    'news.stockTitle':  'News about {ticker}',
    'news.loading':     'Loading news…',
    'news.empty':       'No news available right now.',
    'news.emptyTicker': 'No recent news for {ticker}.',

    // ── Auth ───────────────────────────────────────────────
    'auth.nav.signIn':         'Sign in',
    'auth.nav.signUp':         'Create account',
    'auth.nav.signOut':        'Sign out',

    'auth.field.name':         'Full name',
    'auth.field.email':        'Email',
    'auth.field.password':     'Password',
    'auth.field.passwordHint': 'At least 6 characters.',
    'auth.field.confirm':      'Confirm password',

    'auth.signIn.title':       'Sign in to Kashif',
    'auth.signIn.subtitle':    'Welcome back.',
    'auth.signIn.submit':      'Sign in',
    'auth.signIn.busy':        'Signing in…',
    'auth.signIn.noAccount':   "Don't have an account?",
    'auth.signIn.createOne':   'Create one',

    'auth.signUp.title':       'Create your account',
    'auth.signUp.subtitle':    'Track Saudi-listed stocks with valuation insights.',
    'auth.signUp.submit':      'Create account',
    'auth.signUp.busy':        'Creating account…',
    'auth.signUp.haveAccount': 'Already have an account?',
    'auth.signUp.signInLink':  'Sign in',

    'auth.err.generic':           'Something went wrong. Please try again.',
    'auth.err.noAccount':         'No account found with that email.',
    'auth.err.wrongPassword':     'Incorrect password.',
    'auth.err.emailTaken':        'An account with that email already exists.',
    'auth.err.invalidEmail':      'Please enter a valid email address.',
    'auth.err.nameRequired':      'Please enter your name.',
    'auth.err.passwordTooShort':  'Password must be at least 6 characters.',
    'auth.err.passwordsMismatch': "Passwords don't match.",

    'auth.toast.signedIn':        'Welcome back, {name}.',
    'auth.toast.welcome':         'Account created — welcome, {name}.',
    'auth.toast.signedOut':       'Signed out.',

    // ── About page ─────────────────────────────────────────
    'about.tagline':   'About Kashif',
    'about.title':     'Built for clarity on the Saudi market.',
    'about.subtitle':  'Kashif turns Tadawul filings, valuations, and market news into one fast, bilingual workspace.',

    'about.mission.title': 'Our mission',
    'about.mission.body':  'Make Saudi public-company information radically accessible — to retail investors, students, and analysts alike. We extract the numbers, run the valuation models, and put it all behind a search bar in both English and Arabic.',

    'about.what.title':    'What we do',
    'about.what.subtitle': 'Three things, done well.',

    'about.feature.extract.title': 'Statement extraction',
    'about.feature.extract.body':  'We parse audited PDFs from Tadawul filings and pull the line items that matter — revenue, net income, EPS, balance sheet, cash flow.',
    'about.feature.value.title':   'Fair-value models',
    'about.feature.value.body':    'Each stock gets a blended fair value from DCF, P/E, and P/B models so you can see if it’s under, over, or fairly priced.',
    'about.feature.news.title':    'Live market news',
    'about.feature.news.body':     'Headlines from Finnhub, scoped per ticker, so you always see the story behind the move.',

    'about.value.bilingual.title':    'Bilingual by default',
    'about.value.bilingual.body':     'Every screen works in English and Arabic with full RTL support.',
    'about.value.transparent.title':  'Transparent methodology',
    'about.value.transparent.body':   'Every fair-value comes with the inputs and per-model breakdown — no black box.',
    'about.value.focus.title':        'Tadawul focused',
    'about.value.focus.body':         'We don’t try to cover every market. We try to cover the Saudi market deeply.',

    'about.cta.title':  'Start exploring.',
    'about.cta.body':   'Browse stocks, compare across sectors, and dive into the numbers.',
    'about.cta.button': 'Browse stocks',

    // ── Footer ─────────────────────────────────────────────
    'footer.tagline':   'Tadawul-listed stocks with fair-value insights and bilingual market news.',
    'footer.explore':   'Explore',
    'footer.account':   'Account',
    'footer.copyright': 'All rights reserved.',
  },

  ar: {
    // ── Navbar ─────────────────────────────────────────────
    'nav.home':         'الرئيسية',
    'nav.compare':      'المقارنات',
    'nav.watchlist':    'قائمة المتابعة',
    'nav.about':        'من نحن',

    // ── قائمة المتابعة ─────────────────────────────────────
    'watchlist.title':         'قائمة المتابعة',
    'watchlist.count':         '{n} سهم',
    'watchlist.empty':         'لم تتم إضافة أي سهم بعد',
    'watchlist.emptyHint':     'اضغط على ⭐ في أي بطاقة سهم لإضافته هنا.',
    'watchlist.signinTitle':   'سجّل الدخول لاستخدام قائمة المتابعة',
    'watchlist.signinBody':    'علِّم الأسهم بنجمة في أي مكان في التطبيق وستظهر هنا مع تحديث مباشر لأسعارها وتقييماتها.',
    'watchlist.signinCta':     'تسجيل الدخول',
    'watchlist.addTooltip':    'إضافة إلى قائمة المتابعة',
    'watchlist.removeTooltip': 'إزالة من قائمة المتابعة',
    'watchlist.toggleFailed':  'تعذّر تحديث قائمة المتابعة',

    // ── الملاحظات الشخصية (لكل سهم) ────────────────────────
    'notes.title':       'ملاحظاتك',
    'notes.placeholder': 'سجّل توقعاتك، السعر المستهدف، أو أي شيء تريد تذكره عن هذا السهم…',
    'notes.save':        'حفظ',
    'notes.saving':      'جارٍ الحفظ…',
    'notes.saved':       'تم الحفظ',
    'notes.saveFailed':  'تعذّر حفظ الملاحظة',
    'notes.lastSaved':   'آخر حفظ',

    // ── شوهد مؤخراً (في المتصفح) ──────────────────────────
    'recent.title':      'شوهد مؤخراً',

    // ── الترقيم في الصفحة الرئيسية ────────────────────────
    'home.loadMore':     'عرض {n} إضافية',
    'home.stocksShown':  'تعرض {shown} من {total}',

    // ── أسهم في نفس القطاع (صفحة تفاصيل السهم) ────────────
    'peers.title':       'أسهم في قطاع {sector}',
    'peers.count':       '{n} سهم',
    'peers.empty':       'هذا السهم هو الوحيد المدرج في قطاعه.',

    // ── Search ─────────────────────────────────────────────
    'search.placeholder': 'ابحث برمز السهم أو الاسم',
    'search.go':          'بحث',
    'search.noMatches':   'لا توجد نتائج',

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

    // ── Home page hero ─────────────────────────────────────
    'home.hero.tagline':  'ذكاء السوق السعودي',
    'home.hero.title':    'السوق السعودي، بوضوح.',
    'home.hero.subtitle': 'تابع الشركات المدرجة في تداول مع رؤى القيمة العادلة، والمقارنات المباشرة، وآخر أخبار السوق.',
    'home.kpi.stocks':    'الأسهم المتابَعة',
    'home.kpi.sectors':   'القطاعات',
    'home.kpi.revenue':   'إجمالي الإيرادات',
    'home.section.stocks':     'الأسهم',
    'home.section.stocksSub':  'جميع الشركات الـ{count} التي نتابعها.',
    'home.section.sectors':    'حسب القطاع',
    'home.section.sectorsSub': 'اختر قطاعاً لمقارنة شركاته.',

    // ── Stock detail ───────────────────────────────────────
    'stock.marketPrice': 'سعر السوق',
    'stock.sector':      'القطاع',

    // ── Valuation section ──────────────────────────────────
    'val.title':         'التقييم',
    'val.fairValue':     'القيمة العادلة',
    'val.none':          'لم يتم احتساب تقييم لهذا السهم بعد.',
    'val.calculated':    'تاريخ الاحتساب',
    'val.source':        'المصدر',
    'val.model.dcf':     'التدفقات المخصومة',
    'val.model.pe':      'مكرر الربحية',
    'val.model.pb':      'مكرر القيمة الدفترية',

    // ── أسباب عدم توفر القيمة العادلة ──────────────────────
    'val.unavailable.title':           'القيمة العادلة غير متاحة',
    'val.unavailable.loss_making':     'هذه الشركة تسجّل خسائر حالياً (أرباح سالبة أو تدفقات نقدية سالبة)، لذا لا يمكن احتساب قيمة عادلة موضوعية. تتطلب نماذج التقييم مثل التدفقات النقدية المخصومة ومكرر الربحية أرقاماً موجبة لتعمل.',
    'val.unavailable.insolvent':       'لدى هذه الشركة حقوق مساهمين سالبة، أي أن مطلوباتها تتجاوز أصولها. لا يمكن لنماذج التقييم المعتادة إنتاج قيمة عادلة في هذه الحالة.',
    'val.unavailable.incomplete_data': 'القوائم المالية الأحدث تنقصها قيم أساسية (ربحية السهم أو حقوق المساهمين أو الأسهم القائمة). ستظهر القيمة العادلة عند معالجة الإفصاح القادم.',
    'val.unavailable.no_peers':        'هذه الشركة هي الوحيدة المدرجة في قطاعها، لذا لا يمكن حساب طرق التقييم المعتمدة على الشركات المماثلة (مكرر الربحية ومكرر القيمة الدفترية).',
    'val.unavailable.unknown':         'لم يتم احتساب قيمة عادلة لهذا السهم في الوقت الحالي.',

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
    'up.toast.success':    'تم استخراج البيانات المالية للفترة {period}.',
    'up.extractedValues':  'القيم المستخرجة',
    'up.period':           'الفترة',
    'up.noDbRow':          'لا توجد بيانات في قاعدة البيانات لهذه الفترة',
    'up.col.field':        'الحقل',
    'up.col.dbValue':      'القيمة في القاعدة',
    'up.col.extracted':    'المستخرج',
    'up.col.diff':         'الفرق',
    'up.col.match':        'التطابق',
    'up.summary.match':    '{n} مطابقة',
    'up.summary.mismatch': '{n} اختلاف',
    'up.summary.missing':  '{n} مفقود',
    'up.download.csv':     'تنزيل CSV',
    'up.download.json':    'تنزيل JSON',
    'up.download.report':       'تنزيل التقرير (PDF)',
    'up.download.reportEn':     'تنزيل التقرير (EN)',
    'up.download.reportAr':     'تنزيل التقرير (AR)',
    'up.download.reportBusy':   'جارٍ التوليد…',
    'up.download.reportFailed': 'فشل توليد التقرير',

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

    // ── News ───────────────────────────────────────────────
    'news.marketTitle': 'أخبار السوق',
    'news.subtitle':    'آخر العناوين من تداول والأسواق العالمية.',
    'news.stockTitle':  'أخبار {ticker}',
    'news.loading':     'جارٍ تحميل الأخبار…',
    'news.empty':       'لا توجد أخبار متاحة حالياً.',
    'news.emptyTicker': 'لا توجد أخبار حديثة لـ {ticker}.',

    // ── Auth ───────────────────────────────────────────────
    'auth.nav.signIn':         'تسجيل الدخول',
    'auth.nav.signUp':         'إنشاء حساب',
    'auth.nav.signOut':        'تسجيل الخروج',

    'auth.field.name':         'الاسم الكامل',
    'auth.field.email':        'البريد الإلكتروني',
    'auth.field.password':     'كلمة المرور',
    'auth.field.passwordHint': '٦ أحرف على الأقل.',
    'auth.field.confirm':      'تأكيد كلمة المرور',

    'auth.signIn.title':       'تسجيل الدخول إلى كاشف',
    'auth.signIn.subtitle':    'أهلاً بعودتك.',
    'auth.signIn.submit':      'تسجيل الدخول',
    'auth.signIn.busy':        'جارٍ تسجيل الدخول…',
    'auth.signIn.noAccount':   'ليس لديك حساب؟',
    'auth.signIn.createOne':   'أنشئ حساباً',

    'auth.signUp.title':       'إنشاء حساب جديد',
    'auth.signUp.subtitle':    'تابع الأسهم السعودية مع رؤى التقييم.',
    'auth.signUp.submit':      'إنشاء الحساب',
    'auth.signUp.busy':        'جارٍ إنشاء الحساب…',
    'auth.signUp.haveAccount': 'لديك حساب بالفعل؟',
    'auth.signUp.signInLink':  'سجّل الدخول',

    'auth.err.generic':           'حدث خطأ ما. يرجى المحاولة مرة أخرى.',
    'auth.err.noAccount':         'لا يوجد حساب بهذا البريد الإلكتروني.',
    'auth.err.wrongPassword':     'كلمة المرور غير صحيحة.',
    'auth.err.emailTaken':        'يوجد حساب مسجّل بهذا البريد الإلكتروني.',
    'auth.err.invalidEmail':      'يرجى إدخال بريد إلكتروني صالح.',
    'auth.err.nameRequired':      'يرجى إدخال الاسم.',
    'auth.err.passwordTooShort':  'كلمة المرور يجب أن تكون ٦ أحرف على الأقل.',
    'auth.err.passwordsMismatch': 'كلمتا المرور غير متطابقتين.',

    'auth.toast.signedIn':        'أهلاً بعودتك يا {name}.',
    'auth.toast.welcome':         'تم إنشاء الحساب — أهلاً يا {name}.',
    'auth.toast.signedOut':       'تم تسجيل الخروج.',

    // ── About page ─────────────────────────────────────────
    'about.tagline':   'عن كاشف',
    'about.title':     'صُمم لوضوح السوق السعودي.',
    'about.subtitle':  'كاشف يحوّل التقارير المالية لتداول ونماذج التقييم وأخبار السوق إلى مساحة عمل واحدة سريعة وثنائية اللغة.',

    'about.mission.title': 'مهمتنا',
    'about.mission.body':  'جعل معلومات الشركات السعودية المدرجة في متناول الجميع — للمستثمرين الأفراد والطلاب والمحللين. نستخرج الأرقام، ونشغّل نماذج التقييم، ونقدّم كل ذلك خلف شريط بحث واحد بالعربية والإنجليزية.',

    'about.what.title':    'ماذا نفعل',
    'about.what.subtitle': 'ثلاثة أمور نتقنها.',

    'about.feature.extract.title': 'استخراج البيانات المالية',
    'about.feature.extract.body':  'نقرأ تقارير تداول المُدققة ونستخرج البنود الأهم — الإيرادات، صافي الدخل، ربحية السهم، الميزانية، التدفقات النقدية.',
    'about.feature.value.title':   'نماذج القيمة العادلة',
    'about.feature.value.body':    'كل سهم يحصل على قيمة عادلة مرجَّحة من نماذج DCF و P/E و P/B لتعرف ما إذا كان السهم مقوَّماً بأقل أو أكثر أو بشكل عادل.',
    'about.feature.news.title':    'أخبار السوق المباشرة',
    'about.feature.news.body':     'عناوين من Finnhub، مُصنَّفة حسب رمز السهم، لتعرف دائماً القصة وراء الحركة.',

    'about.value.bilingual.title':    'ثنائي اللغة بشكل افتراضي',
    'about.value.bilingual.body':     'كل شاشة تعمل بالإنجليزية والعربية مع دعم كامل للكتابة من اليمين لليسار.',
    'about.value.transparent.title':  'منهجية شفافة',
    'about.value.transparent.body':   'كل قيمة عادلة تُعرض مع مدخلاتها وتفصيل كل نموذج — لا صناديق سوداء.',
    'about.value.focus.title':        'مُركّز على تداول',
    'about.value.focus.body':         'لا نحاول تغطية كل الأسواق. نحاول تغطية السوق السعودي بعمق.',

    'about.cta.title':  'ابدأ الاستكشاف.',
    'about.cta.body':   'تصفح الأسهم، قارن بين القطاعات، وتعمّق في الأرقام.',
    'about.cta.button': 'تصفح الأسهم',

    // ── Footer ─────────────────────────────────────────────
    'footer.tagline':   'أسهم سعودية مدرجة مع رؤى القيمة العادلة وأخبار السوق ثنائية اللغة.',
    'footer.explore':   'استكشف',
    'footer.account':   'الحساب',
    'footer.copyright': 'جميع الحقوق محفوظة.',
  },
};

// Sector-name translations — kept separate because sector names arrive
// from the backend as English strings, not translation keys.
// If a sector isn't in the map, it falls back to the English name.
// Keys must match the exact `name_en` strings the backend sends
// (sourced from the `sectors` table — name_en column).
export const sectorAr = {
  'Banks':                                        'البنوك',
  'Capital Goods':                                'السلع الرأسمالية',
  'Commercial & Professional Svc':                'الخدمات التجارية والمهنية',
  'Consumer Discretionary Distribution & Retail': 'توزيع السلع الكمالية وتجزئتها',
  'Consumer Durables & Apparel':                  'السلع طويلة الأجل',
  'Consumer Services':                            'الخدمات الاستهلاكية',
  'Consumer Staples Distribution & Retail':       'توزيع السلع الاستهلاكية وتجزئتها',
  'Energy':                                       'الطاقة',
  'Financial Services':                           'الخدمات المالية',
  'Food & Beverages':                             'الأغذية والمشروبات',
  'Health Care Equipment & Svc':                  'المعدات والخدمات الصحية',
  'Household & Personal Products':                'المنتجات المنزلية والشخصية',
  'Insurance':                                    'التأمين',
  'Materials':                                    'المواد الأساسية',
  'Media and Entertainment':                      'الإعلام والترفيه',
  'Pharma, Biotech & Life Science':               'الأدوية والتكنولوجيا الحيوية وعلوم الحياة',
  'Real Estate Mgmt & Dev\'t':                    'إدارة وتطوير العقارات',
  'REITs':                                        'صناديق الاستثمار العقارية المتداولة',
  'Software & Services':                          'البرمجيات والخدمات',
  'Telecommunication Services':                   'الاتصالات',
  'Transportation':                               'النقل',
  'Utilities':                                    'المرافق العامة',
};
