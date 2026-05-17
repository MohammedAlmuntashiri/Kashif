// Home / Dashboard page.

import React, { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';

import { getStocks } from '../services/api.js';
import LoadingSpinner from '../components/common/LoadingSpinner.jsx';
import StockCard from '../components/stocks/StockCard.jsx';
import { useLang } from '../i18n/LanguageContext.jsx';

export default function HomePage() {
  const { t, tSector } = useLang();
  const [stocks, setStocks] = useState(null);
  const [error, setError]   = useState(null);

  useEffect(() => {
    getStocks()
      .then(setStocks)
      .catch((e) => setError(e.message));
  }, []);

  const sectorCounts = useMemo(() => {
    if (!stocks) return {};
    return stocks.reduce((acc, s) => {
      acc[s.sector] = (acc[s.sector] || 0) + 1;
      return acc;
    }, {});
  }, [stocks]);

  if (error) {
    return (
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="text-rose-700 dark:text-rose-300 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/50 p-4 rounded-lg">
          {t('common.error')}: {error}
        </div>
      </div>
    );
  }
  if (stocks === null) return <LoadingSpinner />;

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">

      <div className="mb-6">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">
          {t('home.title')}
        </h1>
        <div className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          {t('home.subtitle', {
            count:   stocks.length,
            sectors: Object.keys(sectorCounts).length,
          })}
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-6">
        {Object.entries(sectorCounts)
          .sort((a, b) => b[1] - a[1])
          .map(([sector, count]) => (
            <Link
              key={sector}
              to={`/sector/${encodeURIComponent(sector)}`}
              className="text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-blue-400 dark:hover:border-blue-500 hover:text-blue-700 dark:hover:text-blue-300 text-slate-700 dark:text-slate-300 px-3 py-1.5 rounded-full transition font-medium"
            >
              {tSector(sector)}
              <span className="text-slate-400 dark:text-slate-500 ms-1 tabular-nums">{count}</span>
            </Link>
          ))}
      </div>

      {stocks.length === 0 ? (
        <div className="text-slate-500 dark:text-slate-400 italic">{t('home.empty')}</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {stocks.map((stock) => (
            <StockCard key={stock.symbol} stock={stock} />
          ))}
        </div>
      )}
    </div>
  );
}
