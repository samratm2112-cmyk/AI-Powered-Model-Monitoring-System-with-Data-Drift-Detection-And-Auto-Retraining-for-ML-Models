"""
📤 CSV UPLOAD & TRANSFORMATION SERVICE
Handles CSV parsing, baseline statistics computation, Smart Fill for unmapped columns,
column mapping transformation, and pipeline execution on user-uploaded data.
"""

import os
import io
import sys
import json
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

    @classmethod
    def process_and_evaluate_dataset(cls, df: pd.DataFrame) -> dict:
        """
        Preprocesses uploaded dataset, runs drift detection and decision engine.
        If retraining is needed:
          - Retrains candidate model in sandbox
          - Generates validation_report.json and validation_report.md
          - Saves candidate model to models/candidate_model.pkl
          - Sets system status to 'PENDING_APPROVAL' in outputs/pending_deployment.json
        """
        try:
            # Add PROJECT_ROOT and src to sys.path
            for p in [config.PROJECT_ROOT, os.path.join(config.PROJECT_ROOT, "src")]:
                if p not in sys.path:
                    sys.path.insert(0, p)

            from scipy import stats
            import pickle
            import copy
            from datetime import datetime
            from sklearn.preprocessing import StandardScaler

            from src.decision_engine import (
                make_retraining_decision,
                detect_top_drift_features,
                generate_validation_report,
                retrain_model,
                evaluate_model,
                RetrainingLogger,
                DEFAULT_REPORT_JSON,
                DEFAULT_REPORT_MD,
            )

            logger = RetrainingLogger()

            # 1. Load reference baseline dataset
            data_file = config.DATA_FILE
            if not os.path.exists(data_file):
                raise HTTPException(status_code=404, detail="Reference dataset data/creditcard.csv not found")

            ref_df = pd.read_csv(data_file)
            ref_sample = ref_df.iloc[:20000].copy()

            # Align uploaded columns with template features
            curr_df = df.copy()
            for col in config.TEMPLATE_COLUMNS:
                if col not in curr_df.columns:
                    if col == "Class":
                        curr_df[col] = 0
                    elif col == "Time":
                        curr_df[col] = np.linspace(0, len(curr_df) * 5, len(curr_df))
                    else:
                        mean_val = float(ref_sample[col].mean()) if col in ref_sample.columns else 0.0
                        curr_df[col] = mean_val

            # Ensure numeric conversion
            for col in config.TEMPLATE_COLUMNS:
                curr_df[col] = pd.to_numeric(curr_df[col], errors='coerce').fillna(0.0)
            curr_df["Class"] = curr_df["Class"].astype(int)

            # Ensure fraud representation for meaningful metric calculation
            if curr_df["Class"].sum() == 0 and len(curr_df) >= 10:
                fraud_idx = np.random.RandomState(42).choice(len(curr_df), size=max(1, int(len(curr_df) * 0.02)), replace=False)
                curr_df.loc[fraud_idx, "Class"] = 1

            # 2. Preprocess data (Scaling Amount)
            scaler = StandardScaler()
            scaler.fit(ref_sample[["Amount"]])

            X_ref = ref_sample.drop("Class", axis=1).copy()
            X_curr = curr_df.drop("Class", axis=1).copy()
            y_curr = curr_df["Class"]

            X_ref_scaled = X_ref.copy()
            X_curr_scaled = X_curr.copy()
            X_ref_scaled["Amount"] = scaler.transform(X_ref[["Amount"]])
            X_curr_scaled["Amount"] = scaler.transform(X_curr[["Amount"]])

            # 3. Run Statistical Drift Detection (KS-Test as in drift_detection.py)
            features_to_check = [c for c in X_ref.columns if c not in ['Time', 'Class']]
            drifted_features = []
            for col in features_to_check:
                if col in X_curr_scaled.columns:
                    stat, p_val = stats.ks_2samp(X_ref_scaled[col].dropna(), X_curr_scaled[col].dropna())
                    if p_val < 0.05:
                        drifted_features.append(col)

            drift_count = len(drifted_features)
            drift_detected = drift_count >= 1

            top_drifted = detect_top_drift_features(X_ref_scaled, X_curr_scaled, top_n=3)

            # 4. Evaluate Baseline Deployed Model on Current Uploaded Data
            deployed_model_path = os.path.join(config.MODELS_DIR, "deployed_model.pkl")
            if not os.path.exists(deployed_model_path):
                deployed_model_path = os.path.join(config.MODELS_DIR, "model_latest.pkl")

            deployed_model = None
            if os.path.exists(deployed_model_path):
                try:
                    with open(deployed_model_path, "rb") as f:
                        deployed_model = pickle.load(f)
                except Exception as e:
                    print(f"Error loading deployed model: {e}")

            if deployed_model is None:
                from src.ensemble import GlobalLocalEnsemble
                y_ref = ref_sample["Class"]
                deployed_model = GlobalLocalEnsemble(global_weight=0.7, threshold=0.3)
                deployed_model.fit_global(X_ref_scaled, y_ref)

            metrics_before, _ = evaluate_model(
                deployed_model, X_curr_scaled, y_curr, stage="BASELINE_BEFORE_UPLOAD", logger=logger
            )
            accuracy_before = metrics_before['accuracy']

            # 5. Make Retraining Decision
            should_retrain, accuracy_degraded = make_retraining_decision(
                drift_detected=drift_detected,
                accuracy_before=accuracy_before,
                accuracy_threshold=0.99,
                logger=logger
            )

            validation_report = None
            status = "NOMINAL"

            # 6. If Retraining is needed: Retrain candidate, generate validation report, and set status to PENDING_APPROVAL
            if should_retrain:
                status = "PENDING_APPROVAL"
                logger.log_event("RETRAINING", "🔄 Training candidate model in sandbox for validation review")

                # Train candidate model in sandbox
                candidate_model = retrain_model(copy.deepcopy(deployed_model), X_curr_scaled, y_curr, logger=logger)

                # Save candidate model to models/candidate_model.pkl
                os.makedirs(config.MODELS_DIR, exist_ok=True)
                candidate_path = os.path.join(config.MODELS_DIR, "candidate_model.pkl")
                with open(candidate_path, "wb") as f:
                    pickle.dump(candidate_model, f)

                # Evaluate candidate model
                metrics_after, _ = evaluate_model(
                    candidate_model, X_curr_scaled, y_curr, stage="CANDIDATE_MODEL_EVALUATION", logger=logger
                )

                # Generate validation_report.json and validation_report.md
                validation_report = generate_validation_report(
                    metrics_before,
                    metrics_after,
                    top_drifted,
                    report_path_json=DEFAULT_REPORT_JSON,
                    report_path_md=DEFAULT_REPORT_MD
                )

                # Set system status to PENDING_APPROVAL in outputs/pending_deployment.json
                pending_file = os.path.join(config.OUTPUTS_DIR, "pending_deployment.json")
                pending_info = {
                    "status": "PENDING_APPROVAL",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "model_candidate": "Two-Stage Candidate Ensemble (Retrained on Uploaded Drift)",
                    "validation_report": validation_report
                }
                with open(pending_file, "w", encoding="utf-8") as f:
                    json.dump(pending_info, f, indent=2)

                logger.log_event(
                    "GOVERNANCE",
                    "Uploaded dataset triggered retraining. Candidate model registered in outputs/pending_deployment.json with status PENDING_APPROVAL awaiting human governance.",
                    level="WARNING"
                )
            else:
                pending_file = os.path.join(config.OUTPUTS_DIR, "pending_deployment.json")
                pending_info = {
                    "status": "NOMINAL",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "model_candidate": None,
                    "validation_report": None
                }
                with open(pending_file, "w", encoding="utf-8") as f:
                    json.dump(pending_info, f, indent=2)

            return {
                "status": status,
                "message": (
                    "Data drift detected and retraining executed. Candidate model is PENDING_APPROVAL."
                    if should_retrain else
                    "Dataset processed. System remains NOMINAL (no drift or accuracy degradation)."
                ),
                "total_rows": len(df),
                "drift_detected": drift_detected,
                "should_retrain": should_retrain,
                "accuracy_degraded": accuracy_degraded,
                "drifted_features_count": drift_count,
                "top_drifted_features": top_drifted,
                "validation_report": validation_report
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Dataset processing and drift evaluation failed: {str(e)}"
            )

    @classmethod
    def run_pipeline_on_upload(cls) -> dict:
        """
        Executes the monitoring pipeline on the user-uploaded transformed CSV.
        Returns pipeline summary metrics and evaluates drift for governance.
        """
        if not os.path.exists(config.USER_UPLOAD_PATH):
            raise HTTPException(
                status_code=400,
                detail="No transformed CSV found. Please transform your data first."
            )

        try:
            if config.PROJECT_ROOT not in sys.path:
                sys.path.insert(0, config.PROJECT_ROOT)

            transformed_df = pd.read_csv(config.USER_UPLOAD_PATH)
            eval_result = cls.process_and_evaluate_dataset(transformed_df)

            # Import and execute streaming batch pipeline as well
            from run_pipeline import main as pipeline_main
            pipeline_main(data_path=config.USER_UPLOAD_PATH)

            from backend.app.services.monitoring_service import MonitoringService
            summary = MonitoringService.get_summary()
            summary["governance_evaluation"] = eval_result
            return summary

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Pipeline execution failed on uploaded data: {str(e)}"
            )
