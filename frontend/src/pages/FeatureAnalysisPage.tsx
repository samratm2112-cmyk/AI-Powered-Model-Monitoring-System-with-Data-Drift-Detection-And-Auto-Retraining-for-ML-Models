import React, { useState, useMemo } from 'react';
import { useDashboardData } from '../hooks/useDashboardData';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  CartesianGrid,
} from 'recharts';
import {
  BarChart3,
  Search,
  Filter,
  RefreshCw,
  AlertOctagon,
  CheckCircle2,
  AlertTriangle,
  Zap,
  Activity,
  ArrowUpDown,
  Info,
  ShieldCheck,
  TrendingUp,
} from 'lucide-react';

const CATEGORY_COLORS: Record<string, string> = {
  Financial: '#EF4444',
  'Behavioral Velocity': '#F59E0B',
  'Novel Attack Vector': '#8B5CF6',
  'Anonymized PCA Vector': '#3B82F6',
};

const PIE_COLORS = ['#EF4444', '#F59E0B', '#8B5CF6', '#3B82F6', '#10B981', '#EC4899'];

interface FeatureDetail {
  feature: string;
  count: number;
  category: string;
  severity: 'High' | 'Medium' | 'Low';
  description: string;
  affectedBatches: number[];
}

export const FeatureAnalysisPage: React.FC = () => {
  const { data, isLoading, isError, error, refetch, isFetching } = useDashboardData();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('All');
  const [sortField, setSortField] = useState<'count' | 'feature'>('count');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Derive feature analysis details
  const featureAnalysisData = useMemo(() => {
    if (!data) return { list: [], totalDrifts: 0, topFeature: 'N/A', categoryCounts: {} };

    const featureCounts = data.drift_analysis?.feature_counts || {};
    const batchTimeline = data.batch_timeline || [];

    // Helper to map features to categories and descriptions
    const list: FeatureDetail[] = Object.entries(featureCounts).map(([feature, count]) => {
      let category = 'Anonymized PCA Vector';
      let description = 'Standard statistical variation across production stream batches.';
      let severity: 'High' | 'Medium' | 'Low' = count >= 4 ? 'High' : count >= 2 ? 'Medium' : 'Low';

      if (feature.toLowerCase() === 'amount') {
        category = 'Financial';
        description = 'Transaction Amount feature shifted during simulated micro-skimming or high-value fraud patterns.';
        severity = 'High';
      } else if (['v11', 'v12', 'v14'].includes(feature.toLowerCase())) {
        category = 'Novel Attack Vector';
        description = 'Unseen behavioral shift characteristic of novel fraud archetype Type D.';
        severity = 'High';
      } else if (['v1', 'v2', 'v3', 'v4', 'v5'].includes(feature.toLowerCase())) {
        category = 'Behavioral Velocity';
        description = 'Primary PCA component variations reflecting transaction frequency and user behavior changes.';
      }

      // Estimate affected batches from batch timeline
      const affectedBatches = batchTimeline
        .filter((b) => b.drifted_feature_count > 0)
        .slice(0, count)
        .map((b) => b.batch_id);

      return {
        feature,
        count,
        category,
        severity,
        description,
        affectedBatches,
      };
    });

    const totalDrifts = list.reduce((acc, f) => acc + f.count, 0);
    const sorted = [...list].sort((a, b) => b.count - a.count);
    const topFeature = sorted.length > 0 ? `${sorted[0].feature} (${sorted[0].count}x)` : 'N/A';

    const categoryCounts: Record<string, number> = {};
    list.forEach((f) => {
      categoryCounts[f.category] = (categoryCounts[f.category] || 0) + f.count;
    });

    return { list, totalDrifts, topFeature, categoryCounts };
  }, [data]);

  // Filtered and sorted list
  const filteredFeatures = useMemo(() => {
    return featureAnalysisData.list
      .filter((item) => {
        const matchesSearch =
          item.feature.toLowerCase().includes(searchTerm.toLowerCase()) ||
          item.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
          item.description.toLowerCase().includes(searchTerm.toLowerCase());

        const matchesCategory = selectedCategory === 'All' || item.category === selectedCategory;
        const matchesSeverity = selectedSeverity === 'All' || item.severity === selectedSeverity;

        return matchesSearch && matchesCategory && matchesSeverity;
      })
      .sort((a, b) => {
        if (sortField === 'count') {
          return sortOrder === 'desc' ? b.count - a.count : a.count - b.count;
        } else {
          return sortOrder === 'desc'
            ? b.feature.localeCompare(a.feature)
            : a.feature.localeCompare(b.feature);
        }
      });
  }, [featureAnalysisData.list, searchTerm, selectedCategory, selectedSeverity, sortField, sortOrder]);

  if (isLoading) {
    return (
      <div className="space-y-6 pb-10 animate-pulse">
        <div className="h-10 bg-slate-200 dark:bg-slate-800 rounded-lg w-1/3"></div>
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-24 bg-slate-200 dark:bg-slate-800 rounded-xl"></div>
          ))}
        </div>
        <div className="h-80 bg-slate-200 dark:bg-slate-800 rounded-xl"></div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-8 rounded-2xl bg-rose-50/60 dark:bg-rose-950/20 border border-rose-200 dark:border-rose-900/40 text-center space-y-6 max-w-2xl mx-auto my-12">
        <div className="w-14 h-14 rounded-full bg-rose-100 dark:bg-rose-900/50 text-rose-600 dark:text-rose-400 mx-auto flex items-center justify-center">
          <AlertOctagon className="w-7 h-7" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100">
            Failed to Load Feature Analysis Data
          </h3>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            {(error as Error)?.message || 'FastAPI service unavailable.'}
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-medium text-sm transition-colors inline-flex items-center space-x-2"
        >
          <RefreshCw className={`w-4 h-4 ${isFetching ? 'animate-spin' : ''}`} />
          <span>Retry Connection</span>
        </button>
      </div>
    );
  }

  const categoryPieData = Object.entries(featureAnalysisData.categoryCounts).map(([name, value]) => ({
    name,
    value,
  }));

  const barChartData = [...featureAnalysisData.list]
    .sort((a, b) => b.count - a.count)
    .map((item) => ({
      feature: item.feature,
      count: item.count,
      category: item.category,
    }));

  return (
    <div className="space-y-6 pb-12">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-gradient-to-r from-brand-600 via-indigo-600 to-purple-600 p-6 rounded-2xl text-white shadow-lg">
        <div className="space-y-1">
          <div className="inline-flex items-center space-x-2 bg-white/10 backdrop-blur-md px-3 py-1 rounded-full text-xs font-semibold">
            <BarChart3 className="w-3.5 h-3.5 text-brand-200" />
            <span>Statistical Feature Profiling</span>
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight">Feature Shift & Drift Analysis</h1>
          <p className="text-sm text-brand-100 max-w-2xl">
            Kolmogorov-Smirnov two-sample statistical testing (p &lt; 0.05) frequency breakdown across evaluated features.
          </p>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="self-start sm:self-center px-4 py-2.5 rounded-xl bg-white/20 hover:bg-white/30 backdrop-blur-md text-white font-medium text-sm transition-all flex items-center space-x-2 shadow-sm"
        >
          <RefreshCw className={`w-4 h-4 ${isFetching ? 'animate-spin' : ''}`} />
          <span>Refresh Analysis</span>
        </button>
      </div>

      {/* Top Summary Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Shifted Features
            </span>
            <div className="p-2 rounded-lg bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400">
              <Zap className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-slate-100">
            {featureAnalysisData.list.length}{' '}
            <span className="text-xs font-normal text-slate-400">/ 29 features</span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">Crossed KS p &lt; 0.05 threshold</p>
        </div>

        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Top Shifted Feature
            </span>
            <div className="p-2 rounded-lg bg-rose-50 dark:bg-rose-950/40 text-rose-600 dark:text-rose-400">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-rose-600 dark:text-rose-400">
            {featureAnalysisData.topFeature}
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">Most frequent drift occurrence</p>
        </div>

        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Total Shift Events
            </span>
            <div className="p-2 rounded-lg bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-slate-100">
            {featureAnalysisData.totalDrifts}
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">Cumulative feature triggers</p>
        </div>

        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              KS Test Sensitivity
            </span>
            <div className="p-2 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400">
            α = 0.05
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">95% statistical confidence level</p>
        </div>
      </div>

      {/* Visualizations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Frequency Bar Chart */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                Shifted Feature Frequencies
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Number of production stream batches where feature distribution drifted
              </p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
              {barChartData.length} Features
            </span>
          </div>

          <div className="h-72 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barChartData} margin={{ top: 10, right: 20, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#334155" opacity={0.15} />
                <XAxis dataKey="feature" stroke="#94A3B8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} allowDecimals={false} />
                <RechartsTooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="p-3 rounded-xl bg-slate-900/95 dark:bg-slate-800/95 text-white border border-slate-700 shadow-xl space-y-1 text-xs">
                          <p className="font-bold text-brand-400">{data.feature}</p>
                          <p className="text-slate-300">Category: {data.category}</p>
                          <p className="font-semibold text-rose-400">
                            Drifted in {data.count} {data.count === 1 ? 'batch' : 'batches'}
                          </p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {barChartData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={CATEGORY_COLORS[entry.category] || '#3B82F6'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Breakdown Pie Chart */}
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-4">
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
              Drift Category Distribution
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Grouping drifted features by domain functional role
            </p>
          </div>

          <div className="h-64 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={categoryPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {categoryPieData.map((_, index) => (
                    <Cell key={`pie-cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0];
                      return (
                        <div className="p-2.5 rounded-lg bg-slate-900 text-white text-xs space-y-1">
                          <p className="font-bold">{data.name}</p>
                          <p className="text-slate-300">{data.value} Total Drift Triggers</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-2 pt-2 border-t border-slate-100 dark:border-slate-800">
            {categoryPieData.map((cat, i) => (
              <div key={cat.name} className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2">
                  <span
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: PIE_COLORS[i % PIE_COLORS.length] }}
                  ></span>
                  <span className="text-slate-700 dark:text-slate-300 font-medium">{cat.name}</span>
                </div>
                <span className="font-bold text-slate-900 dark:text-slate-100">{cat.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Search */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search feature name or category..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 dark:text-slate-100 placeholder:text-slate-400"
          />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto justify-end">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-xs font-medium focus:outline-none dark:text-slate-200"
            >
              <option value="All">All Categories</option>
              <option value="Financial">Financial</option>
              <option value="Behavioral Velocity">Behavioral Velocity</option>
              <option value="Novel Attack Vector">Novel Attack Vector</option>
              <option value="Anonymized PCA Vector">Anonymized PCA Vector</option>
            </select>
          </div>

          <select
            value={selectedSeverity}
            onChange={(e) => setSelectedSeverity(e.target.value)}
            className="px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-xs font-medium focus:outline-none dark:text-slate-200"
          >
            <option value="All">All Severities</option>
            <option value="High">High (≥4 Batches)</option>
            <option value="Medium">Medium (2-3 Batches)</option>
            <option value="Low">Low (1 Batch)</option>
          </select>

          <button
            onClick={() => {
              if (sortField === 'count') {
                setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
              } else {
                setSortField('count');
                setSortOrder('desc');
              }
            }}
            className="px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-xs font-medium text-slate-700 dark:text-slate-300 transition-colors flex items-center space-x-1.5"
          >
            <ArrowUpDown className="w-3.5 h-3.5" />
            <span>Sort by Count ({sortOrder.toUpperCase()})</span>
          </button>
        </div>
      </div>

      {/* Feature Drift Matrix Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredFeatures.length === 0 ? (
          <div className="col-span-full p-8 text-center bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl space-y-2">
            <AlertTriangle className="w-8 h-8 text-amber-500 mx-auto" />
            <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">
              No features match your search criteria.
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Try adjusting your category or severity filters.
            </p>
          </div>
        ) : (
          filteredFeatures.map((item) => (
            <div
              key={item.feature}
              className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm hover:shadow-md transition-all space-y-3 flex flex-col justify-between"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="font-extrabold text-lg text-slate-900 dark:text-slate-100">
                      {item.feature}
                    </span>
                    <span
                      className="px-2 py-0.5 rounded-md text-[10px] font-bold"
                      style={{
                        backgroundColor: `${CATEGORY_COLORS[item.category]}15`,
                        color: CATEGORY_COLORS[item.category],
                      }}
                    >
                      {item.category}
                    </span>
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      item.severity === 'High'
                        ? 'bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-400'
                        : item.severity === 'Medium'
                        ? 'bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-400'
                        : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400'
                    }`}
                  >
                    {item.severity} Severity
                  </span>
                </div>

                <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                  {item.description}
                </p>
              </div>

              <div className="space-y-2 pt-3 border-t border-slate-100 dark:border-slate-800">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-500 dark:text-slate-400 font-medium">
                    Drifted in Batches:
                  </span>
                  <span className="font-bold text-brand-600 dark:text-brand-400">
                    {item.count} / 10 Batches
                  </span>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-slate-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${(item.count / 10) * 100}%`,
                      backgroundColor: CATEGORY_COLORS[item.category] || '#3B82F6',
                    }}
                  ></div>
                </div>

                {item.affectedBatches.length > 0 && (
                  <div className="flex flex-wrap gap-1 pt-1">
                    {item.affectedBatches.map((bId) => (
                      <span
                        key={bId}
                        className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 text-[10px] font-mono"
                      >
                        B{bId}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* KS Test Methodology Documentation Card */}
      <div className="p-6 rounded-2xl bg-slate-900 text-white shadow-xl space-y-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-brand-500/20 text-brand-400">
            <Info className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold">Kolmogorov-Smirnov (KS) Drift Detection Methodology</h3>
            <p className="text-xs text-slate-400">
              Statistical two-sample nonparametric hypothesis testing
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-300">
          <div className="p-4 rounded-xl bg-slate-800/80 space-y-2 border border-slate-700/50">
            <p className="font-bold text-white flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Two-Sample KS Statistic:</span>
            </p>
            <p className="font-mono text-brand-300">
              D = sup_x | F_baseline(x) - F_batch(x) |
            </p>
            <p className="text-slate-400">
              Evaluates whether the empirical cumulative distribution function (eCDF) of an incoming batch deviates significantly from the baseline training distribution (X_train).
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-800/80 space-y-2 border border-slate-700/50">
            <p className="font-bold text-white flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Timestamp Exemption Guardrail:</span>
            </p>
            <p className="text-slate-400">
              Raw <span className="font-mono text-amber-300">Time</span> is excluded strictly from statistical drift testing to eliminate non-stationary false positives while remaining available as an input feature for Random Forest inference.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

