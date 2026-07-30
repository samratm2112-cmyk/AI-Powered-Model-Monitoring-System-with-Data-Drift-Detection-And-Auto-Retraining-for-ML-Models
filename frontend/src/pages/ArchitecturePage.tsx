import React, { useState } from 'react';
import {
  Inbox,
  CheckCircle2,
  SlidersHorizontal,
  Activity,
  GitBranch,
  RefreshCw,
  Layers,
  ShieldAlert,
  FileText,
  Server,
  LayoutDashboard,
  ArrowDown,
  Info,
  Code2,
  Cpu,
  Database,
  Check,
  ChevronRight,
} from 'lucide-react';

interface StageDetail {
  id: string;
  title: string;
  category: string;
  icon: React.ElementType;
  purpose: string;
  input: string;
  output: string;
  tech: string;
  color: string;
}

const STAGES: StageDetail[] = [
  {
    id: 'ingestion',
    title: '1. Incoming Production Stream',
    category: 'Ingestion Layer',
    icon: Inbox,
    purpose: 'Sequentially ingests production streaming data in configurable batch sizes (1,000 records/batch).',
    input: 'Raw credit card transactions (30 features)',
    output: 'Batch DataFrame (X_batch, y_batch)',
    tech: 'Python, Pandas, BatchStreamIngestion',
    color: 'border-blue-500 text-blue-500 bg-blue-50 dark:bg-blue-950/40',
  },
  {
    id: 'validation',
    title: '2. Data Validation',
    category: 'Validation Layer',
    icon: CheckCircle2,
    purpose: 'Verifies schema integrity, feature count (30 columns), null values, and data type alignment.',
    input: 'Unvalidated Batch DataFrame',
    output: 'Validation Status (Passed / Failed)',
    tech: 'DataValidator, Pydantic, Python',
    color: 'border-emerald-500 text-emerald-500 bg-emerald-50 dark:bg-emerald-950/40',
  },
  {
    id: 'preprocess',
    title: '3. Data Preprocessing',
    category: 'Feature Engineering',
    icon: SlidersHorizontal,
    purpose: 'Applies baseline RobustScaler transformation to non-bounded features (Amount) while keeping PCA features intact.',
    input: 'Validated Batch Data',
    output: 'Scaled Feature Array (X_batch_scaled)',
    tech: 'FeaturePreprocessor, Scikit-learn',
    color: 'border-amber-500 text-amber-500 bg-amber-50 dark:bg-amber-950/40',
  },
  {
    id: 'drift',
    title: '4. KS Test Drift Detection',
    category: 'Statistical Drift Detector',
    icon: Activity,
    purpose: 'Performs two-sample Kolmogorov-Smirnov test (alpha = 0.05) across 29 features, excluding monotonic Time feature.',
    input: 'Reference Baseline vs Batch Features',
    output: 'Drift Results (Shifted Features List & Count)',
    tech: 'KSDriftDetector, SciPy Statistical Tests',
    color: 'border-purple-500 text-purple-500 bg-purple-50 dark:bg-purple-950/40',
  },
  {
    id: 'decision',
    title: '5. 3-Tier Decision Engine',
    category: 'MLOps Policy Evaluator',
    icon: GitBranch,
    purpose: 'Evaluates drift severity & accuracy drops to assign GREEN, YELLOW, or RED status without unnecessary model churn.',
    input: 'Drift Results & Pre-Acc Metric',
    output: 'Decision Level (GREEN / YELLOW / RED)',
    tech: 'RetrainingDecisionEngine, Custom Rules',
    color: 'border-rose-500 text-rose-500 bg-rose-50 dark:bg-rose-950/40',
  },
  {
    id: 'retrain',
    title: '6. Local Model Retraining',
    category: 'Adaptive Retraining',
    icon: RefreshCw,
    purpose: 'Fits Local Model on recent batch stream when RED level is triggered, storing up to 5,000 samples in a sliding window buffer.',
    input: 'Recent Batch Stream (RED trigger)',
    output: 'Updated Local Model Weights',
    tech: 'RandomForestClassifier, Sliding Window Buffer',
    color: 'border-cyan-500 text-cyan-500 bg-cyan-50 dark:bg-cyan-950/40',
  },
  {
    id: 'ensemble',
    title: '7. Hybrid Global-Local Ensemble',
    category: 'Model Inference Layer',
    icon: Layers,
    purpose: 'Combines 70% static Global Model (historical memory) with 30% updated Local Model (novel attack adaptation) via soft voting.',
    input: 'Scaled Batch Features',
    output: 'Ensemble Probability Predictions',
    tech: 'GlobalLocalEnsemble, Soft Voting Classifier',
    color: 'border-indigo-500 text-indigo-500 bg-indigo-50 dark:bg-indigo-950/40',
  },
  {
    id: 'prediction',
    title: '8. Prediction Service',
    category: 'Fraud Classification',
    icon: ShieldAlert,
    purpose: 'Generates final fraud classification probabilities and calculates post-adaptation accuracy & recall metrics.',
    input: 'Ensemble Probabilities',
    output: 'Binary Class Labels (0: Normal, 1: Fraud)',
    tech: 'ModelEvaluator, Thresholding (0.50)',
    color: 'border-emerald-500 text-emerald-500 bg-emerald-50 dark:bg-emerald-950/40',
  },
  {
    id: 'logging',
    title: '9. Pipeline Audit Logging',
    category: 'Persistence Layer',
    icon: FileText,
    purpose: 'Persists batch metadata, drift stats, decision levels, and retraining events to structured JSON and text logs.',
    input: 'Batch Record Summary',
    output: 'decision_log.json & retraining_log.txt',
    tech: 'PipelineLogger, Python I/O',
    color: 'border-slate-500 text-slate-500 bg-slate-50 dark:bg-slate-950/40',
  },
  {
    id: 'backend',
    title: '10. FastAPI REST Backend',
    category: 'Service Layer API',
    icon: Server,
    purpose: 'Exposes monitoring metrics, drift stats, batch timelines, and log content via RESTful OpenAPI endpoints.',
    input: 'Pipeline Log Files',
    output: 'REST JSON Responses (GET /dashboard)',
    tech: 'FastAPI, Uvicorn, Pydantic',
    color: 'border-brand-600 text-brand-600 bg-brand-50 dark:bg-brand-950/40',
  },
  {
    id: 'frontend',
    title: '11. React Monitoring Dashboard',
    category: 'Presentation Layer',
    icon: LayoutDashboard,
    purpose: 'Renders real-time executive summaries, interactive Recharts, log viewers, and system architecture visualizations.',
    input: 'REST API Payload (http://localhost:8000)',
    output: 'Interactive UI Web Dashboard (http://localhost:3000)',
    tech: 'React 19, TypeScript, Tailwind CSS, Recharts',
    color: 'border-teal-500 text-teal-500 bg-teal-50 dark:bg-teal-950/40',
  },
];

export const ArchitecturePage: React.FC = () => {
  const [selectedStage, setSelectedStage] = useState<StageDetail>(STAGES[0]);

  return (
    <div className="space-y-8 pb-10">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-slate-100 tracking-tight flex items-center space-x-3">
          <GitBranch className="w-8 h-8 text-brand-600 dark:text-brand-400" />
          <span>System Architecture</span>
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          End-to-End Continuous ML Monitoring and Automatic Model Adaptation Pipeline
        </p>
      </div>

      {/* Main Grid: Interactive Architecture Flow & Stage Detail Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Architecture Flow Stage Diagram (2 Cols) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Interactive Execution Pipeline (Click any block for details)
            </span>
            <span className="text-xs text-brand-600 dark:text-brand-400 font-semibold flex items-center space-x-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
              <span>11 Pipeline Modules</span>
            </span>
          </div>

          <div className="space-y-3">
            {STAGES.map((stage, idx) => {
              const Icon = stage.icon;
              const isSelected = selectedStage.id === stage.id;
              const isDecisionNode = stage.id === 'decision';

              return (
                <div key={stage.id} className="space-y-3">
                  {/* Stage Card */}
                  <div
                    onClick={() => setSelectedStage(stage)}
                    className={`p-4 rounded-xl border-2 cursor-pointer transition-all duration-200 flex items-start justify-between shadow-sm hover:shadow-md ${
                      isSelected
                        ? `${stage.color} ring-2 ring-brand-500/50 scale-[1.01]`
                        : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-start space-x-3.5">
                      <div className={`p-2.5 rounded-lg border ${stage.color}`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-semibold text-slate-400">{stage.category}</span>
                        </div>
                        <h3 className="font-bold text-base text-slate-900 dark:text-slate-100">{stage.title}</h3>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">{stage.purpose}</p>
                      </div>
                    </div>

                    <ChevronRight className={`w-5 h-5 transition-transform ${isSelected ? 'rotate-90 text-brand-600' : 'text-slate-400'}`} />
                  </div>

                  {/* Special Branching Node Display for Decision Engine */}
                  {isDecisionNode && (
                    <div className="p-4 rounded-xl bg-slate-900 text-white border border-slate-800 space-y-3 my-2">
                      <div className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-2">
                        <GitBranch className="w-4 h-4 text-amber-400" />
                        <span>Decision Engine Policy Branching Paths</span>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                        <div className="p-3 rounded-lg bg-emerald-950/60 border border-emerald-800 text-emerald-300">
                          <span className="font-bold block">🟢 GREEN Path</span>
                          <span className="text-[11px] text-slate-300 mt-0.5 block">0 features drifted & Acc &ge; 99% &rarr; Continue Monitoring (No Retraining)</span>
                        </div>
                        <div className="p-3 rounded-lg bg-amber-950/60 border border-amber-800 text-amber-300">
                          <span className="font-bold block">🟡 YELLOW Path</span>
                          <span className="text-[11px] text-slate-300 mt-0.5 block">1–2 features drifted & Acc &ge; 99% &rarr; Log Warning (Suppressed Retrain)</span>
                        </div>
                        <div className="p-3 rounded-lg bg-rose-950/60 border border-rose-800 text-rose-300">
                          <span className="font-bold block">🔴 RED Path</span>
                          <span className="text-[11px] text-slate-300 mt-0.5 block">&ge;3 features drifted or Acc &lt; 99% &rarr; Trigger Local Retraining</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Animated Arrow Connector */}
                  {idx < STAGES.length - 1 && (
                    <div className="flex justify-center my-1">
                      <ArrowDown className="w-4 h-4 text-brand-500 animate-bounce" />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Stage Information Side Panel */}
        <div className="space-y-6">
          <div className="p-6 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm sticky top-20 space-y-6">
            <div className="flex items-center space-x-3 border-b border-slate-100 dark:border-slate-800 pb-4">
              <div className={`p-3 rounded-xl border ${selectedStage.color}`}>
                {React.createElement(selectedStage.icon, { className: 'w-6 h-6' })}
              </div>
              <div>
                <span className="text-xs font-semibold text-brand-600 dark:text-brand-400 uppercase">{selectedStage.category}</span>
                <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">{selectedStage.title}</h3>
              </div>
            </div>

            {/* Purpose */}
            <div className="space-y-1.5">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-1.5">
                <Info className="w-3.5 h-3.5 text-blue-500" />
                <span>Purpose & Description</span>
              </span>
              <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/50 p-3 rounded-lg border border-slate-100 dark:border-slate-800">
                {selectedStage.purpose}
              </p>
            </div>

            {/* Input Data */}
            <div className="space-y-1.5">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-1.5">
                <Database className="w-3.5 h-3.5 text-amber-500" />
                <span>Input Data Payload</span>
              </span>
              <div className="font-mono text-xs text-slate-700 dark:text-slate-300 bg-slate-50 dark:bg-slate-800/50 p-3 rounded-lg border border-slate-100 dark:border-slate-800">
                {selectedStage.input}
              </div>
            </div>

            {/* Output Data */}
            <div className="space-y-1.5">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-1.5">
                <Check className="w-3.5 h-3.5 text-emerald-500" />
                <span>Output Data Payload</span>
              </span>
              <div className="font-mono text-xs text-slate-700 dark:text-slate-300 bg-slate-50 dark:bg-slate-800/50 p-3 rounded-lg border border-slate-100 dark:border-slate-800">
                {selectedStage.output}
              </div>
            </div>

            {/* Technology Stack Used */}
            <div className="space-y-1.5">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-1.5">
                <Code2 className="w-3.5 h-3.5 text-purple-500" />
                <span>Technology Used</span>
              </span>
              <div className="text-xs font-semibold text-slate-900 dark:text-slate-100 bg-purple-50 dark:bg-purple-950/40 p-3 rounded-lg border border-purple-200 dark:border-purple-900/40 text-purple-700 dark:text-purple-300">
                {selectedStage.tech}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ============================================================================ */}
      {/* TECHNOLOGY STACK CARDS */}
      {/* ============================================================================ */}
      <div className="p-6 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center space-x-2 border-b border-slate-100 dark:border-slate-800 pb-3">
          <Cpu className="w-5 h-5 text-brand-600 dark:text-brand-400" />
          <span>Technology Stack Architecture</span>
        </h3>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 text-xs text-center font-semibold">
          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 space-y-1">
            <span className="text-lg block">🐍</span>
            <span className="text-slate-900 dark:text-slate-100">Python 3.11</span>
            <span className="text-[10px] text-slate-400 block font-normal">Core Engine</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 space-y-1">
            <span className="text-lg block">🤖</span>
            <span className="text-slate-900 dark:text-slate-100">Scikit-Learn</span>
            <span className="text-[10px] text-slate-400 block font-normal">Random Forest</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 space-y-1">
            <span className="text-lg block">⚡</span>
            <span className="text-slate-900 dark:text-slate-100">FastAPI</span>
            <span className="text-[10px] text-slate-400 block font-normal">REST Service</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 space-y-1">
            <span className="text-lg block">⚛️</span>
            <span className="text-slate-900 dark:text-slate-100">React 19</span>
            <span className="text-[10px] text-slate-400 block font-normal">UI Framework</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 space-y-1">
            <span className="text-lg block">📘</span>
            <span className="text-slate-900 dark:text-slate-100">TypeScript</span>
            <span className="text-[10px] text-slate-400 block font-normal">Type Safety</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 space-y-1">
            <span className="text-lg block">🎨</span>
            <span className="text-slate-900 dark:text-slate-100">Tailwind CSS</span>
            <span className="text-[10px] text-slate-400 block font-normal">Styling</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 space-y-1">
            <span className="text-lg block">📊</span>
            <span className="text-slate-900 dark:text-slate-100">Recharts</span>
            <span className="text-[10px] text-slate-400 block font-normal">Charts</span>
          </div>
        </div>
      </div>

      {/* Footer System Status Bar */}
      <div className="p-4 rounded-xl bg-slate-900 text-white flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs border border-slate-800">
        <div className="flex items-center space-x-3">
          <span className="font-bold">System Version: <code className="text-brand-400">v1.0.0</code></span>
          <span>•</span>
          <span>Monitoring Mode: <strong className="text-slate-300">KS-Test (Excl Time)</strong></span>
        </div>

        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="font-bold text-emerald-400">Pipeline Status: Operational</span>
        </div>
      </div>
    </div>
  );
};
