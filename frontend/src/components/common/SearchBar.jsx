// Ticker search box with live typeahead.
//
// As soon as the user types one character we filter the full stock list
// by symbol, English name, or Arabic name and show up to 8 matches in a
// dropdown. Arrow keys move the highlight, Enter navigates to the
// highlighted match (or to /stock/<raw value> if there are no matches),
// Escape closes the dropdown, and clicking outside also closes it.

import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';
import { getStocks } from '../../services/api.js';
import { useLang } from '../../i18n/LanguageContext.jsx';

const MAX_SUGGESTIONS = 8;

export default function SearchBar() {
  const navigate = useNavigate();
  const { t, lang } = useLang();

  const [value, setValue]               = useState('');
  const [stocks, setStocks]             = useState([]);
  const [open, setOpen]                 = useState(false);
  const [highlight, setHighlight]       = useState(0);

  const wrapperRef = useRef(null);

  // Load the full stock list once. Cheap — the list endpoint is summary-only
  // and we already pay this cost on the home page.
  useEffect(() => {
    let alive = true;
    getStocks()
      .then((rows) => { if (alive) setStocks(rows || []); })
      .catch(() => { /* ignore — search just falls back to raw-text navigation */ });
    return () => { alive = false; };
  }, []);

  // Close dropdown on outside click.
  useEffect(() => {
    const onClick = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, []);

  // Filter logic: match symbol prefix OR substring in either name.
  const suggestions = useMemo(() => {
    const q = value.trim().toLowerCase();
    if (!q) return [];

    const scored = [];
    for (const s of stocks) {
      const sym = (s.symbol || '').toLowerCase();
      const en  = (s.name_en || '').toLowerCase();
      const ar  = (s.name_ar || '');

      let score = -1;
      if (sym.startsWith(q))      score = 0;   // best: ticker prefix
      else if (sym.includes(q))   score = 1;
      else if (en.startsWith(q))  score = 2;
      else if (en.includes(q))    score = 3;
      else if (ar.includes(value.trim())) score = 4;  // arabic — case n/a

      if (score >= 0) scored.push({ s, score });
    }

    scored.sort((a, b) => a.score - b.score || a.s.symbol.localeCompare(b.s.symbol));
    return scored.slice(0, MAX_SUGGESTIONS).map((x) => x.s);
  }, [value, stocks]);

  // Reset highlight whenever the suggestion list changes.
  useEffect(() => { setHighlight(0); }, [suggestions]);

  const go = (ticker) => {
    const trimmed = (ticker || '').trim();
    if (!trimmed) return;
    navigate(`/stock/${encodeURIComponent(trimmed)}`);
    setValue('');
    setOpen(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (suggestions.length > 0) {
      go(suggestions[highlight]?.symbol || suggestions[0].symbol);
    } else {
      go(value);
    }
  };

  const handleKeyDown = (e) => {
    if (!open || suggestions.length === 0) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlight((h) => (h + 1) % suggestions.length);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlight((h) => (h - 1 + suggestions.length) % suggestions.length);
    } else if (e.key === 'Escape') {
      setOpen(false);
    }
  };

  return (
    <div ref={wrapperRef} className="relative">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="relative">
          <Search
            size={16}
            className="absolute start-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none"
          />
          <input
            type="text"
            value={value}
            onChange={(e) => { setValue(e.target.value); setOpen(true); }}
            onFocus={() => setOpen(true)}
            onKeyDown={handleKeyDown}
            placeholder={t('search.placeholder')}
            // Ticker codes are always Latin digits — force LTR so the cursor
            // and digits don't flip when the page is in Arabic mode.
            dir="ltr"
            className="ps-9 pe-3 py-1.5 rounded-lg bg-slate-800/70 text-white placeholder:text-slate-500 text-sm w-56 focus:outline-none focus:ring-2 focus:ring-brand-500 border border-slate-700"
          />
        </div>
        <button
          type="submit"
          className="px-4 py-1.5 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-sm font-medium transition"
        >
          {t('search.go')}
        </button>
      </form>

      {open && value.trim() && (
        <div
          className="absolute z-50 mt-1 w-72 max-h-80 overflow-y-auto rounded-lg shadow-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700"
          // The dropdown content (ticker + names) is mixed-direction; let
          // each row decide.
        >
          {suggestions.length === 0 ? (
            <div className="px-3 py-3 text-sm text-slate-500 dark:text-slate-400 italic">
              {t('search.noMatches') || 'No matches'}
            </div>
          ) : (
            suggestions.map((s, i) => {
              const primary   = lang === 'ar' ? s.name_ar : s.name_en;
              const secondary = lang === 'ar' ? s.name_en : s.name_ar;
              const secDir    = lang === 'ar' ? 'ltr' : 'rtl';
              const isActive  = i === highlight;
              return (
                <button
                  key={s.symbol}
                  type="button"
                  onMouseEnter={() => setHighlight(i)}
                  onMouseDown={(e) => { e.preventDefault(); go(s.symbol); }}
                  className={`w-full text-start px-3 py-2 flex items-center gap-3 border-b border-slate-100 dark:border-slate-800 last:border-b-0 transition ${
                    isActive
                      ? 'bg-brand-50 dark:bg-brand-950/40'
                      : 'hover:bg-slate-50 dark:hover:bg-slate-800/60'
                  }`}
                >
                  <span
                    className="text-xs font-bold tabular-nums bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 px-2 py-0.5 rounded-md"
                    dir="ltr"
                  >
                    {s.symbol}
                  </span>
                  <span className="flex-1 min-w-0">
                    <span className="block text-sm font-medium text-slate-900 dark:text-slate-100 truncate">
                      {primary || s.name_en || s.name_ar}
                    </span>
                    {secondary && (
                      <span
                        className="block text-xs text-slate-500 dark:text-slate-400 truncate"
                        dir={secDir}
                      >
                        {secondary}
                      </span>
                    )}
                  </span>
                </button>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}
