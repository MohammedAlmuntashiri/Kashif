// Format helpers for displaying financial values in the UI.
//
// All exports return the string "—" when given null/undefined so we
// can drop them directly into JSX without conditional checks at every
// call site. The em-dash convention matches what most financial
// publications use for "data not available".

const DASH = '—';

// Big-number SAR with auto-scaling.
// Picks the smallest suffix that keeps the integer part ≤ 3 digits.
//   1.23e12 → "SAR 1.23T"
//   4.56e9  → "SAR 4.56B"
//   7.89e6  → "SAR 7.89M"
//   12 345  → "SAR 12.35K"
//   250     → "SAR 250.00"
export function formatSAR(value) {
  if (value === null || value === undefined) return DASH;
  const abs = Math.abs(value);
  if (abs >= 1e12) return `SAR ${(value / 1e12).toFixed(2)}T`;
  if (abs >= 1e9)  return `SAR ${(value / 1e9).toFixed(2)}B`;
  if (abs >= 1e6)  return `SAR ${(value / 1e6).toFixed(2)}M`;
  if (abs >= 1e3)  return `SAR ${(value / 1e3).toFixed(2)}K`;
  return `SAR ${value.toFixed(2)}`;
}

// Per-share SAR amount (EPS, DPS, fair value, market price).
// Always 2 decimals — these are typically single- or double-digit numbers
// where K/M/B scaling would be confusing.
//   28.5    → "SAR 28.50"
//   0.12345 → "SAR 0.12"
export function formatSARPerShare(value) {
  if (value === null || value === undefined) return DASH;
  return `SAR ${value.toFixed(2)}`;
}

// Share counts — no currency prefix, but auto-scaled to B/M.
//   2.4e9 → "2.40B"
//   5e8   → "500.00M"
export function formatShares(value) {
  if (value === null || value === undefined) return DASH;
  const abs = Math.abs(value);
  if (abs >= 1e9) return `${(value / 1e9).toFixed(2)}B`;
  if (abs >= 1e6) return `${(value / 1e6).toFixed(2)}M`;
  return value.toFixed(0);
}

// Signed percent change. Input is a decimal ratio, NOT already-multiplied.
//   0.0825 → "+8.3%"
//  -0.05   → "-5.0%"
export function formatPercentChange(value) {
  if (value === null || value === undefined) return DASH;
  const pct = value * 100;
  const sign = pct >= 0 ? '+' : '';
  return `${sign}${pct.toFixed(1)}%`;
}
