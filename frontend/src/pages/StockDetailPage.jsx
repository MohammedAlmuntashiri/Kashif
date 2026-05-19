// Single-stock detail page.

import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';

import { getStock } from '../services/api.js';
import { StockDetailSkeleton } from '../components/common/Skeleton.jsx';
import ValuationBadge from '../components/common/ValuationBadge.jsx';
import ValuationGauge from '../components/stocks/ValuationGauge.jsx';
import FinancialTable from '../components/stocks/FinancialTable.jsx';
import UploadSection from '../components/stocks/UploadSection.jsx';
import NewsList from '../components/news/NewsList.jsx';
import StockLogo from '../components/stocks/StockLogo.jsx';
import { formatSARPerShare } from '../utils/format.js';
import { useLang } from '../i18n/LanguageContext.jsx';

export default function StockDetailPage() {
  const { t, tSector, lang } = useLang();
  const { ticker } = useParams();

  const [data,  setData]  = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    setData(null);
    setError(null);
    getStock(ticker)
      .then(setData)
      .catch((e) => setError(e.response?.data?.error || e.message));
  }, [ticker]);

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
  } = data;

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

        {valuation ? (
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

            {valuation.calculated_at && (
              <div className="text-xs text-slate-400 dark:text-slate-500 mt-4">
                {t('val.calculated')}: {new Date(valuation.calculated_at).toLocaleString()}
                {valuation.source && (
                  <> &nbsp;•&nbsp; {t('val.source')}: {valuation.source}</>
                )}
              </div>
            )}
          </>
        ) : (
          <div className="text-slate-500 dark:text-slate-400 italic">
            {t('val.none')}
          </div>
        )}
      </section>

      {/* Financials section */}
      <section className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">{t('fin.title')}</h2>
        <FinancialTable financials={financials} />
      </section>

      {/* PDF upload section (preview only — never writes DB) */}
      <UploadSection ticker={symbol} />

      {/* Stock-specific news */}
      <section className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm">
        <NewsList ticker={symbol} title={t('news.stockTitle', { ticker: symbol })} />
      </section>

    </div>
  );
}
