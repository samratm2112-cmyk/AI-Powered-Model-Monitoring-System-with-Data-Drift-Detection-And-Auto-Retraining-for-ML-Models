import React, { useState, useMemo } from 'react';
import { useDashboardData } from '../hooks/useDashboardData';
import { BatchItem } from '../types/dashboard';
import {
  Layers,
  Search,
  Filter,
  ArrowUpDown,
  Check,
  X,
  RefreshCw,
  AlertOctagon,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  TrendingUp,
} from 'lucide-react';

type SortField = 'batch_id' | 'accuracy_before' | 'accuracy_after' | 'decision_level';
type SortOrder = 'asc' | 'desc';

export const BatchMonitoringPage: React.FC = () => {
  const { data, isLoading, isError, error, refetch, isFetching } = useDashboardData();

  // Search & Filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [levelFilter, setLevelFilter] = useState<string>('ALL');
  const [retrainFilter, setRetrainFilter] = useState<string>('ALL');

  // Sorting state
  const [sortField, setSortField] = useState<SortField>('batch_id');
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc');

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const rowsPerPage = 10;

  const rawBatches: BatchItem[] = data?.batch_timeline || [];

  // Filtered & Sorted batches
  const processedBatches = useMemo(() => {
    return rawBatches
      .filter((b) => {
        // Search filter
        const matchesSearch =
          searchQuery === '' ||
          `Batch ${b.batch_id}`.toLowerCase().includes(searchQuery.toLowerCase()) ||
          b.batch_id.toString().includes(searchQuery) ||
          b.simulated_drift_type.toLowerCase().includes(searchQuery.toLowerCase());

        // Level filter
        const matchesLevel = levelFilter === 'ALL' || b.decision_level === levelFilter;

        // Retrain filter
        const matchesRetrain =
          retrainFilter === 'ALL' ||
          (retrainFilter === 'YES' && b.retraining_triggered) ||
          (retrainFilter === 'NO' && !b.retraining_triggered);

        return matchesSearch && matchesLevel && matchesRetrain;
      })
      .sort((a, b) => {
        let valA: any = a[sortField];
        let valB: any = b[sortField];

        if (sortField === 'decision_level') {
          const orderMap: Record<string, number> = { GREEN: 1, YELLOW: 2, RED: 3 };
          valA = orderMap[a.decision_level] || 0;
          valB = orderMap[b.decision_level] || 0;
        }

        if (valA < valB) return sortOrder === 'asc' ? -1 : 1;
        if (valA > valB) return sortOrder === 'asc' ? 1 : -1;
        return 0;
      });
  }, [rawBatches, searchQuery, levelFilter, retrainFilter, sortField, sortOrder]);

  // Paginated rows
  const totalPages = Math.ceil(processedBatches.length / rowsPerPage) || 1;
  const paginatedBatches = useMemo(() => {
    const start = (currentPage - 1) * rowsPerPage;
    return processedBatches.slice(start, start + rowsPerPage);
  }, [processedBatches, currentPage]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6 pb-10 animate-pulse">
        <div className="h-10 bg-slate-200 dark:bg-slate-800 rounded-lg w-1/3"></div>
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-24 bg-slate-200 dark:bg-slate-800 rounded-xl"></div>
          ))}
        </div>
        <div className="h-96 bg-slate-200 dark:bg-slate-800 rounded-xl"></div>
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
            Failed to Load Batch Monitoring History
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
          <span>Retry Loading</span>
        </button>
      </div>
    );
  }

  const summary = data?.summary;
  const totalBatches = summary?.total_batches_processed || 0;
  const retrainedBatches = summary?.retraining_count || 0;
  const normalBatches = summary?.green_count || 0;
  const driftEvents = (summary?.yellow_count || 0) + (summary?.red_count || 0);

  return (
    <div className="space-y-6 pb-10">
      {/* Page Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-slate-100 tracking-tight">
            Batch Monitoring
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Detailed Monitoring History of Incoming Production Data
          </p>
        </div>

        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="self-start sm:self-auto inline-flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 font-medium text-xs hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors shadow-sm"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin text-brand-600' : ''}`} />
          <span>Refresh Table</span>
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">Total Batches</span>
            <div className="text-2xl font-extrabold text-slate-900 dark:text-slate-100 mt-0.5">{totalBatches}</div>
            <span className="text-xs text-slate-400">1,000 rec/batch</span>
          </div>
          <div className="p-3 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400">
            <Layers className="w-5 h-5" />
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">Retrained</span>
            <div className="text-2xl font-extrabold text-indigo-600 dark:text-indigo-400 mt-0.5">{retrainedBatches}</div>
            <span className="text-xs text-indigo-500 font-medium">Local Model Adaptation</span>
          </div>
          <div className="p-3 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
            <RefreshCw className="w-5 h-5" />
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">Normal</span>
            <div className="text-2xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-0.5">{normalBatches}</div>
            <span className="text-xs text-emerald-600 font-medium">Nominal Traffic</span>
          </div>
          <div className="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">Drift Events</span>
            <div className="text-2xl font-extrabold text-rose-600 dark:text-rose-400 mt-0.5">{driftEvents}</div>
            <span className="text-xs text-rose-500 font-medium">YELLOW & RED Batches</span>
          </div>
          <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Controls Bar: Search & Filters */}
      <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Search Input */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setCurrentPage(1);
            }}
            placeholder="Search by Batch ID or Traffic Type..."
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3 text-xs">
          {/* Decision Level Filter */}
          <div className="flex items-center space-x-1.5 bg-slate-50 dark:bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-slate-500 dark:text-slate-400 font-medium">Level:</span>
            <select
              value={levelFilter}
              onChange={(e) => {
                setLevelFilter(e.target.value);
                setCurrentPage(1);
              }}
              className="bg-transparent text-slate-900 dark:text-slate-100 font-semibold focus:outline-none cursor-pointer"
            >
              <option value="ALL">All Levels</option>
              <option value="GREEN">🟢 GREEN Only</option>
              <option value="YELLOW">🟡 YELLOW Only</option>
              <option value="RED">🔴 RED Only</option>
            </select>
          </div>

          {/* Retraining Filter */}
          <div className="flex items-center space-x-1.5 bg-slate-50 dark:bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700">
            <span className="text-slate-500 dark:text-slate-400 font-medium">Retraining:</span>
            <select
              value={retrainFilter}
              onChange={(e) => {
                setRetrainFilter(e.target.value);
                setCurrentPage(1);
              }}
              className="bg-transparent text-slate-900 dark:text-slate-100 font-semibold focus:outline-none cursor-pointer"
            >
              <option value="ALL">All Statuses</option>
              <option value="YES">✔ Retrained (Yes)</option>
              <option value="NO">✖ Skipped (No)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Enterprise Monitoring History Table */}
      <div className="rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            {/* Sticky Table Header */}
            <thead className="bg-slate-50 dark:bg-slate-800/80 text-slate-600 dark:text-slate-300 font-bold uppercase tracking-wider border-b border-slate-200 dark:border-slate-800 sticky top-0 z-10">
              <tr>
                <th
                  onClick={() => handleSort('batch_id')}
                  className="px-4 py-3 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                >
                  <div className="flex items-center space-x-1">
                    <span>Batch ID</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-400" />
                  </div>
                </th>

                <th className="px-4 py-3">Traffic Type</th>

                <th
                  onClick={() => handleSort('decision_level')}
                  className="px-4 py-3 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                >
                  <div className="flex items-center space-x-1">
                    <span>Decision Level</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-400" />
                  </div>
                </th>

                <th className="px-4 py-3 text-center">Drifted Features</th>

                <th
                  onClick={() => handleSort('accuracy_before')}
                  className="px-4 py-3 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-right"
                >
                  <div className="flex items-center justify-end space-x-1">
                    <span>Pre Acc</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-400" />
                  </div>
                </th>

                <th
                  onClick={() => handleSort('accuracy_after')}
                  className="px-4 py-3 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-right"
                >
                  <div className="flex items-center justify-end space-x-1">
                    <span>Post Acc</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-400" />
                  </div>
                </th>

                <th className="px-4 py-3 text-right">Gain</th>

                <th className="px-4 py-3 text-center">Retraining</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {paginatedBatches.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-12 text-center text-slate-400">
                    No batch monitoring records match the current filters.
                  </td>
                </tr>
              ) : (
                paginatedBatches.map((batch) => {
                  const gain = (batch.accuracy_after - batch.accuracy_before) * 100;
                  return (
                    <tr
                      key={batch.batch_id}
                      className="hover:bg-slate-50/80 dark:hover:bg-slate-800/50 transition-colors"
                    >
                      {/* Batch ID */}
                      <td className="px-4 py-3.5 font-bold text-slate-900 dark:text-slate-100">
                        Batch {batch.batch_id}
                      </td>

                      {/* Traffic Type */}
                      <td className="px-4 py-3.5 text-slate-600 dark:text-slate-300 font-medium">
                        {batch.simulated_drift_type}
                      </td>

                      {/* Decision Level Badges */}
                      <td className="px-4 py-3.5">
                        {batch.decision_level === 'GREEN' && (
                          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
                            <CheckCircle2 className="w-3 h-3 mr-1" />
                            GREEN
                          </span>
                        )}
                        {batch.decision_level === 'YELLOW' && (
                          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border border-amber-300 dark:border-amber-800">
                            <AlertTriangle className="w-3 h-3 mr-1" />
                            YELLOW
                          </span>
                        )}
                        {batch.decision_level === 'RED' && (
                          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300 border border-rose-300 dark:border-rose-800">
                            <XCircle className="w-3 h-3 mr-1" />
                            RED
                          </span>
                        )}
                      </td>

                      {/* Drifted Feature Count */}
                      <td className="px-4 py-3.5 text-center font-mono font-semibold text-slate-700 dark:text-slate-300">
                        {batch.drifted_feature_count} / 29
                      </td>

                      {/* Accuracy Before */}
                      <td className="px-4 py-3.5 text-right font-mono font-medium text-slate-600 dark:text-slate-400">
                        {(batch.accuracy_before * 100).toFixed(2)}%
                      </td>

                      {/* Accuracy After */}
                      <td className="px-4 py-3.5 text-right font-mono font-bold text-slate-900 dark:text-slate-100">
                        {(batch.accuracy_after * 100).toFixed(2)}%
                      </td>

                      {/* Gain */}
                      <td className="px-4 py-3.5 text-right font-mono font-semibold">
                        {gain > 0 ? (
                          <span className="text-emerald-600 dark:text-emerald-400 inline-flex items-center">
                            <TrendingUp className="w-3 h-3 mr-0.5" />
                            +{gain.toFixed(2)}%
                          </span>
                        ) : (
                          <span className="text-slate-400">0.00%</span>
                        )}
                      </td>

                      {/* Retraining Status */}
                      <td className="px-4 py-3.5 text-center">
                        {batch.retraining_triggered ? (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300">
                            <Check className="w-3 h-3 mr-1" />
                            Yes
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400">
                            <X className="w-3 h-3 mr-1" />
                            No
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="p-4 bg-slate-50 dark:bg-slate-800/50 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
          <div>
            Showing <span className="font-semibold">{paginatedBatches.length}</span> of{' '}
            <span className="font-semibold">{processedBatches.length}</span> batches
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
              disabled={currentPage === 1}
              className="px-3 py-1.5 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 disabled:opacity-40 font-medium hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              Previous
            </button>
            <span className="font-medium px-2">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="px-3 py-1.5 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 disabled:opacity-40 font-medium hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
