// Cross-sector comparison page.

import React, { useEffect, useState, useMemo } from 'react';

import { getComparisons } from '../services/api.js';
import LoadingSpinner from '../components/common/LoadingSpinner.jsx';
import ComparisonTable from '../components/stocks/ComparisonTable.jsx';
import { useLang } from '../i18n/LanguageContext.jsx';

export default function ComparePage() {
  const { t, tSector } = useLang();
  const [rows, setRows]                 = useState(null);
  const [error, setError]               = useState(null);
  const [activeSector, setActiveSector] = useState(null);

  useEffect(() => {
    getComparisons()
      .then(setRows)
      .catch((e) => setError(e.message));
  }, []);

  const sectors = useMemo(() => {
    if (!rows) return [];
    return [...new Set(rows.map((r) => r.sector))].sort();
  }, [rows]);

  const filteredRows = useMemo(() => {
    if (!rows) return [];
    return activeSector
      ? rows.filter((r) => r.sector === activeSector)
      : rows;
  }, [rows, activeSector]);

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="text-rose-700 dark:text-rose-300 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/50 p-4 rounded-lg">
          {t('common.error')}: {error}
        </div>
      </div>
    );
  }
  if (rows === null) return <LoadingSpinner />;

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">

      <div className="mb-6">
        <h1 className="font-display text-3xl sm:text-4xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">
          {t('cmp.title')}
        </h1>
        <div className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          {t('cmp.subtitle', { count: filteredRows.length, total: rows.length })}
          {activeSector && (
            <> {t('cmp.inSector')} <strong className="text-slate-700 dark:text-slate-200">{tSector(activeSector)}</strong></>
          )}
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-4">
        <FilterChip
          label={t('cmp.all')}
          active={activeSector === null}
          onClick={() => setActiveSector(null)}
        />
        {sectors.map((s) => (
          <FilterChip
            key={s}
            label={tSector(s)}
            active={activeSector === s}
            onClick={() => setActiveSector(s)}
          />
        ))}
      </div>

      <ComparisonTable rows={filteredRows} />
    </div>
  );
}

function FilterChip({ label, active, onClick }) {
  const base   = 'text-xs px-3 py-1.5 rounded-full transition font-medium';
  const styles = active
    ? 'bg-brand-600 text-white shadow-md shadow-brand-600/30'
    : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-brand-400 dark:hover:border-brand-500 hover:text-brand-700 dark:hover:text-brand-300 text-slate-700 dark:text-slate-300';
  return (
    <button onClick={onClick} className={`${base} ${styles}`}>
      {label}
    </button>
  );
}
