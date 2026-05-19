// Inline PDF-upload form for the StockDetailPage — PREVIEW ONLY.

import React, { useMemo, useState } from 'react';
import { toast } from 'sonner';
import { uploadPdf, downloadExtractionReport } from '../../services/api.js';
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

// Classify the relative difference between extracted and DB value.
// "match" = ≤1%, "warn" = 1-10%, "bad" = >10%, "missing" = one side null.
function classifyDiff(extracted, db) {
  if (extracted == null && db == null) return { kind: 'missing', pct: null };
  if (extracted == null || db == null)  return { kind: 'missing', pct: null };
  const a = Number(extracted), b = Number(db);
  if (!isFinite(a) || !isFinite(b))     return { kind: 'missing', pct: null };
  if (Math.abs(b) < 1e-9)               return { kind: a === 0 ? 'match' : 'bad', pct: null };
  const pct = Math.abs(a - b) / Math.abs(b) * 100;
  if (pct <= 1)  return { kind: 'match', pct };
  if (pct <= 10) return { kind: 'warn',  pct };
  return { kind: 'bad', pct };
}

// Browser-side file download — Blob + temporary anchor click.
function downloadFile(filename, content, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// Escape a single cell for safe CSV output (RFC 4180 quoting).
const csvCell = (v) => {
  const s = v == null ? '' : String(v);
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};

function buildCSV(ticker, result) {
  const lines = [
    ['ticker', 'period', 'field', 'db_value', 'extracted_value', 'match', 'diff_pct'].map(csvCell).join(','),
  ];
  for (const field of FIELD_KEYS) {
    const info = result.db_comparison[field];
    if (!info) continue;
    const { pct } = classifyDiff(info.extracted, info.db);
    lines.push([
      ticker,
      result.period || '',
      field,
      info.db,
      info.extracted,
      info.match ? 'yes' : 'no',
      pct == null ? '' : pct.toFixed(2),
    ].map(csvCell).join(','));
  }
  return lines.join('\n') + '\n';
}

export default function UploadSection({ ticker }) {
  const { t } = useLang();
  const [file,   setFile]   = useState(null);
  const [busy,   setBusy]   = useState(false);
  const [result, setResult] = useState(null);
  const [error,  setError]  = useState(null);
  const [reportBusy, setReportBusy] = useState(null);  // 'en' | 'ar' | null

  // Roll-up counts shown as chips above the table.
  const summary = useMemo(() => {
    if (!result) return null;
    let match = 0, mismatch = 0, missing = 0;
    for (const field of FIELD_KEYS) {
      const info = result.db_comparison[field];
      if (!info) continue;
      const { kind } = classifyDiff(info.extracted, info.db);
      if (kind === 'missing')      missing++;
      else if (kind === 'match')   match++;
      else                         mismatch++;
    }
    return { match, mismatch, missing, total: match + mismatch + missing };
  }, [result]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || busy) return;

    setBusy(true);
    setError(null);
    setResult(null);

    try {
      const r = await uploadPdf(ticker, file, { dryRun: true });
      setResult(r);
      toast.success(t('up.toast.success', { period: r?.period || '—' }));
    } catch (e) {
      const msg = e.response?.data?.error || e.message || t('up.failed');
      setError(msg);
      toast.error(msg);
    } finally {
      setBusy(false);
    }
  };

  // Filename stem shared by both download formats.
  const downloadBase = result
    ? `kashif_${ticker}_${(result.period || 'extract').replace(/\s+/g, '_')}`
    : null;

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
          className="px-4 py-1.5 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-500 disabled:bg-slate-300 dark:disabled:bg-slate-700 dark:disabled:text-slate-500 disabled:cursor-not-allowed transition"
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
          <div className="text-sm text-slate-700 dark:text-slate-300 mb-3 flex flex-wrap items-center gap-2">
            <span className="font-semibold">{t('up.extractedValues')}</span>
            <span className="text-slate-400">•</span>
            <span>
              {t('up.period')}: <code className="bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded text-xs" dir="ltr">{result.period}</code>
            </span>
            {result.is_new_row && (
              <span className="text-xs text-brand-700 dark:text-brand-300 bg-brand-50 dark:bg-brand-950/40 px-2 py-0.5 rounded-full">
                {t('up.noDbRow')}
              </span>
            )}
          </div>

          {/* Summary chips — quick at-a-glance counts. */}
          {summary && (
            <div className="flex flex-wrap gap-2 mb-3">
              <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-900/40 text-emerald-800 dark:text-emerald-300 font-medium">
                {t('up.summary.match', { n: summary.match })}
              </span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-rose-100 dark:bg-rose-900/40 text-rose-800 dark:text-rose-300 font-medium">
                {t('up.summary.mismatch', { n: summary.mismatch })}
              </span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium">
                {t('up.summary.missing', { n: summary.missing })}
              </span>
            </div>
          )}

          <div className="overflow-x-auto bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-700">
                  <th className="text-start  py-2.5 px-3 text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300">{t('up.col.field')}</th>
                  <th className="text-right  py-2.5 px-3 text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300">{t('up.col.dbValue')}</th>
                  <th className="text-right  py-2.5 px-3 text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300">{t('up.col.extracted')}</th>
                  <th className="text-right  py-2.5 px-3 text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300">{t('up.col.diff')}</th>
                  <th className="text-center py-2.5 px-3 text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300">{t('up.col.match')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {FIELD_KEYS.map((field) => {
                  const info = result.db_comparison[field];
                  if (!info) return null;
                  const fmt = FIELD_FORMATTERS[field];
                  const { kind, pct } = classifyDiff(info.extracted, info.db);

                  // Color the diff cell so the eye can find big gaps fast.
                  const diffColor =
                    kind === 'match' ? 'text-emerald-600 dark:text-emerald-400' :
                    kind === 'warn'  ? 'text-amber-600  dark:text-amber-400'  :
                    kind === 'bad'   ? 'text-rose-600   dark:text-rose-400'   :
                                       'text-slate-400  dark:text-slate-500';

                  return (
                    <tr key={field} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                      <td className="py-2.5 px-3 font-medium text-slate-700 dark:text-slate-300">{t(`fin.${field}`)}</td>
                      <td className="py-2.5 px-3 text-right tabular-nums whitespace-nowrap text-slate-900 dark:text-slate-100" dir="ltr">
                        {fmt(info.db)}
                      </td>
                      <td className="py-2.5 px-3 text-right tabular-nums whitespace-nowrap text-slate-900 dark:text-slate-100" dir="ltr">
                        {fmt(info.extracted)}
                      </td>
                      <td className={`py-2.5 px-3 text-right tabular-nums whitespace-nowrap font-medium ${diffColor}`} dir="ltr">
                        {pct == null ? '—' : `${pct.toFixed(2)}%`}
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

          {/* Download buttons — CSV/JSON are built client-side; the PDF
              report is generated server-side via /api/pdf/report. */}
          <div className="flex flex-wrap gap-2 mt-3">
            <button
              type="button"
              onClick={() => downloadFile(`${downloadBase}.csv`, buildCSV(ticker, result), 'text/csv;charset=utf-8;')}
              className="text-xs px-3 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-lg font-medium transition"
            >
              {t('up.download.csv')}
            </button>
            <button
              type="button"
              onClick={() => downloadFile(`${downloadBase}.json`, JSON.stringify(result, null, 2), 'application/json;charset=utf-8;')}
              className="text-xs px-3 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-lg font-medium transition"
            >
              {t('up.download.json')}
            </button>
            {['en', 'ar'].map((reportLang) => (
              <button
                key={reportLang}
                type="button"
                disabled={!!reportBusy}
                onClick={async () => {
                  setReportBusy(reportLang);
                  try {
                    const blob = await downloadExtractionReport(ticker, result, file?.name, reportLang);
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `${downloadBase}_${reportLang}.pdf`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                  } catch (e) {
                    toast.error(e.response?.data?.error || e.message || t('up.download.reportFailed'));
                  } finally {
                    setReportBusy(null);
                  }
                }}
                className="text-xs px-3 py-1.5 bg-brand-600 hover:bg-brand-500 text-white rounded-lg font-medium transition disabled:bg-slate-300 dark:disabled:bg-slate-700 dark:disabled:text-slate-500 disabled:cursor-not-allowed"
              >
                {reportBusy === reportLang
                  ? t('up.download.reportBusy')
                  : t(reportLang === 'ar' ? 'up.download.reportAr' : 'up.download.reportEn')}
              </button>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
