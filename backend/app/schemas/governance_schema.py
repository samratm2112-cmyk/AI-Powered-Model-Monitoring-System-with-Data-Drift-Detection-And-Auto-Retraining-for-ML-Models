"""
📋 PYDANTIC SCHEMAS FOR HITL GOVERNANCE & ENSEMBLE SYSTEM HEALTH
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class MetricComparisonDetail(BaseModel):
    old_model: float
    new_model: float
    delta: float
    delta_pct: float
    improved: bool

class TopDriftFeatureItem(BaseModel):
    feature: str
    ks_statistic: float
    p_value: float
    drift_detected: bool

class ValidationReportData(BaseModel):
    timestamp: str
    metrics_comparison: Dict[str, MetricComparisonDetail]
    top_drifted_features: List[TopDriftFeatureItem]
    recommendation: str
    recommendation_rationale: str

class DeploymentStatusResponse(BaseModel):
    has_pending_deployment: bool
    status: str = Field(..., example="PENDING")
    timestamp: Optional[str] = None
    validation_report: Optional[ValidationReportData] = None
    model_candidate: Optional[str] = None
    message: Optional[str] = None

class DeploymentApproveRequest(BaseModel):
    reviewer: Optional[str] = "Human Compliance Officer"
    notes: Optional[str] = "Approved via MLOps Governance Portal"

class DeploymentApproveResponse(BaseModel):
    success: bool
    message: str
    status: str
    approved_at: Optional[str] = None
    active_model: Optional[str] = None

class PipelineStageInfo(BaseModel):
    name: str
    type: str
    status: str
    description: str

class EnsembleStatusInfo(BaseModel):
    architecture: str
    global_weight: float
    local_weight: float
    global_weight_percentage: str
    local_weight_percentage: str
    threshold: float
    local_buffer_size: int
    max_buffer_capacity: int
    global_fitted: bool
    local_fitted: bool

class SystemHealthResponse(BaseModel):
    status: str = Field(..., example="Healthy")
    system_state: str = Field(..., example="Active")
    ensemble: EnsembleStatusInfo
    pipeline_stages: Dict[str, PipelineStageInfo]
    deployed_model: Dict[str, Any]
    governance_status: str
