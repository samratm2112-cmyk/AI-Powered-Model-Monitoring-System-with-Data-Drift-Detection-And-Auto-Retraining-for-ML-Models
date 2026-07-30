import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DashboardLayout } from './layouts/DashboardLayout';
import { DashboardPage } from './pages/DashboardPage';
import { BatchMonitoringPage } from './pages/BatchMonitoringPage';
import { DriftAnalyticsPage } from './pages/DriftAnalyticsPage';
import { AccuracyTrendsPage } from './pages/AccuracyTrendsPage';
import { FeatureAnalysisPage } from './pages/FeatureAnalysisPage';
import { LogsPage } from './pages/LogsPage';
import { ArchitecturePage } from './pages/ArchitecturePage';
import { SettingsPage } from './pages/SettingsPage';
import { NotFoundPage } from './pages/NotFoundPage';
import './styles/globals.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<DashboardLayout />}>
            <Route index element={<DashboardPage />} />
            <Route path="batches" element={<BatchMonitoringPage />} />
            <Route path="drift" element={<DriftAnalyticsPage />} />
            <Route path="accuracy" element={<AccuracyTrendsPage />} />
            <Route path="features" element={<FeatureAnalysisPage />} />
            <Route path="logs" element={<LogsPage />} />
            <Route path="architecture" element={<ArchitecturePage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

export default App;
