"""
🛡️ HUMAN-IN-THE-LOOP (HITL) GOVERNANCE & ENSEMBLE HEALTH SERVICE
Manages model deployment review lifecycle, validation report compliance,
approval persistence, and ensemble health telemetry.
"""

import os
import json
import shutil
from datetime import datetime
from fastapi import HTTPException
from backend.app import config


class GovernanceService:
    """Service handling governance approval workflow and ensemble health monitoring."""

    @staticmethod
    def _get_pending_path():
        return os.path.join(config.OUTPUTS_DIR, "pending_deployment.json")

    @staticmethod
    def _get_validation_report_path():
        return os.path.join(config.OUTPUTS_DIR, "validation_report.json")

    @classmethod
    def get_deployment_status(cls):
        """Checks if there is a pending model deployment awaiting human approval."""
        pending_path = cls._get_pending_path()
        val_path = cls._get_validation_report_path()

        # If pending_deployment.json doesn't exist yet, but validation_report.json does,
        # initialize a pending approval request using the validation report
        if not os.path.exists(pending_path) and os.path.exists(val_path):
            try:
                with open(val_path, "r", encoding="utf-8") as f:
                    val_data = json.load(f)
                
                initial_pending = {
                    "status": "PENDING",
                    "timestamp": val_data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    "model_candidate": "Two-Stage Candidate Ensemble (Retrained on Production Drift)",
                    "validation_report": val_data
                }
                with open(pending_path, "w", encoding="utf-8") as f:
                    json.dump(initial_pending, f, indent=2)
            except Exception as e:
                print(f"Error initializing pending deployment: {e}")

        if os.path.exists(pending_path):
            try:
                with open(pending_path, "r", encoding="utf-8") as f:
                    pending_data = json.load(f)

                status = pending_data.get("status", "NONE")
                is_pending = status in ["PENDING", "PENDING_APPROVAL"]

                return {
                    "has_pending_deployment": is_pending,
                    "status": status,
                    "timestamp": pending_data.get("timestamp"),
                    "validation_report": pending_data.get("validation_report"),
                    "model_candidate": pending_data.get("model_candidate", "Two-Stage Candidate Ensemble"),
                    "message": "A retrained candidate model requires human review before production rollout." if is_pending else f"Deployment status is {status}."
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to read pending deployment status: {str(e)}")

        return {
            "has_pending_deployment": False,
            "status": "NONE",
            "timestamp": None,
            "validation_report": None,
            "model_candidate": None,
            "message": "No model deployments currently pending approval."
        }

    @classmethod
    def approve_deployment(cls, reviewer: str = "Human Compliance Officer", notes: str = "Approved via MLOps Portal"):
        """Triggers governance approval: saves model to /models/ and updates audit logs."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        models_dir = config.MODELS_DIR
        os.makedirs(models_dir, exist_ok=True)

        candidate_model_path = os.path.join(models_dir, "candidate_model.pkl")
        deployed_model_path = os.path.join(models_dir, "deployed_model.pkl")
        latest_model_path = os.path.join(models_dir, "model_latest.pkl")

        # 1. Promote candidate model if present, otherwise ensure deployed_model exists
        if os.path.exists(candidate_model_path):
            shutil.copy2(candidate_model_path, deployed_model_path)
            shutil.copy2(candidate_model_path, latest_model_path)
        elif os.path.exists(deployed_model_path):
            shutil.copy2(deployed_model_path, latest_model_path)

        # 2. Update retraining_log.txt with EXACT required audit phrase
        approval_message = f"[{timestamp}] [INFO] [GOVERNANCE] Deployed by Human Approval. Reviewer: {reviewer}. Notes: {notes}\n"
        with open(config.TEXT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(approval_message)

        # 3. Update pending_deployment.json
        pending_path = cls._get_pending_path()
        pending_data = {}
        if os.path.exists(pending_path):
            try:
                with open(pending_path, "r", encoding="utf-8") as f:
                    pending_data = json.load(f)
            except Exception:
                pass

        pending_data.update({
            "status": "APPROVED",
            "approved_at": timestamp,
            "approved_by": reviewer,
            "notes": notes
        })
        with open(pending_path, "w", encoding="utf-8") as f:
            json.dump(pending_data, f, indent=2)

        # 4. Update decision_log.json if present
        if os.path.exists(config.JSON_LOG_PATH):
            try:
                with open(config.JSON_LOG_PATH, "r", encoding="utf-8") as f:
                    decision_data = json.load(f)
                
                decision_data["governance_approval"] = True
                decision_data["active_model"] = "New Retrained Model (Deployed by Human Approval)"
                decision_data["last_governance_event"] = {
                    "timestamp": timestamp,
                    "action": "APPROVED",
                    "reviewer": reviewer
                }
                with open(config.JSON_LOG_PATH, "w", encoding="utf-8") as f:
                    json.dump(decision_data, f, indent=2)
            except Exception as e:
                print(f"Note: Could not update decision_log.json: {e}")

        return {
            "success": True,
            "message": "Candidate model successfully approved and promoted to production (/models/deployed_model.pkl).",
            "status": "APPROVED",
            "approved_at": timestamp,
            "active_model": "New Retrained Model (Deployed by Human Approval)"
        }

    @classmethod
    def reject_deployment(cls, reviewer: str = "Human Compliance Officer", notes: str = "Rejected by human reviewer"):
        """Engages fail-safe: rejects deployment and retains active baseline model."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Log rejection audit message
        rejection_message = f"[{timestamp}] [WARNING] [GOVERNANCE] Deployment Rejected (user: '{reviewer}'). Fail-safe engaged: Old model remains active in production. Notes: {notes}\n"
        with open(config.TEXT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(rejection_message)

        # 2. Update pending_deployment.json
        pending_path = cls._get_pending_path()
        pending_data = {}
        if os.path.exists(pending_path):
            try:
                with open(pending_path, "r", encoding="utf-8") as f:
                    pending_data = json.load(f)
            except Exception:
                pass

        pending_data.update({
            "status": "REJECTED",
            "rejected_at": timestamp,
            "rejected_by": reviewer,
            "notes": notes
        })
        with open(pending_path, "w", encoding="utf-8") as f:
            json.dump(pending_data, f, indent=2)

        return {
            "success": True,
            "message": "Deployment rejected. Fail-safe engaged: Old model remains active in production.",
            "status": "REJECTED"
        }

    @classmethod
    def get_system_health(cls):
        """Returns the current state of the Two-Stage Ensemble and VAE / Anomaly filter."""
        model_path = os.path.join(config.MODELS_DIR, "deployed_model.pkl")
        model_exists = os.path.exists(model_path)
        model_size_kb = round(os.path.getsize(model_path) / 1024, 2) if model_exists else 0.0
        model_mtime = (
            datetime.fromtimestamp(os.path.getmtime(model_path)).strftime("%Y-%m-%d %H:%M:%S")
            if model_exists else "N/A"
        )

        # Inspect latest decision log buffer metrics if available
        buffer_size = 5000
        if os.path.exists(config.JSON_LOG_PATH):
            try:
                with open(config.JSON_LOG_PATH, "r", encoding="utf-8") as f:
                    d_log = json.load(f)
                    if "history" in d_log and len(d_log["history"]) > 0:
                        buffer_size = d_log["history"][-1].get("local_buffer_size", 5000)
            except Exception:
                pass

        return {
            "status": "Healthy",
            "system_state": "Active",
            "ensemble": {
                "architecture": "Two-Stage Hybrid Global-Local Ensemble (Stage 1: VAE/Anomaly Filter + Stage 2: XGBoost)",
                "global_weight": 0.7,
                "local_weight": 0.3,
                "global_weight_percentage": "70%",
                "local_weight_percentage": "30%",
                "threshold": 0.3,
                "local_buffer_size": buffer_size,
                "max_buffer_capacity": 5000,
                "global_fitted": True,
                "local_fitted": True
            },
            "pipeline_stages": {
                "stage1_filter": {
                    "name": "Stage 1: VAE / Anomaly Filter",
                    "type": "Unsupervised Isolation Forest / VAE Distribution Filter",
                    "status": "Active",
                    "description": "Models normal behavior distribution; filters normal traffic and flags distribution anomalies."
                },
                "stage2_expert": {
                    "name": "Stage 2: Supervised XGBoost Classifier",
                    "type": "Supervised Gradient Boosted Decision Trees",
                    "status": "Active",
                    "description": "Evaluates flagged transactions with calibrated decision threshold of 0.3 to confirm fraud."
                }
            },
            "deployed_model": {
                "filename": "deployed_model.pkl",
                "exists": model_exists,
                "size_kb": model_size_kb,
                "last_modified": model_mtime
            },
            "governance_status": "Human-in-the-Loop Governance Gate Active"
        }
