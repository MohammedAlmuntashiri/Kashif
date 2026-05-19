// Centralized API client for the Kashif backend.
//
// We use the create-react-app dev proxy (configured in package.json as
//   "proxy": "http://localhost:5000"
// ) so the frontend can call relative URLs like "/api/stocks/" and the
// dev server forwards them to the Flask backend. No CORS headaches.
//
// PRODUCTION NOTE: when we ship a static build (nginx, etc.) this proxy
// will no longer apply. At that point baseURL should come from an env
// variable, e.g. REACT_APP_API_BASE. Left as a polish-phase TODO.
//
// ─────────────────────────────────────────────────────────────────────
// MOCK MODE
// ─────────────────────────────────────────────────────────────────────
// While the DB on this machine is empty (real data lives on the
// accuracy team's machine), every export below can transparently serve
// baked-in mock data from ./mocks/data.js instead of hitting the
// backend. Flip USE_MOCKS to false once real data is in the DB — no
// other files in the frontend need to change.

import axios from 'axios';
import * as mocks from '../mocks/data.js';
import { news as mockNews } from '../mocks/news.js';
import {
  hasFinnhubKey,
  fetchCompanyNews,
  fetchMarketNews,
} from './finnhub.js';

// ⚠️  Flip this to false when the real DB is populated.  ⚠️
const USE_MOCKS = false;

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,                     // 30s — PDF upload + OCR can take a while
  headers: { 'Content-Type': 'application/json' },
});

// Inject the JWT (stored by AuthContext after sign-in) on every request.
// We read it fresh per-request so a sign-in / sign-out is picked up
// without recreating the axios instance.
api.interceptors.request.use((cfg) => {
  try {
    const token = localStorage.getItem('kashif.token');
    if (token) cfg.headers.Authorization = `Bearer ${token}`;
  } catch (_) { /* localStorage blocked — fine */ }
  return cfg;
});

// Helper: simulate axios's 404 error shape for mock-mode "not found".
// StockDetailPage reads e.response.data.error, so we mirror that shape.
const mockNotFound = (msg) =>
  Promise.reject({ response: { data: { error: msg } }, message: msg });

// ─── Stocks ───────────────────────────────────────────────────────────
// GET /api/stocks/  — lightweight list of every stock (summary only).
export const getStocks = () =>
  USE_MOCKS
    ? Promise.resolve(mocks.stocks)
    : api.get('/stocks/').then((r) => r.data);

// GET /api/stocks/<ticker>  — full detail for one stock.
export const getStock = (ticker) => {
  if (USE_MOCKS) {
    const d = mocks.stockDetails[ticker];
    return d ? Promise.resolve(d) : mockNotFound(`Stock ${ticker} not found`);
  }
  return api.get(`/stocks/${encodeURIComponent(ticker)}`).then((r) => r.data);
};

// ─── Valuations ───────────────────────────────────────────────────────
// GET /api/valuations/<ticker>  — DCF + P/E + P/B blended fair value.
export const getValuation = (ticker) => {
  if (USE_MOCKS) {
    const v = mocks.valuations[ticker];
    return v ? Promise.resolve(v) : mockNotFound(`No valuation for ${ticker}`);
  }
  return api.get(`/valuations/${encodeURIComponent(ticker)}`).then((r) => r.data);
};

// ─── Comparisons ──────────────────────────────────────────────────────
// GET /api/comparisons/[?sector=<name>]
//   - No sector  → all stocks across all sectors
//   - sector set → filtered to that one sector (case-insensitive)
export const getComparisons = ({ sector } = {}) => {
  if (USE_MOCKS) {
    let rows = mocks.comparisons;
    if (sector) {
      const wanted = sector.toLowerCase();
      rows = rows.filter((r) => r.sector.toLowerCase() === wanted);
    }
    return Promise.resolve(rows);
  }
  const params = sector ? { sector } : {};
  return api.get('/comparisons/', { params }).then((r) => r.data);
};

// ─── Sectors ──────────────────────────────────────────────────────────
// GET /api/sectors/  — metadata for every Tadawul sector.
export const getSectors = () =>
  USE_MOCKS
    ? Promise.resolve(mocks.sectors)
    : api.get('/sectors/').then((r) => r.data);

// ─── PDF upload ───────────────────────────────────────────────────────
// POST /api/pdf/upload?ticker=<symbol>[&dry_run=true]
// NOT mocked — the UploadPage is still a placeholder and a real upload
// only makes sense against a real backend anyway.
export const uploadPdf = (ticker, file, { dryRun = false } = {}) => {
  if (USE_MOCKS) {
    return mockNotFound(
      'PDF upload is disabled in mock mode. Flip USE_MOCKS in services/api.js.'
    );
  }

  const form = new FormData();
  form.append('pdf', file);

  const params = { ticker };
  if (dryRun) params.dry_run = 'true';

  return api.post('/pdf/upload', form, {
    params,
    headers: { 'Content-Type': 'multipart/form-data' },
    // OCR-heavy scanned PDFs can take several minutes. Override the
    // global 30s timeout for this single call so the extractor has room.
    timeout: 480000,
  }).then((r) => r.data);
};

// POST /api/pdf/report/<ticker>?lang=en|ar
// Sends the dry-run extraction result the frontend already has and
// gets back a PDF report (blob) for immediate download. `lang` chooses
// which localized variant to render (full RTL + Arabic font when lang='ar').
export const downloadExtractionReport = (ticker, result, sourceFilename, lang = 'en') =>
  api.post(
    `/pdf/report/${encodeURIComponent(ticker)}`,
    { ...result, source_filename: sourceFilename || undefined },
    { params: { lang }, responseType: 'blob', timeout: 60000 },
  ).then((r) => r.data);

// ─── Watchlist (auth-gated) ───────────────────────────────────────────
// All three endpoints require the Bearer token (interceptor adds it).

// GET /api/watchlist/  — array of stocks the current user has starred.
export const fetchWatchlist = () =>
  api.get('/watchlist/').then((r) => r.data);

// POST /api/watchlist/<ticker>  — star a stock (idempotent).
export const addToWatchlist = (ticker) =>
  api.post(`/watchlist/${encodeURIComponent(ticker)}`).then((r) => r.data);

// DELETE /api/watchlist/<ticker>  — unstar a stock (idempotent).
export const removeFromWatchlist = (ticker) =>
  api.delete(`/watchlist/${encodeURIComponent(ticker)}`).then((r) => r.data);

// ─── Personal notes (auth-gated) ──────────────────────────────────────

// GET /api/notes/<ticker>  — returns {symbol, content, updated_at}.
// Content is "" when the user has no note yet.
export const fetchNote = (ticker) =>
  api.get(`/notes/${encodeURIComponent(ticker)}`).then((r) => r.data);

// PUT /api/notes/<ticker>  — create or overwrite. Empty content deletes the row.
export const saveNote = (ticker, content) =>
  api.put(`/notes/${encodeURIComponent(ticker)}`, { content }).then((r) => r.data);

// ─── News ─────────────────────────────────────────────────────────────
// Real news comes from Finnhub (called directly from the browser, no
// backend involvement) when REACT_APP_FINNHUB_KEY is set. Without a key
// we fall back to the bundled mock headlines so the page still renders.
//
// See services/finnhub.js for the client + normalizer. Provider response
// is mapped to the same shape as mocks/news.js so the UI is agnostic.
const sortByPublished = (a, b) => new Date(b.publishedAt) - new Date(a.publishedAt);

export const getNews = async ({ ticker, limit } = {}) => {
  // Try Finnhub first when a key is configured. Any failure (rate limit,
  // bad key, network) silently degrades to the mock feed.
  if (hasFinnhubKey()) {
    try {
      const rows = ticker
        ? await fetchCompanyNews(ticker)
        : await fetchMarketNews();
      rows.sort(sortByPublished);
      const out = limit ? rows.slice(0, limit) : rows;

      // Success log — confirms the live source is working and lets you
      // sanity-check the first headline in DevTools.
      const scope = ticker ? `ticker=${ticker}` : 'market';
      console.log(
        `[news] Finnhub OK (${scope}): ${out.length} headline(s)` +
          (out[0] ? ` — first: "${out[0].title}"` : '')
      );
      return out;
    } catch (err) {
      // Don't blow up the page — log and fall through to mocks.
      // err.message is shaped "Finnhub <status>: <body>" by finnhub.js,
      // which produces the required final log format:
      //   [news] Finnhub failed, falling back to mocks: Finnhub 401: ...
      console.warn(`[news] Finnhub failed, falling back to mocks: ${err.message}`);
    }
  }

  let rows = mockNews.slice();
  if (ticker) rows = rows.filter((n) => (n.tickers || []).includes(ticker));
  rows.sort(sortByPublished);
  return limit ? rows.slice(0, limit) : rows;
};

// ─── Auth ─────────────────────────────────────────────────────────────
// Real backend endpoints, never mocked. Errors from the API come back as
// { error: "NO_ACCOUNT" } etc. — we re-throw the code so AuthContext can
// translate it via the existing i18n error map.
function throwAuthError(err) {
  const code = err?.response?.data?.error;
  throw new Error(code || 'GENERIC');
}

export const apiSignUp = ({ name, email, password }) =>
  api.post('/auth/signup', { name, email, password })
     .then((r) => r.data)
     .catch(throwAuthError);

export const apiSignIn = ({ email, password }) =>
  api.post('/auth/signin', { email, password })
     .then((r) => r.data)
     .catch(throwAuthError);

export const apiFetchMe = () =>
  api.get('/auth/me')
     .then((r) => r.data)
     .catch(throwAuthError);

export default api;
