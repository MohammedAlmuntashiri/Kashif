// Tiny area chart rendered inside StockCard. Until we have a real
// historical price endpoint, the series is a deterministic random walk
// seeded from the ticker so the same stock always shows the same line.

import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Area, AreaChart, ResponsiveContainer } from 'recharts';

// Mulberry32 — fast, tiny seeded PRNG. We hash the ticker into a 32-bit
// seed so 2222 and 1120 don't collide.
function mulberry32(seed) {
  return function () {
    seed |= 0;
    seed = (seed + 0x6D2B79F5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function seedFromTicker(ticker) {
  let h = 2166136261;
  for (let i = 0; i < ticker.length; i++) {
    h ^= ticker.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

// Builds N points of a gentle random walk anchored on `anchor`. Range
// roughly ±10% with smoother trend, so the chart reads as a real series.
function buildSeries({ ticker, anchor = 100, days = 30 }) {
  const rand = mulberry32(seedFromTicker(ticker));
  const drift = (rand() - 0.5) * 0.04;  // -2% .. +2% bias per series
  const points = [];
  let v = anchor * (0.92 + rand() * 0.16);
  for (let i = 0; i < days; i++) {
    const shock = (rand() - 0.5) * 0.03;  // ±1.5% daily
    v = v * (1 + drift + shock);
    points.push({ i, v });
  }
  return points;
}

export default function Sparkline({ ticker, anchor, height = 44 }) {
  const data = useMemo(
    () => buildSeries({ ticker, anchor: anchor || 100 }),
    [ticker, anchor],
  );

  const first = data[0]?.v ?? 0;
  const last  = data[data.length - 1]?.v ?? 0;
  const up    = last >= first;

  // Match emerald (up) and rose (down) — tailwind 500-ish.
  const stroke = up ? '#10b981' : '#f43f5e';
  const fillId = `spark-${ticker}-${up ? 'up' : 'dn'}`;

  // Defer mounting the recharts SVG until the placeholder scrolls into view.
  // 49 stock cards × an off-screen recharts tree was the main jank source on
  // the HomePage. Once visible, the chart stays mounted forever.
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    if (visible) return;
    if (typeof IntersectionObserver === 'undefined') {
      setVisible(true);
      return;
    }
    const node = ref.current;
    if (!node) return;
    const io = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) {
          setVisible(true);
          io.disconnect();
        }
      },
      { rootMargin: '200px 0px' },  // start rendering just before it scrolls in
    );
    io.observe(node);
    return () => io.disconnect();
  }, [visible]);

  return (
    <div ref={ref} style={{ width: '100%', height }} aria-hidden>
      {visible && (
        <ResponsiveContainer>
          <AreaChart data={data} margin={{ top: 2, right: 0, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id={fillId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%"   stopColor={stroke} stopOpacity={0.35} />
                <stop offset="100%" stopColor={stroke} stopOpacity={0} />
              </linearGradient>
            </defs>
            <Area
              type="monotone"
              dataKey="v"
              stroke={stroke}
              strokeWidth={1.75}
              fill={`url(#${fillId})`}
              isAnimationActive={false}
              dot={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

// Helper used by callers that want the directional delta to show a
// matching ▲/▼ badge alongside the chart.
export function deltaForTicker(ticker, anchor = 100, days = 30) {
  const series = buildSeries({ ticker, anchor, days });
  const first = series[0]?.v ?? 0;
  const last  = series[series.length - 1]?.v ?? 0;
  if (!first) return { pct: 0, up: true };
  const pct = ((last - first) / first) * 100;
  return { pct, up: pct >= 0 };
}
