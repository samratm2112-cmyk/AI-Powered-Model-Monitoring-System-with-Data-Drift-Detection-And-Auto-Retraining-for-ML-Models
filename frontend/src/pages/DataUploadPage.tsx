import React, { useState, useCallback, useRef, useMemo, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Upload,
  FileSpreadsheet,
  Columns,
  Eye,
  Rocket,
  Check,
  ChevronRight,
  AlertTriangle,
  RefreshCw,
  Info,
  Sparkles,
  ArrowLeft,
  CheckCircle2,
  Loader2,
  BarChart3,
} from 'lucide-react';
import {
  uploadService,
  CSVPreviewResponse,
  TemplateInfoResponse,
  TransformPreviewResponse,
  UploadPipelineResponse,
} from '../services/uploadService';

// ─── Step Configuration ───
const STEPS = [
  { id: 1, label: 'Upload CSV', icon: Upload },
  { id: 2, label: 'Map Columns', icon: Columns },
  { id: 3, label: 'Preview', icon: Eye },
  { id: 4, label: 'Execute', icon: Rocket },
];

export const DataUploadPage: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Wizard state
  const [currentStep, setCurrentStep] = useState(1);

  // Step 1 state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [csvPreview, setCsvPreview] = useState<CSVPreviewResponse | null>(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  // Step 2 state
  const [templateInfo, setTemplateInfo] = useState<TemplateInfoResponse | null>(null);
  const [columnMapping, setColumnMapping] = useState<Record<string, string | null>>({});
  const [templateLoading, setTemplateLoading] = useState(false);

  // Step 3 state
  const [transformPreview, setTransformPreview] = useState<TransformPreviewResponse | null>(null);
  const [transformLoading, setTransformLoading] = useState(false);
  const [transformError, setTransformError] = useState<string | null>(null);

  // Step 4 state
  const [pipelineResult, setPipelineResult] = useState<UploadPipelineResponse | null>(null);
  const [pipelineLoading, setPipelineLoading] = useState(false);
  const [pipelineError, setPipelineError] = useState<string | null>(null);

  // ─── File Upload Handlers ───
  const handleFileSelect = useCallback(async (file: File) => {
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setUploadError('Please upload a .csv file.');
      return;
    }
    if (file.size > 50 * 1024 * 1024) {
      setUploadError('File exceeds 50 MB limit.');
      return;
    }

    setSelectedFile(file);
    setUploadError(null);
    setUploadLoading(true);

    try {
      const preview = await uploadService.uploadCSVPreview(file);
      setCsvPreview(preview);
    } catch (err: any) {
      setUploadError(err.response?.data?.detail || err.message || 'Failed to parse CSV.');
    } finally {
      setUploadLoading(false);
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files?.[0];
      if (file) handleFileSelect(file);
    },
    [handleFileSelect]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => setIsDragging(false), []);

  // ─── Step 2: Load Template Info ───
  const loadTemplateInfo = useCallback(async () => {
    setTemplateLoading(true);
    try {
      const info = await uploadService.getTemplateInfo();
      setTemplateInfo(info);
      // Initialize mapping with all null (Smart Fill)
      const initialMapping: Record<string, string | null> = {};
      info.template_columns.forEach((col) => {
        initialMapping[col] = null;
      });
      setColumnMapping(initialMapping);
    } catch (err: any) {
      setUploadError(err.message || 'Failed to load template info.');
    } finally {
      setTemplateLoading(false);
    }
  }, []);

  useEffect(() => {
    if (currentStep === 2 && !templateInfo) {
      loadTemplateInfo();
    }
  }, [currentStep, templateInfo, loadTemplateInfo]);

  // ─── Step 3: Transform Preview ───
  const handleTransformPreview = useCallback(async () => {
    if (!selectedFile) return;
    setTransformLoading(true);
    setTransformError(null);
    try {
      const preview = await uploadService.transformCSV(selectedFile, columnMapping);
      setTransformPreview(preview);
    } catch (err: any) {
      setTransformError(err.response?.data?.detail || err.message || 'Transform failed.');
    } finally {
      setTransformLoading(false);
    }
  }, [selectedFile, columnMapping]);

  useEffect(() => {
    if (currentStep === 3 && !transformPreview && selectedFile) {
      handleTransformPreview();
    }
  }, [currentStep, transformPreview, selectedFile, handleTransformPreview]);

  // ─── Step 4: Execute Pipeline ───
  const handleExecutePipeline = useCallback(async () => {
    if (!selectedFile) return;
    setPipelineLoading(true);
    setPipelineError(null);
    try {
      const result = await uploadService.executeUploadPipeline(selectedFile, columnMapping);
      setPipelineResult(result);
    } catch (err: any) {
      setPipelineError(err.response?.data?.detail || err.message || 'Pipeline execution failed.');
    } finally {
      setPipelineLoading(false);
    }
  }, [selectedFile, columnMapping]);

  // ─── Computed Mapping Stats ───
  const mappingStats = useMemo(() => {
    const mapped = Object.values(columnMapping).filter((v) => v !== null && v !== '').length;
    const total = Object.keys(columnMapping).length;
    return { mapped, smartFilled: total - mapped, total };
  }, [columnMapping]);

  const requiredMapped = useMemo(() => {
    if (!templateInfo) return false;
    return templateInfo.required_columns.every(
      (col) => columnMapping[col] !== null && columnMapping[col] !== ''
    );
  }, [templateInfo, columnMapping]);

  // ─── Navigation ───
  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return csvPreview !== null;
      case 2:
        return requiredMapped;
      case 3:
        return transformPreview !== null;
      case 4:
        return true;
      default:
        return false;
    }
  };

  const goNext = () => {
    if (canProceed() && currentStep < 4) {
      setCurrentStep((s) => s + 1);
    }
  };

  const goBack = () => {
    if (currentStep > 1) {
      if (currentStep === 3) setTransformPreview(null);
      setCurrentStep((s) => s - 1);
    }
  };

  const resetWizard = () => {
    setCurrentStep(1);
    setSelectedFile(null);
    setCsvPreview(null);
    setUploadError(null);
    setTemplateInfo(null);
    setColumnMapping({});
    setTransformPreview(null);
    setTransformError(null);
    setPipelineResult(null);
    setPipelineError(null);
  };

  // ─── Render ───
  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 p-6 rounded-2xl text-white shadow-lg">
        <div className="space-y-1">
          <div className="inline-flex items-center space-x-2 bg-white/10 backdrop-blur-md px-3 py-1 rounded-full text-xs font-semibold">
            <Upload className="w-3.5 h-3.5" />
            <span>CSV Data Ingestion</span>
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight">Upload & Map Your Dataset</h1>
          <p className="text-sm text-purple-100 max-w-2xl">
            Upload your own CSV, map columns to the 31-feature template, and run the drift monitoring pipeline.
          </p>
        </div>
        <button
          onClick={resetWizard}
          className="self-start sm:self-center px-4 py-2.5 rounded-xl bg-white/20 hover:bg-white/30 backdrop-blur-md text-white font-medium text-sm transition-all flex items-center space-x-2"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Reset</span>
        </button>
      </div>

      {/* Stepper */}
      <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm">
        <div className="flex items-center justify-between">
          {STEPS.map((step, index) => {
            const Icon = step.icon;
            const isActive = step.id === currentStep;
            const isCompleted = step.id < currentStep;
            return (
              <React.Fragment key={step.id}>
                <div className="flex items-center space-x-2.5">
                  <div
                    className={`w-9 h-9 rounded-full flex items-center justify-center transition-all ${
                      isCompleted
                        ? 'bg-emerald-500 text-white'
                        : isActive
                        ? 'bg-brand-600 text-white shadow-lg shadow-brand-500/30'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-400'
                    }`}
                  >
                    {isCompleted ? <Check className="w-4 h-4" /> : <Icon className="w-4 h-4" />}
                  </div>
                  <span
                    className={`text-sm font-medium hidden sm:block ${
                      isActive
                        ? 'text-brand-700 dark:text-brand-400'
                        : isCompleted
                        ? 'text-emerald-600 dark:text-emerald-400'
                        : 'text-slate-400'
                    }`}
                  >
                    {step.label}
                  </span>
                </div>
                {index < STEPS.length - 1 && (
                  <div
                    className={`flex-1 h-0.5 mx-3 rounded-full transition-colors ${
                      step.id < currentStep
                        ? 'bg-emerald-400'
                        : 'bg-slate-200 dark:bg-slate-700'
                    }`}
                  />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Step Content */}
      <div className="min-h-[400px]">
        {/* ═══════════════ STEP 1: Upload CSV ═══════════════ */}
        {currentStep === 1 && (
          <div className="space-y-5">
            {/* Drop Zone */}
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => fileInputRef.current?.click()}
              className={`relative p-10 rounded-2xl border-2 border-dashed cursor-pointer transition-all text-center space-y-3 ${
                isDragging
                  ? 'border-brand-500 bg-brand-50/50 dark:bg-brand-950/20'
                  : csvPreview
                  ? 'border-emerald-400 bg-emerald-50/30 dark:bg-emerald-950/10'
                  : 'border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-900/50 hover:border-brand-400 hover:bg-brand-50/20'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleFileSelect(file);
                }}
              />
              {uploadLoading ? (
                <div className="flex flex-col items-center space-y-3">
                  <Loader2 className="w-10 h-10 text-brand-600 animate-spin" />
                  <p className="text-sm font-medium text-slate-600 dark:text-slate-400">
                    Parsing CSV file...
                  </p>
                </div>
              ) : csvPreview ? (
                <div className="flex flex-col items-center space-y-2">
                  <CheckCircle2 className="w-10 h-10 text-emerald-500" />
                  <p className="text-base font-bold text-slate-900 dark:text-slate-100">
                    {csvPreview.filename}
                  </p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {csvPreview.row_count.toLocaleString()} rows · {csvPreview.column_count} columns · {csvPreview.file_size_mb} MB
                  </p>
                  <p className="text-xs text-brand-500 mt-1">Click or drop again to replace</p>
                </div>
              ) : (
                <div className="flex flex-col items-center space-y-2">
                  <FileSpreadsheet className="w-10 h-10 text-slate-400" />
                  <p className="text-base font-semibold text-slate-700 dark:text-slate-300">
                    Drag & drop your CSV file here
                  </p>
                  <p className="text-sm text-slate-400">or click to browse · Max 50 MB</p>
                </div>
              )}
            </div>

            {uploadError && (
              <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/20 border border-rose-200 dark:border-rose-800 flex items-center space-x-3">
                <AlertTriangle className="w-5 h-5 text-rose-500 shrink-0" />
                <p className="text-sm text-rose-700 dark:text-rose-400">{uploadError}</p>
              </div>
            )}

            {/* CSV Preview Table */}
            {csvPreview && (
              <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                    Data Preview (First 5 Rows)
                  </h3>
                  <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500">
                    {csvPreview.columns.length} Columns
                  </span>
                </div>
                <div className="overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-700">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="bg-slate-50 dark:bg-slate-800/80">
                        {csvPreview.columns.map((col) => (
                          <th
                            key={col}
                            className="px-3 py-2 text-left font-bold text-slate-600 dark:text-slate-400 whitespace-nowrap border-b border-slate-200 dark:border-slate-700"
                          >
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {csvPreview.preview_rows.map((row, idx) => (
                        <tr
                          key={idx}
                          className="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/40"
                        >
                          {csvPreview.columns.map((col) => (
                            <td
                              key={col}
                              className="px-3 py-1.5 text-slate-700 dark:text-slate-300 whitespace-nowrap font-mono"
                            >
                              {row[col] !== null && row[col] !== undefined
                                ? typeof row[col] === 'number'
                                  ? Number(row[col]).toFixed(4)
                                  : String(row[col])
                                : '—'}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ═══════════════ STEP 2: Column Mapping ═══════════════ */}
        {currentStep === 2 && (
          <div className="space-y-5">
            {templateLoading ? (
              <div className="flex flex-col items-center justify-center min-h-[300px] space-y-3">
                <Loader2 className="w-8 h-8 text-brand-600 animate-spin" />
                <p className="text-sm text-slate-500">Loading template schema...</p>
              </div>
            ) : templateInfo ? (
              <>
                {/* Mapping Stats Banner */}
                <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 rounded-full bg-brand-500" />
                      <span className="text-xs font-bold text-slate-700 dark:text-slate-300">
                        Mapped: {mappingStats.mapped}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 rounded-full bg-amber-400" />
                      <span className="text-xs font-bold text-slate-700 dark:text-slate-300">
                        Smart Fill: {mappingStats.smartFilled}
                      </span>
                    </div>
                    <div className="text-xs text-slate-400">/ {mappingStats.total} total</div>
                  </div>
                  {!requiredMapped && (
                    <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-800">
                      <AlertTriangle className="w-3.5 h-3.5 text-rose-500" />
                      <span className="text-xs font-semibold text-rose-600 dark:text-rose-400">
                        Amount & Class must be mapped
                      </span>
                    </div>
                  )}
                </div>

                {/* Info Card */}
                <div className="p-3 rounded-xl bg-blue-50/60 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900/40 flex items-start space-x-3">
                  <Info className="w-4 h-4 text-blue-500 shrink-0 mt-0.5" />
                  <p className="text-xs text-blue-700 dark:text-blue-400">
                    For each template column, select the matching column from your CSV. Unmapped columns
                    will be <strong>Smart Filled</strong> using baseline distribution statistics (mean ± std)
                    to prevent false KS drift triggers.
                  </p>
                </div>

                {/* Mapping Table */}
                <div className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="bg-slate-50 dark:bg-slate-800/80">
                          <th className="px-4 py-3 text-left font-bold text-slate-600 dark:text-slate-400 w-40">
                            Template Column
                          </th>
                          <th className="px-4 py-3 text-left font-bold text-slate-600 dark:text-slate-400">
                            Your CSV Column
                          </th>
                          <th className="px-4 py-3 text-center font-bold text-slate-600 dark:text-slate-400 w-28">
                            Status
                          </th>
                          <th className="px-4 py-3 text-right font-bold text-slate-600 dark:text-slate-400 w-36">
                            Baseline Stats
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {templateInfo.template_columns.map((templateCol) => {
                          const isRequired = templateInfo.required_columns.includes(templateCol);
                          const isMapped =
                            columnMapping[templateCol] !== null &&
                            columnMapping[templateCol] !== '' &&
                            columnMapping[templateCol] !== undefined;
                          const stat = templateInfo.baseline_statistics.find(
                            (s) => s.column === templateCol
                          );

                          return (
                            <tr
                              key={templateCol}
                              className={`border-b border-slate-100 dark:border-slate-800 transition-colors ${
                                isRequired && !isMapped
                                  ? 'bg-rose-50/40 dark:bg-rose-950/10'
                                  : ''
                              }`}
                            >
                              <td className="px-4 py-2.5">
                                <div className="flex items-center space-x-2">
                                  <span className="font-bold text-slate-900 dark:text-slate-100 font-mono text-xs">
                                    {templateCol}
                                  </span>
                                  {isRequired && (
                                    <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-rose-100 text-rose-700 dark:bg-rose-950/50 dark:text-rose-400">
                                      REQUIRED
                                    </span>
                                  )}
                                </div>
                              </td>
                              <td className="px-4 py-2.5">
                                <select
                                  value={columnMapping[templateCol] || ''}
                                  onChange={(e) =>
                                    setColumnMapping((prev) => ({
                                      ...prev,
                                      [templateCol]: e.target.value || null,
                                    }))
                                  }
                                  className={`w-full px-3 py-1.5 rounded-lg border text-xs font-medium focus:outline-none focus:ring-2 focus:ring-brand-500 transition-colors ${
                                    isMapped
                                      ? 'bg-brand-50 dark:bg-brand-950/30 border-brand-300 dark:border-brand-700 text-brand-800 dark:text-brand-300'
                                      : 'bg-slate-50 dark:bg-slate-800/80 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400'
                                  }`}
                                >
                                  <option value="">Smart Fill (Auto)</option>
                                  {csvPreview?.columns.map((userCol) => (
                                    <option key={userCol} value={userCol}>
                                      {userCol}
                                    </option>
                                  ))}
                                </select>
                              </td>
                              <td className="px-4 py-2.5 text-center">
                                {isMapped ? (
                                  <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full bg-brand-100 dark:bg-brand-950/40 text-brand-700 dark:text-brand-400 text-[10px] font-bold">
                                    <Check className="w-3 h-3" />
                                    <span>Mapped</span>
                                  </span>
                                ) : (
                                  <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400 text-[10px] font-bold">
                                    <Sparkles className="w-3 h-3" />
                                    <span>Smart Fill</span>
                                  </span>
                                )}
                              </td>
                              <td className="px-4 py-2.5 text-right">
                                <span className="text-[10px] font-mono text-slate-400">
                                  μ={stat?.mean.toFixed(3)} σ={stat?.std.toFixed(3)}
                                </span>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            ) : null}
          </div>
        )}

        {/* ═══════════════ STEP 3: Preview Transformed Data ═══════════════ */}
        {currentStep === 3 && (
          <div className="space-y-5">
            {transformLoading ? (
              <div className="flex flex-col items-center justify-center min-h-[300px] space-y-3">
                <Loader2 className="w-8 h-8 text-brand-600 animate-spin" />
                <p className="text-sm text-slate-500">Transforming CSV to template format...</p>
              </div>
            ) : transformError ? (
              <div className="p-6 rounded-2xl bg-rose-50 dark:bg-rose-950/20 border border-rose-200 dark:border-rose-800 text-center space-y-3">
                <AlertTriangle className="w-8 h-8 text-rose-500 mx-auto" />
                <p className="text-sm font-semibold text-rose-700 dark:text-rose-400">
                  {transformError}
                </p>
                <button
                  onClick={handleTransformPreview}
                  className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium transition-colors"
                >
                  Retry Transform
                </button>
              </div>
            ) : transformPreview ? (
              <>
                {/* Mapping Summary */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm text-center space-y-1">
                    <p className="text-2xl font-black text-slate-900 dark:text-slate-100">
                      {transformPreview.total_rows.toLocaleString()}
                    </p>
                    <p className="text-xs font-medium text-slate-500">Total Rows</p>
                  </div>
                  <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm text-center space-y-1">
                    <p className="text-2xl font-black text-brand-600 dark:text-brand-400">
                      {transformPreview.mapped_count}
                    </p>
                    <p className="text-xs font-medium text-slate-500">Columns Mapped</p>
                  </div>
                  <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm text-center space-y-1">
                    <p className="text-2xl font-black text-amber-500">
                      {transformPreview.smart_filled_count}
                    </p>
                    <p className="text-xs font-medium text-slate-500">Smart Filled</p>
                  </div>
                </div>

                {/* Transformed Preview Table */}
                <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
                  <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                    Transformed Data Preview (First 5 Rows)
                  </h3>
                  <div className="overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-700">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="bg-slate-50 dark:bg-slate-800/80">
                          {Object.keys(transformPreview.preview_rows[0] || {}).map((col) => {
                            const isMapped = transformPreview.mapped_columns.includes(col);
                            return (
                              <th
                                key={col}
                                className={`px-3 py-2 text-left font-bold whitespace-nowrap border-b ${
                                  isMapped
                                    ? 'text-brand-700 dark:text-brand-400 bg-brand-50/50 dark:bg-brand-950/20 border-brand-200 dark:border-brand-800'
                                    : 'text-amber-600 dark:text-amber-400 border-slate-200 dark:border-slate-700'
                                }`}
                              >
                                <span className="flex items-center space-x-1">
                                  <span>{col}</span>
                                  {isMapped ? (
                                    <Check className="w-3 h-3" />
                                  ) : (
                                    <Sparkles className="w-3 h-3" />
                                  )}
                                </span>
                              </th>
                            );
                          })}
                        </tr>
                      </thead>
                      <tbody>
                        {transformPreview.preview_rows.map((row, idx) => (
                          <tr
                            key={idx}
                            className="border-b border-slate-100 dark:border-slate-800"
                          >
                            {Object.entries(row).map(([col, val]) => (
                              <td
                                key={col}
                                className="px-3 py-1.5 text-slate-700 dark:text-slate-300 whitespace-nowrap font-mono"
                              >
                                {typeof val === 'number' ? val.toFixed(4) : String(val ?? '—')}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Column Legend */}
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 flex flex-wrap gap-4 text-xs">
                  <div className="flex items-center space-x-2">
                    <Check className="w-3.5 h-3.5 text-brand-600" />
                    <span className="font-medium text-slate-600 dark:text-slate-400">
                      User-Mapped ({transformPreview.mapped_columns.join(', ') || 'None'})
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                    <span className="font-medium text-slate-600 dark:text-slate-400">
                      Smart Filled from Baseline Distribution
                    </span>
                  </div>
                </div>
              </>
            ) : null}
          </div>
        )}

        {/* ═══════════════ STEP 4: Execute Pipeline ═══════════════ */}
        {currentStep === 4 && (
          <div className="space-y-5">
            {!pipelineResult && !pipelineLoading && !pipelineError && (
              <div className="p-8 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm text-center space-y-6">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-brand-500 to-purple-600 text-white mx-auto flex items-center justify-center shadow-xl shadow-brand-500/20">
                  <Rocket className="w-8 h-8" />
                </div>
                <div className="space-y-1">
                  <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">
                    Ready to Run Pipeline
                  </h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md mx-auto">
                    Your CSV has been transformed to the template format. Click below to execute
                    the continuous drift monitoring pipeline on your data.
                  </p>
                </div>

                {/* Summary Card */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 max-w-lg mx-auto">
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800 text-center">
                    <p className="text-lg font-black text-slate-900 dark:text-slate-100">
                      {transformPreview?.total_rows.toLocaleString() || '—'}
                    </p>
                    <p className="text-[10px] text-slate-500">Total Rows</p>
                  </div>
                  <div className="p-3 rounded-xl bg-brand-50 dark:bg-brand-950/30 text-center">
                    <p className="text-lg font-black text-brand-600 dark:text-brand-400">
                      {transformPreview?.mapped_count || 0}
                    </p>
                    <p className="text-[10px] text-slate-500">Mapped Cols</p>
                  </div>
                  <div className="p-3 rounded-xl bg-amber-50 dark:bg-amber-950/30 text-center">
                    <p className="text-lg font-black text-amber-600 dark:text-amber-400">
                      {transformPreview?.smart_filled_count || 0}
                    </p>
                    <p className="text-[10px] text-slate-500">Smart Filled</p>
                  </div>
                </div>

                <button
                  onClick={handleExecutePipeline}
                  className="px-8 py-3 rounded-xl bg-gradient-to-r from-brand-600 to-purple-600 hover:from-brand-700 hover:to-purple-700 text-white font-bold text-sm transition-all shadow-lg shadow-brand-500/25 flex items-center space-x-2 mx-auto"
                >
                  <Rocket className="w-4 h-4" />
                  <span>Run Monitoring Pipeline</span>
                </button>
              </div>
            )}

            {pipelineLoading && (
              <div className="p-12 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm text-center space-y-4">
                <div className="relative w-16 h-16 mx-auto">
                  <Loader2 className="w-16 h-16 text-brand-600 animate-spin" />
                </div>
                <div className="space-y-1">
                  <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">
                    Pipeline Executing...
                  </h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    Training models, detecting drift, and evaluating ensemble performance.
                    This may take up to 60 seconds.
                  </p>
                </div>
              </div>
            )}

            {pipelineError && (
              <div className="p-6 rounded-2xl bg-rose-50 dark:bg-rose-950/20 border border-rose-200 dark:border-rose-800 text-center space-y-3">
                <AlertTriangle className="w-8 h-8 text-rose-500 mx-auto" />
                <p className="text-sm font-semibold text-rose-700 dark:text-rose-400">
                  {pipelineError}
                </p>
                <button
                  onClick={handleExecutePipeline}
                  className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium transition-colors"
                >
                  Retry Pipeline
                </button>
              </div>
            )}

            {pipelineResult && (
              <div className="space-y-5">
                {/* Success Banner */}
                <div className="p-6 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg text-center space-y-2">
                  <CheckCircle2 className="w-12 h-12 mx-auto" />
                  <h3 className="text-xl font-extrabold">Pipeline Execution Complete!</h3>
                  <p className="text-sm text-emerald-100">{pipelineResult.message}</p>
                </div>

                {/* Pipeline Summary KPIs */}
                {pipelineResult.pipeline_summary && (
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm text-center space-y-1">
                      <p className="text-xl font-black text-slate-900 dark:text-slate-100">
                        {pipelineResult.pipeline_summary.total_batches_processed || '—'}
                      </p>
                      <p className="text-[10px] font-medium text-slate-500">Batches Processed</p>
                    </div>
                    <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm text-center space-y-1">
                      <p className="text-xl font-black text-emerald-600">
                        {pipelineResult.pipeline_summary.green_count || 0}
                      </p>
                      <p className="text-[10px] font-medium text-slate-500">🟢 GREEN</p>
                    </div>
                    <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm text-center space-y-1">
                      <p className="text-xl font-black text-amber-500">
                        {pipelineResult.pipeline_summary.yellow_count || 0}
                      </p>
                      <p className="text-[10px] font-medium text-slate-500">🟡 YELLOW</p>
                    </div>
                    <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm text-center space-y-1">
                      <p className="text-xl font-black text-rose-500">
                        {pipelineResult.pipeline_summary.red_count || 0}
                      </p>
                      <p className="text-[10px] font-medium text-slate-500">🔴 RED</p>
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center justify-center gap-3">
                  <button
                    onClick={() => navigate('/')}
                    className="px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-medium text-sm transition-colors flex items-center space-x-2"
                  >
                    <BarChart3 className="w-4 h-4" />
                    <span>View Dashboard</span>
                  </button>
                  <button
                    onClick={resetWizard}
                    className="px-5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-medium text-sm transition-colors flex items-center space-x-2"
                  >
                    <RefreshCw className="w-4 h-4" />
                    <span>Upload Another</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Bottom Navigation */}
      {!(currentStep === 4 && pipelineResult) && (
        <div className="flex items-center justify-between p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm">
          <button
            onClick={goBack}
            disabled={currentStep === 1}
            className="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-medium text-sm transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back</span>
          </button>
          {currentStep < 4 && (
            <button
              onClick={goNext}
              disabled={!canProceed()}
              className="px-5 py-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-medium text-sm transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex items-center space-x-2 shadow-sm"
            >
              <span>Continue</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          )}
        </div>
      )}
    </div>
  );
};
