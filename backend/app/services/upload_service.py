"""
📤 CSV UPLOAD & TRANSFORMATION SERVICE
Handles CSV parsing, baseline statistics computation, Smart Fill for unmapped columns,
column mapping transformation, and pipeline execution on user-uploaded data.
"""

import os
import io
import sys
import numpy as np
import pandas as pd
from fastapi import UploadFile, HTTPException
from backend.app import config


class UploadService:
    """Service for CSV upload, column mapping, Smart Fill transformation, and pipeline execution."""

    # Cache baseline statistics after first computation
    _baseline_stats_cache = None

    @staticmethod
    async def parse_uploaded_csv(file: UploadFile) -> pd.DataFrame:
        """
        Reads and validates an uploaded CSV file.
        Returns the parsed DataFrame.
        """
        # Validate file extension
        if not file.filename or not file.filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload a .csv file."
            )

        # Read file content
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)

        # Validate file size
        if file_size_mb > config.MAX_UPLOAD_SIZE_MB:
            raise HTTPException(
                status_code=413,
                detail=f"File size ({file_size_mb:.1f} MB) exceeds maximum allowed size ({config.MAX_UPLOAD_SIZE_MB} MB)."
            )

        # Parse CSV
        try:
            df = pd.read_csv(io.BytesIO(content))
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse CSV file: {str(e)}"
            )

        if df.empty:
            raise HTTPException(status_code=400, detail="Uploaded CSV file is empty.")

        return df

    @staticmethod
    def get_file_size_mb(content: bytes) -> float:
        """Returns file size in megabytes."""
        return round(len(content) / (1024 * 1024), 2)

    @staticmethod
    def get_template_columns() -> list:
        """Returns the ordered list of 31 template columns."""
        return list(config.TEMPLATE_COLUMNS)

    @staticmethod
    def get_baseline_statistics() -> list:
        """
        Computes per-column mean and std from the baseline training partition
        (first 20,000 rows) of the template CSV.
        Results are cached after first computation.
        """
        if UploadService._baseline_stats_cache is not None:
            return UploadService._baseline_stats_cache

        if not os.path.exists(config.TEMPLATE_CSV_PATH):
            raise HTTPException(
                status_code=500,
                detail="Template CSV (creditcard.csv) not found. Cannot compute baseline statistics."
            )

        try:
            df = pd.read_csv(config.TEMPLATE_CSV_PATH, nrows=config.BASELINE_TRAIN_SIZE)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to read template CSV: {str(e)}"
            )

        stats = []
        for col in config.TEMPLATE_COLUMNS:
            if col in df.columns:
                col_mean = float(df[col].mean())
                col_std = float(df[col].std())
                # Ensure std is at least a small value to avoid zero-variance fills
                if col_std < 1e-10:
                    col_std = 0.01
                stats.append({
                    "column": col,
                    "mean": round(col_mean, 6),
                    "std": round(col_std, 6)
                })
            else:
                stats.append({"column": col, "mean": 0.0, "std": 1.0})

        UploadService._baseline_stats_cache = stats
        return stats

    @staticmethod
    def transform_csv(
        df: pd.DataFrame,
        column_mapping: dict,
    ) -> tuple:
        """
        Transforms a user CSV DataFrame into the template schema using column mapping.
        Unmapped columns are Smart Filled from the baseline distribution.

        Args:
            df: The user's uploaded DataFrame.
            column_mapping: Dict mapping template_col -> user_col (or None for Smart Fill).

        Returns:
            (transformed_df, mapped_columns, smart_filled_columns)
        """
        n_rows = len(df)
        baseline_stats = UploadService.get_baseline_statistics()
        stats_lookup = {s["column"]: s for s in baseline_stats}

        transformed = pd.DataFrame()
        mapped_columns = []
        smart_filled_columns = []

        for template_col in config.TEMPLATE_COLUMNS:
            user_col = column_mapping.get(template_col)

            if user_col and user_col in df.columns:
                # User mapped this column — use their data
                transformed[template_col] = df[user_col].values
                mapped_columns.append(template_col)
            else:
                # Smart Fill: sample from baseline distribution
                col_stats = stats_lookup.get(template_col, {"mean": 0.0, "std": 1.0})

                if template_col == "Class":
                    # Class column: default to all 0 (legitimate) if not mapped
                    transformed[template_col] = 0
                    smart_filled_columns.append(template_col)
                elif template_col == "Time":
                    # Time column: generate monotonically increasing sequence
                    transformed[template_col] = np.linspace(0, n_rows * 5, n_rows)
                    smart_filled_columns.append(template_col)
                else:
                    # Numeric feature: sample from N(mean, std)
                    np.random.seed(42)
                    values = np.random.normal(
                        col_stats["mean"],
                        col_stats["std"],
                        n_rows
                    )
                    transformed[template_col] = values
                    smart_filled_columns.append(template_col)

        # Ensure numeric types
        for col in transformed.columns:
            transformed[col] = pd.to_numeric(transformed[col], errors='coerce').fillna(0.0)

        # Ensure Class column is integer
        transformed["Class"] = transformed["Class"].astype(int)

        return transformed, mapped_columns, smart_filled_columns

    @staticmethod
    def save_transformed_csv(transformed_df: pd.DataFrame) -> str:
        """Saves the transformed DataFrame to the user upload path."""
        output_path = config.USER_UPLOAD_PATH
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        transformed_df.to_csv(output_path, index=False)
        return output_path

    @staticmethod
    def run_pipeline_on_upload() -> dict:
        """
        Executes the monitoring pipeline on the user-uploaded transformed CSV.
        Returns pipeline summary metrics.
        """
        if not os.path.exists(config.USER_UPLOAD_PATH):
            raise HTTPException(
                status_code=400,
                detail="No transformed CSV found. Please transform your data first."
            )

        try:
            if config.PROJECT_ROOT not in sys.path:
                sys.path.insert(0, config.PROJECT_ROOT)

            # Import and execute pipeline with the user's uploaded data path
            from run_pipeline import main as pipeline_main
            pipeline_main(data_path=config.USER_UPLOAD_PATH)

            # Read results from updated decision_log.json
            from backend.app.services.monitoring_service import MonitoringService
            summary = MonitoringService.get_summary()
            return summary

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Pipeline execution failed on uploaded data: {str(e)}"
            )
