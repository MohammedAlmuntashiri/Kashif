// News feed section — handles loading/error/empty states.
// Used on both the Home page (market-wide) and Stock detail page (ticker-filtered).

import React, { useEffect, useState } from 'react';
import { getNews } from '../../services/api.js';
import NewsCard from './NewsCard.jsx';
import { useLang } from '../../i18n/LanguageContext.jsx';

export default function NewsList({ ticker, limit, title }) {
  const { t } = useLang();
  const [items, setItems] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    setItems(null);
    setError(null);
    getNews({ ticker, limit })
      .then(setItems)
      .catch((e) => setError(e.message || String(e)));
  }, [ticker, limit]);

  return (
    <section className="space-y-3">
      {title && (
        <div className="flex items-center justify-between gap-2">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
            {title}
          </h2>
        </div>
      )}

      {error && (
        <div className="text-sm text-rose-700 dark:text-rose-300 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/50 px-3 py-2 rounded-lg">
          {t('common.error')}: {error}
        </div>
      )}

      {!error && items === null && (
        <div className="text-sm text-slate-500 dark:text-slate-400 italic">
          {t('news.loading')}
        </div>
      )}

      {!error && items && items.length === 0 && (
        <div className="text-sm text-slate-500 dark:text-slate-400 italic">
          {ticker ? t('news.emptyTicker', { ticker }) : t('news.empty')}
        </div>
      )}

      {!error && items && items.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {items.map((n) => (
            <NewsCard key={n.id} item={n} />
          ))}
        </div>
      )}
    </section>
  );
}
