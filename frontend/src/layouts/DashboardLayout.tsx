import React from 'react';
import { Outlet } from 'react-router-dom';
import { TopNavbar } from '../components/TopNavbar';
import { Sidebar } from '../components/Sidebar';

export const DashboardLayout: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 transition-colors">
      <TopNavbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};
