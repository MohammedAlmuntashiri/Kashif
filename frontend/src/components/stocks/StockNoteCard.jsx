// Per-user freeform note attached to a stock. Only renders when signed in.
// Auto-saves on blur (or when the user clicks Save). Empty content
// deletes the note from the server side.

import React, { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { StickyNote } from 'lucide-react';

import { useAuth } from '../../auth/AuthContext.jsx';
import { useLang } from '../../i18n/LanguageContext.jsx';
import { fetchNote, saveNote } from '../../services/api.js';

export default function StockNoteCard({ ticker }) {
  const { user } = useAuth();
  const { t } = useLang();

  const [content, setContent] = useState('');
  const [savedContent, setSavedContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [updatedAt, setUpdatedAt] = useState(null);

  // Load the user's existing note when the ticker (or auth) changes.
  useEffect(() => {
    if (!user) return;
    let cancelled = false;
    setLoading(true);
    fetchNote(ticker)
      .then((data) => {
        if (cancelled) return;
        setContent(data.content || '');
        setSavedContent(data.content || '');
        setUpdatedAt(data.updated_at);
      })
      .catch(() => { /* swallow — empty note is a fine starting state */ })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [user, ticker]);

  if (!user) return null;

  const dirty = content !== savedContent;

  const handleSave = async () => {
    if (busy) return;
    setBusy(true);
    try {
      const data = await saveNote(ticker, content);
      setSavedContent(data.content || '');
      setUpdatedAt(data.updated_at);
      toast.success(t('notes.saved'));
    } catch (e) {
      toast.error(e.response?.data?.error || e.message || t('notes.saveFailed'));
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm">
      <div className="flex items-center gap-2 mb-3 flex-wrap">
        <StickyNote size={18} strokeWidth={2} className="text-amber-500" />
        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
          {t('notes.title')}
        </h2>
        {updatedAt && (
          <span className="text-xs text-slate-400 dark:text-slate-500 ms-auto" dir="ltr">
            {t('notes.lastSaved')}: {new Date(updatedAt).toLocaleString()}
          </span>
        )}
      </div>

      {loading ? (
        <div className="h-32 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />
      ) : (
        <>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            onBlur={() => { if (dirty) handleSave(); }}
            placeholder={t('notes.placeholder')}
            maxLength={8000}
            rows={6}
            className="w-full p-3 text-sm text-slate-900 dark:text-slate-100 bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-lg resize-y focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent placeholder:text-slate-400 dark:placeholder:text-slate-500"
          />
          <div className="flex items-center justify-between mt-2">
            <span className="text-xs text-slate-400 dark:text-slate-500">
              {content.length} / 8000
            </span>
            <button
              type="button"
              disabled={!dirty || busy}
              onClick={handleSave}
              className="text-xs px-3 py-1.5 bg-brand-600 hover:bg-brand-500 text-white rounded-lg font-medium transition disabled:bg-slate-300 dark:disabled:bg-slate-700 dark:disabled:text-slate-500 disabled:cursor-not-allowed"
            >
              {busy ? t('notes.saving') : (dirty ? t('notes.save') : t('notes.saved'))}
            </button>
          </div>
        </>
      )}
    </section>
  );
}
