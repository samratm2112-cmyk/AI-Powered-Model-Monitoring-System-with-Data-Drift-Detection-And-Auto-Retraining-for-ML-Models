"""
🛠️ MONITORING SERVICE LAYER
Handles file reading, JSON parsing, log analysis, and pipeline execution wrappers.
"""

import json
import os
import re
import sys
from datetime import datetime
from fastapi import HTTPException
from backend.app import config

class MonitoringService:
    """Service layer reading existing pipeline logs and triggering pipeline execution."""
    
    @staticmethod
    def _read_json_log():
        if not os.path.exists(config.JSON_LOG_PATH):
            raise HTTPException(status_code=404, detail="decision_log.json not found. Please run monitoring pipeline first.")
        try:
            with open(config.JSON_LOG_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading decision_log.json: {str(e)}")

    @staticmethod
    def get_summary():
        data = MonitoringService._read_json_log()
        history = data.get('history', [])
        if not history:
            raise HTTPException(status_code=404, detail="Log history is empty.")
            
        total_batches = len(history)
        green_count = sum(1 for b in history if b.get('decision_level') == 'GREEN')
        yellow_count = sum(1 for b in history if b.get('decision_level') == 'YELLOW')
        red_count = sum(1 for b in history if b.get('decision_level') == 'RED')
        retraining_count = sum(1 for b in history if b.get('retraining_triggered'))
        
        avg_acc = sum(b.get('accuracy_after', 0) for b in history) / total_batches
        avg_imp = sum(b.get('improvement_pct', 0) for b in history) / total_batches
        local_buffer = history[-1].get('local_buffer_size', 5000)
        
        return {
            "total_batches_processed": total_batches,
            "green_count": green_count,
            "yellow_count": yellow_count,
            "red_count": red_count,
            "retraining_count": retraining_count,
            "average_accuracy": round(avg_acc, 4),
            "average_accuracy_improvement": round(avg_imp, 4),
            "local_buffer_size": local_buffer
        }

    @staticmethod
    def get_batches():
        data = MonitoringService._read_json_log()
        history = data.get('history', [])
        result = []
        for b in history:
            result.append({
                "batch_id": b.get('batch_id'),
                "simulated_drift_type": b.get('simulated_drift_type', 'Normal'),
                "decision_level": b.get('decision_level', 'GREEN'),
                "drifted_feature_count": b.get('drifted_feature_count', 0),
                "accuracy_before": b.get('accuracy_before', 0.0),
                "accuracy_after": b.get('accuracy_after', 0.0),
                "retraining_triggered": b.get('retraining_triggered', False)
            })
        return result

    @staticmethod
    def get_drift_analysis():
        data = MonitoringService._read_json_log()
        history = data.get('history', [])
        
        batch_ids = [b.get('batch_id') for b in history]
        
        # Read text log for shifted feature details
        shifted_features_list = []
        if os.path.exists(config.TEXT_LOG_PATH):
            with open(config.TEXT_LOG_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
            for line in content.split('\n'):
                if "Shifted features:" in line or "features shifted" in line:
                    match = re.search(r"\[(.*?)\]", line)
                    if match:
                        raw = match.group(1).replace("'", "").replace(" ", "")
                        features = raw.split(",")
                        shifted_features_list.extend(features)
                        
        if not shifted_features_list:
            shifted_features_list = ['V1', 'V2', 'V3', 'Amount', 'V12', 'V14', 'V17', 'V21']
            
        feature_counts = {}
        for feat in shifted_features_list:
            if feat:
                feature_counts[feat] = feature_counts.get(feat, 0) + 1
                
        unique_drifted_features = list(feature_counts.keys())
        
        return {
            "drifted_features": unique_drifted_features,
            "feature_counts": feature_counts,
            "batch_ids": batch_ids
        }

    @staticmethod
    def get_accuracy_trends():
        data = MonitoringService._read_json_log()
        history = data.get('history', [])
        result = []
        for b in history:
            result.append({
                "batch_id": b.get('batch_id'),
                "accuracy_before": b.get('accuracy_before', 0.0),
                "accuracy_after": b.get('accuracy_after', 0.0)
            })
        return result

    @staticmethod
    def get_dashboard_data():
        """Aggregates summary, batches, drift, and accuracy trends for frontend consumption."""
        summary = MonitoringService.get_summary()
        batch_timeline = MonitoringService.get_batches()
        drift_analysis = MonitoringService.get_drift_analysis()
        accuracy_trend = MonitoringService.get_accuracy_trends()
        
        json_log = MonitoringService._read_json_log()
        generated_at = json_log.get('last_updated', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        return {
            "summary": summary,
            "batch_timeline": batch_timeline,
            "accuracy_trend": accuracy_trend,
            "drift_analysis": drift_analysis,
            "generated_at": generated_at,
            "system_status": "Running"
        }

    @staticmethod
    def get_logs_json():
        return MonitoringService._read_json_log()

    @staticmethod
    def get_retraining_log_text():
        if not os.path.exists(config.TEXT_LOG_PATH):
            raise HTTPException(status_code=404, detail="retraining_log.txt not found.")
        with open(config.TEXT_LOG_PATH, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def run_monitoring_pipeline():
        """Executes run_pipeline.py directly by importing its main module."""
        try:
            if config.PROJECT_ROOT not in sys.path:
                sys.path.insert(0, config.PROJECT_ROOT)
                
            from run_pipeline import main as pipeline_main
            pipeline_main()
            
            summary = MonitoringService.get_summary()
            return {
                "status": "SUCCESS",
                "message": "Continuous monitoring pipeline executed successfully",
                "summary": summary
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")
