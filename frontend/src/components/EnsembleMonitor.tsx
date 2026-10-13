import React from 'react';
import { useSystemHealth } from '../hooks/useSystemHealth';
import { Layers, Database, Activity, CheckCircle2 } from 'lucide-react';

export const EnsembleMonitor: React.FC = () => {
  const { data: health, isLoading } = useSystemHealth();

  if (isLoading) {
    return (
      <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 animate-pulse">
        <div className="h-5 w-48 bg-slate-200 dark:bg-slate-800 rounded mb-4"></div>
        <div className="h-24 bg-slate-100 dark:bg-slate-800/50 rounded-xl"></div>
      </div>
    );
  }

  const ensemble = health?.ensemble;
  const stages = health?.pipeline_stages;

  return (
    <div className="p-6 rounded-2xl bg-gradient-to-br from-white via-white to-indigo-50/30 dark:from-slate-900 dark:via-slate-900 dark:to-indigo-950/20 border border-indigo-100 dark:border-indigo-900/40 shadow-sm relative overflow-hidden">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              Two-Stage Ensemble Monitor
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400 border border-emerald-500/30">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5 animate-pulse"></span>
                {health?.status || 'Active'}
              </span>
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Hybrid Fusion: Long-Term Memory (Global) + Rapid Sliding Window Adaptation (Local)
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 text-xs font-medium text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700">
          <Database className="w-3.5 h-3.5 text-indigo-500" />
          <span>Active Model: <code className="text-indigo-600 dark:text-indigo-400 font-mono">deployed_model.pkl</code></span>
        </div>
      </div>

      {/* Pipeline Stages Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5">
        {/* Stage 1: VAE / Anomaly Filter */}
        <div className="p-4 rounded-xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-xs relative group hover:border-indigo-300 dark:hover:border-indigo-700 transition-all">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <span className="w-6 h-6 rounded-lg bg-indigo-100 dark:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300 font-bold text-xs flex items-center justify-center">
                1
              </span>
              <span className="text-sm font-bold text-slate-900 dark:text-slate-100">
                {stages?.stage1_filter?.name || 'Stage 1: VAE / Anomaly Filter'}
              </span>
            </div>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
              <CheckCircle2 className="w-3 h-3 mr-1" />
              {stages?.stage1_filter?.status || 'Active'}
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-2 leading-relaxed">
            {stages?.stage1_filter?.description || 'Models normal behavior distribution; flags distribution weirdness & zero-day anomalies.'}
          </p>
          <div className="flex items-center justify-between text-xs text-slate-600 dark:text-slate-400 pt-2 border-t border-slate-100 dark:border-slate-800/80">
            <span>Filter Type:</span>
            <span className="font-semibold text-slate-700 dark:text-slate-300">Isolation Forest / VAE</span>
          </div>
        </div>

        {/* Stage 2: Supervised XGBoost Classifier */}
        <div className="p-4 rounded-xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-xs relative group hover:border-indigo-300 dark:hover:border-indigo-700 transition-all">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <span className="w-6 h-6 rounded-lg bg-indigo-100 dark:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300 font-bold text-xs flex items-center justify-center">
                2
              </span>
              <span className="text-sm font-bold text-slate-900 dark:text-slate-100">
                {stages?.stage2_expert?.name || 'Stage 2: XGBoost Expert Classifier'}
              </span>
            </div>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
              <CheckCircle2 className="w-3 h-3 mr-1" />
              {stages?.stage2_expert?.status || 'Active'}
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-2 leading-relaxed">
            {stages?.stage2_expert?.description || 'Processes flagged samples with calibrated decision threshold of 0.3 to confirm target class classification.'}
          </p>
          <div className="flex items-center justify-between text-xs text-slate-600 dark:text-slate-400 pt-2 border-t border-slate-100 dark:border-slate-800/80">
            <span>Classifier:</span>
            <span className="font-semibold text-slate-700 dark:text-slate-300">Supervised XGBoost Trees</span>
          </div>
        </div>
      </div>

      {/* Ensemble Weights & Telemetry Progress Bar */}
      <div className="p-4 rounded-xl bg-slate-50/80 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/60">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
            Hybrid Fusion Weights
          </span>
          <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
            Threshold Cutoff: <strong className="text-slate-800 dark:text-slate-200">0.30</strong>
          </span>
        </div>

        {/* Dual Progress Bar */}
        <div className="w-full h-3 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden flex mb-2">
          <div
            style={{ width: `${(ensemble?.global_weight || 0.7) * 100}%` }}
            className="bg-indigo-600 dark:bg-indigo-500 h-full transition-all duration-500"
            title="Global Model (70%)"
          ></div>
          <div
            style={{ width: `${(ensemble?.local_weight || 0.3) * 100}%` }}
            className="bg-cyan-500 dark:bg-cyan-400 h-full transition-all duration-500"
            title="Local Model (30%)"
          ></div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs pt-1">
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-indigo-600"></span>
            <span className="text-slate-600 dark:text-slate-400">
              Global Expert: <strong>{ensemble?.global_weight_percentage || '70%'}</strong>
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-500"></span>
            <span className="text-slate-600 dark:text-slate-400">
              Local Expert: <strong>{ensemble?.local_weight_percentage || '30%'}</strong>
            </span>
          </div>
          <div className="flex items-center space-x-2 text-slate-600 dark:text-slate-400">
            <Activity className="w-3.5 h-3.5 text-slate-500" />
            <span>
              Sliding Buffer: <strong>{ensemble?.local_buffer_size?.toLocaleString() || '5,000'} / 5,000</strong>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
