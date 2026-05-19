// Shimmer skeleton primitives — used in place of LoadingSpinner while
// the initial data fetch is in flight. Keeps layout stable and feels
// faster than a centered spinner.

import React from 'react';

// Base shimmer block. Pass tailwind sizing via className.
export function Skeleton({ className = '' }) {
  return (
    <div
      className={
        'relative overflow-hidden rounded-md bg-slate-200/70 dark:bg-slate-800/60 ' +
        'before:absolute before:inset-0 before:-translate-x-full before:animate-[shimmer_1.6s_infinite] ' +
        'before:bg-gradient-to-r before:from-transparent before:via-white/40 dark:before:via-white/5 before:to-transparent ' +
        className
      }
    />
  );
}

// Mirrors StockCard layout so the grid doesn't reflow when real data arrives.
export function StockCardSkeleton() {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5">
      <div className="flex items-start justify-between gap-2 mb-3">
        <div className="flex items-center gap-2.5 min-w-0">
          <Skeleton className="w-10 h-10 rounded-lg" />
          <Skeleton className="h-7 w-16" />
        </div>
        <Skeleton className="h-5 w-20 rounded-full" />
      </div>
      <Skeleton className="h-4 w-3/4 mb-2" />
      <Skeleton className="h-3 w-1/2 mb-5" />
      <Skeleton className="h-3 w-20 mb-2" />
      <Skeleton className="h-8 w-32 mb-4" />
      <div className="grid grid-cols-3 gap-2 pt-3 border-t border-slate-100 dark:border-slate-800">
        <div className="space-y-1.5"><Skeleton className="h-3 w-10" /><Skeleton className="h-4 w-14" /></div>
        <div className="space-y-1.5"><Skeleton className="h-3 w-10" /><Skeleton className="h-4 w-14" /></div>
        <div className="space-y-1.5"><Skeleton className="h-3 w-10" /><Skeleton className="h-4 w-14" /></div>
      </div>
    </div>
  );
}

export function StockGridSkeleton({ count = 8 }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mt-4">
      {Array.from({ length: count }).map((_, i) => <StockCardSkeleton key={i} />)}
    </div>
  );
}

// For the StockDetailPage initial load.
export function StockDetailSkeleton() {
  return (
    <div className="max-w-6xl mx-auto px-6 py-8 space-y-6">
      <Skeleton className="h-4 w-32" />
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="flex items-start gap-4">
            <Skeleton className="w-14 h-14 rounded-lg" />
            <div className="space-y-2">
              <Skeleton className="h-10 w-24" />
              <Skeleton className="h-6 w-64" />
              <Skeleton className="h-5 w-48" />
            </div>
          </div>
          <div className="space-y-2">
            <Skeleton className="h-3 w-20" />
            <Skeleton className="h-9 w-32" />
          </div>
        </div>
      </div>
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 space-y-3">
        <Skeleton className="h-6 w-40" />
        <Skeleton className="h-10 w-3/4" />
        <Skeleton className="h-24 w-full" />
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <Skeleton className="h-20" />
          <Skeleton className="h-20" />
          <Skeleton className="h-20" />
        </div>
      </div>
    </div>
  );
}
