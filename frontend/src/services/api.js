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

// ⚠️  Flip this to false when the real DB is populated.  ⚠️
const USE_MOCKS = true;

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,                     // 30s — PDF upload + OCR can take a while
  headers: { 'Content-Type': 'application/json' },
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
  }).then((r) => r.data);
};

export default api;
