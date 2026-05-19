// Table of the 10 key financial values across all available periods.
// Metric labels are translated; numeric values render as-is (always
// Latin digits — Arabic finance UIs conventionally use them).

import React from 'react';
import {
  formatSAR,
  formatSARPerShare,
  formatShares,
} from '../../utils/format.js';
import { useLang } from '../../i18n/LanguageContext.jsx';

// Each metric's key here matches both the backend field name AND the
// translation key (under 'fin.<key>'). One source of truth.
const FIELDS = [
  { key: 'revenue',              fmt: formatSAR        },
  { key: 'net_income',           fmt: formatSAR        },
  { key: 'eps',                  fmt: formatSARPerShare },
  { key: 'total_assets',         fmt: formatSAR        },
  { key: 'total_borrowings',     fmt: formatSAR        },
  { key: 'shareholders_equity',  fmt: formatSAR        },
  { key: 'cash_and_equivalents', fmt: formatSAR        },
  { key: 'free_cash_flow',       fmt: formatSAR        },
  { key: 'dividends_per_share',  fmt: formatSARPerShare },
  { key: 'shares_outstanding',   fmt: formatShares     },
];

export default function FinancialTable({ financials }) {
  const { t } = useLang();

  if (!financials || financials.length === 0) {
    return (
      <div className="text-slate-500 dark:text-slate-400 italic text-sm">
        {t('fin.empty')}
      </div>
    );
  }

  const periods = financials.map((fd) => fd.period);

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 dark:border-slate-700">
            <th className="text-start py-2.5 px-3 font-semibold text-slate-600 dark:text-slate-400 text-xs uppercase tracking-wide">
              {t('fin.metric')}
            </th>
            {periods.map((p) => (
              <th
                key={p}
                // Physical right + dir="ltr" so period labels and the numeric
                // cells below them line up identically in both LTR and RTL.
                className="text-right py-2.5 px-3 font-semibold text-slate-600 dark:text-slate-400 text-xs uppercase tracking-wide whitespace-nowrap"
                dir="ltr"
              >
                {p}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
          {FIELDS.map(({ key, fmt }) => (
            <tr key={key} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
              <td className="py-2.5 px-3 font-medium text-slate-700 dark:text-slate-300">
                {t(`fin.${key}`)}
              </td>
              {financials.map((fd) => (
                <td
                  key={fd.period}
                  className="py-2.5 px-3 text-right tabular-nums text-slate-900 dark:text-slate-100 whitespace-nowrap"
                  dir="ltr"
                >
                  {fmt(fd[key])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
