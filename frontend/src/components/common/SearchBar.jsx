// Ticker search box. Submitting navigates to /stock/<ticker>.

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLang } from '../../i18n/LanguageContext.jsx';

export default function SearchBar() {
  const [value, setValue] = useState('');
  const navigate = useNavigate();
  const { t } = useLang();

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed) return;
    navigate(`/stock/${trimmed}`);
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={t('search.placeholder')}
        // Ticker codes are always Latin digits — force LTR so the cursor
        // and digits don't flip when the page is in Arabic mode.
        dir="ltr"
        className="px-3 py-1.5 rounded-lg bg-slate-800 text-white placeholder:text-slate-500 text-sm w-56 focus:outline-none focus:ring-2 focus:ring-blue-500 border border-slate-700"
      />
      <button
        type="submit"
        className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition"
      >
        {t('search.go')}
      </button>
    </form>
  );
}
