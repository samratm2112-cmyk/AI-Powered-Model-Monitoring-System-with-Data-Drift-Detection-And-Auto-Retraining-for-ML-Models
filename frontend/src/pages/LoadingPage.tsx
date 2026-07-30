import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingPage: React.FC = () => {
  return (
    <div className="min-h-[400px] flex flex-col items-center justify-center space-y-4">
      <Loader2 className="w-8 h-8 text-brand-600 animate-spin" />
      <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
        Connecting to Backend & Loading Pipeline Data...
      </p>
    </div>
  );
};
