// Star toggle for adding/removing a stock from the signed-in user's watchlist.
// Renders nothing for signed-out users — the auth gate lives in this component
// so callers don't need to check `useAuth().user` themselves.

import React, { useEffect, useState } from 'react';
import { Star } from 'lucide-react';
import { toast } from 'sonner';

import { useAuth } from '../../auth/AuthContext.jsx';
import { useLang } from '../../i18n/LanguageContext.jsx';
import {
  fetchWatchlist,
  addToWatchlist,
  removeFromWatchlist,
} from '../../services/api.js';

// Cache the set of starred tickers in module scope so flipping between
// HomePage cards doesn't trigger N parallel GETs. We invalidate on every
// mutation and refresh from the server.
let _cache = null;
const _subscribers = new Set();
function _publish() {
  for (const fn of _subscribers) fn();
}
async function _refresh() {
  try {
    const rows = await fetchWatchlist();
    _cache = new Set(rows.map((r) => r.symbol));
  } catch {
    _cache = new Set();
  }
  _publish();
}

export default function WatchlistStar({ symbol, size = 18 }) {
  const { user } = useAuth();
  const { t } = useLang();
  const [busy, setBusy] = useState(false);
  const [watched, setWatched] = useState(false);

  useEffect(() => {
    if (!user) return;
    const sync = () => setWatched(_cache?.has(symbol) || false);
    _subscribers.add(sync);
    if (_cache === null) {
      _refresh();
    } else {
      sync();
    }
    return () => { _subscribers.delete(sync); };
  }, [user, symbol]);

  if (!user) return null;

  const handleToggle = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (busy) return;
    setBusy(true);
    const wasWatched = watched;
    // Optimistic update — flip immediately, roll back on failure.
    setWatched(!wasWatched);
    try {
      if (wasWatched) {
        await removeFromWatchlist(symbol);
        _cache?.delete(symbol);
      } else {
        await addToWatchlist(symbol);
        _cache?.add(symbol);
      }
      _publish();
    } catch (err) {
      setWatched(wasWatched);
      toast.error(err.response?.data?.error || err.message || t('watchlist.toggleFailed'));
    } finally {
      setBusy(false);
    }
  };

  return (
    <button
      type="button"
      onClick={handleToggle}
      disabled={busy}
      title={watched ? t('watchlist.removeTooltip') : t('watchlist.addTooltip')}
      aria-label={watched ? t('watchlist.removeTooltip') : t('watchlist.addTooltip')}
      className={`inline-flex items-center justify-center rounded-md p-1 transition
        ${watched
          ? 'text-amber-400 hover:text-amber-300'
          : 'text-slate-400 hover:text-amber-400'}
        ${busy ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      <Star
        size={size}
        strokeWidth={2}
        fill={watched ? 'currentColor' : 'none'}
      />
    </button>
  );
}
