// Finnhub API client — called directly from the browser.
//
// Endpoints used:
//   - Per-stock:  GET https://finnhub.io/api/v1/company-news?symbol=2222.SR&from=YYYY-MM-DD&to=YYYY-MM-DD&token=KEY
//   - Market:     GET https://finnhub.io/api/v1/news?category=general&token=KEY
//
// Tadawul mapping:
//   Saudi Exchange tickers are numeric (2222 for Aramco). Finnhub
//   suffixes the exchange code, so we append ".SR" before each request.
//
// Auth:
//   Reads REACT_APP_FINNHUB_KEY from the build-time env (Create React
//   App convention). If the key is missing, hasFinnhubKey() returns
//   false and callers can fall back to mocks.
//
// Rate limit:
//   Finnhub free tier = 60 req/min. The 5-minute in-memory cache below
//   stops the same tab from re-hitting the network on tab switches.

const KEY      = process.env.REACT_APP_FINNHUB_KEY || '';
const BASE     = 'https://finnhub.io/api/v1';
const CACHE_MS = 5 * 60 * 1000;       // 5-minute TTL — plenty for news

export const hasFinnhubKey = () => !!KEY;

// ── In-memory cache: key → { at, value } ──────────────────────────────
const cache = new Map();
const fromCache = (key) => {
  const hit = cache.get(key);
  if (hit && Date.now() - hit.at < CACHE_MS) return hit.value;
  return null;
};
const toCache = (key, value) => {
  cache.set(key, { at: Date.now(), value });
  return value;
};

// ── Helpers ───────────────────────────────────────────────────────────
const yyyymmdd = (d) => d.toISOString().slice(0, 10);

// Tadawul numeric ticker → Finnhub symbol. If a ticker is already
// suffixed (e.g. "AAPL"), leave it alone.
const toFinnhubSymbol = (ticker) =>
  /^\d+$/.test(ticker) ? `${ticker}.SR` : ticker;

// Normalize one Finnhub item into our internal news shape. Finnhub
// doesn't provide Arabic text — title_ar/summary_ar stay null so the
// NewsCard falls back to the English text in both UI languages.
const normalize = (raw, relatedTicker = null) => ({
  id:          `fh-${raw.id || raw.url}`,
  title:       raw.headline || '',
  title_ar:    null,
  summary:     raw.summary  || '',
  summary_ar:  null,
  source:      raw.source   || 'Finnhub',
  url:         raw.url      || '',
  publishedAt: new Date((raw.datetime || 0) * 1000).toISOString(),
  tickers:     raw.related
                 ? raw.related.split(',').map((s) => s.trim()).filter(Boolean)
                 : (relatedTicker ? [relatedTicker] : []),
  image:       raw.image || null,
});

// ── Fetch ─────────────────────────────────────────────────────────────
async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) {
    // 429 = rate-limited, 401 = bad key. Surface a useful message.
    const txt = await res.text().catch(() => '');
    throw new Error(`Finnhub ${res.status}: ${txt || res.statusText}`);
  }
  return res.json();
}

// ── Public API ────────────────────────────────────────────────────────

// Company news for one ticker (last 14 days by default).
export async function fetchCompanyNews(ticker, { days = 14 } = {}) {
  const sym = toFinnhubSymbol(ticker);
  const to   = new Date();
  const from = new Date(to.getTime() - days * 86_400_000);

  const cacheKey = `co:${sym}:${days}`;
  const cached = fromCache(cacheKey);
  if (cached) return cached;

  const url = `${BASE}/company-news?symbol=${encodeURIComponent(sym)}` +
              `&from=${yyyymmdd(from)}&to=${yyyymmdd(to)}` +
              `&token=${encodeURIComponent(KEY)}`;

  const raw = await fetchJson(url);
  // Keep the ticker as a related tag so the UI chip still works.
  const normalized = (Array.isArray(raw) ? raw : []).map((r) => normalize(r, ticker));
  return toCache(cacheKey, normalized);
}

// Market-wide / general news (no per-symbol filter).
export async function fetchMarketNews() {
  const cacheKey = 'market:general';
  const cached = fromCache(cacheKey);
  if (cached) return cached;

  const url = `${BASE}/news?category=general&token=${encodeURIComponent(KEY)}`;
  const raw = await fetchJson(url);
  const normalized = (Array.isArray(raw) ? raw : []).map((r) => normalize(r));
  return toCache(cacheKey, normalized);
}
