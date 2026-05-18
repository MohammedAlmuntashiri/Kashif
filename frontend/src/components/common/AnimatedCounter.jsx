// Smooth count-up for KPI numerics. Falls back to plain text when the
// value isn't a finite number (e.g., already-formatted strings like "1.2B").

import React, { useEffect, useRef } from 'react';
import { animate, useInView } from 'framer-motion';

export default function AnimatedCounter({
  value,
  duration = 1.2,
  format = (n) => Math.round(n).toLocaleString('en-US'),
  className = '',
}) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '0px 0px -20% 0px' });

  useEffect(() => {
    if (!ref.current || !inView) return;
    if (typeof value !== 'number' || !Number.isFinite(value)) {
      ref.current.textContent = String(value ?? '');
      return;
    }
    const controls = animate(0, value, {
      duration,
      ease: [0.16, 1, 0.3, 1],
      onUpdate: (latest) => {
        if (ref.current) ref.current.textContent = format(latest);
      },
    });
    return () => controls.stop();
  }, [value, inView, duration, format]);

  return <span ref={ref} className={className}>{format(0)}</span>;
}
