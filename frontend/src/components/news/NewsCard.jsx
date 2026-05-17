// One news headline card — Yahoo-style: title, source • time, summary,
// and an optional ticker chip row.

import React from 'react';
import { Link } from 'react-router-dom';
import { useLang } from '../../i18n/LanguageContext.jsx';
import { timeAgo } from '../../utils/time.js';

export default function NewsCard({ item }) {
  const { lang } = useLang();

  const title   = (lang === 'ar' && item.title_ar)   ? item.title_ar   : item.title;
  const summary = (lang === 'ar' && item.summary_ar) ? item.summary_ar : item.summary;
  const when    = timeAgo(item.publishedAt, lang);

  return (
    <article className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm hover:border-brand-300 dark:hover:border-brand-700 transition">
      <a
        href={item.url}
        target="_blank"
        rel="noopener noreferrer"
        className="block"
      >
        <h3 className="text-base font-semibold text-slate-900 dark:text-slate-100 leading-snug hover:text-brand-600 dark:hover:text-brand-400 transition">
          {title}
        </h3>
        {summary && (
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1.5 leading-relaxed">
            {summary}
          </p>
        )}
      </a>

      <div className="flex items-center justify-between gap-2 mt-3 flex-wrap">
        <div className="text-xs text-slate-500 dark:text-slate-500">
          <span className="font-medium text-slate-700 dark:text-slate-300">{item.source}</span>
          <span className="mx-1.5">•</span>
          <span>{when}</span>
        </div>

        {item.tickers && item.tickers.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {item.tickers.map((t) => (
              <Link
                key={t}
                to={`/stock/${t}`}
                className="text-xs font-bold tabular-nums bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-brand-100 dark:hover:bg-brand-900/40 hover:text-brand-700 dark:hover:text-brand-300 px-2 py-0.5 rounded-md transition"
                dir="ltr"
                onClick={(e) => e.stopPropagation()}
              >
                {t}
              </Link>
            ))}
          </div>
        )}
      </div>
    </article>
  );
}
