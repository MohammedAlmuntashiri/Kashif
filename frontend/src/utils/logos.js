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
//
// Domain selection rule: only include a domain whose Google S2 favicon
// returns a real icon (>=1KB usually). Domains that return the 726-byte
// "generic globe" default are deliberately omitted so the stock falls
// through to the initial avatar — a clean letter looks better than a
// fake globe pretending to be the company's logo.

export const LOGO_DOMAINS = {
  // Banks & Financial Services
  '1120': 'alrajhibank.com.sa',        // Al Rajhi Bank
  '1150': 'alinma.com',                // Alinma Bank
  '1180': 'snb.com',                   // Saudi National Bank (SNB)
  '4330': 'riyadcapital.com',          // Riyad REIT (managed by Riyad Capital)

  // Energy & Materials
  '1210': 'bci.com.sa',                // Basic Chemical Industries
  '2010': 'sabic.com',                 // SABIC
  '2020': 'agri-nutrients.com',        // SABIC Agri-Nutrients
  '2222': 'aramco.com',                // Saudi Aramco
  '2250': 'siig.com.sa',               // Saudi Industrial Investment Group
  '2382': 'adesgroup.com',             // ADES Holding
  '5110': 'se.com.sa',                 // Saudi Electricity

  // Capital Goods / Industrials
  '1212': 'astra.com.sa',              // Astra Industrial
  '2081': 'alkhorayef.com',            // Alkhorayef Water & Power

  // Consumer Staples / Food
  '2050': 'savola.com',                // Savola
  '2280': 'almarai.com',               // Almarai
  '4001': 'othaimmarkets.com',         // Al-Othaim Markets
  '6002': 'herfy.com',                 // Herfy
  '6004': 'catrion.com',               // Catrion

  // Consumer Discretionary / Retail / Services
  '1820': 'baan.sa',                   // BAAN Holding
  '1831': 'maharah.com',               // Maharah for Human Resources
  '4011': 'lazurdi.com',               // L'azurde
  '4071': 'al-arabia.com',             // Arabian Contracting Services (Al-Arabia outdoor advertising)
  '4190': 'jarir.com',                 // Jarir Marketing
  '4210': 'srmg.com',                  // Saudi Research & Media Group
  '4240': 'cenomiretail.com',          // AFG International (rebranded from Fawaz Al-Hokair → Cenomi Retail)
  '4260': 'budgetsaudi.com',           // United Intl Transportation (Budget)

  // Healthcare
  '4002': 'mouwasat.com',              // Mouwasat Medical
  '4013': 'hmg.com.sa',                // Dr. Sulaiman Al Habib

  // Real Estate
  '4020': 'alakaria.com',              // Saudi Real Estate (Alakaria)
  '4250': 'jabalomar.com.sa',          // Jabal Omar Development
  '4300': 'daralarkan.com',            // Dar Al Arkan
  '4338': 'snbcapital.com',            // Al-Ahli REIT (managed by SNB Capital)

  // Transportation
  '4030': 'bahri.sa',                  // Bahri
  '4040': 'saptco.com.sa',             // SAPTCO

  // Telecom & Tech
  '7010': 'stc.com.sa',                // stc
  '7020': 'mobily.com.sa',             // Etihad Etisalat (Mobily)
  '7030': 'sa.zain.com',               // Zain Saudi Arabia
  '7202': 'stcsolutions.com',          // Arabian Internet (Solutions by stc)

  // Insurance
  '8010': 'tawuniya.com',              // Tawuniya
  '8210': 'bupa.com',                  // Bupa Arabia

  // Domains exist but Google S2 returns the generic globe (no real favicon)
  // — kept as initial-avatar fallback rather than misleading icon:
  //   1111 Tadawul Group, 1140 Bank Albilad, 2070 SPIMACO,
  //   2320 Al-Babtain Power, 2381 Arabian Drilling, 4004 Dallah Healthcare
  //
  // No reliable domain found at all:
  //   4005 NMCC, 4061 Anaam International, 4170 Tourism (Shams)
  //
  // For any of the above, drop a PNG at frontend/public/logos/<ticker>.png
  // and the local file takes priority over this map.
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
