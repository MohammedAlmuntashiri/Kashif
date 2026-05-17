// Home / Dashboard page.

import React, { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, Layers, Briefcase, Newspaper, LineChart, Sparkles } from 'lucide-react';

import { getStocks } from '../services/api.js';
import LoadingSpinner from '../components/common/LoadingSpinner.jsx';
import StockCard from '../components/stocks/StockCard.jsx';
import NewsList from '../components/news/NewsList.jsx';
import { formatSAR } from '../utils/format.js';
import { useLang } from '../i18n/LanguageContext.jsx';

// Mock TASI value — replace with a real index endpoint when one is wired.
const TASI = { value: 11_234.56, change: 0.84 };

export default function HomePage() {
  const { t, tSector } = useLang();
  const [stocks, setStocks] = useState(null);
  const [error,  setError]  = useState(null);

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

  const totalRevenue = useMemo(() => {
    if (!stocks) return 0;
    return stocks.reduce((sum, s) => sum + (s.revenue || 0), 0);
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

  const tasiUp = TASI.change >= 0;

  return (
    <div className="max-w-7xl mx-auto px-6 py-10 space-y-12">

      {/* ── Hero band ────────────────────────────────────────── */}
      <section className="relative">
        {/* Decorative dot-grid backdrop behind the hero only — masks to a
            soft circle so it fades to the page edges. */}
        <div
          aria-hidden
          className="absolute inset-x-0 -top-10 h-[420px] -z-10 opacity-60 dark:opacity-40"
          style={{
            backgroundImage:
              'radial-gradient(circle at 1px 1px, rgba(16,185,129,0.25) 1px, transparent 0)',
            backgroundSize: '22px 22px',
            maskImage:
              'radial-gradient(ellipse 60% 60% at 50% 35%, black 40%, transparent 75%)',
            WebkitMaskImage:
              'radial-gradient(ellipse 60% 60% at 50% 35%, black 40%, transparent 75%)',
          }}
        />

        {/* TASI ticker chip — pinned top-right of hero. */}
        <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
          <div className="inline-flex items-center gap-2 text-xs font-semibold text-brand-700 dark:text-brand-300 bg-brand-50 dark:bg-brand-950/40 border border-brand-200/60 dark:border-brand-800/40 px-3 py-1.5 rounded-full">
            <Sparkles size={14} strokeWidth={2.5} />
            {t('home.hero.tagline')}
          </div>
          <div className="inline-flex items-center gap-2 text-sm font-medium bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-3 py-1.5 rounded-full shadow-sm">
            <span className="text-slate-500 dark:text-slate-400 text-xs">TASI</span>
            <span className="text-slate-900 dark:text-slate-100 tabular-nums" dir="ltr">
              {TASI.value.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </span>
            <span
              className={`tabular-nums text-xs font-bold ${
                tasiUp ? 'text-emerald-600 dark:text-emerald-400'
                       : 'text-rose-600 dark:text-rose-400'
              }`}
              dir="ltr"
            >
              {tasiUp ? '▲' : '▼'} {Math.abs(TASI.change).toFixed(2)}%
            </span>
          </div>
        </div>

        {/* Gradient headline — slate body color fades into emerald accent. */}
        <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight leading-tight bg-clip-text text-transparent bg-gradient-to-br from-slate-900 via-slate-700 to-brand-600 dark:from-slate-50 dark:via-slate-200 dark:to-brand-400 pb-1">
          {t('home.hero.title')}
        </h1>
        <p className="text-base sm:text-lg text-slate-600 dark:text-slate-400 mt-4 max-w-2xl leading-relaxed">
          {t('home.hero.subtitle')}
        </p>

        {/* KPI tiles */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-7">
          <Kpi
            icon={Briefcase}
            label={t('home.kpi.stocks')}
            value={stocks.length}
          />
          <Kpi
            icon={Layers}
            label={t('home.kpi.sectors')}
            value={Object.keys(sectorCounts).length}
          />
          <Kpi
            icon={TrendingUp}
            label={t('home.kpi.revenue')}
            value={formatSAR(totalRevenue)}
            mono
          />
        </div>
      </section>

      {/* ── Sectors band ─────────────────────────────────────── */}
      <section>
        <SectionHeader
          icon={Layers}
          title={t('home.section.sectors')}
          subtitle={t('home.section.sectorsSub')}
        />
        <div className="flex flex-wrap gap-2 mt-4">
          {Object.entries(sectorCounts)
            .sort((a, b) => b[1] - a[1])
            .map(([sector, count]) => (
              <Link
                key={sector}
                to={`/sector/${encodeURIComponent(sector)}`}
                className="text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-brand-400 dark:hover:border-brand-500 hover:text-brand-700 dark:hover:text-brand-300 text-slate-700 dark:text-slate-300 px-3 py-1.5 rounded-full transition font-medium"
              >
                {tSector(sector)}
                <span className="text-slate-400 dark:text-slate-500 ms-1 tabular-nums">{count}</span>
              </Link>
            ))}
        </div>
      </section>

      {/* ── Stocks band ──────────────────────────────────────── */}
      <section>
        <SectionHeader
          icon={LineChart}
          title={t('home.section.stocks')}
          subtitle={t('home.section.stocksSub', { count: stocks.length })}
        />

        {stocks.length === 0 ? (
          <EmptyState
            icon={Briefcase}
            title={t('home.empty')}
          />
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mt-4">
            {stocks.map((stock) => (
              <StockCard key={stock.symbol} stock={stock} />
            ))}
          </div>
        )}
      </section>

      {/* ── News band ────────────────────────────────────────── */}
      <section>
        <SectionHeader
          icon={Newspaper}
          title={t('news.marketTitle')}
          subtitle={t('news.subtitle')}
        />
        <div className="mt-4">
          <NewsList limit={8} />
        </div>
      </section>

    </div>
  );
}

// ── Sub-components ─────────────────────────────────────────────────

function Kpi({ icon: Icon, label, value, mono = false }) {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm">
      <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
        <Icon size={14} strokeWidth={2.5} className="text-brand-600 dark:text-brand-400" />
        {label}
      </div>
      <div
        className={`mt-2 text-2xl sm:text-3xl font-bold text-slate-900 dark:text-slate-100 font-display ${
          mono ? 'tabular-nums' : ''
        }`}
        dir={mono ? 'ltr' : undefined}
      >
        {value}
      </div>
    </div>
  );
}

function SectionHeader({ icon: Icon, title, subtitle }) {
  return (
    <div className="flex items-end justify-between gap-3 border-b border-slate-200 dark:border-slate-800 pb-3">
      <div>
        <h2 className="font-display text-xl sm:text-2xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          {Icon && <Icon size={20} strokeWidth={2} className="text-brand-600 dark:text-brand-400" />}
          {title}
        </h2>
        {subtitle && (
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">{subtitle}</p>
        )}
      </div>
    </div>
  );
}

function EmptyState({ icon: Icon, title, subtitle }) {
  return (
    <div className="bg-white dark:bg-slate-900 border border-dashed border-slate-300 dark:border-slate-700 rounded-xl p-10 text-center mt-4">
      {Icon && <Icon size={28} strokeWidth={1.5} className="text-slate-400 dark:text-slate-500 mx-auto mb-3" />}
      <div className="text-sm font-medium text-slate-700 dark:text-slate-200">{title}</div>
      {subtitle && (
        <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">{subtitle}</div>
      )}
    </div>
  );
}
