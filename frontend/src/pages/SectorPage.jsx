// Per-sector listing page.

import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';

import { getComparisons } from '../services/api.js';
import LoadingSpinner from '../components/common/LoadingSpinner.jsx';
import ComparisonTable from '../components/stocks/ComparisonTable.jsx';
import { useLang } from '../i18n/LanguageContext.jsx';

export default function SectorPage() {
  const { name } = useParams();
  const { t, tSector } = useLang();

  const [rows, setRows]   = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    setRows(null);
    setError(null);
    getComparisons({ sector: name })
      .then(setRows)
      .catch((e) => setError(e.message));
  }, [name]);

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

  const sectorLabel = tSector(name);

  // English pluralization is simple (singular/plural). Arabic plurals are
  // complex but for now we pick a singular key vs a many key — close enough.
  const countKey = rows.length === 1 ? 'sec.count.one' : 'sec.count.many';

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">

      <nav className="text-sm text-slate-500 dark:text-slate-400 mb-3">
        <Link to="/" className="hover:text-brand-600 dark:hover:text-brand-400">{t('common.home')}</Link>
        <span className="mx-2">/</span>
        <span className="text-slate-900 dark:text-slate-100 font-medium">{t('sec.breadcrumb')}: {sectorLabel}</span>
      </nav>

      <div className="mb-6">
        <h1 className="font-display text-3xl sm:text-4xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">
          {sectorLabel}
        </h1>
        <div className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          {t(countKey, { count: rows.length })}
        </div>
      </div>

      {rows.length === 0 ? (
        <div className="text-slate-500 dark:text-slate-400 italic">
          {t('sec.empty', { sector: sectorLabel })}
        </div>
      ) : (
        <ComparisonTable rows={rows} />
      )}
    </div>
  );
}
