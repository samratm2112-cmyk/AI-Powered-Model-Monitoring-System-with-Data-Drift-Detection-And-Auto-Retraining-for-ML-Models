import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorPageProps {
  message?: string;
  onRetry?: () => void;
}

export const ErrorPage: React.FC<ErrorPageProps> = ({ message, onRetry }) => {
  return (
    <div className="min-h-[400px] flex flex-col items-center justify-center space-y-4 text-center p-6 bg-red-50/50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/40 rounded-xl">
      <div className="w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/50 text-red-600 dark:text-red-400 flex items-center justify-center">
        <AlertTriangle className="w-6 h-6" />
      </div>
      <div>
        <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">API Connection Error</h3>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 max-w-md">
          {message || 'Unable to connect to FastAPI backend at http://localhost:8000/dashboard. Ensure uvicorn server is running.'}
        </p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-brand-600 text-white font-medium text-sm hover:bg-brand-700 transition-colors shadow-sm"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Retry Connection</span>
        </button>
      )}
    </div>
  );
};
