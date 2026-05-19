// Signed-in users' watchlist — same StockCard renderer as HomePage, polled
// every 60s so prices stay live. Signed-out visitors see a sign-in nudge
// instead of an empty page.

import React from 'react';
import { Link } from 'react-router-dom';
import { Star } from 'lucide-react';

import { useAuth } from '../auth/AuthContext.jsx';
import { useLang } from '../i18n/LanguageContext.jsx';
import { usePolling } from '../hooks/usePolling.js';
import { fetchWatchlist } from '../services/api.js';
import StockCard from '../components/stocks/StockCard.jsx';
import { StockGridSkeleton } from '../components/common/Skeleton.jsx';

export default function WatchlistPage() {
  const { user } = useAuth();
  const { t } = useLang();

  // Sign-in nudge — gate the whole page behind auth.
  if (!user) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-16 text-center">
        <Star size={48} strokeWidth={1.5} className="mx-auto text-amber-400 mb-4" />
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-2">
          {t('watchlist.signinTitle')}
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mb-6">
          {t('watchlist.signinBody')}
        </p>
        <Link
          to="/signin"
          className="inline-block px-5 py-2 bg-brand-600 text-white rounded-lg font-medium hover:bg-brand-500 transition"
        >
          {t('watchlist.signinCta')}
        </Link>
      </div>
    );
  }

  // Live polling — same cadence as HomePage so cards stay current.
  const { data: stocks, error } = usePolling(fetchWatchlist, 60_000);

  if (error) {
    return (
      <div className="max-w-6xl mx-auto px-6 py-8 text-rose-700 dark:text-rose-300">
        {t('common.error')}: {error}
      </div>
    );
  }

  if (stocks === null) return <StockGridSkeleton />;

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="flex items-center gap-3 mb-6">
        <Star size={28} strokeWidth={2} className="text-amber-400" fill="currentColor" />
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100 font-display">
          {t('watchlist.title')}
        </h1>
        <span className="text-sm text-slate-500 dark:text-slate-400 ms-auto">
          {t('watchlist.count', { n: stocks.length })}
        </span>
      </div>

      {stocks.length === 0 ? (
        <div className="text-center py-16">
          <Star size={48} strokeWidth={1.5} className="mx-auto text-slate-300 dark:text-slate-700 mb-4" />
          <p className="text-slate-600 dark:text-slate-400 mb-2">{t('watchlist.empty')}</p>
          <p className="text-sm text-slate-500 dark:text-slate-500">{t('watchlist.emptyHint')}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {stocks.map((s) => (
            <StockCard key={s.symbol} stock={s} />
          ))}
        </div>
      )}
    </div>
  );
}
