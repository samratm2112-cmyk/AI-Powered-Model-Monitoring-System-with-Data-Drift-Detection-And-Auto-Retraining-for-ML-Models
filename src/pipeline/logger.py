"""
📝 PIPELINE LOGGER MODULE
Handles structured timestamped text logging to outputs/retraining_log.txt and JSON metrics archiving to outputs/decision_log.json.
"""

import json
from datetime import datetime
import os

class PipelineLogger:
    """Manages event logging and JSON metrics history for batch monitoring."""
    
    def __init__(self, text_log_path=None, json_log_path=None):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        outputs_dir = os.path.join(base_dir, "outputs")
        
        self.text_log_path = text_log_path or os.path.join(outputs_dir, "retraining_log.txt")
        self.json_log_path = json_log_path or os.path.join(outputs_dir, "decision_log.json")
        
        os.makedirs(os.path.dirname(self.text_log_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.json_log_path), exist_ok=True)
        self.history = []
        
    def log_event(self, stage, message, level="INFO"):
        """Logs timestamped entry to console and text log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [{level}] [{stage}] {message}"
        try:
            print(entry)
        except OSError:
            pass
        
        os.makedirs(os.path.dirname(self.text_log_path), exist_ok=True)
        with open(self.text_log_path, 'a', encoding='utf-8') as f:
            f.write(entry + "\n")
            
    def log_batch_record(self, batch_record):
        """Appends structured batch execution record to JSON log history."""
        self.history.append(batch_record)
        
        os.makedirs(os.path.dirname(self.json_log_path), exist_ok=True)
        with open(self.json_log_path, 'w', encoding='utf-8') as f:
            json.dump({
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'total_batches_processed': len(self.history),
                'history': self.history
            }, f, indent=2)
