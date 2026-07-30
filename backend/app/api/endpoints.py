"""
🌐 REST API ENDPOINTS ROUTER
Defines all production endpoints using FastAPI APIRouter and Pydantic response models.
"""

from fastapi import APIRouter, Response, status
from typing import List, Dict, Any
from backend.app.config import PROJECT_NAME, PROJECT_VERSION
from backend.app.schemas.monitoring_schema import (
    RootResponse,
    SummaryResponse,
    BatchItem,
    DriftAnalysisResponse,
    AccuracyItem,
    RunPipelineResponse,
    DashboardResponse
)
from backend.app.services.monitoring_service import MonitoringService

router = APIRouter()

@router.get("/", response_model=RootResponse, summary="API Health Check", tags=["System"])
def get_root():
    """Returns basic system status, project name, and version."""
    return {
        "project": PROJECT_NAME,
        "status": "Running",
        "version": PROJECT_VERSION
    }

@router.get("/summary", response_model=SummaryResponse, summary="Pipeline Execution Summary", tags=["Monitoring"])
def get_summary():
    """Returns high-level KPI summary metrics across all processed batches."""
    return MonitoringService.get_summary()

@router.get("/batches", response_model=List[BatchItem], summary="Batch Monitoring Timeline", tags=["Monitoring"])
def get_batches():
    """Returns sequential batch monitoring records including drift counts, decision levels, and accuracy."""
    return MonitoringService.get_batches()

@router.get("/drift", response_model=DriftAnalysisResponse, summary="Feature Drift Frequency Analysis", tags=["Drift"])
def get_drift():
    """Returns unique shifted features, feature drift frequency counts, and batch IDs."""
    return MonitoringService.get_drift_analysis()

@router.get("/accuracy", response_model=List[AccuracyItem], summary="Accuracy Trends", tags=["Monitoring"])
def get_accuracy():
    """Returns pre-adaptation and post-adaptation accuracy trends for every batch."""
    return MonitoringService.get_accuracy_trends()

@router.get("/dashboard", response_model=DashboardResponse, summary="Aggregated Dashboard Payload", tags=["Dashboard"])
def get_dashboard():
    """Returns aggregated summary, batch timeline, accuracy trends, and drift analysis in a single payload."""
    return MonitoringService.get_dashboard_data()

@router.get("/logs", summary="Structured Decision Log (JSON)", tags=["Logs"])
def get_logs():
    """Returns the complete structured decision log as JSON."""
    return MonitoringService.get_logs_json()

@router.get("/retraining-log", summary="Pipeline Event Log (Text)", tags=["Logs"])
def get_retraining_log():
    """Returns retraining_log.txt as plain text."""
    content = MonitoringService.get_retraining_log_text()
    return Response(content=content, media_type="text/plain")

@router.post("/run-monitoring", response_model=RunPipelineResponse, summary="Execute Monitoring Pipeline", tags=["Pipeline Execution"])
def run_monitoring():
    """Executes the monitoring pipeline once, updates logs, and returns execution summary."""
    return MonitoringService.run_monitoring_pipeline()
