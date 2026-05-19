// Sortable peer-comparison table.

import React, { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useLang } from '../../i18n/LanguageContext.jsx';

const fmtNum = (decimals) => (v) =>
  v === null || v === undefined ? '—' : v.toFixed(decimals);

// Column config. labelKey is a translation key — fetched at render time
// via t(). Ratio names (P/E, ROE %, etc.) are universal across languages
// in finance and aren't translated.
const COLUMNS = [
  { key: 'symbol',         labelKey: 'cmp.col.ticker', fmt: (v) => v,   rankKey: null,                  avgKey: null },
  { key: 'name',           labelKey: 'cmp.col.name',   fmt: (v) => v,   rankKey: null,                  avgKey: null },
  { key: 'sector',         labelKey: 'cmp.col.sector', fmt: (v) => v,   rankKey: null,                  avgKey: null, isSector: true },
  { key: 'pe_ratio',       label: 'P/E',               fmt: fmtNum(2),  rankKey: 'pe_rank',             avgKey: 'sector_avg_pe' },
  { key: 'pb_ratio',       label: 'P/B',               fmt: fmtNum(2),  rankKey: 'pb_rank',             avgKey: 'sector_avg_pb' },
  { key: 'roe',            label: 'ROE %',             fmt: fmtNum(1),  rankKey: 'roe_rank',            avgKey: 'sector_avg_roe' },
  { key: 'roa',            label: 'ROA %',             fmt: fmtNum(2),  rankKey: 'roa_rank',            avgKey: 'sector_avg_roa' },
  { key: 'debt_to_equity', label: 'D/E',               fmt: fmtNum(2),  rankKey: 'debt_to_equity_rank', avgKey: 'sector_avg_debt_to_equity' },
  { key: 'profit_margin',  label: 'Margin %',          fmt: fmtNum(1),  rankKey: 'profit_margin_rank',  avgKey: 'sector_avg_profit_margin' },
  { key: 'dividend_yield', label: 'Yield %',           fmt: fmtNum(2),  rankKey: 'dividend_yield_rank', avgKey: 'sector_avg_dividend_yield' },
];

function rankColorClass(rank, peerCount) {
  if (!rank || !peerCount || peerCount <= 1) return '';
  if (rank === 1)         return 'bg-emerald-50 text-emerald-900 dark:bg-emerald-900/30 dark:text-emerald-200';
  if (rank === peerCount) return 'bg-rose-50 text-rose-900 dark:bg-rose-900/30 dark:text-rose-200';
  return '';
}

export default function ComparisonTable({ rows }) {
  const { t, tSector, lang } = useLang();
  const [sortBy, setSortBy] = useState({ key: 'symbol', direction: 'asc' });

  // Build a `name` field per row that follows the current UI language.
  // Falls back to English if the Arabic name is missing.
  const localizedRows = useMemo(
    () => rows.map((r) => ({ ...r, name: (lang === 'ar' && r.name_ar) ? r.name_ar : r.name_en })),
    [rows, lang]
  );

  const handleSort = (key) => {
    setSortBy((cur) =>
      cur.key === key
        ? { key, direction: cur.direction === 'asc' ? 'desc' : 'asc' }
        : { key, direction: 'asc' }
    );
  };

  const sortedRows = useMemo(() => {
    const { key, direction } = sortBy;
    const factor = direction === 'asc' ? 1 : -1;
    return [...localizedRows].sort((a, b) => {
      const av = a[key];
      const bv = b[key];
      if (av === null || av === undefined) return 1;
      if (bv === null || bv === undefined) return -1;
      if (typeof av === 'string') return av.localeCompare(bv) * factor;
      return (av - bv) * factor;
    });
  }, [localizedRows, sortBy]);

  if (!rows || rows.length === 0) {
    return (
      <div className="text-slate-500 dark:text-slate-400 italic text-sm">
        {t('cmp.empty')}
      </div>
    );
  }

  return (
    <div>
      <div className="overflow-x-auto bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-700">
              {COLUMNS.map((col) => {
                // Ratio columns hold LTR numbers; force physical right so they
                // line up with their cells in both LTR and RTL mode. Text
                // columns follow page direction (text-end = end of line).
                const align = col.rankKey ? 'text-right' : 'text-end';
                return (
                <th
                  key={col.key}
                  onClick={() => handleSort(col.key)}
                  className={`py-3 px-3 ${align} text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-700/60 select-none whitespace-nowrap`}
                >
                  {col.labelKey ? t(col.labelKey) : col.label}
                  {sortBy.key === col.key && (
                    <span className="ms-1 text-brand-600 dark:text-brand-400">
                      {sortBy.direction === 'asc' ? '▲' : '▼'}
                    </span>
                  )}
                </th>
                );
              })}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
            {sortedRows.map((row) => (
              <tr key={row.symbol} className="hover:bg-brand-50/50 dark:hover:bg-brand-950/30 text-slate-900 dark:text-slate-100">
                {COLUMNS.map((col) => {
                  const value = row[col.key];
                  // Sectors get translated; everything else uses the column formatter.
                  const formatted = col.isSector ? tSector(value) : col.fmt(value);
                  const isRatio   = !!col.rankKey;

                  const colorCls = isRatio
                    ? rankColorClass(row[col.rankKey], row.peer_count)
                    : '';
                  const title = isRatio
                    ? t('cmp.tooltip', {
                        rank:   row[col.rankKey],
                        peers:  row.peer_count,
                        sector: tSector(row.sector),
                        avg:    col.fmt(row[col.avgKey]),
                      })
                    : '';

                  const cellContent =
                    col.key === 'symbol' ? (
                      <Link
                        to={`/stock/${row.symbol}`}
                        className="text-blue-600 dark:text-blue-400 font-semibold hover:underline"
                        dir="ltr"
                      >
                        {row.symbol}
                      </Link>
                    ) : (
                      formatted
                    );

                  // Ratio cells: physical right so they align with the header
                  // (which is also text-right) in both LTR and RTL.
                  // Text cells: text-end follows page direction.
                  const cellAlign = isRatio ? 'text-right' : 'text-end';
                  return (
                    <td
                      key={col.key}
                      title={title}
                      // Numeric cells force LTR so the digits don't flip in RTL.
                      dir={isRatio ? 'ltr' : undefined}
                      className={`py-2.5 px-3 ${cellAlign} tabular-nums whitespace-nowrap ${colorCls}`}
                    >
                      {cellContent}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="text-xs text-slate-500 dark:text-slate-400 mt-3 flex gap-4 flex-wrap items-center">
        <span className="flex items-center">
          <span className="inline-block w-3 h-3 bg-emerald-100 dark:bg-emerald-900/40 ring-1 ring-emerald-300 dark:ring-emerald-700 me-1.5 rounded-sm" />
          {t('cmp.legend.best')}
        </span>
        <span className="flex items-center">
          <span className="inline-block w-3 h-3 bg-rose-100 dark:bg-rose-900/40 ring-1 ring-rose-300 dark:ring-rose-700 me-1.5 rounded-sm" />
          {t('cmp.legend.worst')}
        </span>
        <span>{t('cmp.legend.hint')}</span>
      </div>
    </div>
  );
}
