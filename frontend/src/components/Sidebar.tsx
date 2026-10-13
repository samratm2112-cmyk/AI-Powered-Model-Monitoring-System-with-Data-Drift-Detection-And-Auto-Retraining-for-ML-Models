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
  Sparkles,
  Zap,
  ShieldCheck,
} from 'lucide-react';
import { useDeploymentStatus } from '../hooks/useDeploymentStatus';

interface SidebarItem {
  name: string;
  path: string;
  icon: React.ElementType;
  badge?: string;
  badgeType?: 'warning' | 'info';
}

export const Sidebar: React.FC = () => {
  const { data: deploymentStatus } = useDeploymentStatus();
  const hasPending = Boolean(deploymentStatus?.has_pending_deployment);

  const navItems: SidebarItem[] = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Explainability Hub', path: '/explain', icon: Zap },
    {
      name: 'Governance Portal',
      path: '/governance',
      icon: ShieldCheck,
      badge: hasPending ? 'Pending' : undefined,
      badgeType: 'warning',
    },
    { name: 'Data Upload', path: '/upload', icon: Upload },
    { name: 'Batch Monitoring', path: '/batches', icon: Layers },
    { name: 'Drift Analytics', path: '/drift', icon: Activity },
    { name: 'Accuracy Trends', path: '/accuracy', icon: TrendingUp },
    { name: 'Feature Analysis', path: '/features', icon: BarChart3 },
    { name: 'Logs', path: '/logs', icon: FileText },
    { name: 'System Architecture', path: '/architecture', icon: GitFork },
    { name: 'AI Insights', path: '/settings', icon: Sparkles },
  ];

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
                `flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-brand-50 text-brand-700 dark:bg-brand-950/60 dark:text-brand-400'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-slate-200'
                }`
              }
            >
              <div className="flex items-center space-x-3">
                <Icon className="w-4 h-4" />
                <span>{item.name}</span>
              </div>
              {item.badge && (
                <span className="px-1.5 py-0.5 text-[10px] font-bold rounded-full bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border border-amber-300 dark:border-amber-700 animate-pulse">
                  {item.badge}
                </span>
              )}
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
