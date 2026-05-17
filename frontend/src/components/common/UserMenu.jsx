// Navbar right-side: either Sign In / Sign Up buttons (logged out) or a
// small user chip with a sign-out dropdown (logged in).

import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { LogIn, UserPlus, LogOut } from 'lucide-react';
import { useAuth } from '../../auth/AuthContext.jsx';
import { useLang } from '../../i18n/LanguageContext.jsx';

export default function UserMenu() {
  const { user, signOut, ready } = useAuth();
  const { t } = useLang();
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const onClick = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, []);

  // Don't flash "Sign In" before we've checked localStorage.
  if (!ready) return null;

  if (!user) {
    return (
      <div className="flex items-center gap-2">
        <Link
          to="/signin"
          className="flex items-center gap-1.5 text-sm font-medium text-slate-300 hover:text-white transition"
        >
          <LogIn size={16} strokeWidth={2} />
          {t('auth.nav.signIn')}
        </Link>
        <Link
          to="/signup"
          className="flex items-center gap-1.5 text-sm font-semibold text-white bg-brand-600 hover:bg-brand-500 px-3 py-1.5 rounded-lg transition shadow-lg shadow-brand-600/20"
        >
          <UserPlus size={16} strokeWidth={2} />
          {t('auth.nav.signUp')}
        </Link>
      </div>
    );
  }

  // First initial as a tiny avatar.
  const initial = (user.name || user.email || '?').trim().charAt(0).toUpperCase();

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-2 px-2 py-1 rounded-lg hover:bg-slate-800 transition"
      >
        <span className="w-7 h-7 rounded-full bg-brand-600 text-white text-xs font-bold flex items-center justify-center">
          {initial}
        </span>
        <span className="text-sm text-slate-200 hidden sm:inline max-w-[10rem] truncate">
          {user.name}
        </span>
      </button>

      {open && (
        <div className="absolute end-0 mt-1 w-56 rounded-lg shadow-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 z-50 overflow-hidden">
          <div className="px-3 py-2 border-b border-slate-100 dark:border-slate-800">
            <div className="text-sm font-medium text-slate-900 dark:text-slate-100 truncate">
              {user.name}
            </div>
            <div className="text-xs text-slate-500 dark:text-slate-400 truncate" dir="ltr">
              {user.email}
            </div>
          </div>
          <button
            onClick={() => { setOpen(false); signOut(); }}
            className="w-full text-start px-3 py-2 text-sm text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition flex items-center gap-2"
          >
            <LogOut size={16} strokeWidth={2} />
            {t('auth.nav.signOut')}
          </button>
        </div>
      )}
    </div>
  );
}
