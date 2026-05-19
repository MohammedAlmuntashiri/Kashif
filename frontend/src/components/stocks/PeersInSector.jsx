// "Other stocks in this sector" strip shown at the bottom of StockDetailPage.
// Pulls the full stocks list (cached by the polling on HomePage anyway),
// filters by sector_en, drops the current ticker. Falls back to a "no peers"
// message if the stock is alone in its sector (1111, 1212, 4011, 7202 etc.).

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users } from 'lucide-react';

import { useLang } from '../../i18n/LanguageContext.jsx';
import { getStocks } from '../../services/api.js';
import { formatSARPerShare } from '../../utils/format.js';
import StockLogo from './StockLogo.jsx';

export default function PeersInSector({ currentSymbol, sectorEn }) {
  const { t, tSector, lang } = useLang();
  const [peers, setPeers] = useState(null);

  useEffect(() => {
    let cancelled = false;
    getStocks()
      .then((rows) => {
        if (cancelled) return;
        setPeers(
          rows.filter((s) => s.sector === sectorEn && s.symbol !== currentSymbol),
        );
      })
      .catch(() => { if (!cancelled) setPeers([]); });
    return () => { cancelled = true; };
  }, [currentSymbol, sectorEn]);

  if (peers === null) {
    return (
      <section className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm">
        <div className="h-20 bg-slate-100 dark:bg-slate-800 rounded animate-pulse" />
      </section>
    );
  }

  return (
    <section className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm">
      <div className="flex items-center gap-2 mb-4 flex-wrap">
        <Users size={18} strokeWidth={2} className="text-brand-600 dark:text-brand-400" />
        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
          {t('peers.title', { sector: tSector(sectorEn) })}
        </h2>
        <span className="text-xs text-slate-500 dark:text-slate-400 ms-auto">
          {t('peers.count', { n: peers.length })}
        </span>
      </div>

      {peers.length === 0 ? (
        <div className="text-sm text-slate-500 dark:text-slate-400 italic">
          {t('peers.empty')}
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {peers.map((s) => {
            const label = lang === 'ar' ? (s.name_ar || s.name_en) : (s.name_en || s.name_ar);
            return (
              <Link
                key={s.symbol}
                to={`/stock/${s.symbol}`}
                className="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700 rounded-lg hover:border-brand-400 dark:hover:border-brand-500 hover:bg-brand-50 dark:hover:bg-brand-950/30 transition"
              >
                <StockLogo symbol={s.symbol} name={s.name_en} size="sm" />
                <div className="min-w-0 flex-1">
                  <div className="flex items-baseline gap-2">
                    <span className="text-sm font-bold text-blue-600 dark:text-blue-400 tabular-nums" dir="ltr">
                      {s.symbol}
                    </span>
                    <span className="text-xs text-slate-500 dark:text-slate-400 tabular-nums truncate" dir="ltr">
                      {formatSARPerShare(s.market_price)}
                    </span>
                  </div>
                  <div className="text-xs text-slate-700 dark:text-slate-300 truncate">
                    {label}
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </section>
  );
}
