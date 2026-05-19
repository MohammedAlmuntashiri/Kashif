// Last 5 stocks this browser opened. Stored in localStorage (zero backend
// dependency), works for signed-out users too. Updated by StockDetailPage
// via the `recordRecentlyViewed` helper exported below.

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Clock } from 'lucide-react';

import { useLang } from '../../i18n/LanguageContext.jsx';
import StockLogo from './StockLogo.jsx';

const STORAGE_KEY = 'kashif.recentlyViewed';
const MAX = 5;

function load() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

/**
 * Push a stock to the front of the recently-viewed queue (dedup, max 5).
 * Call from StockDetailPage when a stock detail finishes loading.
 */
export function recordRecentlyViewed({ symbol, name_en, name_ar }) {
  if (!symbol) return;
  const current = load().filter((s) => s.symbol !== symbol);
  const next = [{ symbol, name_en, name_ar }, ...current].slice(0, MAX);
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    // Notify same-tab listeners (the storage event only fires across tabs).
    window.dispatchEvent(new Event('kashif:recentlyViewed'));
  } catch { /* quota errors are harmless here */ }
}

export default function RecentlyViewedStrip() {
  const { t, lang } = useLang();
  const [items, setItems] = useState(load);

  useEffect(() => {
    const refresh = () => setItems(load());
    window.addEventListener('storage', refresh);
    window.addEventListener('kashif:recentlyViewed', refresh);
    return () => {
      window.removeEventListener('storage', refresh);
      window.removeEventListener('kashif:recentlyViewed', refresh);
    };
  }, []);

  if (items.length === 0) return null;

  return (
    <section className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm">
      <div className="flex items-center gap-2 mb-3">
        <Clock size={16} strokeWidth={2} className="text-brand-600 dark:text-brand-400" />
        <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-200">
          {t('recent.title')}
        </h3>
      </div>
      <div className="flex flex-wrap gap-2">
        {items.map((s) => {
          const label = lang === 'ar' ? (s.name_ar || s.name_en) : (s.name_en || s.name_ar);
          return (
            <Link
              key={s.symbol}
              to={`/stock/${s.symbol}`}
              className="flex items-center gap-2 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-full px-3 py-1.5 hover:border-brand-400 dark:hover:border-brand-500 hover:bg-brand-50 dark:hover:bg-brand-950/30 transition"
            >
              <StockLogo symbol={s.symbol} name={s.name_en} size="sm" />
              <span className="text-xs font-bold text-blue-600 dark:text-blue-400 tabular-nums" dir="ltr">{s.symbol}</span>
              <span className="text-xs text-slate-600 dark:text-slate-300 max-w-[12rem] truncate">
                {label}
              </span>
            </Link>
          );
        })}
      </div>
    </section>
  );
}
