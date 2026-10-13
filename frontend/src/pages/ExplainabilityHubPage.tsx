import React, { useState } from 'react';
import { useExplainability } from '../hooks/useExplainability';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
  CartesianGrid,
} from 'recharts';
import {
  Zap,
  Search,
  Sparkles,
  TrendingUp,
  TrendingDown,
  RefreshCw,
} from 'lucide-react';

export const ExplainabilityHubPage: React.FC = () => {
  const [selectedId, setSelectedId] = useState<number>(42);
  const [inputVal, setInputVal] = useState<string>('42');
  const [filterQuery, setFilterQuery] = useState<string>('');
  const [sortDirection, setSortDirection] = useState<'all' | 'positive' | 'negative'>('all');

  const { data, isLoading, isError, error, refetch, isFetching } = useExplainability(selectedId);

  const handleSelectSample = (id: number) => {
    setSelectedId(id);
    setInputVal(id.toString());
  };

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const parsed = parseInt(inputVal, 10);
    if (!isNaN(parsed) && parsed >= 0) {
      setSelectedId(parsed);
    }
  };

  // Filter features for the table & chart
  const displayedFeatures = (data?.features || [])
    .filter((f) => {
      if (filterQuery) {
        return f.feature.toLowerCase().includes(filterQuery.toLowerCase());
      }
      return true;
    })
    .filter((f) => {
      if (sortDirection === 'positive') return f.direction === 'positive';
      if (sortDirection === 'negative') return f.direction === 'negative';
      return true;
    });

  // Top 15 features for clean horizontal bar chart visualization
  const chartData = [...(data?.features || [])]
    .sort((a, b) => b.abs_shap - a.abs_shap)
    .slice(0, 14)
    .map((item) => ({
      feature: item.feature,
      shap: item.shap_value,
      value: item.value,
      direction: item.direction,
    }))
    .reverse(); // Reverse so highest appears on top of YAxis

  return (
    <div className="space-y-6 pb-12">
      {/* ============================================================================ */}
      {/* HEADER SECTION */}
      {/* ============================================================================ */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950 to-purple-950 p-6 md:p-8 text-white shadow-xl border border-indigo-900/50">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div className="space-y-2">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-bold border border-indigo-500/30">
              <Zap className="w-3.5 h-3.5 text-indigo-400" />
              <span>SHAP Interpretability Engine</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">
              Drift Root Cause Analysis
            </h1>
            <p className="text-sm md:text-base text-slate-300 max-w-2xl">
              Inspect granular, mathematical feature-level attributions for any transaction using Shapley Additive Explanations.
            </p>
          </div>

          <div className="flex items-center space-x-2 bg-white/5 backdrop-blur-md p-3 rounded-xl border border-white/10 shrink-0">
            <button
              onClick={() => refetch()}
              disabled={isFetching}
              className="flex items-center space-x-2 px-3.5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-xs transition-colors shadow-sm disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin' : ''}`} />
              <span>{isFetching ? 'Computing...' : 'Recalculate SHAP'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* ============================================================================ */}
      {/* TRANSACTION SELECTOR BAR */}
      {/* ============================================================================ */}
      <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider block mb-1">
              Select or Search Transaction
            </span>
            <div className="flex flex-wrap gap-2">
              {data?.sample_ids?.map((s) => (
                <button
                  key={s.id}
                  onClick={() => handleSelectSample(s.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    selectedId === s.id
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : s.class_label === 1
                      ? 'bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300 border border-rose-200 dark:border-rose-900/40 hover:bg-rose-100'
                      : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                  }`}
                >
                  {s.label}
                </button>
              ))}
            </div>
          </div>

          {/* Direct ID search input */}
          <form onSubmit={handleManualSubmit} className="flex items-center space-x-2 shrink-0">
            <div className="relative">
              <input
                type="number"
                min="0"
                value={inputVal}
                onChange={(e) => setInputVal(e.target.value)}
                placeholder="Enter Transaction ID..."
                className="w-44 px-3 py-2 rounded-lg text-xs bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <button
              type="submit"
              className="px-3.5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition-colors"
            >
              Analyze ID
            </button>
          </form>
        </div>
      </div>

      {isLoading ? (
        <div className="p-12 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center space-y-3">
          <RefreshCw className="w-8 h-8 text-indigo-500 animate-spin mx-auto" />
          <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">
            Computing TreeExplainer SHAP Values for Transaction #{selectedId}...
          </p>
        </div>
      ) : isError ? (
        <div className="p-8 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-center text-rose-700 dark:text-rose-300">
          <p className="text-sm font-bold">Failed to compute SHAP explanation:</p>
          <p className="text-xs mt-1">{(error as Error)?.message || 'Internal error'}</p>
        </div>
      ) : data ? (
        <>
          {/* ============================================================================ */}
          {/* HUMAN-FRIENDLY NATURAL LANGUAGE EXPLANATION BANNER */}
          {/* ============================================================================ */}
          {data.human_explanation && (
            <div className="p-6 rounded-2xl bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-indigo-500/10 border-2 border-indigo-500/30 dark:border-indigo-500/40 shadow-sm relative overflow-hidden">
              <div className="flex items-start space-x-4">
                <div className="p-3.5 rounded-2xl bg-indigo-600 text-white shadow-md shrink-0">
                  <Sparkles className="w-6 h-6" />
                </div>
                <div className="space-y-2 flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-bold uppercase bg-indigo-600 text-white shadow-xs">
                      Natural Language Explanation
                    </span>
                    <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                      Translated from SHAP Feature Attributions
                    </span>
                  </div>
                  <p className="text-base sm:text-lg font-bold text-slate-900 dark:text-slate-100 leading-relaxed">
                    "{data.human_explanation}"
                  </p>
                  {data.human_sentences && data.human_sentences.length > 0 && (
                    <div className="pt-2 border-t border-indigo-100 dark:border-indigo-950/60 grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                      {data.human_sentences.map((sentence, idx) => (
                        <div key={idx} className="flex items-start space-x-2 text-slate-700 dark:text-slate-300">
                          <span className="text-indigo-500 font-bold mt-0.5">•</span>
                          <span>{sentence}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* ============================================================================ */}
          {/* TRANSACTION PREDICTION TELEMETRY BANNER */}
          {/* ============================================================================ */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Prediction Label */}
            <div className={`p-5 rounded-2xl border ${
              data.predicted_class === 1
                ? 'bg-rose-50/80 dark:bg-rose-950/30 border-rose-200 dark:border-rose-900/60'
                : 'bg-emerald-50/80 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-900/60'
            }`}>
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider block">
                Model Prediction
              </span>
              <div className="mt-2 flex items-center space-x-2">
                <span className={`text-2xl font-black ${
                  data.predicted_class === 1 ? 'text-rose-600 dark:text-rose-400' : 'text-emerald-600 dark:text-emerald-400'
                }`}>
                  {data.prediction_label}
                </span>
              </div>
              <span className="text-xs text-slate-500 dark:text-slate-400 mt-1 block">
                Calibrated Threshold: <strong>0.30</strong>
              </span>
            </div>

            {/* Probability Gauge */}
            <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider block">
                Anomaly Score
              </span>
              <div className="mt-2 flex items-baseline space-x-2">
                <span className="text-3xl font-extrabold text-slate-900 dark:text-slate-100">
                  {(data.anomaly_score * 100).toFixed(2)}%
                </span>
              </div>
              <div className="w-full h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden mt-2">
                <div
                  style={{ width: `${Math.min(100, data.anomaly_score * 100)}%` }}
                  className={`h-full ${data.anomaly_score >= 0.3 ? 'bg-rose-500' : 'bg-emerald-500'}`}
                ></div>
              </div>
            </div>

            {/* True Label */}
            <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider block">
                Ground Truth Label
              </span>
              <div className="mt-2 flex items-center space-x-2">
                <span className="text-xl font-bold text-slate-800 dark:text-slate-200">
                  {data.is_target_class === 1 ? 'Class 1 (Anomalous)' : 'Class 0 (Baseline)'}
                </span>
              </div>
              <span className="text-xs text-slate-500 dark:text-slate-400 mt-1 block">
                Dataset Record #{data.transaction_id}
              </span>
            </div>

            {/* Base Value vs Output */}
            <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider block">
                SHAP Function Output
              </span>
              <div className="mt-2 space-y-1 text-xs">
                <div className="flex justify-between text-slate-600 dark:text-slate-400">
                  <span>Base E[f(x)]:</span>
                  <strong className="font-mono text-slate-800 dark:text-slate-200">{data.base_value}</strong>
                </div>
                <div className="flex justify-between text-slate-600 dark:text-slate-400">
                  <span>Output f(x):</span>
                  <strong className={`font-mono font-bold ${data.model_output > 0 ? 'text-rose-500' : 'text-emerald-500'}`}>
                    {data.model_output}
                  </strong>
                </div>
              </div>
            </div>
          </div>

          {/* ============================================================================ */}
          {/* TOP PUSH SUMMARY CARDS */}
          {/* ============================================================================ */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Top Anomaly Pushes (+ SHAP) */}
            <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-rose-200/80 dark:border-rose-900/40 shadow-xs space-y-3">
              <div className="flex items-center space-x-2 text-rose-600 dark:text-rose-400">
                <TrendingUp className="w-4 h-4" />
                <h3 className="text-sm font-bold uppercase tracking-wide">
                  Top Features Pushing Towards Anomaly (+ SHAP)
                </h3>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                These feature deviations contributed the strongest positive pressure towards the anomalous verdict:
              </p>
              <div className="space-y-2">
                {data.top_anomaly_pushes?.map((item) => (
                  <div
                    key={item.feature}
                    className="p-3 rounded-xl bg-rose-50/70 dark:bg-rose-950/40 border border-rose-200/60 dark:border-rose-900/40 text-xs space-y-1"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="font-extrabold text-slate-900 dark:text-slate-100">{item.feature}</span>
                        {item.human_description && (
                          <span className="text-slate-500 dark:text-slate-400">({item.human_description})</span>
                        )}
                      </div>
                      <span className="font-mono text-[11px] font-bold text-rose-600 dark:text-rose-400 bg-rose-100/80 dark:bg-rose-900/60 px-1.5 py-0.5 rounded">
                        +{item.shap_value.toFixed(4)}
                      </span>
                    </div>
                    {item.human_sentence && (
                      <p className="text-xs font-semibold text-rose-700 dark:text-rose-300">
                        {item.human_sentence}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Top Legit Pushes (- SHAP) */}
            <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-emerald-200/80 dark:border-emerald-900/40 shadow-xs space-y-3">
              <div className="flex items-center space-x-2 text-emerald-600 dark:text-emerald-400">
                <TrendingDown className="w-4 h-4" />
                <h3 className="text-sm font-bold uppercase tracking-wide">
                  Top Features Pushing Towards Legitimate (- SHAP)
                </h3>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                These features exerted negative pressure, pushing the transaction towards benign classification:
              </p>
              <div className="space-y-2">
                {data.top_legit_pushes?.map((item) => (
                  <div
                    key={item.feature}
                    className="p-3 rounded-xl bg-emerald-50/70 dark:bg-emerald-950/40 border border-emerald-200/60 dark:border-emerald-900/40 text-xs space-y-1"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="font-extrabold text-slate-900 dark:text-slate-100">{item.feature}</span>
                        {item.human_description && (
                          <span className="text-slate-500 dark:text-slate-400">({item.human_description})</span>
                        )}
                      </div>
                      <span className="font-mono text-[11px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-100/80 dark:bg-emerald-900/60 px-1.5 py-0.5 rounded">
                        {item.shap_value.toFixed(4)}
                      </span>
                    </div>
                    {item.human_sentence && (
                      <p className="text-xs font-semibold text-emerald-700 dark:text-emerald-300">
                        {item.human_sentence}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* ============================================================================ */}
          {/* DYNAMIC SHAP HORIZONTAL BAR CHART */}
          {/* ============================================================================ */}
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-indigo-500" />
                  Dynamic SHAP Feature Contribution Waterfall
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Relative impact of the top 14 features on transaction #{data.transaction_id}. Red pushes toward anomaly (+), Green pushes toward baseline (-).
                </p>
              </div>

              <div className="flex items-center space-x-3 text-xs">
                <span className="flex items-center space-x-1 text-slate-600 dark:text-slate-400">
                  <span className="w-3 h-3 rounded-xs bg-rose-500"></span>
                  <span>+ SHAP (Anomaly Risk)</span>
                </span>
                <span className="flex items-center space-x-1 text-slate-600 dark:text-slate-400">
                  <span className="w-3 h-3 rounded-xs bg-emerald-500"></span>
                  <span>- SHAP (Legitimate)</span>
                </span>
              </div>
            </div>

            <div className="h-96 w-full pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={chartData}
                  layout="vertical"
                  margin={{ top: 10, right: 30, left: 40, bottom: 20 }}
                >
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} opacity={0.3} />
                  <XAxis
                    type="number"
                    tick={{ fontSize: 11, fill: '#64748B' }}
                    label={{ value: 'SHAP Value Contribution', position: 'bottom', offset: 0, fontSize: 11 }}
                  />
                  <YAxis
                    dataKey="feature"
                    type="category"
                    tick={{ fontSize: 12, fill: '#64748B' }}
                    width={55}
                  />
                  <ReferenceLine x={0} stroke="#94A3B8" strokeWidth={1.5} />
                  <RechartsTooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const item = payload[0].payload;
                        return (
                          <div className="p-3 rounded-xl bg-slate-900 text-white text-xs shadow-lg space-y-1 border border-slate-700">
                            <p className="font-bold text-sm text-indigo-300">{item.feature}</p>
                            <p className="text-slate-300">Feature Value: <strong>{item.value}</strong></p>
                            <p className={item.shap > 0 ? 'text-rose-400 font-bold' : 'text-emerald-400 font-bold'}>
                              SHAP Impact: {item.shap > 0 ? `+${item.shap.toFixed(4)} (Increases Anomaly Score)` : `${item.shap.toFixed(4)} (Pushes Baseline)`}
                            </p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Bar dataKey="shap" radius={[4, 4, 4, 4]}>
                    {chartData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={entry.shap > 0 ? '#EF4444' : '#10B981'}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* ============================================================================ */}
          {/* COMPLETE FEATURES ATTRIBUTION TABLE */}
          {/* ============================================================================ */}
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                  Complete Feature Attributions (All 30 Features)
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Search and inspect exact numerical values and mathematical weights.
                </p>
              </div>

              <div className="flex items-center space-x-2">
                {/* Search */}
                <div className="relative">
                  <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    value={filterQuery}
                    onChange={(e) => setFilterQuery(e.target.value)}
                    placeholder="Search feature..."
                    className="pl-8 pr-3 py-1.5 rounded-lg text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                </div>

                {/* Filter direction buttons */}
                <select
                  value={sortDirection}
                  onChange={(e) => setSortDirection(e.target.value as any)}
                  className="px-3 py-1.5 rounded-lg text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300"
                >
                  <option value="all">All Features</option>
                  <option value="positive">+ SHAP (Anomaly)</option>
                  <option value="negative">- SHAP (Legitimate)</option>
                </select>
              </div>
            </div>

            <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 dark:bg-slate-800/80 text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800 font-semibold">
                  <tr>
                    <th className="py-3 px-4">Feature</th>
                    <th className="py-3 px-4">Human-Friendly Meaning</th>
                    <th className="py-3 px-4">Raw Value</th>
                    <th className="py-3 px-4">SHAP Attribution</th>
                    <th className="py-3 px-4">Model Impact</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                  {displayedFeatures.map((f) => (
                    <tr key={f.feature} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition-colors">
                      <td className="py-2.5 px-4 font-bold text-slate-900 dark:text-slate-100">
                        {f.feature}
                      </td>
                      <td className="py-2.5 px-4">
                        <div className="space-y-0.5">
                          <span className="font-semibold text-slate-800 dark:text-slate-200 block text-xs">
                            {f.human_description || f.feature}
                          </span>
                          {f.human_sentence && (
                            <span className="text-[11px] text-slate-500 dark:text-slate-400 block">
                              {f.human_sentence}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-2.5 px-4 font-mono text-slate-600 dark:text-slate-400">
                        {f.value}
                      </td>
                      <td className={`py-2.5 px-4 font-mono font-bold ${
                        f.shap_value > 0 ? 'text-rose-600 dark:text-rose-400' : 'text-emerald-600 dark:text-emerald-400'
                      }`}>
                        {f.shap_value > 0 ? `+${f.shap_value.toFixed(4)}` : f.shap_value.toFixed(4)}
                      </td>
                      <td className="py-2.5 px-4">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${
                          f.direction === 'positive'
                            ? 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                            : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                        }`}>
                          {f.impact}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
};
