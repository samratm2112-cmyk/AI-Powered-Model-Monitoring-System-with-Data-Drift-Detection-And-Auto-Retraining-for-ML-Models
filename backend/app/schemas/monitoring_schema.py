"""
📋 PYDANTIC SCHEMAS FOR REST API REQUESTS AND RESPONSES
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class RootResponse(BaseModel):
    project: str = Field(..., example="ML Drift Detection & Monitoring System")
    status: str = Field(..., example="Running")
    version: str = Field(..., example="1.0")

class SummaryResponse(BaseModel):
    total_batches_processed: int = Field(..., example=10)
    green_count: int = Field(..., example=1)
    yellow_count: int = Field(..., example=4)
    red_count: int = Field(..., example=5)
    retraining_count: int = Field(..., example=5)
    average_accuracy: float = Field(..., example=0.9986)
    average_accuracy_improvement: float = Field(..., example=0.08)
    local_buffer_size: int = Field(..., example=5000)

class BatchItem(BaseModel):
    batch_id: int = Field(..., example=1)
    simulated_drift_type: str = Field(..., example="Normal")
    decision_level: str = Field(..., example="RED")
    drifted_feature_count: int = Field(..., example=3)
    accuracy_before: float = Field(..., example=0.999)
    accuracy_after: float = Field(..., example=1.0)
    retraining_triggered: bool = Field(..., example=True)

class DriftAnalysisResponse(BaseModel):
    drifted_features: List[str]
    feature_counts: Dict[str, int]
    batch_ids: List[int]

class AccuracyItem(BaseModel):
    batch_id: int
    accuracy_before: float
    accuracy_after: float

class RunPipelineResponse(BaseModel):
    status: str = Field(..., example="SUCCESS")
    message: str = Field(..., example="Monitoring pipeline executed successfully")
    summary: SummaryResponse

class DashboardResponse(BaseModel):
    summary: SummaryResponse
    batch_timeline: List[BatchItem]
    accuracy_trend: List[AccuracyItem]
    drift_analysis: DriftAnalysisResponse
    generated_at: str = Field(..., example="2026-07-24 16:45:00")
    system_status: str = Field(..., example="Running")
