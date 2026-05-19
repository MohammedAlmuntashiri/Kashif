// Single-stock detail page.

import React, { useEffect } from 'react';
import { usePolling } from '../hooks/usePolling.js';
import { Link, useParams } from 'react-router-dom';

import { getStock } from '../services/api.js';
import { StockDetailSkeleton } from '../components/common/Skeleton.jsx';
import ValuationBadge from '../components/common/ValuationBadge.jsx';
import ValuationGauge from '../components/stocks/ValuationGauge.jsx';
import StockNoteCard from '../components/stocks/StockNoteCard.jsx';
import WatchlistStar from '../components/stocks/WatchlistStar.jsx';
import { recordRecentlyViewed } from '../components/stocks/RecentlyViewedStrip.jsx';
import { getMarketStatus, formatTimeAgo } from '../utils/market.js';
import FinancialTable from '../components/stocks/FinancialTable.jsx';
import UploadSection from '../components/stocks/UploadSection.jsx';
import PeersInSector from '../components/stocks/PeersInSector.jsx';
import StockLogo from '../components/stocks/StockLogo.jsx';
import { formatSARPerShare } from '../utils/format.js';
import { useLang } from '../i18n/LanguageContext.jsx';

export default function StockDetailPage() {
  const { t, tSector, lang } = useLang();
  const { ticker } = useParams();

  // Live polling — 30s on the detail page so price + valuation gauge
  // stay current; the hook resets state when `ticker` changes.
  const { data, error } = usePolling(() => getStock(ticker), 30_000, [ticker]);

  // Remember this visit for the home page's "recently viewed" strip.
  // MUST be declared above any conditional return — React's rules-of-hooks
  // require the same number of hooks on every render.
  useEffect(() => {
    if (data?.symbol) {
      recordRecentlyViewed({
        symbol:  data.symbol,
        name_en: data.name_en,
        name_ar: data.name_ar,
      });
    }
  }, [data?.symbol, data?.name_en, data?.name_ar]);

  if (error) {
    return (
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="text-rose-700 dark:text-rose-300 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/50 p-4 rounded-lg">
          {t('common.error')}: {error}
        </div>
      </div>
    );
  }
  if (data === null) return <StockDetailSkeleton />;

  const {
    symbol,
    name_en,
    name_ar,
    sector,
    market_price,
    financials,
    valuation,
    valuation_unavailable_reason,
  } = data;

  // Treat a valuation row with no fair_value the same as having no row at all,
  // so the "unavailable" message is shown consistently.
  const hasFairValue = !!(valuation && valuation.fair_value != null);
  const unavailableKey = valuation_unavailable_reason
    ? `val.unavailable.${valuation_unavailable_reason}`
    : 'val.none';

  // Pick the headline name based on UI language.
  const primaryName   = lang === 'ar' ? name_ar : name_en;
  const secondaryName = lang === 'ar' ? name_en : name_ar;
  const secondaryDir  = lang === 'ar' ? 'ltr' : 'rtl';

  return (
    <div className="max-w-6xl mx-auto px-6 py-8 space-y-6">

      {/* Breadcrumb */}
      <nav className="text-sm text-slate-500 dark:text-slate-400">
        <Link to="/" className="hover:text-brand-600 dark:hover:text-brand-400">{t('common.home')}</Link>
        <span className="mx-2">/</span>
        <span className="text-slate-900 dark:text-slate-100 font-medium" dir="ltr">{symbol}</span>
      </nav>

      {/* Header card */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="flex items-start gap-4 min-w-0">
            <StockLogo symbol={symbol} name={name_en} size="lg" />
            <div className="min-w-0">
              <div className="flex items-center gap-3 flex-wrap">
                <h1 className="font-display text-3xl sm:text-4xl font-bold text-slate-900 dark:text-slate-100 tracking-tight tabular-nums" dir="ltr">
                  {symbol}
                </h1>
                <WatchlistStar symbol={symbol} size={22} />
                <span className="text-xs bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-2.5 py-1 rounded-full font-medium">
                  {tSector(sector)}
                </span>
              </div>
              <div className="text-xl font-semibold text-slate-800 dark:text-slate-200 mt-2">{primaryName}</div>
              <div className="text-lg text-slate-500 dark:text-slate-400" dir={secondaryDir}>{secondaryName}</div>
            </div>
          </div>

          {market_price != null && (
            <div className="text-end">
              <div className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wide font-medium">
                {t('stock.marketPrice')}
              </div>
              <div className="text-3xl font-bold text-slate-900 dark:text-slate-100 tabular-nums" dir="ltr">
                {formatSARPerShare(market_price)}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Valuation section */}
      <section className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">{t('val.title')}</h2>

        {hasFairValue ? (
          <>
            <div className="flex items-center gap-4 mb-4 flex-wrap">
              <div className="text-2xl text-slate-900 dark:text-slate-100">
                {t('val.fairValue')}:{' '}
                <span className="font-bold tabular-nums" dir="ltr">
                  {formatSARPerShare(valuation.fair_value)}
                </span>
              </div>
              <ValuationBadge status={valuation.status} />
            </div>

            <ValuationGauge
              marketPrice={valuation.market_price ?? market_price}
              fairValue={valuation.fair_value}
            />

            {/* Per-model breakdown — DCF / P/E / P/B side-by-side. */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-5">
              {[
                { label: t('val.model.dcf'), value: valuation.dcf_value },
                { label: t('val.model.pe'),  value: valuation.pe_value },
                { label: t('val.model.pb'),  value: valuation.pb_value },
              ].map(({ label, value }) => (
                <div
                  key={label}
                  className="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 p-4 rounded-lg"
                >
                  <div className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wide font-medium">
                    {label}
                  </div>
                  <div className="text-xl font-semibold text-slate-900 dark:text-slate-100 tabular-nums" dir="ltr">
                    {formatSARPerShare(value)}
                  </div>
                </div>
              ))}
            </div>

            {valuation.calculated_at && (() => {
              // Show relative time ("3 hr ago") plus a small market-status
              // badge so the user understands WHY the timestamp is stale.
              // Both computed client-side so we don't have to ping the backend
              // just to know the time.
              const ago = formatTimeAgo(valuation.calculated_at);
              const m = getMarketStatus();
              const isOpen = m.status === 'open';
              const dot = (
                <span className={`inline-block w-1.5 h-1.5 rounded-full ${
                  isOpen ? 'bg-emerald-500 animate-pulse' : 'bg-slate-400'
                }`} />
              );
              return (
                <div className="text-xs text-slate-500 dark:text-slate-400 mt-4 flex items-center gap-2 flex-wrap">
                  {dot}
                  <span>
                    {t('val.calculated')}:{' '}
                    <span className="font-medium text-slate-700 dark:text-slate-300">
                      {ago ? t(ago.key, ago.args) : '—'}
                    </span>
                  </span>
                  <span className="text-slate-300 dark:text-slate-600">·</span>
                  <span>{t(`market.${m.status}`, m.nextOpenDay ? { when: t(`market.when.${m.nextOpenDay}`) } : {})}</span>
                  {valuation.source && (
                    <>
                      <span className="text-slate-300 dark:text-slate-600">·</span>
                      <span>{t('val.source')}: {valuation.source}</span>
                    </>
                  )}
                </div>
              );
            })()}
          </>
        ) : (
          <div className="bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/50 rounded-lg p-4">
            <div className="text-amber-900 dark:text-amber-200 font-semibold mb-1">
              {t('val.unavailable.title')}
            </div>
            <div className="text-amber-800 dark:text-amber-300 text-sm leading-relaxed">
              {t(unavailableKey)}
            </div>
          </div>
        )}
      </section>

      {/* Financials section */}
      <section className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">{t('fin.title')}</h2>
        <FinancialTable financials={financials} />
      </section>

      {/* PDF upload section (preview only — never writes DB) */}
      {/* Personal notes — only renders when signed in. */}
      <StockNoteCard ticker={symbol} />

      <UploadSection ticker={symbol} />

      {/* Peers in the same sector — quick link to comparable stocks. */}
      <PeersInSector currentSymbol={symbol} sectorEn={sector} />

    </div>
  );
}
