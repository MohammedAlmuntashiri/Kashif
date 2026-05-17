// Loading indicator — CSS-animated spinner with a localized label.

import React from 'react';
import { useLang } from '../../i18n/LanguageContext.jsx';

export default function LoadingSpinner() {
  const { t } = useLang();
  return (
    <div className="flex items-center gap-3 text-slate-500 dark:text-slate-400 p-6">
      <div className="w-5 h-5 border-2 border-slate-300 dark:border-slate-600 border-t-brand-600 dark:border-t-brand-400 rounded-full animate-spin" />
      <span className="text-sm">{t('common.loading')}</span>
    </div>
  );
}
