"""
📋 PYDANTIC SCHEMAS FOR CSV UPLOAD, COLUMN MAPPING & TRANSFORMATION
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any


class CSVPreviewResponse(BaseModel):
    """Response after uploading a CSV file for preview."""
    filename: str = Field(..., example="transactions.csv")
    row_count: int = Field(..., example=50000)
    column_count: int = Field(..., example=12)
    columns: List[str] = Field(..., example=["timestamp", "amount", "merchant", "is_fraud"])
    preview_rows: List[Dict[str, Any]] = Field(
        ..., description="First 5 rows of the uploaded CSV as list of dicts"
    )
    file_size_mb: float = Field(..., example=4.2)


class ColumnStatistic(BaseModel):
    """Per-column baseline distribution statistics."""
    column: str = Field(..., example="V1")
    mean: float = Field(..., example=-0.0234)
    std: float = Field(..., example=1.9564)


class TemplateInfoResponse(BaseModel):
    """Response providing the template schema and baseline statistics."""
    template_columns: List[str] = Field(
        ..., description="The 31 required columns in order"
    )
    required_columns: List[str] = Field(
        default=["Amount", "Class"],
        description="Columns the user MUST map"
    )
    baseline_statistics: List[ColumnStatistic] = Field(
        ..., description="Mean and std for each template column from baseline training data"
    )


class TransformRequest(BaseModel):
    """Request body specifying the column mapping."""
    column_mapping: Dict[str, Optional[str]] = Field(
        ...,
        description="Mapping of template columns to user CSV columns. Use null for Smart Fill.",
        example={"Time": None, "V1": "feature_1", "Amount": "transaction_amount", "Class": "is_fraud"}
    )


class TransformPreviewResponse(BaseModel):
    """Response showing a preview of the transformed data."""
    preview_rows: List[Dict[str, Any]] = Field(
        ..., description="First 5 rows of the transformed CSV"
    )
    total_rows: int = Field(..., example=50000)
    mapped_columns: List[str] = Field(..., description="Columns explicitly mapped by the user")
    smart_filled_columns: List[str] = Field(..., description="Columns auto-filled from baseline distribution")
    mapped_count: int = Field(..., example=8)
    smart_filled_count: int = Field(..., example=23)


class UploadPipelineResponse(BaseModel):
    """Response after executing the pipeline on uploaded data."""
    status: str = Field(..., example="SUCCESS")
    message: str = Field(..., example="Pipeline executed on uploaded data")
    total_rows: int = Field(..., example=50000)
    mapped_columns: List[str]
    smart_filled_columns: List[str]
    pipeline_summary: Optional[Dict[str, Any]] = Field(
        None, description="Pipeline execution summary metrics"
    )
