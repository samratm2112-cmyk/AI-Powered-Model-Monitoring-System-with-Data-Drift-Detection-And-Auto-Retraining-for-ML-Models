export interface MetricComparisonDetail {
  old_model: number;
  new_model: number;
  delta: number;
  delta_pct: number;
  improved: boolean;
}

export interface TopDriftFeatureItem {
  feature: string;
  ks_statistic: number;
  p_value: number;
  drift_detected: boolean;
}

export interface ValidationReportData {
  timestamp: string;
  metrics_comparison: Record<string, MetricComparisonDetail>;
  top_drifted_features: TopDriftFeatureItem[];
  recommendation: string;
  recommendation_rationale: string;
}

export interface DeploymentStatusResponse {
  has_pending_deployment: boolean;
  status: 'PENDING' | 'PENDING_APPROVAL' | 'APPROVED' | 'REJECTED' | 'NOMINAL' | 'NONE';
  timestamp?: string;
  validation_report?: ValidationReportData;
  model_candidate?: string;
  message?: string;
}

export interface DeploymentApproveResponse {
  success: boolean;
  message: string;
  status: string;
  approved_at?: string;
  active_model?: string;
}

export interface PipelineStageInfo {
  name: string;
  type: string;
  status: string;
  description: string;
}

export interface EnsembleStatusInfo {
  architecture: string;
  global_weight: number;
  local_weight: number;
  global_weight_percentage: string;
  local_weight_percentage: string;
  threshold: number;
  local_buffer_size: number;
  max_buffer_capacity: number;
  global_fitted: boolean;
  local_fitted: boolean;
}

export interface SystemHealthResponse {
  status: string;
  system_state: string;
  ensemble: EnsembleStatusInfo;
  pipeline_stages: Record<string, PipelineStageInfo>;
  deployed_model: {
    filename: string;
    exists: boolean;
    size_kb: number;
    last_modified: string;
  };
  governance_status: string;
}
