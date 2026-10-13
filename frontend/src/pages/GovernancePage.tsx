import React, { useState } from 'react';
import { useDeploymentStatus } from '../hooks/useDeploymentStatus';
import {
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  Activity,
  FileText,
  RefreshCw,
} from 'lucide-react';

export const GovernancePage: React.FC = () => {
  const {
    data: statusData,
    isLoading,
    isError,
    error,
    approveDeployment,
    rejectDeployment,
    isApproving,
    isRejecting,
    refetch,
    isFetching,
  } = useDeploymentStatus();

  const [reviewerName, setReviewerName] = useState<string>('Compliance Officer (Human)');
  const [reviewNotes, setReviewNotes] = useState<string>('Approved via Governance Portal: Superior F1 metrics verified.');
  const [actionSuccessMessage, setActionSuccessMessage] = useState<string | null>(null);

  const handleApprove = async () => {
    try {
      const res = await approveDeployment({
        reviewer: reviewerName,
        notes: reviewNotes,
      });
      setActionSuccessMessage(res.message || 'Model deployment approved successfully!');
      setTimeout(() => setActionSuccessMessage(null), 6000);
    } catch (err: any) {
      alert(`Approval failed: ${err.message || 'Error'}`);
    }
  };

  const handleReject = async () => {
    if (!window.confirm('Are you sure you want to REJECT this deployment? The old baseline model will remain active in production.')) {
      return;
    }
    try {
      const res = await rejectDeployment({
        reviewer: reviewerName,
        notes: 'Rejected by human operator: Fail-safe engaged.',
      });
      setActionSuccessMessage(res.message || 'Model deployment rejected. Fail-safe engaged.');
      setTimeout(() => setActionSuccessMessage(null), 6000);
    } catch (err: any) {
      alert(`Rejection failed: ${err.message || 'Error'}`);
    }
  };

  const isPending = statusData?.has_pending_deployment;
  const report = statusData?.validation_report;
  const metrics = report?.metrics_comparison;

  return (
    <div className="space-y-6 pb-12">
      {/* ============================================================================ */}
      {/* HEADER SECTION */}
      {/* ============================================================================ */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-purple-950 to-slate-900 p-6 md:p-8 text-white shadow-xl border border-purple-900/50">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div className="space-y-2">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 text-xs font-bold border border-purple-500/30">
              <ShieldCheck className="w-3.5 h-3.5 text-purple-400" />
              <span>HITL Governance & Compliance</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">
              Human-in-the-Loop Governance Gate
            </h1>
            <p className="text-sm md:text-base text-slate-300 max-w-2xl">
              Inspect candidate model retraining validation reports and grant human sign-off before promoting new weights to production.
            </p>
          </div>

          <div className="flex items-center space-x-2 bg-white/5 backdrop-blur-md p-3 rounded-xl border border-white/10 shrink-0">
            <button
              onClick={() => refetch()}
              disabled={isFetching}
              className="flex items-center space-x-2 px-3.5 py-2 rounded-lg bg-purple-600 hover:bg-purple-700 text-white font-medium text-xs transition-colors shadow-sm disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin' : ''}`} />
              <span>{isFetching ? 'Checking...' : 'Check Status'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Success Notification Alert */}
      {actionSuccessMessage && (
        <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 flex items-center space-x-3 text-sm font-semibold shadow-xs">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0" />
          <span>{actionSuccessMessage}</span>
        </div>
      )}

      {/* Loading state */}
      {isLoading ? (
        <div className="p-12 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center space-y-3">
          <RefreshCw className="w-8 h-8 text-purple-500 animate-spin mx-auto" />
          <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">
            Checking Human-in-the-Loop Governance Status...
          </p>
        </div>
      ) : isError ? (
        <div className="p-8 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-center text-rose-700 dark:text-rose-300">
          <p className="text-sm font-bold">Failed to load governance status:</p>
          <p className="text-xs mt-1">{(error as Error)?.message || 'Internal error'}</p>
        </div>
      ) : (
        <>
          {/* ============================================================================ */}
          {/* STATUS BANNER */}
          {/* ============================================================================ */}
          <div className={`p-6 rounded-2xl border shadow-sm ${
            isPending
              ? 'bg-amber-50/80 dark:bg-amber-950/20 border-amber-300 dark:border-amber-800/80'
              : statusData?.status === 'APPROVED'
              ? 'bg-emerald-50/80 dark:bg-emerald-950/20 border-emerald-300 dark:border-emerald-800/80'
              : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800'
          }`}>
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-start space-x-4">
                <div className={`p-3 rounded-2xl shrink-0 ${
                  isPending
                    ? 'bg-amber-100 dark:bg-amber-900/60 text-amber-700 dark:text-amber-300'
                    : 'bg-emerald-100 dark:bg-emerald-900/60 text-emerald-700 dark:text-emerald-300'
                }`}>
                  {isPending ? <AlertTriangle className="w-6 h-6 animate-pulse" /> : <ShieldCheck className="w-6 h-6" />}
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold ${
                      isPending
                        ? 'bg-amber-200 text-amber-900 dark:bg-amber-900 dark:text-amber-200'
                        : 'bg-emerald-200 text-emerald-900 dark:bg-emerald-900 dark:text-emerald-200'
                    }`}>
                      {statusData?.status}
                    </span>
                    <span className="text-xs text-slate-400 dark:text-slate-500">
                      Timestamp: {statusData?.timestamp || 'N/A'}
                    </span>
                  </div>
                  <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 mt-1">
                    {isPending
                      ? '⚠️ Deployment Request: Pending Human Operator Approval'
                      : '✅ Governance Gate: Production Model Deployed & Verified'}
                  </h2>
                  <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                    {statusData?.message}
                  </p>
                </div>
              </div>

              {isPending && (
                <div className="flex items-center space-x-2 shrink-0">
                  <button
                    onClick={handleApprove}
                    disabled={isApproving}
                    className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-bold text-xs shadow-md transition-all flex items-center space-x-2"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>{isApproving ? 'Deploying...' : 'Approve Deployment'}</span>
                  </button>
                  <button
                    onClick={handleReject}
                    disabled={isRejecting}
                    className="px-4 py-2.5 rounded-xl bg-slate-200 dark:bg-slate-800 hover:bg-rose-100 dark:hover:bg-rose-950/60 text-slate-700 dark:text-slate-300 hover:text-rose-600 text-xs font-bold transition-all"
                  >
                    {isRejecting ? 'Rejecting...' : 'Reject (Keep Old Model)'}
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* ============================================================================ */}
          {/* VALIDATION REPORT: METRICS COMPARISON TABLE */}
          {/* ============================================================================ */}
          {metrics && (
            <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-purple-500" />
                    Retraining Validation Report: Old vs. New Model
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Calculated automatically by RetrainingDecisionEngine before disk promotion.
                  </p>
                </div>

                <span className="text-xs font-bold px-3 py-1 rounded-full bg-purple-50 text-purple-700 dark:bg-purple-950/80 dark:text-purple-300 border border-purple-200 dark:border-purple-800">
                  {report?.recommendation || 'Strongly Recommend Deployment'}
                </span>
              </div>

              <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 dark:bg-slate-800/80 text-slate-500 dark:text-slate-400 font-semibold border-b border-slate-200 dark:border-slate-800">
                    <tr>
                      <th className="py-3 px-4">Evaluation Metric</th>
                      <th className="py-3 px-4">Old Baseline Model</th>
                      <th className="py-3 px-4">Retrained Candidate</th>
                      <th className="py-3 px-4">Delta</th>
                      <th className="py-3 px-4">% Change</th>
                      <th className="py-3 px-4">Governance Evaluation</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-mono">
                    {Object.entries(metrics).map(([key, val]) => (
                      <tr key={key} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40">
                        <td className="py-3 px-4 font-sans font-bold capitalize text-slate-800 dark:text-slate-200">
                          {key}
                        </td>
                        <td className="py-3 px-4 text-slate-600 dark:text-slate-400">
                          {val.old_model.toFixed(4)}
                        </td>
                        <td className="py-3 px-4 font-bold text-indigo-600 dark:text-indigo-400">
                          {val.new_model.toFixed(4)}
                        </td>
                        <td className="py-3 px-4 text-emerald-600 dark:text-emerald-400 font-bold">
                          {val.delta >= 0 ? `+${val.delta.toFixed(4)}` : val.delta.toFixed(4)}
                        </td>
                        <td className="py-3 px-4 text-emerald-600 dark:text-emerald-400 font-bold">
                          {val.delta_pct >= 0 ? `+${val.delta_pct.toFixed(2)}%` : `${val.delta_pct.toFixed(2)}%`}
                        </td>
                        <td className="py-3 px-4 font-sans">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold ${
                            val.improved
                              ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                              : 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                          }`}>
                            {val.improved ? '🟢 Improved' : '🔴 Degraded'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ============================================================================ */}
          {/* TOP 3 DRIFTED FEATURES & RATIONALE */}
          {/* ============================================================================ */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Top Drift Features */}
            <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
              <div className="flex items-center space-x-2 text-slate-900 dark:text-slate-100">
                <Activity className="w-4 h-4 text-purple-500" />
                <h3 className="text-sm font-bold uppercase tracking-wide">
                  Top 3 Shifted Features That Triggered Retraining
                </h3>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Kolmogorov-Smirnov statistical divergence identified in incoming production distribution:
              </p>

              <div className="space-y-2.5 pt-1">
                {report?.top_drifted_features?.map((f, i) => (
                  <div
                    key={f.feature}
                    className="p-3 rounded-xl bg-purple-50/50 dark:bg-purple-950/20 border border-purple-100 dark:border-purple-900/40 text-xs flex items-center justify-between"
                  >
                    <div className="flex items-center space-x-2">
                      <span className="w-5 h-5 rounded-full bg-purple-200 dark:bg-purple-900 text-purple-800 dark:text-purple-200 font-bold flex items-center justify-center text-xs">
                        {i + 1}
                      </span>
                      <strong className="text-slate-800 dark:text-slate-200">{f.feature}</strong>
                    </div>
                    <div className="space-x-3 font-mono text-slate-600 dark:text-slate-400">
                      <span>KS: <strong>{f.ks_statistic.toFixed(4)}</strong></span>
                      <span className="text-purple-600 dark:text-purple-400 font-bold">p &lt; 0.05</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommendation & Reviewer Form */}
            <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
              <div className="flex items-center space-x-2 text-slate-900 dark:text-slate-100">
                <FileText className="w-4 h-4 text-indigo-500" />
                <h3 className="text-sm font-bold uppercase tracking-wide">
                  Governance Rationale & Human Sign-Off
                </h3>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
                {report?.recommendation_rationale || 'The retrained model demonstrates superior performance and counteracts distribution drift.'}
              </div>

              {/* Reviewer Metadata Inputs */}
              <div className="space-y-3 pt-2">
                <div>
                  <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 block mb-1">
                    Reviewer Name / Sign-off Title:
                  </label>
                  <input
                    type="text"
                    value={reviewerName}
                    onChange={(e) => setReviewerName(e.target.value)}
                    className="w-full px-3 py-1.5 rounded-lg text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-1 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 block mb-1">
                    Compliance Audit Notes:
                  </label>
                  <input
                    type="text"
                    value={reviewNotes}
                    onChange={(e) => setReviewNotes(e.target.value)}
                    className="w-full px-3 py-1.5 rounded-lg text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-1 focus:ring-purple-500"
                  />
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
