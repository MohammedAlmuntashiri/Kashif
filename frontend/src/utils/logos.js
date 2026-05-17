// Logo resolution for a stock ticker.
//
// Source priority (StockLogo.jsx tries them in this order):
//   1. /logos/<ticker>.png  — drop a file in frontend/public/logos/ to override.
//   2. Google S2 favicon for the company's known domain — always returns
//      something for popular sites; 128 px is enough for our small avatars.
//   3. Colored initial avatar (in-component fallback when both above fail).
//
// To add a new ticker, just append to LOGO_DOMAINS. To override with a
// crisp hand-cropped PNG, put it at frontend/public/logos/<ticker>.png.

export const LOGO_DOMAINS = {
  '2222': 'aramco.com',           // Saudi Aramco
  '1120': 'alrajhibank.com.sa',   // Al Rajhi Bank
  '1180': 'alahli.com',           // Saudi National Bank
  '2010': 'sabic.com',            // SABIC
  '7010': 'stc.com.sa',           // stc
  '2280': 'almarai.com',          // Almarai
  '4030': 'bahri.sa',             // Bahri
  // '4338' AlAhli REIT — no public domain logo, falls back to initial.
};

// Local file under public/ — same path served by the dev/prod server.
export const localLogoPath = (ticker) => `/logos/${ticker}.png`;

// Remote favicon — Google's S2 endpoint. Returns up to 128 px. Works
// for almost every public domain because Google's crawler has it.
export const remoteLogoUrl = (ticker) => {
  const domain = LOGO_DOMAINS[ticker];
  return domain
    ? `https://www.google.com/s2/favicons?domain=${domain}&sz=128`
    : null;
};

// Deterministic background color for the initial-fallback avatar.
const PALETTE = [
  'bg-blue-600',  'bg-emerald-600', 'bg-amber-600', 'bg-rose-600',
  'bg-violet-600','bg-cyan-600',    'bg-pink-600',  'bg-teal-600',
];
export function colorForTicker(ticker) {
  const s = String(ticker || '');
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return PALETTE[h % PALETTE.length];
}
