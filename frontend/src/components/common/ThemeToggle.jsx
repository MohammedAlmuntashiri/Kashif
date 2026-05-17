// Sun/moon theme toggle for the Navbar.
//
// How it works:
//   - On first mount, reads whether the `dark` class is already on <html>
//     (the inline script in public/index.html sets it before React runs).
//   - Clicking the button flips the state, which:
//       1. toggles the `dark` class on <html>
//       2. writes the choice to localStorage so it persists across reloads

import React, { useEffect, useState } from 'react';
import { Sun, Moon } from 'lucide-react';
import { useLang } from '../../i18n/LanguageContext.jsx';

export default function ThemeToggle() {
  const { t } = useLang();
  const [dark, setDark] = useState(() =>
    typeof document !== 'undefined' &&
    document.documentElement.classList.contains('dark')
  );

  useEffect(() => {
    const root = document.documentElement;
    if (dark) {
      root.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      root.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [dark]);

  const tooltip = dark ? t('toggle.theme.toLight') : t('toggle.theme.toDark');

  return (
    <button
      onClick={() => setDark((d) => !d)}
      title={tooltip}
      aria-label={tooltip}
      className="w-9 h-9 flex items-center justify-center rounded-lg text-slate-300 hover:text-white hover:bg-slate-700/60 transition"
    >
      {/* Show the icon for the *target* mode — universal convention. */}
      {dark
        ? <Sun  size={18} strokeWidth={2} />
        : <Moon size={18} strokeWidth={2} />}
    </button>
  );
}
