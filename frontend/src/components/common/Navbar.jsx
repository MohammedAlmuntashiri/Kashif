// Persistent top navigation bar — appears on every page.
// Includes theme + language toggles.

import React from 'react';
import { Link, NavLink } from 'react-router-dom';
import SearchBar from './SearchBar.jsx';
import ThemeToggle from './ThemeToggle.jsx';
import LanguageToggle from './LanguageToggle.jsx';
import { useLang } from '../../i18n/LanguageContext.jsx';

const linkBase     = 'text-sm font-medium transition';
const linkInactive = 'text-slate-300 hover:text-white';
const linkActive   = 'text-white';

const navLinkCls = ({ isActive }) =>
  `${linkBase} ${isActive ? linkActive : linkInactive}`;

export default function Navbar() {
  const { t } = useLang();

  return (
    <nav className="bg-gradient-to-r from-slate-900 via-slate-900 to-slate-800 text-white shadow-sm border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center gap-6 flex-wrap">

        {/* Brand mark — bilingual. */}
        <Link to="/" className="text-xl font-bold tracking-tight">
          <span className="text-blue-400">Kashif</span>
          <span className="text-slate-400 ms-2 font-medium">كاشف</span>
        </Link>

        <NavLink to="/"        end className={navLinkCls}>{t('nav.home')}</NavLink>
        <NavLink to="/compare"     className={navLinkCls}>{t('nav.compare')}</NavLink>

        {/* Push everything to the far edge of the bar. */}
        <div className="ms-auto flex items-center gap-2">
          <SearchBar />
          <LanguageToggle />
          <ThemeToggle />
        </div>
      </div>
    </nav>
  );
}
