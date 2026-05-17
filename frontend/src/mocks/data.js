// Mock data for the frontend — used when USE_MOCKS in api.js is true.
//
// Why: the DB on this machine is empty (data lives on the accuracy
// team's machine). This file lets us build/iterate on the UI without
// waiting for the real DB.
//
// Shape parity: every export here matches the EXACT shape of its
// corresponding backend endpoint, so flipping USE_MOCKS off requires
// zero changes anywhere else in the frontend.
//
// 8 stocks across 7 sectors — enough variety to exercise every UI
// component (different sectors, different valuation statuses, one
// stock with no valuation, etc.).

// ─── Helper: build a financials array spanning 4 years ─────────────────
// Each yearly entry is constructed by multiplying the 2024 baseline by
// a small per-year delta so the table shows realistic trends without
// us having to type 40 numbers per stock.
function buildFinancials(base) {
  // deltas indexed by year offset (0 = 2024, 1 = 2023, ...)
  const deltas = [1.00, 0.92, 0.78, 0.85];
  const years  = [2024, 2023, 2022, 2021];

  return years.map((year, i) => {
    const k = deltas[i];
    return {
      period:               `${year}-annual`,
      revenue:              round(base.revenue              * k),
      net_income:           round(base.net_income           * k),
      eps:                  round2(base.eps                 * k),
      total_assets:         round(base.total_assets         * k),
      total_borrowings:     round(base.total_borrowings     * k),
      shareholders_equity:  round(base.shareholders_equity  * k),
      cash_and_equivalents: round(base.cash_and_equivalents * k),
      free_cash_flow:       round(base.free_cash_flow       * k),
      dividends_per_share:  round2(base.dividends_per_share * k),
      // Shares outstanding stays roughly constant across years (no buyback drama).
      shares_outstanding:   base.shares_outstanding,
    };
  });
}

const round  = (n) => Math.round(n);
const round2 = (n) => Math.round(n * 100) / 100;

// ─── Stock summaries (matches GET /api/stocks/) ───────────────────────
// Just the lightweight fields the list endpoint returns.
export const stocks = [
  {
    symbol: "2222", name_en: "Saudi Aramco",        name_ar: "أرامكو السعودية",
    sector: "Energy",         market_price: 28.50,
    latest_period: "2024-annual", revenue: 1.85e12, net_income: 4.54e11, eps: 1.88,
  },
  {
    symbol: "1120", name_en: "Al Rajhi Bank",       name_ar: "مصرف الراجحي",
    sector: "Banks",          market_price: 92.30,
    latest_period: "2024-annual", revenue: 8.5e10,  net_income: 1.80e10, eps: 4.50,
  },
  {
    symbol: "1180", name_en: "Saudi National Bank", name_ar: "البنك الأهلي السعودي",
    sector: "Banks",          market_price: 38.20,
    latest_period: "2024-annual", revenue: 6.2e10,  net_income: 2.10e10, eps: 3.50,
  },
  {
    symbol: "2010", name_en: "SABIC",               name_ar: "سابك",
    sector: "Materials",      market_price: 75.40,
    latest_period: "2024-annual", revenue: 1.45e11, net_income: 5.80e9,  eps: 1.93,
  },
  {
    symbol: "7010", name_en: "stc",                 name_ar: "الاتصالات السعودية",
    sector: "Telecom",        market_price: 39.80,
    latest_period: "2024-annual", revenue: 7.50e10, net_income: 1.20e10, eps: 2.40,
  },
  {
    symbol: "2280", name_en: "Almarai",             name_ar: "المراعي",
    sector: "Food",           market_price: 53.20,
    latest_period: "2024-annual", revenue: 1.95e10, net_income: 1.75e9,  eps: 1.75,
  },
  {
    symbol: "4030", name_en: "Bahri",               name_ar: "البحري",
    sector: "Transportation", market_price: 32.10,
    latest_period: "2024-annual", revenue: 9.20e9,  net_income: 1.30e9,  eps: 3.30,
  },
  {
    symbol: "4338", name_en: "AlAhli REIT",         name_ar: "الأهلي ريت",
    sector: "Real Estate",    market_price: 9.45,
    latest_period: "2024-annual", revenue: 1.20e8,  net_income: 6.50e7,  eps: 0.65,
  },
];

// ─── Stock details (matches GET /api/stocks/<ticker>) ─────────────────
// Keyed by ticker so getStock(ticker) is an O(1) lookup.
// Each value contains full financials history + a valuation row.
// 4338 AlAhli REIT intentionally has valuation=null so the
// StockDetailPage's "No valuation computed yet" branch is exercised.
export const stockDetails = {
  "2222": {
    symbol: "2222", name_en: "Saudi Aramco", name_ar: "أرامكو السعودية",
    sector: "Energy", sector_id: 1, market_price: 28.50,
    financials: buildFinancials({
      revenue: 1.85e12, net_income: 4.54e11, eps: 1.88,
      total_assets: 2.45e12, total_borrowings: 2.96e11,
      shareholders_equity: 9.70e11, cash_and_equivalents: 1.64e11,
      free_cash_flow: 3.45e11, dividends_per_share: 1.74,
      shares_outstanding: 2.416e11,
    }),
    valuation: {
      dcf_value: 30.50, pe_value: 32.00, pb_value: 27.50,
      fair_value: 30.20, market_price: 28.50,
      status: "undervalued",
      calculated_at: "2026-05-15T10:30:00",
    },
  },

  "1120": {
    symbol: "1120", name_en: "Al Rajhi Bank", name_ar: "مصرف الراجحي",
    sector: "Banks", sector_id: 2, market_price: 92.30,
    financials: buildFinancials({
      revenue: 8.5e10, net_income: 1.80e10, eps: 4.50,
      total_assets: 8.10e11, total_borrowings: 6.50e10,
      shareholders_equity: 9.50e10, cash_and_equivalents: 4.20e10,
      free_cash_flow: 1.50e10, dividends_per_share: 3.20,
      shares_outstanding: 4.00e9,
    }),
    valuation: {
      dcf_value: 88.00, pe_value: 94.00, pb_value: 90.50,
      fair_value: 91.00, market_price: 92.30,
      status: "fair",
      calculated_at: "2026-05-15T10:30:00",
    },
  },

  "1180": {
    symbol: "1180", name_en: "Saudi National Bank", name_ar: "البنك الأهلي السعودي",
    sector: "Banks", sector_id: 2, market_price: 38.20,
    financials: buildFinancials({
      revenue: 6.2e10, net_income: 2.10e10, eps: 3.50,
      total_assets: 1.02e12, total_borrowings: 8.20e10,
      shareholders_equity: 1.65e11, cash_and_equivalents: 7.50e10,
      free_cash_flow: 1.80e10, dividends_per_share: 1.95,
      shares_outstanding: 6.00e9,
    }),
    valuation: {
      dcf_value: 35.00, pe_value: 40.00, pb_value: 33.50,
      fair_value: 35.80, market_price: 38.20,
      status: "overvalued",
      calculated_at: "2026-05-15T10:30:00",
    },
  },

  "2010": {
    symbol: "2010", name_en: "SABIC", name_ar: "سابك",
    sector: "Materials", sector_id: 3, market_price: 75.40,
    financials: buildFinancials({
      revenue: 1.45e11, net_income: 5.80e9, eps: 1.93,
      total_assets: 3.10e11, total_borrowings: 6.20e10,
      shareholders_equity: 1.45e11, cash_and_equivalents: 4.10e10,
      free_cash_flow: 1.10e10, dividends_per_share: 2.00,
      shares_outstanding: 3.00e9,
    }),
    valuation: {
      dcf_value: 72.00, pe_value: 78.00, pb_value: 74.50,
      fair_value: 74.80, market_price: 75.40,
      status: "fair",
      calculated_at: "2026-05-15T10:30:00",
    },
  },

  "7010": {
    symbol: "7010", name_en: "stc", name_ar: "الاتصالات السعودية",
    sector: "Telecom", sector_id: 4, market_price: 39.80,
    financials: buildFinancials({
      revenue: 7.50e10, net_income: 1.20e10, eps: 2.40,
      total_assets: 1.30e11, total_borrowings: 2.50e10,
      shareholders_equity: 6.50e10, cash_and_equivalents: 1.80e10,
      free_cash_flow: 1.50e10, dividends_per_share: 1.80,
      shares_outstanding: 5.00e9,
    }),
    valuation: {
      dcf_value: 42.00, pe_value: 44.50, pb_value: 38.00,
      fair_value: 42.10, market_price: 39.80,
      status: "undervalued",
      calculated_at: "2026-05-15T10:30:00",
    },
  },

  "2280": {
    symbol: "2280", name_en: "Almarai", name_ar: "المراعي",
    sector: "Food", sector_id: 5, market_price: 53.20,
    financials: buildFinancials({
      revenue: 1.95e10, net_income: 1.75e9, eps: 1.75,
      total_assets: 3.40e10, total_borrowings: 1.10e10,
      shareholders_equity: 1.45e10, cash_and_equivalents: 1.20e9,
      free_cash_flow: 2.10e9, dividends_per_share: 1.20,
      shares_outstanding: 1.00e9,
    }),
    valuation: {
      dcf_value: 50.00, pe_value: 55.00, pb_value: 48.00,
      fair_value: 51.20, market_price: 53.20,
      status: "fair",
      calculated_at: "2026-05-15T10:30:00",
    },
  },

  "4030": {
    symbol: "4030", name_en: "Bahri", name_ar: "البحري",
    sector: "Transportation", sector_id: 6, market_price: 32.10,
    financials: buildFinancials({
      revenue: 9.20e9, net_income: 1.30e9, eps: 3.30,
      total_assets: 2.50e10, total_borrowings: 8.50e9,
      shareholders_equity: 1.20e10, cash_and_equivalents: 1.50e9,
      free_cash_flow: 1.40e9, dividends_per_share: 1.50,
      shares_outstanding: 3.94e8,
    }),
    valuation: {
      dcf_value: 36.00, pe_value: 38.00, pb_value: 30.50,
      fair_value: 35.50, market_price: 32.10,
      status: "undervalued",
      calculated_at: "2026-05-15T10:30:00",
    },
  },

  "4338": {
    symbol: "4338", name_en: "AlAhli REIT", name_ar: "الأهلي ريت",
    sector: "Real Estate", sector_id: 7, market_price: 9.45,
    financials: buildFinancials({
      revenue: 1.20e8, net_income: 6.50e7, eps: 0.65,
      total_assets: 1.50e9, total_borrowings: 6.50e8,
      shareholders_equity: 8.50e8, cash_and_equivalents: 4.50e7,
      free_cash_flow: 5.00e7, dividends_per_share: 0.80,
      shares_outstanding: 1.00e8,
    }),
    // Intentionally null — exercises the "no valuation" UI branch.
    valuation: null,
  },
};

// ─── Sectors (matches GET /api/sectors/) ──────────────────────────────
// Stock counts reflect the mock list above. Weights are realistic
// industry conventions: banks lean on P/B, energy on DCF, etc.
export const sectors = [
  { id: 1, name_en: "Energy",         name_ar: "الطاقة",        dcf_weight: 0.50, pe_weight: 0.30, pb_weight: 0.20, stock_count: 1 },
  { id: 2, name_en: "Banks",          name_ar: "البنوك",        dcf_weight: 0.20, pe_weight: 0.40, pb_weight: 0.40, stock_count: 2 },
  { id: 3, name_en: "Materials",      name_ar: "المواد الأساسية", dcf_weight: 0.40, pe_weight: 0.35, pb_weight: 0.25, stock_count: 1 },
  { id: 4, name_en: "Telecom",        name_ar: "الاتصالات",     dcf_weight: 0.45, pe_weight: 0.35, pb_weight: 0.20, stock_count: 1 },
  { id: 5, name_en: "Food",           name_ar: "الغذاء",        dcf_weight: 0.40, pe_weight: 0.40, pb_weight: 0.20, stock_count: 1 },
  { id: 6, name_en: "Transportation", name_ar: "النقل",         dcf_weight: 0.40, pe_weight: 0.40, pb_weight: 0.20, stock_count: 1 },
  { id: 7, name_en: "Real Estate",    name_ar: "العقارات",       dcf_weight: 0.30, pe_weight: 0.30, pb_weight: 0.40, stock_count: 1 },
];

// ─── Comparisons (matches GET /api/comparisons/) ──────────────────────
// One row per stock with the 7 ratios + sector average + rank.
// Ranks within a sector are 1..peer_count (1 = best).
export const comparisons = [
  // Energy (1 stock — ranks all 1)
  {
    symbol: "2222", name_en: "Saudi Aramco", sector: "Energy", peer_count: 1,
    pe_ratio: 15.2, sector_avg_pe: 15.2, pe_rank: 1,
    pb_ratio: 1.85, sector_avg_pb: 1.85, pb_rank: 1,
    roe: 24.5,      sector_avg_roe: 24.5, roe_rank: 1,
    roa: 12.3,      sector_avg_roa: 12.3, roa_rank: 1,
    debt_to_equity: 0.30, sector_avg_debt_to_equity: 0.30, debt_to_equity_rank: 1,
    profit_margin:  24.5, sector_avg_profit_margin:  24.5, profit_margin_rank:  1,
    dividend_yield:  6.10, sector_avg_dividend_yield: 6.10, dividend_yield_rank: 1,
    calculated_at: "2026-05-15T10:30:00",
  },
  // Banks (2 stocks)
  {
    symbol: "1120", name_en: "Al Rajhi Bank", sector: "Banks", peer_count: 2,
    pe_ratio: 20.5, sector_avg_pe: 16.8, pe_rank: 2,
    pb_ratio: 3.90, sector_avg_pb: 2.65, pb_rank: 2,
    roe: 19.0,      sector_avg_roe: 17.4, roe_rank: 1,
    roa: 2.22,      sector_avg_roa: 2.16, roa_rank: 1,
    debt_to_equity: 0.68, sector_avg_debt_to_equity: 0.59, debt_to_equity_rank: 2,
    profit_margin:  21.2, sector_avg_profit_margin:  27.5, profit_margin_rank:  2,
    dividend_yield:  3.47, sector_avg_dividend_yield: 3.29, dividend_yield_rank: 1,
    calculated_at: "2026-05-15T10:30:00",
  },
  {
    symbol: "1180", name_en: "Saudi National Bank", sector: "Banks", peer_count: 2,
    pe_ratio: 10.9, sector_avg_pe: 16.8, pe_rank: 1,
    pb_ratio: 1.39, sector_avg_pb: 2.65, pb_rank: 1,
    roe: 12.7,      sector_avg_roe: 17.4, roe_rank: 2,
    roa: 2.06,      sector_avg_roa: 2.16, roa_rank: 2,
    debt_to_equity: 0.50, sector_avg_debt_to_equity: 0.59, debt_to_equity_rank: 1,
    profit_margin:  33.9, sector_avg_profit_margin:  27.5, profit_margin_rank:  1,
    dividend_yield:  5.10, sector_avg_dividend_yield: 3.29, dividend_yield_rank: 2,
    calculated_at: "2026-05-15T10:30:00",
  },
  // Materials
  {
    symbol: "2010", name_en: "SABIC", sector: "Materials", peer_count: 1,
    pe_ratio: 39.1, sector_avg_pe: 39.1, pe_rank: 1,
    pb_ratio: 1.56, sector_avg_pb: 1.56, pb_rank: 1,
    roe: 4.0,       sector_avg_roe: 4.0,  roe_rank: 1,
    roa: 1.87,      sector_avg_roa: 1.87, roa_rank: 1,
    debt_to_equity: 0.43, sector_avg_debt_to_equity: 0.43, debt_to_equity_rank: 1,
    profit_margin:  4.0,  sector_avg_profit_margin:  4.0,  profit_margin_rank:  1,
    dividend_yield: 2.65, sector_avg_dividend_yield: 2.65, dividend_yield_rank: 1,
    calculated_at: "2026-05-15T10:30:00",
  },
  // Telecom
  {
    symbol: "7010", name_en: "stc", sector: "Telecom", peer_count: 1,
    pe_ratio: 16.6, sector_avg_pe: 16.6, pe_rank: 1,
    pb_ratio: 3.06, sector_avg_pb: 3.06, pb_rank: 1,
    roe: 18.5,      sector_avg_roe: 18.5, roe_rank: 1,
    roa: 9.23,      sector_avg_roa: 9.23, roa_rank: 1,
    debt_to_equity: 0.38, sector_avg_debt_to_equity: 0.38, debt_to_equity_rank: 1,
    profit_margin:  16.0, sector_avg_profit_margin:  16.0, profit_margin_rank:  1,
    dividend_yield:  4.52, sector_avg_dividend_yield: 4.52, dividend_yield_rank: 1,
    calculated_at: "2026-05-15T10:30:00",
  },
  // Food
  {
    symbol: "2280", name_en: "Almarai", sector: "Food", peer_count: 1,
    pe_ratio: 30.4, sector_avg_pe: 30.4, pe_rank: 1,
    pb_ratio: 3.67, sector_avg_pb: 3.67, pb_rank: 1,
    roe: 12.1,      sector_avg_roe: 12.1, roe_rank: 1,
    roa: 5.15,      sector_avg_roa: 5.15, roa_rank: 1,
    debt_to_equity: 0.76, sector_avg_debt_to_equity: 0.76, debt_to_equity_rank: 1,
    profit_margin:  9.0,  sector_avg_profit_margin:  9.0,  profit_margin_rank:  1,
    dividend_yield: 2.26, sector_avg_dividend_yield: 2.26, dividend_yield_rank: 1,
    calculated_at: "2026-05-15T10:30:00",
  },
  // Transportation
  {
    symbol: "4030", name_en: "Bahri", sector: "Transportation", peer_count: 1,
    pe_ratio:  9.7, sector_avg_pe:  9.7, pe_rank: 1,
    pb_ratio: 1.05, sector_avg_pb: 1.05, pb_rank: 1,
    roe: 10.8,      sector_avg_roe: 10.8, roe_rank: 1,
    roa: 5.20,      sector_avg_roa: 5.20, roa_rank: 1,
    debt_to_equity: 0.71, sector_avg_debt_to_equity: 0.71, debt_to_equity_rank: 1,
    profit_margin:  14.1, sector_avg_profit_margin:  14.1, profit_margin_rank:  1,
    dividend_yield:  4.67, sector_avg_dividend_yield: 4.67, dividend_yield_rank: 1,
    calculated_at: "2026-05-15T10:30:00",
  },
  // Real Estate
  {
    symbol: "4338", name_en: "AlAhli REIT", sector: "Real Estate", peer_count: 1,
    pe_ratio: 14.5, sector_avg_pe: 14.5, pe_rank: 1,
    pb_ratio: 1.11, sector_avg_pb: 1.11, pb_rank: 1,
    roe: 7.6,       sector_avg_roe: 7.6,  roe_rank: 1,
    roa: 4.33,      sector_avg_roa: 4.33, roa_rank: 1,
    debt_to_equity: 0.76, sector_avg_debt_to_equity: 0.76, debt_to_equity_rank: 1,
    profit_margin:  54.2, sector_avg_profit_margin:  54.2, profit_margin_rank:  1,
    dividend_yield:  8.47, sector_avg_dividend_yield: 8.47, dividend_yield_rank: 1,
    calculated_at: "2026-05-15T10:30:00",
  },
];

// ─── Valuations (matches GET /api/valuations/<ticker>) ────────────────
// Same data as stockDetails[].valuation but in the slightly different
// shape that the valuations endpoint returns (adds symbol/name/source).
export const valuations = Object.fromEntries(
  Object.entries(stockDetails).map(([ticker, d]) => [
    ticker,
    d.valuation
      ? {
          symbol:        d.symbol,
          name_en:       d.name_en,
          market_price:  d.market_price,
          dcf_value:     d.valuation.dcf_value,
          pe_value:      d.valuation.pe_value,
          pb_value:      d.valuation.pb_value,
          fair_value:    d.valuation.fair_value,
          status:        d.valuation.status,
          calculated_at: d.valuation.calculated_at,
          source:        "mock",
        }
      : null,
  ])
);
