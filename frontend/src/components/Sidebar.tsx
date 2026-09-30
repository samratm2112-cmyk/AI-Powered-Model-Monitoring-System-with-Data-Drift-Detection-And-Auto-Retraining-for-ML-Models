import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Upload,
  Layers,
  Activity,
  TrendingUp,
  BarChart3,
  FileText,
  GitFork,
  Sparkles
} from 'lucide-react';

interface SidebarItem {
  name: string;
  path: string;
  icon: React.ElementType;
}

const navItems: SidebarItem[] = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Data Upload', path: '/upload', icon: Upload },
  { name: 'Batch Monitoring', path: '/batches', icon: Layers },
  { name: 'Drift Analytics', path: '/drift', icon: Activity },
  { name: 'Accuracy Trends', path: '/accuracy', icon: TrendingUp },
  { name: 'Feature Analysis', path: '/features', icon: BarChart3 },
  { name: 'Logs', path: '/logs', icon: FileText },
  { name: 'System Architecture', path: '/architecture', icon: GitFork },
  { name: 'AI Insights', path: '/settings', icon: Sparkles },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col transition-colors shrink-0">
      <div className="p-4 border-b border-slate-100 dark:border-slate-800">
        <span className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
          MLOps Platform
        </span>
      </div>
      
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-brand-50 text-brand-700 dark:bg-brand-950/60 dark:text-brand-400'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-slate-200'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-200 dark:border-slate-800 text-xs text-slate-400 dark:text-slate-600">
        ML Drift Detector v1.0.0
      </div>
    </aside>
  );
};
