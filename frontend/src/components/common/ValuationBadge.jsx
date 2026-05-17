// Colored pill showing valuation status, with a matching trend icon.

import React from 'react';
import { TrendingUp, Minus, TrendingDown, HelpCircle } from 'lucide-react';
import { useLang } from '../../i18n/LanguageContext.jsx';

const STYLES = {
  undervalued: 'bg-emerald-100 text-emerald-800 ring-emerald-300 ' +
               'dark:bg-emerald-900/40 dark:text-emerald-300 dark:ring-emerald-700/50',
  fair:        'bg-amber-100 text-amber-800 ring-amber-300 ' +
               'dark:bg-amber-900/40 dark:text-amber-300 dark:ring-amber-700/50',
  overvalued:  'bg-rose-100 text-rose-800 ring-rose-300 ' +
               'dark:bg-rose-900/40 dark:text-rose-300 dark:ring-rose-700/50',
};

const FALLBACK =
  'bg-slate-100 text-slate-600 ring-slate-300 ' +
  'dark:bg-slate-800 dark:text-slate-400 dark:ring-slate-700';

const ICONS = {
  undervalued: TrendingUp,
  fair:        Minus,
  overvalued:  TrendingDown,
};

// Map backend status string → translation key.
const LABEL_KEYS = {
  undervalued: 'badge.undervalued',
  fair:        'badge.fair',
  overvalued:  'badge.overvalued',
};

export default function ValuationBadge({ status }) {
  const { t } = useLang();
  const className = STYLES[status] || FALLBACK;
  const label     = LABEL_KEYS[status] ? t(LABEL_KEYS[status]) : t('badge.unknown');
  const Icon      = ICONS[status] || HelpCircle;

  return (
    <span
      className={
        `inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold tracking-wide ring-1 ring-inset ${className}`
      }
    >
      <Icon size={12} strokeWidth={2.5} />
      {label}
    </span>
  );
}
