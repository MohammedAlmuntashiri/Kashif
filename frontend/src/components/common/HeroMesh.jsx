// Animated gradient-mesh backdrop for the home hero.
//
// Three layered radial blobs in emerald/teal that drift slowly via the
// `mesh-drift` keyframe (registered in tailwind.config.js). Lives behind
// the hero with `-z-10`; the parent must set position: relative.

import React from 'react';

export default function HeroMesh() {
  return (
    <div
      aria-hidden
      className="pointer-events-none absolute inset-x-0 -top-24 h-[540px] -z-10 overflow-hidden"
    >
      {/* Soft canvas tint so the blobs blend on both themes */}
      <div className="absolute inset-0 bg-gradient-to-b from-brand-50/70 via-white/0 to-transparent dark:from-brand-950/40 dark:via-slate-950/0" />

      {/* Blob 1 — primary emerald */}
      <div
        className="absolute -top-24 -left-20 w-[520px] h-[520px] rounded-full opacity-60 dark:opacity-40 blur-3xl animate-mesh-drift"
        style={{
          background: 'radial-gradient(circle at 30% 30%, #10b981 0%, transparent 65%)',
        }}
      />
      {/* Blob 2 — teal accent, opposite corner */}
      <div
        className="absolute -top-10 right-[-120px] w-[480px] h-[480px] rounded-full opacity-50 dark:opacity-35 blur-3xl animate-mesh-drift"
        style={{
          background: 'radial-gradient(circle at 60% 40%, #14b8a6 0%, transparent 60%)',
          animationDelay: '-6s',
        }}
      />
      {/* Blob 3 — lime sparkle, low center */}
      <div
        className="absolute top-40 left-1/3 w-[420px] h-[420px] rounded-full opacity-40 dark:opacity-25 blur-3xl animate-mesh-drift"
        style={{
          background: 'radial-gradient(circle at 50% 50%, #84cc16 0%, transparent 60%)',
          animationDelay: '-12s',
        }}
      />

      {/* Faint dot grid on top to keep the original texture vibe */}
      <div
        className="absolute inset-0 opacity-40 dark:opacity-25"
        style={{
          backgroundImage:
            'radial-gradient(circle at 1px 1px, rgba(16,185,129,0.35) 1px, transparent 0)',
          backgroundSize: '24px 24px',
          maskImage:
            'radial-gradient(ellipse 65% 55% at 50% 30%, black 35%, transparent 75%)',
          WebkitMaskImage:
            'radial-gradient(ellipse 65% 55% at 50% 30%, black 35%, transparent 75%)',
        }}
      />
    </div>
  );
}
