// Persistent top navigation bar — appears on every page.
// Includes theme + language toggles.

import React from 'react';
import { Link, NavLink } from 'react-router-dom';
import { Home as HomeIcon, BarChart3, Info, LineChart, Star } from 'lucide-react';
import SearchBar from './SearchBar.jsx';
import ThemeToggle from './ThemeToggle.jsx';
import LanguageToggle from './LanguageToggle.jsx';
import UserMenu from './UserMenu.jsx';
import { useLang } from '../../i18n/LanguageContext.jsx';
import { useAuth } from '../../auth/AuthContext.jsx';

const linkBase     = 'flex items-center gap-1.5 text-sm font-medium transition';
const linkInactive = 'text-slate-300 hover:text-white';
const linkActive   = 'text-white';

const navLinkCls = ({ isActive }) =>
  `${linkBase} ${isActive ? linkActive : linkInactive}`;

export default function Navbar() {
  const { t } = useLang();
  const { user } = useAuth();

  return (
    <nav className="sticky top-0 z-40 backdrop-blur-xl bg-slate-950/80 text-white border-b border-white/5 shadow-[0_1px_0_0_rgba(255,255,255,0.04)]">
      <div className="max-w-7xl mx-auto px-6 py-3.5 flex items-center gap-6 flex-wrap">

        {/* Brand mark — small chart-line glyph + wordmark, bilingual. */}
        <Link to="/" className="flex items-center gap-2 text-xl font-bold tracking-tight group">
          <span className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-emerald-700 flex items-center justify-center shadow-md shadow-brand-700/30 group-hover:scale-105 transition">
            <LineChart size={18} strokeWidth={2.5} className="text-white" />
          </span>
          <span className="text-brand-400 font-display">Kashif</span>
          <span className="text-slate-400 font-medium font-display hidden sm:inline">كاشف</span>
        </Link>

        <NavLink to="/" end className={navLinkCls}>
          <HomeIcon size={16} strokeWidth={2} />
          {t('nav.home')}
        </NavLink>
        <NavLink to="/compare" className={navLinkCls}>
          <BarChart3 size={16} strokeWidth={2} />
          {t('nav.compare')}
        </NavLink>
        {user && (
          <NavLink to="/watchlist" className={navLinkCls}>
            <Star size={16} strokeWidth={2} />
            {t('nav.watchlist')}
          </NavLink>
        )}
        <NavLink to="/about" className={navLinkCls}>
          <Info size={16} strokeWidth={2} />
          {t('nav.about')}
        </NavLink>

        {/* Push everything to the far edge of the bar. */}
        <div className="ms-auto flex items-center gap-3">
          <SearchBar />
          <LanguageToggle />
          <ThemeToggle />
          <span className="w-px h-6 bg-slate-700 mx-1" />
          <UserMenu />
        </div>
      </div>
    </nav>
  );
}
