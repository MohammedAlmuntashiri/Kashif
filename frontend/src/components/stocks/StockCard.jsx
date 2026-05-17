// Clickable summary card for a single stock — used in the HomePage grid.
//
// Locale behavior:
//   - In English mode: shows English name prominently, Arabic name muted.
//   - In Arabic mode:  shows Arabic name prominently, English name muted.
//   - Ticker stays in Latin digits in both modes (forced dir="ltr").

import React from 'react';
import { Link } from 'react-router-dom';
import { formatSAR, formatSARPerShare } from '../../utils/format.js';
import { useLang } from '../../i18n/LanguageContext.jsx';

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
    <Link
      to={`/stock/${symbol}`}
      className="block bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 hover:shadow-lg dark:hover:shadow-blue-500/10 hover:border-blue-400 dark:hover:border-blue-500 hover:-translate-y-0.5 transition-all"
    >
      {/* Header row: ticker + sector pill */}
      <div className="flex items-start justify-between gap-2 mb-3">
        <div className="text-2xl font-bold text-blue-600 dark:text-blue-400 tracking-tight tabular-nums" dir="ltr">
          {symbol}
        </div>
        <span className="text-xs bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-2.5 py-1 rounded-full whitespace-nowrap font-medium">
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

      {/* Headline price */}
      <div className="mb-3">
        <div className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wide font-medium">
          {t('stock.marketPrice')}
        </div>
        <div className="text-2xl font-bold text-slate-900 dark:text-slate-100 tabular-nums" dir="ltr">
          {formatSARPerShare(market_price)}
        </div>
      </div>

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
    </Link>
  );
}
