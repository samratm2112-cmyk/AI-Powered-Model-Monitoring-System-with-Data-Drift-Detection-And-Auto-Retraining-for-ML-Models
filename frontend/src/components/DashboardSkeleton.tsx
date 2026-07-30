import React from 'react';

export const DashboardSkeleton: React.FC = () => {
  return (
    <div className="space-y-8 animate-pulse pb-10">
      {/* Hero Skeleton */}
      <div className="h-44 rounded-2xl bg-slate-200 dark:bg-slate-800/60 w-full"></div>

      {/* KPI Cards Grid Skeleton */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="h-32 rounded-xl bg-slate-200 dark:bg-slate-800/60 p-5 space-y-3">
            <div className="flex justify-between items-center">
              <div className="h-4 bg-slate-300 dark:bg-slate-700 rounded w-1/2"></div>
              <div className="w-8 h-8 rounded-lg bg-slate-300 dark:bg-slate-700"></div>
            </div>
            <div className="h-8 bg-slate-300 dark:bg-slate-700 rounded w-1/3 mt-2"></div>
            <div className="h-3 bg-slate-300 dark:bg-slate-700 rounded w-3/4"></div>
          </div>
        ))}
      </div>

      {/* Charts Grid Skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="h-80 rounded-xl bg-slate-200 dark:bg-slate-800/60 p-6"></div>
        <div className="lg:col-span-2 h-80 rounded-xl bg-slate-200 dark:bg-slate-800/60 p-6"></div>
      </div>

      {/* Stats Skeleton */}
      <div className="h-32 rounded-xl bg-slate-200 dark:bg-slate-800/60 p-6"></div>
    </div>
  );
};
