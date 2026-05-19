// Home / Dashboard page.

import React, { useMemo, useState } from 'react';
import { usePolling } from '../hooks/usePolling.js';
import { Link } from 'react-router-dom';
import { TrendingUp, Layers, Briefcase, Newspaper, LineChart, Sparkles } from 'lucide-react';

import { getStocks } from '../services/api.js';
import StockCard from '../components/stocks/StockCard.jsx';
import NewsList from '../components/news/NewsList.jsx';
import { StockGridSkeleton } from '../components/common/Skeleton.jsx';
import AnimatedCounter from '../components/common/AnimatedCounter.jsx';
import HeroMesh from '../components/common/HeroMesh.jsx';
import RecentlyViewedStrip from '../components/stocks/RecentlyViewedStrip.jsx';
import { formatSAR } from '../utils/format.js';
import { useLang } from '../i18n/LanguageContext.jsx';

// Mock TASI value — replace with a real index endpoint when one is wired.
const TASI = { value: 11_234.56, change: 0.84 };

export default function HomePage() {
  const { t, tSector } = useLang();
  // Live polling — refresh every 60s so prices and valuations on the home
  // cards keep up with the scheduler's 10-min DB refreshes during market hours.
  const { data: stocks, error } = usePolling(getStocks, 60_000);

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

  const loading = stocks === null;
  const tasiUp = TASI.change >= 0;

  return (
    <div className="max-w-7xl mx-auto px-6 py-10 space-y-12">

      {/* ── Hero band ────────────────────────────────────────── */}
      <section className="relative">
        {/* Animated gradient mesh backdrop. */}
        <HeroMesh />

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
            numericValue={loading ? null : stocks.length}
          />
          <Kpi
            icon={Layers}
            label={t('home.kpi.sectors')}
            numericValue={loading ? null : Object.keys(sectorCounts).length}
          />
          <Kpi
            icon={TrendingUp}
            label={t('home.kpi.revenue')}
            value={loading ? '—' : formatSAR(totalRevenue)}
            mono
          />
        </div>
      </section>

      {/* ── Recently viewed strip (browser-local, self-hides when empty) ── */}
      <RecentlyViewedStrip />

      {/* ── Sectors band ─────────────────────────────────────── */}
      <section>
        <SectionHeader
          icon={Layers}
          title={t('home.section.sectors')}
          subtitle={t('home.section.sectorsSub')}
        />
        <div className="flex flex-wrap gap-2 mt-4">
          {loading ? (
            Array.from({ length: 8 }).map((_, i) => (
              <div
                key={i}
                className="h-7 w-24 rounded-full bg-slate-200/70 dark:bg-slate-800/60 animate-pulse"
              />
            ))
          ) : (
            Object.entries(sectorCounts)
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
              ))
          )}
        </div>
      </section>

      {/* ── Stocks band ──────────────────────────────────────── */}
      <StocksBand
        loading={loading}
        stocks={loading ? [] : stocks}
        t={t}
      />

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

function Kpi({ icon: Icon, label, value, numericValue, mono = false }) {
  const isNumeric = typeof numericValue === 'number' && Number.isFinite(numericValue);
  return (
    <div className="group relative overflow-hidden bg-white/70 dark:bg-slate-900/60 backdrop-blur-xl border border-white/60 dark:border-slate-800/80 rounded-2xl p-5 shadow-[0_8px_24px_-12px_rgba(15,23,42,0.18)] dark:shadow-[0_8px_24px_-12px_rgba(0,0,0,0.5)] hover:border-brand-400/70 dark:hover:border-brand-500/70 hover:shadow-brand-glow transition-all">
      {/* Decorative emerald glow that slides in on hover */}
      <div
        aria-hidden
        className="pointer-events-none absolute -top-12 -end-12 w-32 h-32 rounded-full bg-brand-400/30 dark:bg-brand-500/20 blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
      />
      <div className="relative flex items-center gap-2 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
        <span className="flex items-center justify-center w-7 h-7 rounded-lg bg-brand-50 dark:bg-brand-950/50 text-brand-600 dark:text-brand-400 ring-1 ring-brand-200/60 dark:ring-brand-800/50">
          <Icon size={14} strokeWidth={2.5} />
        </span>
        {label}
      </div>
      <div
        className={`relative mt-3 text-3xl sm:text-4xl font-bold text-slate-900 dark:text-slate-100 font-display tracking-tight ${
          mono || isNumeric ? 'tabular-nums' : ''
        }`}
        dir={mono || isNumeric ? 'ltr' : undefined}
      >
        {isNumeric
          ? <AnimatedCounter value={numericValue} />
          : (value ?? '—')}
      </div>
    </div>
  );
}

// Initial visible batch size + how many more "Load more" reveals each click.
// Limiting initial render is the main perf win — 49 cards × (logo + sparkline)
// was visibly choppy on low-end devices.
const STOCKS_PAGE_SIZE = 12;

function StocksBand({ loading, stocks, t }) {
  const [visible, setVisible] = useState(STOCKS_PAGE_SIZE);

  if (loading) {
    return (
      <section>
        <SectionHeader
          icon={LineChart}
          title={t('home.section.stocks')}
          subtitle=""
        />
        <StockGridSkeleton count={8} />
      </section>
    );
  }
  if (stocks.length === 0) {
    return (
      <section>
        <SectionHeader
          icon={LineChart}
          title={t('home.section.stocks')}
        />
        <EmptyState icon={Briefcase} title={t('home.empty')} />
      </section>
    );
  }

  const shown = stocks.slice(0, visible);
  const hasMore = visible < stocks.length;
  const remaining = stocks.length - visible;

  return (
    <section>
      <SectionHeader
        icon={LineChart}
        title={t('home.section.stocks')}
        subtitle={t('home.section.stocksSub', { count: stocks.length })}
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mt-4">
        {shown.map((stock) => (
          <StockCard key={stock.symbol} stock={stock} />
        ))}
      </div>

      {hasMore && (
        <div className="mt-6 text-center">
          <button
            type="button"
            onClick={() => setVisible((v) => v + STOCKS_PAGE_SIZE)}
            className="px-5 py-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-sm font-medium text-slate-700 dark:text-slate-200 hover:border-brand-500 dark:hover:border-brand-500 hover:text-brand-600 dark:hover:text-brand-400 transition"
          >
            {t('home.loadMore', { n: Math.min(STOCKS_PAGE_SIZE, remaining) })}
          </button>
          <div className="text-xs text-slate-500 dark:text-slate-400 mt-2">
            {t('home.stocksShown', { shown: visible, total: stocks.length })}
          </div>
        </div>
      )}
    </section>
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
