// Clickable summary card for a single stock — used in the HomePage grid.
//
// Locale behavior:
//   - In English mode: shows English name prominently, Arabic name muted.
//   - In Arabic mode:  shows Arabic name prominently, English name muted.
//   - Ticker stays in Latin digits in both modes (forced dir="ltr").

import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { formatSAR, formatSARPerShare } from '../../utils/format.js';
import { useLang } from '../../i18n/LanguageContext.jsx';
import StockLogo from './StockLogo.jsx';
import Sparkline, { deltaForTicker } from './Sparkline.jsx';

const MotionLink = motion(Link);

export default function StockCard({ stock }) {
  const { t, tSector, lang } = useLang();
  const {
    symbol,
    name_en,
    name_ar,
    sector,
    market_price,
    latest_period,
    revenue,
    eps,
  } = stock;

  // Pick which name is the headline based on UI language.
  const primaryName    = lang === 'ar' ? name_ar : name_en;
  const secondaryName  = lang === 'ar' ? name_en : name_ar;
  const secondaryDir   = lang === 'ar' ? 'ltr' : 'rtl';

  return (
    <MotionLink
      to={`/stock/${symbol}`}
      initial={{ opacity: 0, y: 12 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '0px 0px -10% 0px' }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      whileHover={{ y: -4 }}
      className="block bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 hover:shadow-lg dark:hover:shadow-brand-500/10 hover:border-brand-400 dark:hover:border-brand-500 transition-[box-shadow,border-color]"
    >
      {/* Header row: logo + ticker + sector pill */}
      <div className="flex items-start justify-between gap-2 mb-3">
        <div className="flex items-center gap-2.5 min-w-0">
          <StockLogo symbol={symbol} name={name_en} size="md" />
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400 tracking-tight tabular-nums" dir="ltr">
            {symbol}
          </div>
        </div>
        <span
          className="text-xs bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-2.5 py-1 rounded-full font-medium max-w-[7.5rem] truncate shrink-0"
          title={tSector(sector)}
        >
          {tSector(sector)}
        </span>
      </div>

      {/* Stock names: primary (current language) + secondary (the other). */}
      <div className="font-semibold text-slate-900 dark:text-slate-100 leading-tight">
        {primaryName}
      </div>
      <div className="text-sm text-slate-500 dark:text-slate-400 leading-tight mb-4" dir={secondaryDir}>
        {secondaryName}
      </div>

      {/* Headline price + 30-day sparkline (deterministic mock until we
          have a real OHLC endpoint — see Sparkline.jsx). */}
      {(() => {
        const d = deltaForTicker(symbol, market_price || 100);
        const deltaColor = d.up
          ? 'text-emerald-600 dark:text-emerald-400'
          : 'text-rose-600 dark:text-rose-400';
        return (
          <div className="mb-3">
            <div className="flex items-end justify-between gap-3 mb-2">
              <div>
                <div className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wide font-medium">
                  {t('stock.marketPrice')}
                </div>
                <div className="text-2xl font-bold text-slate-900 dark:text-slate-100 tabular-nums" dir="ltr">
                  {formatSARPerShare(market_price)}
                </div>
              </div>
              <div className={`text-xs font-bold tabular-nums ${deltaColor}`} dir="ltr">
                {d.up ? '▲' : '▼'} {Math.abs(d.pct).toFixed(2)}%
              </div>
            </div>
            <Sparkline ticker={symbol} anchor={market_price || 100} />
          </div>
        );
      })()}

      {/* Snapshot row */}
      <div className="grid grid-cols-3 gap-2 text-xs pt-3 border-t border-slate-100 dark:border-slate-800">
        <div>
          <div className="text-slate-500 dark:text-slate-400">{t('card.period')}</div>
          <div className="font-semibold text-slate-700 dark:text-slate-200 tabular-nums" dir="ltr">{latest_period || '—'}</div>
        </div>
        <div>
          <div className="text-slate-500 dark:text-slate-400">{t('card.eps')}</div>
          <div className="font-semibold text-slate-700 dark:text-slate-200 tabular-nums" dir="ltr">{formatSARPerShare(eps)}</div>
        </div>
        <div>
          <div className="text-slate-500 dark:text-slate-400">{t('card.revenue')}</div>
          <div className="font-semibold text-slate-700 dark:text-slate-200 tabular-nums" dir="ltr">{formatSAR(revenue)}</div>
        </div>
      </div>
    </MotionLink>
  );
}
