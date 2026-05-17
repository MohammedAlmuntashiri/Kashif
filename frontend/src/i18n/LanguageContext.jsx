// React Context for the active UI language (en/ar).
//
// Exposes:
//   - lang        — current language code, 'en' or 'ar'
//   - setLang     — switch language and persist to localStorage
//   - t(key, vars) — translate a key with optional {placeholder} interpolation
//   - tSector(name) — translate a backend sector name (English → Arabic when applicable)
//   - dir         — convenience: 'ltr' or 'rtl' based on language
//
// Persistence: localStorage 'lang' key. On first visit, falls back to
// the browser language if Arabic, else English.

import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { translations, sectorAr } from './translations.js';

const LanguageContext = createContext({
  lang: 'en',
  setLang: () => {},
  t: (k) => k,
  tSector: (n) => n,
  dir: 'ltr',
});

// Pick the initial language: localStorage > browser language > English.
function pickInitialLang() {
  try {
    const saved = localStorage.getItem('lang');
    if (saved === 'en' || saved === 'ar') return saved;
  } catch (_) { /* localStorage blocked — ignore */ }

  if (typeof navigator !== 'undefined' && navigator.language) {
    if (navigator.language.toLowerCase().startsWith('ar')) return 'ar';
  }
  return 'en';
}

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState(pickInitialLang);

  // Whenever the language changes:
  //   - flip <html dir> so Tailwind's ms-/me- utilities mirror correctly
  //   - update <html lang> for accessibility / browser hints
  //   - persist the choice to localStorage
  useEffect(() => {
    const root = document.documentElement;
    root.lang = lang;
    root.dir  = lang === 'ar' ? 'rtl' : 'ltr';
    try { localStorage.setItem('lang', lang); } catch (_) {}
  }, [lang]);

  // Translation helpers. Wrapped in useMemo so the context value reference
  // is stable across re-renders when nothing has changed.
  const value = useMemo(() => {
    const dict = translations[lang] || translations.en;

    // t('home.subtitle', { count: 8, sectors: 7 })
    //   → '8 stocks across 7 sectors'
    function t(key, vars) {
      let str = dict[key];
      if (str === undefined) return key;     // missing key — show it raw so we notice
      if (!vars) return str;
      for (const [k, v] of Object.entries(vars)) {
        str = str.replace(new RegExp(`\\{${k}\\}`, 'g'), v);
      }
      return str;
    }

    // Translate a backend sector name. Backend always sends English.
    function tSector(name) {
      if (lang === 'ar' && sectorAr[name]) return sectorAr[name];
      return name;
    }

    return {
      lang,
      setLang,
      t,
      tSector,
      dir: lang === 'ar' ? 'rtl' : 'ltr',
    };
  }, [lang]);

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

// Hook for components to consume the context.
// Usage: const { t, lang, setLang } = useLang();
export const useLang = () => useContext(LanguageContext);
