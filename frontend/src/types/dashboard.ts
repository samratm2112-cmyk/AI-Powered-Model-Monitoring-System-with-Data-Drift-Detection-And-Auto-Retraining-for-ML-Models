export interface SummaryData {
  total_batches_processed: number;
  green_count: number;
  yellow_count: number;
  red_count: number;
  retraining_count: number;
  average_accuracy: number;
  average_accuracy_improvement: number;
  local_buffer_size: number;
}

export interface BatchItem {
  batch_id: number;
  simulated_drift_type: string;
  decision_level: 'GREEN' | 'YELLOW' | 'RED';
  drifted_feature_count: number;
  accuracy_before: number;
  accuracy_after: number;
  retraining_triggered: boolean;
}

export interface AccuracyItem {
  batch_id: number;
  accuracy_before: number;
  accuracy_after: number;
}

export interface DriftAnalysisData {
  drifted_features: string[];
  feature_counts: Record<string, number>;
  batch_ids: number[];
}

export interface DashboardData {
  summary: SummaryData;
  batch_timeline: BatchItem[];
  accuracy_trend: AccuracyItem[];
  drift_analysis: DriftAnalysisData;
  generated_at: string;
  system_status: string;
}
