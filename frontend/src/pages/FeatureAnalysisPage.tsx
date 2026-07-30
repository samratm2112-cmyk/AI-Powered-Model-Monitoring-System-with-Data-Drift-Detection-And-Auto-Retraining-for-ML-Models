import React from 'react';
import { BarChart3 } from 'lucide-react';

export const FeatureAnalysisPage: React.FC = () => {
  return (
    <div className="p-8 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm text-center space-y-3">
      <BarChart3 className="w-10 h-10 text-brand-600 dark:text-brand-400 mx-auto" />
      <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100">Feature Analysis Page</h3>
      <p className="text-sm text-slate-500 dark:text-slate-400">
        Placeholder route for Shifted Feature Frequency and importance rankings.
      </p>
    </div>
  );
};
