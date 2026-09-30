"""
🌐 REST API ENDPOINTS ROUTER
Defines all production endpoints using FastAPI APIRouter and Pydantic response models.
"""

from fastapi import APIRouter, Response, status, UploadFile, File, Form
from typing import List, Dict, Any
import json
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
from backend.app.schemas.upload_schema import (
    CSVPreviewResponse,
    TemplateInfoResponse,
    TransformPreviewResponse,
    UploadPipelineResponse,
)
from backend.app.services.monitoring_service import MonitoringService
from backend.app.services.upload_service import UploadService

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


# ─────────────────────────────────────────────────────────────────────
# CSV UPLOAD & COLUMN MAPPING ENDPOINTS
# ─────────────────────────────────────────────────────────────────────

@router.post(
    "/upload/preview",
    response_model=CSVPreviewResponse,
    summary="Upload CSV & Preview",
    tags=["CSV Upload"]
)
async def upload_preview(file: UploadFile = File(...)):
    """
    Upload a CSV file and return a preview of its first 5 rows,
    column names, row count, and file size.
    """
    # Read file content for size calculation
    content = await file.read()
    file_size_mb = round(len(content) / (1024 * 1024), 2)

    # Reset file position and parse
    import io
    import pandas as pd
    df = pd.read_csv(io.BytesIO(content))

    if df.empty:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Uploaded CSV file is empty.")

    preview_rows = df.head(5).to_dict(orient='records')
    # Convert any NaN to None for JSON serialization
    for row in preview_rows:
        for key in row:
            if pd.isna(row[key]):
                row[key] = None

    return {
        "filename": file.filename or "unknown.csv",
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "preview_rows": preview_rows,
        "file_size_mb": file_size_mb,
    }


@router.get(
    "/upload/template",
    response_model=TemplateInfoResponse,
    summary="Get Template Schema & Baseline Statistics",
    tags=["CSV Upload"]
)
def get_template():
    """
    Returns the 31-column template schema and per-column baseline
    distribution statistics (mean, std) computed from the training partition.
    """
    return {
        "template_columns": UploadService.get_template_columns(),
        "required_columns": ["Amount", "Class"],
        "baseline_statistics": UploadService.get_baseline_statistics(),
    }


@router.post(
    "/upload/transform",
    response_model=TransformPreviewResponse,
    summary="Transform CSV & Preview Result",
    tags=["CSV Upload"]
)
async def transform_preview(
    file: UploadFile = File(...),
    column_mapping: str = Form(...),
):
    """
    Upload a CSV file with a JSON column mapping string.
    Returns a preview of the first 5 rows of the transformed data in template format.
    """
    mapping_dict = json.loads(column_mapping)

    df = await UploadService.parse_uploaded_csv(file)
    transformed_df, mapped_cols, smart_filled_cols = UploadService.transform_csv(df, mapping_dict)

    preview_rows = transformed_df.head(5).to_dict(orient='records')

    return {
        "preview_rows": preview_rows,
        "total_rows": len(transformed_df),
        "mapped_columns": mapped_cols,
        "smart_filled_columns": smart_filled_cols,
        "mapped_count": len(mapped_cols),
        "smart_filled_count": len(smart_filled_cols),
    }


@router.post(
    "/upload/execute",
    response_model=UploadPipelineResponse,
    summary="Transform CSV & Execute Monitoring Pipeline",
    tags=["CSV Upload"]
)
async def execute_upload_pipeline(
    file: UploadFile = File(...),
    column_mapping: str = Form(...),
):
    """
    Upload a CSV file with a column mapping, transform it to the template format,
    save it, and execute the full monitoring pipeline on the transformed data.
    """
    mapping_dict = json.loads(column_mapping)

    df = await UploadService.parse_uploaded_csv(file)
    transformed_df, mapped_cols, smart_filled_cols = UploadService.transform_csv(df, mapping_dict)

    # Save transformed CSV
    UploadService.save_transformed_csv(transformed_df)

    # Execute pipeline
    pipeline_summary = UploadService.run_pipeline_on_upload()

    return {
        "status": "SUCCESS",
        "message": f"Pipeline executed successfully on {len(transformed_df)} rows ({len(mapped_cols)} mapped, {len(smart_filled_cols)} Smart Filled)",
        "total_rows": len(transformed_df),
        "mapped_columns": mapped_cols,
        "smart_filled_columns": smart_filled_cols,
        "pipeline_summary": pipeline_summary,
    }

