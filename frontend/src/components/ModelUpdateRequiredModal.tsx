import React, { useState, useEffect } from 'react';
import { useDeploymentStatus } from '../hooks/useDeploymentStatus';
import {
  ShieldAlert,
  ShieldCheck,
  TrendingUp,
  AlertTriangle,
  X,
  RefreshCw,
  CheckCircle2,
  ExternalLink,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const ModelUpdateRequiredModal: React.FC = () => {
  const navigate = useNavigate();
  const { data: deploymentStatus, approveDeployment, isApproving } = useDeploymentStatus();
  const [isOpen, setIsOpen] = useState(false);
  const [hasDismissed, setHasDismissed] = useState(false);
  const [reviewerName, setReviewerName] = useState('Human Compliance Officer');
  const [successToast, setSuccessToast] = useState<string | null>(null);

  const isPending = Boolean(
    deploymentStatus?.has_pending_deployment ||
    deploymentStatus?.status === 'PENDING_APPROVAL' ||
    deploymentStatus?.status === 'PENDING'
  );

  useEffect(() => {
    if (isPending && !hasDismissed) {
      setIsOpen(true);
    } else if (!isPending) {
      setIsOpen(false);
    }
  }, [isPending, hasDismissed]);

  const handleApprove = async () => {
    try {
      await approveDeployment({
        reviewer: reviewerName.trim() || 'Human Compliance Officer',
        notes: 'Approved via Model Update Required governance modal.',
      });
      setSuccessToast('Candidate model successfully approved and deployed to production!');
      setTimeout(() => {
        setSuccessToast(null);
        setIsOpen(false);
      }, 2500);
    } catch (err: any) {
      alert(`Approval failed: ${err?.message || 'Server error'}`);
    }
  };

  const handleDismiss = () => {
    setIsOpen(false);
    setHasDismissed(true);
  };

  const handleViewPortal = () => {
    setIsOpen(false);
    navigate('/governance');
  };

  if (!isOpen || !isPending) {
    return null;
  }

  const report = deploymentStatus?.validation_report;
  const metrics = report?.metrics_comparison || {};
  const topDrifted = report?.top_drifted_features || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-3xl rounded-3xl bg-white dark:bg-slate-900 border-2 border-amber-500/50 dark:border-amber-500/60 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="p-6 bg-gradient-to-r from-amber-500/20 via-rose-500/15 to-amber-500/20 border-b border-amber-500/30 flex items-start justify-between">
          <div className="flex items-center space-x-3.5">
            <div className="p-3 rounded-2xl bg-amber-500 text-white shadow-lg animate-pulse shrink-0">
              <ShieldAlert className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-extrabold uppercase tracking-wide bg-amber-500 text-white shadow-xs">
                  Governance Gate Active
                </span>
                <span className="text-xs text-amber-700 dark:text-amber-400 font-mono font-bold">
                  Status: PENDING_APPROVAL
                </span>
              </div>
              <h2 className="text-2xl font-black text-slate-900 dark:text-slate-100 tracking-tight mt-0.5">
                Model Update Required
              </h2>
              <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300">
                Data drift exceeded safety limits. An auto-retrained candidate model is waiting for your review.
              </p>
            </div>
          </div>

          <button
            onClick={handleDismiss}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors shrink-0"
            title="Dismiss"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-6 overflow-y-auto flex-1">
          {successToast && (
            <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 flex items-center space-x-3 text-sm font-semibold shadow-xs">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0" />
              <span>{successToast}</span>
            </div>
          )}

          {/* Candidate Model Details */}
          <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 text-xs flex flex-wrap items-center justify-between gap-3">
            <div>
              <span className="text-slate-400 font-medium block">Candidate Architecture</span>
              <strong className="text-slate-800 dark:text-slate-200 text-sm font-bold">
                {deploymentStatus?.model_candidate || 'Two-Stage Candidate Ensemble'}
              </strong>
            </div>
            <div>
              <span className="text-slate-400 font-medium block">Generated At</span>
              <strong className="text-slate-800 dark:text-slate-200">
                {deploymentStatus?.timestamp || 'Just now'}
              </strong>
            </div>
            <div>
              <span className="text-slate-400 font-medium block">Target Location</span>
              <code className="text-indigo-600 dark:text-indigo-400 font-mono">
                /models/deployed_model.pkl
              </code>
            </div>
          </div>

          {/* Validation Report Table (Old vs New) */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center space-x-1.5">
              <TrendingUp className="w-4 h-4 text-indigo-500" />
              <span>Validation Report: Old vs Retrained Candidate</span>
            </h3>

            <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-100 dark:bg-slate-800/80 text-slate-600 dark:text-slate-400 font-semibold border-b border-slate-200 dark:border-slate-800">
                  <tr>
                    <th className="py-2.5 px-3">Metric</th>
                    <th className="py-2.5 px-3 text-center">Old Production Model</th>
                    <th className="py-2.5 px-3 text-center">New Candidate Model</th>
                    <th className="py-2.5 px-3 text-center">Difference (Delta)</th>
                    <th className="py-2.5 px-3 text-right">Assessment</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {Object.entries(metrics).map(([key, item]) => (
                    <tr key={key} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                      <td className="py-2.5 px-3 font-bold text-slate-800 dark:text-slate-200 capitalize">
                        {key.replace('_', ' ')}
                      </td>
                      <td className="py-2.5 px-3 text-center font-mono text-slate-500 dark:text-slate-400">
                        {(item.old_model * 100).toFixed(2)}%
                      </td>
                      <td className="py-2.5 px-3 text-center font-mono font-bold text-indigo-600 dark:text-indigo-400">
                        {(item.new_model * 100).toFixed(2)}%
                      </td>
                      <td className="py-2.5 px-3 text-center font-mono font-semibold text-emerald-600 dark:text-emerald-400">
                        {item.delta >= 0 ? `+${(item.delta * 100).toFixed(2)}%` : `${(item.delta * 100).toFixed(2)}%`}
                      </td>
                      <td className="py-2.5 px-3 text-right">
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                          {item.improved ? '🟢 Improved' : 'Stable'}
                        </span>
                      </td>
                    </tr>
                  ))}
                  {Object.keys(metrics).length === 0 && (
                    <tr>
                      <td colSpan={5} className="py-4 text-center text-slate-400">
                        Evaluating candidate metrics...
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Top Drifted Features */}
          {topDrifted.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center space-x-1.5">
                <AlertTriangle className="w-4 h-4 text-amber-500" />
                <span>Primary Features Driving Drift (KS-Test)</span>
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
                {topDrifted.map((feat, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-xl bg-amber-50/70 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/60 space-y-1"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900 dark:text-slate-100">{feat.feature}</span>
                      <span className="px-1.5 py-0.2 rounded text-[10px] font-extrabold bg-amber-500 text-white">
                        Rank #{idx + 1}
                      </span>
                    </div>
                    <div className="text-slate-500 dark:text-slate-400 text-[11px]">
                      KS-Stat: <strong className="text-slate-700 dark:text-slate-300">{feat.ks_statistic.toFixed(4)}</strong>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Reviewer Field */}
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700 space-y-2">
            <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block">
              Approver Signature / Reviewer Name:
            </label>
            <input
              type="text"
              value={reviewerName}
              onChange={(e) => setReviewerName(e.target.value)}
              placeholder="Enter your name or role"
              className="w-full px-3.5 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 text-xs font-medium focus:ring-2 focus:ring-indigo-500 outline-none"
            />
          </div>
        </div>

        {/* Modal Footer Actions */}
        <div className="p-4 bg-slate-50 dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3">
          <button
            onClick={handleViewPortal}
            className="w-full sm:w-auto px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-xs font-bold transition-all inline-flex items-center justify-center space-x-1.5"
          >
            <span>Open Governance Portal</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </button>

          <div className="flex items-center space-x-2 w-full sm:w-auto">
            <button
              onClick={handleDismiss}
              className="flex-1 sm:flex-none px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-xs font-semibold transition-all"
            >
              Remind Later
            </button>
            <button
              onClick={handleApprove}
              disabled={isApproving}
              className="flex-1 sm:flex-none px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-bold text-xs shadow-md transition-all inline-flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {isApproving ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Deploying Model...</span>
                </>
              ) : (
                <>
                  <ShieldCheck className="w-4 h-4" />
                  <span>Approve & Deploy Model</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
