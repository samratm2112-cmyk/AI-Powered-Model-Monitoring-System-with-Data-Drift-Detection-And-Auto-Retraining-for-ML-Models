import React, { useState } from 'react';
import { useDashboardData } from '../hooks/useDashboardData';
import { DashboardSkeleton } from '../components/DashboardSkeleton';
import { AnimatedNumber } from '../components/AnimatedNumber';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts';
import {
  Layers,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  RefreshCw,
  Target,
  TrendingUp,
  Database,
  Cpu,
  Clock,
  Server,
  Activity,
  Zap,
  ArrowUpRight,
  Minus,
  AlertOctagon,
  Check,
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { data, isLoading, isError, error, refetch, isFetching, dataUpdatedAt } = useDashboardData();
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const handleManualRefresh = async () => {
    try {
      await refetch();
      setToastMessage('Dashboard data refreshed successfully!');
      setTimeout(() => setToastMessage(null), 3500);
    } catch {
      setToastMessage('Failed to refresh dashboard data.');
      setTimeout(() => setToastMessage(null), 3500);
    }
  };

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  if (isError) {
    return (
      <div className="p-8 rounded-2xl bg-rose-50/60 dark:bg-rose-950/20 border border-rose-200 dark:border-rose-900/40 text-center space-y-6 max-w-3xl mx-auto my-12">
        <div className="w-16 h-16 rounded-full bg-rose-100 dark:bg-rose-900/50 text-rose-600 dark:text-rose-400 mx-auto flex items-center justify-center">
          <AlertOctagon className="w-8 h-8" />
        </div>
        <div className="space-y-2">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-rose-200/60 text-rose-800 dark:bg-rose-950 dark:text-rose-300 text-xs font-bold">
            <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping"></span>
            <span>🔴 Backend Offline</span>
          </div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
            Unable to Connect to Monitoring API
          </h2>
          <p className="text-sm text-slate-600 dark:text-slate-400 max-w-lg mx-auto">
            {(error as Error)?.message || 'FastAPI backend service is currently unreachable at http://localhost:8000/dashboard.'}
          </p>
        </div>

        <div className="pt-2 flex items-center justify-center space-x-4">
          <button
            onClick={() => refetch()}
            className="px-5 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-semibold text-sm transition-all shadow-md inline-flex items-center space-x-2"
          >
            <RefreshCw className={`w-4 h-4 ${isFetching ? 'animate-spin' : ''}`} />
            <span>Retry Connection</span>
          </button>
        </div>
      </div>
    );
  }

  const summary = data?.summary;
  const accuracyTrend = data?.accuracy_trend || [];
  const lastRefreshedTime = dataUpdatedAt ? new Date(dataUpdatedAt).toLocaleTimeString() : 'Just now';

  // Decision Chart Data
  const decisionChartData = [
    { name: '🟢 GREEN (Stable)', value: summary?.green_count || 0, color: '#10B981' },
    { name: '🟡 YELLOW (Minor Variation)', value: summary?.yellow_count || 0, color: '#F59E0B' },
    { name: '🔴 RED (Retrained)', value: summary?.red_count || 0, color: '#EF4444' },
  ];

  // Accuracy Chart Data
  const accuracyChartData = accuracyTrend.map((item) => ({
    batch: `Batch ${item.batch_id}`,
    'Pre-Adaptation (Global)': Number((item.accuracy_before * 100).toFixed(2)),
    'Post-Adaptation (Ensemble)': Number((item.accuracy_after * 100).toFixed(2)),
  }));

  const avgBoost = summary?.average_accuracy_improvement || 0;

  return (
    <div className="space-y-8 pb-10">
      {/* Toast Notification Banner */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 p-4 rounded-xl bg-slate-900 text-white shadow-2xl border border-slate-700 flex items-center space-x-3 transition-all animate-bounce">
          <Check className="w-5 h-5 text-emerald-400" />
          <span className="text-sm font-medium">{toastMessage}</span>
        </div>
      )}

      {/* ============================================================================ */}
      {/* SECTION 1: HERO HEADER */}
      {/* ============================================================================ */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 p-8 text-white shadow-lg border border-slate-800">
        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div className="space-y-2 max-w-3xl">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30 text-xs font-semibold tracking-wide">
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              <span>Production MLOps Pipeline Active</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
              AI-Powered Continuous ML Monitoring System
            </h1>
            <p className="text-base text-slate-300">
              Real-time Monitoring of Data Drift and Automatic Local Model Adaptation
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 bg-white/5 backdrop-blur-md p-4 rounded-xl border border-white/10 shrink-0">
            {/* Live Indicator */}
            <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-xs font-bold">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping"></span>
              <span>🟢 Live Monitoring</span>
            </div>

            {/* Refresh Button */}
            <button
              onClick={handleManualRefresh}
              disabled={isFetching}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white font-medium text-xs transition-colors shadow-sm"
              title="Manual Trigger Refetch"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin' : ''}`} />
              <span>{isFetching ? 'Refetching...' : 'Refresh'}</span>
            </button>

            {/* Last Refresh Time */}
            <div className="flex items-center space-x-1.5 text-xs text-slate-300 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              <span>Refreshed: {lastRefreshedTime}</span>
            </div>
          </div>
        </div>

        {/* Ambient glow decoration */}
        <div className="absolute -right-10 -top-10 w-64 h-64 bg-brand-500/10 rounded-full blur-3xl pointer-events-none"></div>
      </div>

      {/* ============================================================================ */}
      {/* SECTION 2: EXECUTIVE KPI CARDS */}
      {/* ============================================================================ */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1: Total Batches */}
        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-200">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Total Batches
            </span>
            <div className="p-2 rounded-lg bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400">
              <Layers className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-slate-900 dark:text-slate-100">
              <AnimatedNumber value={summary?.total_batches_processed || 0} />
            </span>
            <span className="text-xs text-slate-500 dark:text-slate-400 font-medium inline-flex items-center">
              <Minus className="w-3 h-3 mr-1 text-slate-400" /> Steady
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Total streaming batches processed
          </p>
        </div>

        {/* KPI 2: GREEN Batches */}
        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-200">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              GREEN Batches
            </span>
            <div className="p-2 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400">
              <AnimatedNumber value={summary?.green_count || 0} />
            </span>
            <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/80 px-2 py-0.5 rounded">
              Nominal
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Stable stream with 0 drift
          </p>
        </div>

        {/* KPI 3: YELLOW Batches */}
        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-200">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              YELLOW Batches
            </span>
            <div className="p-2 rounded-lg bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-amber-600 dark:text-amber-400">
              <AnimatedNumber value={summary?.yellow_count || 0} />
            </span>
            <span className="text-xs font-semibold text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/80 px-2 py-0.5 rounded">
              Minor Variation
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            1–2 features drifted (No retrain)
          </p>
        </div>

        {/* KPI 4: RED Batches */}
        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-200">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              RED Batches
            </span>
            <div className="p-2 rounded-lg bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400">
              <XCircle className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-rose-600 dark:text-rose-400">
              <AnimatedNumber value={summary?.red_count || 0} />
            </span>
            <span className="text-xs font-semibold text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/80 px-2 py-0.5 rounded">
              Action Needed
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            ≥3 features drifted or drop in acc
          </p>
        </div>

        {/* KPI 5: Retraining Events */}
        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-200">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Retraining Events
            </span>
            <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
              <RefreshCw className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-slate-900 dark:text-slate-100">
              <AnimatedNumber value={summary?.retraining_count || 0} />
            </span>
            <span className="text-xs font-semibold text-indigo-600 dark:text-indigo-400">
              Local Expert
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Automated retraining executions
          </p>
        </div>

        {/* KPI 6: Average Accuracy */}
        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-200">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Average Accuracy
            </span>
            <div className="p-2 rounded-lg bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400">
              <Target className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-slate-900 dark:text-slate-100">
              <AnimatedNumber value={(summary?.average_accuracy || 0) * 100} decimals={2} suffix="%" />
            </span>
            <span className="text-xs font-medium text-emerald-600 dark:text-emerald-400 inline-flex items-center">
              <ArrowUpRight className="w-3.5 h-3.5 mr-0.5 text-emerald-500" /> High Precision
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Mean Post-Adaptation Ensemble Accuracy
          </p>
        </div>

        {/* KPI 7: Average Accuracy Improvement */}
        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-200">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Avg Acc Boost
            </span>
            <div className="p-2 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400">
              <TrendingUp className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400">
              <AnimatedNumber value={avgBoost} decimals={2} prefix="+" suffix="%" />
            </span>
            <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/80 px-2 py-0.5 rounded inline-flex items-center">
              <ArrowUpRight className="w-3 h-3 mr-0.5" /> Improved
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Local model adaptation improvement
          </p>
        </div>

        {/* KPI 8: Local Buffer Size */}
        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-200">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Local Buffer
            </span>
            <div className="p-2 rounded-lg bg-cyan-50 dark:bg-cyan-950/60 text-cyan-600 dark:text-cyan-400">
              <Database className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-slate-900 dark:text-slate-100">
              <AnimatedNumber value={summary?.local_buffer_size || 0} />
            </span>
            <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
              Max 5,000
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Sliding window memory size
          </p>
        </div>
      </div>

      {/* ============================================================================ */}
      {/* SECTIONS 3 & 4: CHARTS GRID */}
      {/* ============================================================================ */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* SECTION 3: DECISION POLICY DISTRIBUTION */}
        <div className="p-6 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center space-x-2">
                <Activity className="w-5 h-5 text-brand-600 dark:text-brand-400" />
                <span>Decision Policy Breakdown</span>
              </h3>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">
              Distribution of 3-tier decision engine triggers (GREEN, YELLOW, RED)
            </p>
          </div>

          <div className="h-64 my-4">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={decisionChartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={5}
                  dataKey="value"
                  animationDuration={1000}
                >
                  {decisionChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip
                  contentStyle={{
                    backgroundColor: '#0F172A',
                    borderColor: '#334155',
                    borderRadius: '8px',
                    color: '#FFF',
                  }}
                />
                <Legend verticalAlign="bottom" height={36} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="pt-3 border-t border-slate-100 dark:border-slate-800 grid grid-cols-3 text-center text-xs">
            <div>
              <span className="block font-bold text-emerald-600 dark:text-emerald-400">{summary?.green_count}</span>
              <span className="text-slate-400">🟢 GREEN</span>
            </div>
            <div>
              <span className="block font-bold text-amber-600 dark:text-amber-400">{summary?.yellow_count}</span>
              <span className="text-slate-400">🟡 YELLOW</span>
            </div>
            <div>
              <span className="block font-bold text-rose-600 dark:text-rose-400">{summary?.red_count}</span>
              <span className="text-slate-400">🔴 RED</span>
            </div>
          </div>
        </div>

        {/* SECTION 4: ACCURACY TREND CHART */}
        <div className="lg:col-span-2 p-6 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center space-x-2">
                <TrendingUp className="w-5 h-5 text-brand-600 dark:text-brand-400" />
                <span>Accuracy Trend Across Sequential Batches</span>
              </h3>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">
              Comparison of Pre-adaptation Global Accuracy vs Post-adaptation Ensemble Accuracy
            </p>
          </div>

          <div className="h-72 my-4">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={accuracyChartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.15} />
                <XAxis dataKey="batch" stroke="#64748B" fontSize={12} tickLine={false} />
                <YAxis domain={[98.5, 100.2]} stroke="#64748B" fontSize={12} tickFormatter={(val) => `${val}%`} />
                <RechartsTooltip
                  contentStyle={{
                    backgroundColor: '#0F172A',
                    borderColor: '#334155',
                    borderRadius: '8px',
                    color: '#FFF',
                  }}
                  formatter={(value: any) => [`${value}%`]}
                />
                <Legend verticalAlign="top" height={36} />
                <Line
                  type="monotone"
                  dataKey="Pre-Adaptation (Global)"
                  stroke="#EF4444"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={{ r: 4 }}
                  animationDuration={1000}
                />
                <Line
                  type="monotone"
                  dataKey="Post-Adaptation (Ensemble)"
                  stroke="#10B981"
                  strokeWidth={3}
                  dot={{ r: 5, fill: '#10B981' }}
                  animationDuration={1000}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="pt-3 border-t border-slate-100 dark:border-slate-800 text-xs text-slate-500 dark:text-slate-400 flex items-center justify-between">
            <span>🛡️ Threshold Level: 99.00%</span>
            <span className="font-semibold text-emerald-600 dark:text-emerald-400">
              Avg Post-Adaptation Accuracy: {((summary?.average_accuracy || 0) * 100).toFixed(2)}%
            </span>
          </div>
        </div>
      </div>

      {/* ============================================================================ */}
      {/* SECTION 5: QUICK STATISTICS PANEL */}
      {/* ============================================================================ */}
      <div className="p-6 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
        <div className="border-b border-slate-100 dark:border-slate-800 pb-3 mb-4 flex items-center justify-between">
          <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-brand-600 dark:text-brand-400" />
            <span>Quick System Statistics & Health Status</span>
          </h3>
          <span className="text-xs text-slate-400">API: http://localhost:8000</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4 text-sm">
          <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800/80">
            <span className="block text-xs font-semibold text-slate-400 uppercase">System Status</span>
            <span className="text-base font-bold text-emerald-600 dark:text-emerald-400 flex items-center space-x-1.5 mt-1">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>{data?.system_status || 'Running'}</span>
            </span>
          </div>

          <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800/80">
            <span className="block text-xs font-semibold text-slate-400 uppercase">Generated Time</span>
            <span className="text-sm font-bold text-slate-900 dark:text-slate-100 mt-1 block truncate">
              {data?.generated_at}
            </span>
          </div>

          <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800/80">
            <span className="block text-xs font-semibold text-slate-400 uppercase">Pipeline State</span>
            <span className="text-sm font-bold text-indigo-600 dark:text-indigo-400 mt-1 block">
              Continuous Stream
            </span>
          </div>

          <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800/80">
            <span className="block text-xs font-semibold text-slate-400 uppercase">Monitoring Mode</span>
            <span className="text-sm font-bold text-brand-600 dark:text-brand-400 mt-1 block">
              KS-Test (Excl Time)
            </span>
          </div>

          <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800/80">
            <span className="block text-xs font-semibold text-slate-400 uppercase">Backend Status</span>
            <span className="text-sm font-bold text-emerald-600 dark:text-emerald-400 flex items-center space-x-1 mt-1">
              <Server className="w-4 h-4 text-emerald-500" />
              <span>FastAPI Connected</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
