// Language toggle button for the Navbar — switches between English and Arabic.
// Shows the *target* language's native name so the user knows what clicking
// will do (English mode → "العربية", Arabic mode → "English").

import React from 'react';
import { Languages } from 'lucide-react';
import { useLang } from '../../i18n/LanguageContext.jsx';

export default function LanguageToggle() {
  const { lang, setLang, t } = useLang();
  const targetLang  = lang === 'en' ? 'ar' : 'en';
  const buttonLabel = lang === 'en' ? 'العربية' : 'English';
  const tooltip     = lang === 'en' ? t('toggle.lang.toAr') : t('toggle.lang.toEn');

  return (
    <button
      onClick={() => setLang(targetLang)}
      title={tooltip}
      aria-label={tooltip}
      className="flex items-center gap-1.5 text-sm font-medium px-3 py-1.5 rounded-lg hover:bg-slate-700/60 transition text-slate-200"
    >
      <Languages size={16} strokeWidth={2} />
      {buttonLabel}
    </button>
  );
}
