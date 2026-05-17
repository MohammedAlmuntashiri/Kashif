// Inline PDF-upload form for the StockDetailPage — PREVIEW ONLY.

import React, { useState } from 'react';
import { uploadPdf } from '../../services/api.js';
import {
  formatSAR,
  formatSARPerShare,
  formatShares,
} from '../../utils/format.js';
import { useLang } from '../../i18n/LanguageContext.jsx';

const FIELD_FORMATTERS = {
  revenue:              formatSAR,
  net_income:           formatSAR,
  eps:                  formatSARPerShare,
  total_assets:         formatSAR,
  total_borrowings:     formatSAR,
  shareholders_equity:  formatSAR,
  cash_and_equivalents: formatSAR,
  free_cash_flow:       formatSAR,
  dividends_per_share:  formatSARPerShare,
  shares_outstanding:   formatShares,
};

// Field keys here match both backend names AND translation keys
// (fin.<key>) — same convention as FinancialTable.
const FIELD_KEYS = Object.keys(FIELD_FORMATTERS);

export default function UploadSection({ ticker }) {
  const { t } = useLang();
  const [file,   setFile]   = useState(null);
  const [busy,   setBusy]   = useState(false);
  const [result, setResult] = useState(null);
  const [error,  setError]  = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || busy) return;

    setBusy(true);
    setError(null);
    setResult(null);

    try {
      const r = await uploadPdf(ticker, file, { dryRun: true });
      setResult(r);
    } catch (e) {
      setError(e.response?.data?.error || e.message || t('up.failed'));
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm">
      <div className="flex items-center gap-2 mb-1 flex-wrap">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{t('up.title')}</h2>
        <span className="text-xs bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-300 px-2 py-0.5 rounded-full font-medium">
          {t('up.previewOnly')}
        </span>
      </div>
      <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
        {t('up.description', { ticker })}
      </p>

      <form onSubmit={handleSubmit} className="flex flex-wrap items-center gap-3 mb-3">
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files[0] || null)}
          className="text-sm text-slate-700 dark:text-slate-300
                     file:mr-3 file:py-1.5 file:px-4
                     file:rounded-lg file:border-0
                     file:text-sm file:font-medium
                     file:bg-slate-100 dark:file:bg-slate-800
                     file:text-slate-700 dark:file:text-slate-200
                     hover:file:bg-slate-200 dark:hover:file:bg-slate-700
                     file:cursor-pointer cursor-pointer"
        />

        <button
          type="submit"
          disabled={!file || busy}
          className="px-4 py-1.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-500 disabled:bg-slate-300 dark:disabled:bg-slate-700 dark:disabled:text-slate-500 disabled:cursor-not-allowed transition"
        >
          {busy ? t('up.extracting') : t('up.extract')}
        </button>
      </form>

      {error && (
        <div className="text-rose-700 dark:text-rose-300 text-sm bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/50 p-3 rounded-lg">
          {error}
        </div>
      )}

      {result && (
        <div className="border-t border-slate-200 dark:border-slate-800 pt-4 mt-4">
          <div className="text-sm text-slate-700 dark:text-slate-300 mb-3">
            <span className="font-semibold">{t('up.extractedValues')}</span>
            <span className="mx-2 text-slate-400">•</span>
            {t('up.period')}: <code className="bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded text-xs" dir="ltr">{result.period}</code>
            {result.is_new_row && (
              <span className="ms-2 text-xs text-blue-700 dark:text-blue-300 bg-blue-50 dark:bg-blue-950/40 px-2 py-0.5 rounded-full">
                {t('up.noDbRow')}
              </span>
            )}
          </div>

          <div className="overflow-x-auto bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-700">
                  <th className="text-start py-2.5 px-3 text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300">{t('up.col.field')}</th>
                  <th className="text-end   py-2.5 px-3 text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300">{t('up.col.dbValue')}</th>
                  <th className="text-end   py-2.5 px-3 text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300">{t('up.col.extracted')}</th>
                  <th className="text-center py-2.5 px-3 text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300">{t('up.col.match')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {FIELD_KEYS.map((field) => {
                  const info = result.db_comparison[field];
                  if (!info) return null;
                  const fmt = FIELD_FORMATTERS[field];
                  return (
                    <tr key={field} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                      <td className="py-2.5 px-3 font-medium text-slate-700 dark:text-slate-300">{t(`fin.${field}`)}</td>
                      <td className="py-2.5 px-3 text-end tabular-nums whitespace-nowrap text-slate-900 dark:text-slate-100" dir="ltr">
                        {fmt(info.db)}
                      </td>
                      <td className="py-2.5 px-3 text-end tabular-nums whitespace-nowrap text-slate-900 dark:text-slate-100" dir="ltr">
                        {fmt(info.extracted)}
                      </td>
                      <td
                        className={`py-2.5 px-3 text-center font-bold ${
                          info.match
                            ? 'text-emerald-600 dark:text-emerald-400'
                            : 'text-rose-600 dark:text-rose-400'
                        }`}
                      >
                        {info.match ? '✓' : '✗'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  );
}
