// Site footer — brand mark, secondary nav, copyright.

import React from 'react';
import { Link } from 'react-router-dom';
import { LineChart } from 'lucide-react';
import { useLang } from '../../i18n/LanguageContext.jsx';

export default function Footer() {
  const { t } = useLang();
  const year = new Date().getFullYear();

  return (
    <footer className="mt-16 border-t border-slate-200 dark:border-slate-800 bg-white/60 dark:bg-slate-950/50 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-6 py-10 grid grid-cols-1 sm:grid-cols-3 gap-8">

        {/* Brand column */}
        <div>
          <Link to="/" className="flex items-center gap-2 mb-3">
            <span className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-emerald-700 flex items-center justify-center shadow-md shadow-brand-700/20">
              <LineChart size={18} strokeWidth={2.5} className="text-white" />
            </span>
            <span className="font-display text-lg font-bold">
              <span className="text-brand-600 dark:text-brand-400">Kashif</span>
              <span className="text-slate-400 ms-2">كاشف</span>
            </span>
          </Link>
          <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed max-w-xs">
            {t('footer.tagline')}
          </p>
        </div>

        {/* Explore */}
        <div>
          <div className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-3">
            {t('footer.explore')}
          </div>
          <ul className="space-y-2 text-sm">
            <li><FooterLink to="/">{t('nav.home')}</FooterLink></li>
            <li><FooterLink to="/compare">{t('nav.compare')}</FooterLink></li>
            <li><FooterLink to="/about">{t('nav.about')}</FooterLink></li>
          </ul>
        </div>

        {/* Account */}
        <div>
          <div className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-3">
            {t('footer.account')}
          </div>
          <ul className="space-y-2 text-sm">
            <li><FooterLink to="/signin">{t('auth.nav.signIn')}</FooterLink></li>
            <li><FooterLink to="/signup">{t('auth.nav.signUp')}</FooterLink></li>
          </ul>
        </div>
      </div>

      {/* Bottom strip */}
      <div className="border-t border-slate-200 dark:border-slate-800">
        <div className="max-w-7xl mx-auto px-6 py-4 text-xs text-slate-500 dark:text-slate-400">
          © {year} Kashif · {t('footer.copyright')}
        </div>
      </div>
    </footer>
  );
}

function FooterLink({ to, children }) {
  return (
    <Link
      to={to}
      className="text-slate-600 dark:text-slate-300 hover:text-brand-600 dark:hover:text-brand-400 transition"
    >
      {children}
    </Link>
  );
}
