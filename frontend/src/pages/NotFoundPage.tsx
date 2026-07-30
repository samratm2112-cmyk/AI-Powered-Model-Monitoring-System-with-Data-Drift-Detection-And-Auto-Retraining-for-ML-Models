import React from 'react';
import { Link } from 'react-router-dom';
import { FileQuestion, ArrowLeft } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-[400px] flex flex-col items-center justify-center space-y-4 text-center">
      <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500 flex items-center justify-center">
        <FileQuestion className="w-6 h-6" />
      </div>
      <div>
        <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100">404 - Page Not Found</h3>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          The page or route you are looking for does not exist.
        </p>
      </div>
      <Link
        to="/"
        className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900 font-medium text-sm hover:bg-slate-800 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Dashboard</span>
      </Link>
    </div>
  );
};
