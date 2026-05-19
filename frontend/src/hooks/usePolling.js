// usePolling — call a fetcher on mount, then re-call it every `intervalMs`
// until unmount. Background refetches do NOT clear `data`, so existing
// content stays on screen while new values silently replace it (no
// skeleton flash). Polling is paused while the browser tab is hidden so
// we don't waste calls on backgrounded tabs.

import { useEffect, useState, useRef } from 'react';

export function usePolling(fetcher, intervalMs, deps = []) {
  const [data,  setData]  = useState(null);
  const [error, setError] = useState(null);
  // Latest fetcher in a ref so the interval always calls the current one
  // without re-binding the interval on every render.
  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;

  useEffect(() => {
    let cancelled = false;

    const tick = () => {
      fetcherRef.current()
        .then((result) => {
          if (!cancelled) {
            setData(result);
            setError(null);
          }
        })
        .catch((e) => {
          // Keep showing the last good data; only surface error if we have
          // nothing on screen yet.
          if (!cancelled) setError(e.response?.data?.error || e.message);
        });
    };

    // Reset state when deps change (e.g. ticker switches on detail page).
    setData(null);
    setError(null);
    tick();

    const id = setInterval(() => {
      if (document.visibilityState === 'visible') tick();
    }, intervalMs);

    return () => {
      cancelled = true;
      clearInterval(id);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, intervalMs]);

  return { data, error };
}
