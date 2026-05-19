// About / Mission page.

import React from 'react';
import { Link } from 'react-router-dom';
import {
  Target, FileText, Scale, Globe2, ShieldCheck,
  Sparkles, ArrowRight,
} from 'lucide-react';
import { useLang } from '../i18n/LanguageContext.jsx';

export default function AboutPage() {
  const { t } = useLang();

  return (
    <div className="max-w-6xl mx-auto px-6 py-12 space-y-16">

      {/* ── Hero ─────────────────────────────────────────────── */}
      <section className="relative text-center">
        <div className="inline-flex items-center gap-2 text-xs font-semibold text-brand-700 dark:text-brand-300 bg-brand-50 dark:bg-brand-950/40 border border-brand-200/60 dark:border-brand-800/40 px-3 py-1.5 rounded-full mb-5">
          <Sparkles size={14} strokeWidth={2.5} />
          {t('about.tagline')}
        </div>
        <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight leading-tight bg-clip-text text-transparent bg-gradient-to-br from-slate-900 via-slate-700 to-brand-600 dark:from-slate-50 dark:via-slate-200 dark:to-brand-400">
          {t('about.title')}
        </h1>
        <p className="text-base sm:text-lg text-slate-600 dark:text-slate-400 mt-5 max-w-2xl mx-auto leading-relaxed">
          {t('about.subtitle')}
        </p>
      </section>

      {/* ── Mission card ────────────────────────────────────── */}
      <section className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-8 sm:p-10 shadow-sm">
        <div className="flex items-center gap-3 mb-4">
          <span className="w-10 h-10 rounded-lg bg-brand-100 dark:bg-brand-900/40 text-brand-700 dark:text-brand-300 flex items-center justify-center">
            <Target size={20} strokeWidth={2.5} />
          </span>
          <h2 className="font-display text-2xl font-bold text-slate-900 dark:text-slate-100">
            {t('about.mission.title')}
          </h2>
        </div>
        <p className="text-slate-700 dark:text-slate-300 leading-relaxed">
          {t('about.mission.body')}
        </p>
      </section>

      {/* ── What we do — 3-up grid ──────────────────────────── */}
      <section>
        <div className="text-center mb-8">
          <h2 className="font-display text-3xl font-bold text-slate-900 dark:text-slate-100">
            {t('about.what.title')}
          </h2>
          <p className="text-slate-500 dark:text-slate-400 mt-2">
            {t('about.what.subtitle')}
          </p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <Feature
            icon={FileText}
            title={t('about.feature.extract.title')}
            body={t('about.feature.extract.body')}
          />
          <Feature
            icon={Scale}
            title={t('about.feature.value.title')}
            body={t('about.feature.value.body')}
          />
        </div>
      </section>

      {/* ── Values strip ────────────────────────────────────── */}
      <section className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <Value
          icon={Globe2}
          title={t('about.value.bilingual.title')}
          body={t('about.value.bilingual.body')}
        />
        <Value
          icon={ShieldCheck}
          title={t('about.value.transparent.title')}
          body={t('about.value.transparent.body')}
        />
        <Value
          icon={Target}
          title={t('about.value.focus.title')}
          body={t('about.value.focus.body')}
        />
      </section>

      {/* ── CTA band ────────────────────────────────────────── */}
      <section className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-brand-600 via-brand-700 to-emerald-800 text-white p-10 text-center shadow-xl shadow-brand-900/20">
        {/* Decorative grid behind the CTA copy. */}
        <div
          aria-hidden
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage:
              'linear-gradient(rgba(255,255,255,0.15) 1px, transparent 1px),' +
              'linear-gradient(90deg, rgba(255,255,255,0.15) 1px, transparent 1px)',
            backgroundSize: '32px 32px',
          }}
        />
        <div className="relative">
          <h2 className="font-display text-2xl sm:text-3xl font-bold mb-3">
            {t('about.cta.title')}
          </h2>
          <p className="text-emerald-50/90 max-w-xl mx-auto mb-6">
            {t('about.cta.body')}
          </p>
          <Link
            to="/"
            className="inline-flex items-center gap-2 bg-white text-brand-700 font-semibold px-5 py-2.5 rounded-lg hover:bg-emerald-50 transition shadow-lg"
          >
            {t('about.cta.button')}
            <ArrowRight size={16} strokeWidth={2.5} />
          </Link>
        </div>
      </section>
    </div>
  );
}

// ── Sub-components ─────────────────────────────────────────────────

function Feature({ icon: Icon, title, body }) {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm hover:border-brand-400 dark:hover:border-brand-500 hover:-translate-y-0.5 transition-all">
      <span className="w-10 h-10 rounded-lg bg-brand-100 dark:bg-brand-900/40 text-brand-700 dark:text-brand-300 flex items-center justify-center mb-4">
        <Icon size={20} strokeWidth={2.5} />
      </span>
      <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-2">{title}</h3>
      <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">{body}</p>
    </div>
  );
}

function Value({ icon: Icon, title, body }) {
  return (
    <div className="flex items-start gap-3">
      <Icon size={20} strokeWidth={2.5} className="text-brand-600 dark:text-brand-400 shrink-0 mt-0.5" />
      <div>
        <div className="font-semibold text-slate-900 dark:text-slate-100">{title}</div>
        <div className="text-sm text-slate-600 dark:text-slate-400 mt-1 leading-relaxed">{body}</div>
      </div>
    </div>
  );
}
