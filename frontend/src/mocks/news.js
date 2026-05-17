// Mock news feed — used when USE_MOCKS in api.js is true.
//
// Shape parity: each item matches what a normalized news endpoint would
// return — title (en+ar), summary (en+ar), source, url, publishedAt,
// optional tickers list. When wired to a real provider (Marketaux,
// Finnhub, Argaam RSS, etc.), the backend should normalize to this shape
// so the frontend doesn't have to change.

// Build relative dates so the "X hours ago" display always looks fresh.
const hoursAgo = (h) => new Date(Date.now() - h * 3600 * 1000).toISOString();

export const news = [
  // ── Tadawul-wide / market news ───────────────────────────────────
  {
    id: 'n-1001',
    title:     'Tadawul All Share Index closes higher as Aramco leads gains',
    title_ar:  'مؤشر تاسي يغلق مرتفعاً بقيادة مكاسب أرامكو',
    summary:   'The Saudi benchmark rose 0.8% with energy and banking names leading volume.',
    summary_ar:'ارتفع المؤشر السعودي بنسبة ٠٫٨٪ بقيادة أسهم الطاقة والبنوك في صدارة التداولات.',
    source:    'Argaam',
    url:       'https://www.argaam.com/',
    publishedAt: hoursAgo(2),
    tickers:   ['2222', '1120'],
  },
  {
    id: 'n-1002',
    title:     'SAMA holds repo rate steady, banks expected to maintain margins',
    title_ar:  'مؤسسة النقد تثبّت معدل إعادة الشراء، والبنوك تتوقع المحافظة على هوامش الربح',
    summary:   'Saudi Central Bank kept policy rates unchanged, lifting sentiment for the banking sector.',
    summary_ar:'أبقى البنك المركزي السعودي على معدلات الفائدة دون تغيير، مما عزّز ثقة قطاع البنوك.',
    source:    'Reuters',
    url:       'https://www.reuters.com/',
    publishedAt: hoursAgo(6),
    tickers:   ['1120', '1180'],
  },
  {
    id: 'n-1003',
    title:     'Foreign investor flows into Saudi equities hit a six-month high',
    title_ar:  'تدفقات المستثمرين الأجانب إلى الأسهم السعودية تسجل أعلى مستوى في ستة أشهر',
    summary:   'QFI net buying accelerated last week, concentrated in large-cap petrochemicals and banks.',
    summary_ar:'تسارع صافي شراء المستثمرين الأجانب المؤهلين الأسبوع الماضي، مع تركّز في كبرى شركات البتروكيماويات والبنوك.',
    source:    'Bloomberg',
    url:       'https://www.bloomberg.com/',
    publishedAt: hoursAgo(12),
    tickers:   [],
  },

  // ── Aramco (2222) ────────────────────────────────────────────────
  {
    id: 'n-2222-1',
    title:     'Saudi Aramco posts Q1 net income above analyst expectations',
    title_ar:  'أرامكو السعودية تعلن صافي ربح للربع الأول يفوق توقعات المحللين',
    summary:   'Quarterly profit rose 4% YoY on higher upstream volumes, with capex guidance unchanged.',
    summary_ar:'ارتفع صافي الربح الفصلي ٤٪ على أساس سنوي مع زيادة أحجام الإنتاج، مع الإبقاء على توجيهات النفقات الرأسمالية.',
    source:    'Argaam',
    url:       'https://www.argaam.com/',
    publishedAt: hoursAgo(3),
    tickers:   ['2222'],
  },
  {
    id: 'n-2222-2',
    title:     'Aramco announces second tranche of base + performance dividend',
    title_ar:  'أرامكو تعلن الدفعة الثانية من توزيعات الأرباح الأساسية والمرتبطة بالأداء',
    summary:   'The dividend reaffirms management commitment to shareholder distributions through 2025.',
    summary_ar:'تعكس التوزيعات التزام الإدارة بمواصلة توزيع الأرباح على المساهمين حتى نهاية ٢٠٢٥.',
    source:    'Tadawul',
    url:       'https://www.saudiexchange.sa/',
    publishedAt: hoursAgo(20),
    tickers:   ['2222'],
  },

  // ── Al Rajhi (1120) ──────────────────────────────────────────────
  {
    id: 'n-1120-1',
    title:     'Al Rajhi Bank loan book grows 11% YoY led by mortgages',
    title_ar:  'محفظة قروض مصرف الراجحي ترتفع ١١٪ سنوياً بقيادة التمويل العقاري',
    summary:   'Retail lending continues to outpace the sector; cost-to-income ratio improved 60 bps.',
    summary_ar:'استمر التمويل التجزئة في تجاوز نمو القطاع؛ وتحسنت نسبة التكلفة إلى الدخل بمقدار ٦٠ نقطة أساس.',
    source:    'Argaam',
    url:       'https://www.argaam.com/',
    publishedAt: hoursAgo(8),
    tickers:   ['1120'],
  },

  // ── SNB (1180) ───────────────────────────────────────────────────
  {
    id: 'n-1180-1',
    title:     'SNB completes sukuk issuance of SAR 5 billion',
    title_ar:  'البنك الأهلي السعودي يتم إصدار صكوك بقيمة ٥ مليارات ريال',
    summary:   'The dual-tranche sukuk was oversubscribed 3x, supporting Tier 2 capital base.',
    summary_ar:'تمت تغطية الصكوك ذات الشريحتين بثلاثة أضعاف، مما يعزز قاعدة رأس المال من الشريحة الثانية.',
    source:    'Tadawul',
    url:       'https://www.saudiexchange.sa/',
    publishedAt: hoursAgo(30),
    tickers:   ['1180'],
  },

  // ── SABIC (2010) ─────────────────────────────────────────────────
  {
    id: 'n-2010-1',
    title:     'SABIC quarterly margins pressured by softer polyethylene prices',
    title_ar:  'تراجع هوامش سابك الفصلية بفعل ضعف أسعار البولي إيثيلين',
    summary:   'Management guides for stable volumes; cost optimization program on track.',
    summary_ar:'تتوقع الإدارة استقرار الأحجام، مع تقدم برنامج تحسين التكاليف وفق الخطة.',
    source:    'Bloomberg',
    url:       'https://www.bloomberg.com/',
    publishedAt: hoursAgo(14),
    tickers:   ['2010'],
  },

  // ── stc (7010) ───────────────────────────────────────────────────
  {
    id: 'n-7010-1',
    title:     'stc expands 5G coverage to additional 12 Saudi cities',
    title_ar:  'إس تي سي توسّع تغطية شبكة الجيل الخامس لتشمل ١٢ مدينة سعودية إضافية',
    summary:   'Network investment cycle continues; ARPU expected to lift modestly in H2.',
    summary_ar:'تستمر دورة الاستثمار في الشبكة، مع توقع ارتفاع طفيف في متوسط الإيراد لكل مستخدم في النصف الثاني.',
    source:    'Argaam',
    url:       'https://www.argaam.com/',
    publishedAt: hoursAgo(26),
    tickers:   ['7010'],
  },

  // ── Almarai (2280) ───────────────────────────────────────────────
  {
    id: 'n-2280-1',
    title:     'Almarai raises full-year capex guidance on dairy expansion',
    title_ar:  'المراعي ترفع توجيهات النفقات الرأسمالية للعام مع توسعها في قطاع الألبان',
    summary:   'New processing facility in Hail to add capacity by Q4 2026.',
    summary_ar:'منشأة معالجة جديدة في حائل ستضيف طاقة إنتاجية بحلول الربع الرابع من ٢٠٢٦.',
    source:    'Reuters',
    url:       'https://www.reuters.com/',
    publishedAt: hoursAgo(40),
    tickers:   ['2280'],
  },

  // ── Bahri (4030) ─────────────────────────────────────────────────
  {
    id: 'n-4030-1',
    title:     'Bahri secures long-term VLCC charter contract with major buyer',
    title_ar:  'البحري تحصل على عقد استئجار طويل الأجل لناقلة نفط عملاقة مع مشترٍ رئيسي',
    summary:   'Multi-year contract expected to add stable cash flows starting Q3 2026.',
    summary_ar:'من المتوقع أن يضيف العقد متعدد السنوات تدفقات نقدية مستقرة بدءاً من الربع الثالث ٢٠٢٦.',
    source:    'Argaam',
    url:       'https://www.argaam.com/',
    publishedAt: hoursAgo(48),
    tickers:   ['4030'],
  },

  // ── AlAhli REIT (4338) ───────────────────────────────────────────
  {
    id: 'n-4338-1',
    title:     'AlAhli REIT distributes Q1 dividend, occupancy improves to 94%',
    title_ar:  'الأهلي ريت يوزع أرباح الربع الأول مع ارتفاع نسبة الإشغال إلى ٩٤٪',
    summary:   'Stable rental yields, modest increase in office and retail tenancy.',
    summary_ar:'استقرار في عوائد الإيجار، مع ارتفاع طفيف في إشغال المكاتب والتجزئة.',
    source:    'Tadawul',
    url:       'https://www.saudiexchange.sa/',
    publishedAt: hoursAgo(60),
    tickers:   ['4338'],
  },
];
