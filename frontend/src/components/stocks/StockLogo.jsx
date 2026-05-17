// Company logo for a stock — tries multiple sources before falling back
// to a colored-initial avatar.
//
// Source chain (see utils/logos.js for URL formats):
//   1. Local PNG at public/logos/<ticker>.png
//   2. Google S2 favicon for the company domain
//   3. Initial avatar (always succeeds)
//
// We advance to the next source on <img> error, so a missing local file
// just transparently falls through to the favicon.

import React, { useEffect, useState } from 'react';
import {
  localLogoPath,
  remoteLogoUrl,
  colorForTicker,
} from '../../utils/logos.js';

const SIZE = {
  sm: 'w-8 h-8 text-sm',
  md: 'w-12 h-12 text-base',
  lg: 'w-16 h-16 text-2xl',
};

export default function StockLogo({ symbol, name, size = 'md' }) {
  // Build the source chain once per ticker. Filter out null sources
  // (e.g. tickers without a known domain).
  const sources = [localLogoPath(symbol), remoteLogoUrl(symbol)].filter(Boolean);

  // Index into `sources`; when it goes past the end we render the initial.
  const [idx, setIdx] = useState(0);

  // Reset whenever the ticker changes (e.g. navigating between stocks).
  useEffect(() => { setIdx(0); }, [symbol]);

  const dim = SIZE[size] || SIZE.md;
  const initial = (name || symbol || '?').trim().charAt(0).toUpperCase();

  if (idx < sources.length) {
    return (
      <div
        className={`${dim} rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex items-center justify-center overflow-hidden shrink-0`}
      >
        <img
          key={sources[idx]}                // remount on src change
          src={sources[idx]}
          alt={`${name || symbol} logo`}
          onError={() => setIdx((i) => i + 1)}
          className="w-full h-full object-contain p-1"
          loading="lazy"
        />
      </div>
    );
  }

  // Initial-avatar final fallback.
  return (
    <div
      className={`${dim} rounded-lg ${colorForTicker(symbol)} text-white font-bold flex items-center justify-center shrink-0`}
      aria-label={`${name || symbol} logo placeholder`}
    >
      {initial}
    </div>
  );
}
