// Horizontal gauge: market price relative to fair value.
//
// The gauge itself stays LTR in both modes — financial charts
// conventionally read left-to-right (negative to positive) regardless
// of UI language. Only the surrounding labels translate.

import React from 'react';
import { formatSARPerShare, formatPercentChange } from '../../utils/format.js';
import { useLang } from '../../i18n/LanguageContext.jsx';

export default function ValuationGauge({ marketPrice, fairValue }) {
  const { t } = useLang();

  if (marketPrice == null || fairValue == null || fairValue === 0) {
    return (
      <div className="text-slate-500 dark:text-slate-400 italic text-sm">
        {t('gauge.insufficient')}
      </div>
    );
  }

  const MIN_RATIO = 0.7;
  const MAX_RATIO = 1.3;

  const ratio = marketPrice / fairValue;
  const clampedRatio = Math.max(MIN_RATIO, Math.min(MAX_RATIO, ratio));
  const positionPct = ((clampedRatio - MIN_RATIO) / (MAX_RATIO - MIN_RATIO)) * 100;
  const pctDiff = (marketPrice - fairValue) / fairValue;

  return (
    // Force LTR on the whole gauge so the bar's geometry is stable.
    <div className="my-2" dir="ltr">
      {/* Top scale labels. */}
      <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400 mb-2 font-medium">
        <span>-30%</span>
        <span>{t('gauge.fairValue')}</span>
        <span>+30%</span>
      </div>

      <div className="relative h-8 bg-slate-100 dark:bg-slate-800 rounded-lg overflow-hidden ring-1 ring-inset ring-slate-200 dark:ring-slate-700">
        <div
          className="absolute top-0 bottom-0 bg-emerald-200/70 dark:bg-emerald-900/50"
          style={{ left: '33.33%', width: '33.34%' }}
        />
        <div
          className="absolute top-0 bottom-0 w-px bg-slate-400 dark:bg-slate-500"
          style={{ left: '50%' }}
        />
        <div
          className="absolute top-0 bottom-0 w-1.5 bg-blue-600 dark:bg-blue-400 rounded-sm shadow-md"
          style={{ left: `${positionPct}%`, transform: 'translateX(-50%)' }}
          title={`Market: ${formatSARPerShare(marketPrice)} | Fair: ${formatSARPerShare(fairValue)}`}
        />
      </div>

      {/* Readout under the bar. */}
      <div className="flex justify-between text-sm mt-3 flex-wrap gap-3 text-slate-700 dark:text-slate-300">
        <span>
          <span className="text-slate-500 dark:text-slate-400">{t('gauge.market')}:</span>{' '}
          <span className="font-semibold tabular-nums">{formatSARPerShare(marketPrice)}</span>
        </span>
        <span>
          <span className="text-slate-500 dark:text-slate-400">{t('gauge.fair')}:</span>{' '}
          <span className="font-semibold tabular-nums">{formatSARPerShare(fairValue)}</span>
        </span>
        <span>
          <span className="text-slate-500 dark:text-slate-400">{t('gauge.diff')}:</span>{' '}
          <span className="font-semibold tabular-nums">{formatPercentChange(pctDiff)}</span>
        </span>
      </div>
    </div>
  );
}
