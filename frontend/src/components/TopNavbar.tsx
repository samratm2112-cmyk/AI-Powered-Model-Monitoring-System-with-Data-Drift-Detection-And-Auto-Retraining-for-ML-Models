import React, { useState, useEffect } from 'react';
import { Sun, Moon, RefreshCw, Shield, User, Clock } from 'lucide-react';
import { useTheme } from '../hooks/useTheme';
import { useQueryClient } from '@tanstack/react-query';

export const TopNavbar: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const queryClient = useQueryClient();
  const [timeStr, setTimeStr] = useState<string>('');
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  useEffect(() => {
    const updateClock = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    };
    updateClock();
    const interval = setInterval(updateClock, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await queryClient.invalidateQueries({ queryKey: ['dashboardData'] });
    setTimeout(() => setIsRefreshing(false), 600);
  };

  return (
    <header className="h-16 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-6 flex items-center justify-between sticky top-0 z-30 transition-colors">
      {/* Title & Status */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2 text-brand-600 dark:text-brand-500 font-bold text-lg">
          <Shield className="w-6 h-6" />
          <span>ML Drift Monitoring</span>
        </div>
        <span className="hidden sm:inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
          <span className="w-2 h-2 rounded-full bg-emerald-500 mr-1.5 animate-pulse"></span>
          Running
        </span>
      </div>

      {/* Right Controls */}
      <div className="flex items-center space-x-3">
        {/* Clock */}
        <div className="hidden md:flex items-center space-x-1.5 text-xs text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 px-3 py-1.5 rounded-md font-mono">
          <Clock className="w-3.5 h-3.5" />
          <span>{timeStr}</span>
        </div>

        {/* Refresh Button */}
        <button
          onClick={handleRefresh}
          className="p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          title="Refresh Data"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-brand-600' : ''}`} />
        </button>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
        >
          {theme === 'light' ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4 text-amber-400" />}
        </button>

        {/* User Profile Placeholder */}
        <div className="flex items-center space-x-2 pl-2 border-l border-slate-200 dark:border-slate-800">
          <div className="w-8 h-8 rounded-full bg-brand-100 dark:bg-brand-900 text-brand-700 dark:text-brand-300 flex items-center justify-center font-semibold text-sm">
            <User className="w-4 h-4" />
          </div>
        </div>
      </div>
    </header>
  );
};
