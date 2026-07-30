"""
📝 PIPELINE LOGGER MODULE
Handles structured timestamped text logging to retraining_log.txt and JSON metrics archiving to decision_log.json.
"""

import json
from datetime import datetime
import os

class PipelineLogger:
    """Manages event logging and JSON metrics history for batch monitoring."""
    
    def __init__(self, text_log_path="retraining_log.txt", json_log_path="decision_log.json"):
        self.text_log_path = text_log_path
        self.json_log_path = json_log_path
        self.history = []
        
    def log_event(self, stage, message, level="INFO"):
        """Logs timestamped entry to console and text log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [{level}] [{stage}] {message}"
        print(entry)
        
        with open(self.text_log_path, 'a', encoding='utf-8') as f:
            f.write(entry + "\n")
            
    def log_batch_record(self, batch_record):
        """Appends structured batch execution record to JSON log history."""
        self.history.append(batch_record)
        
        with open(self.json_log_path, 'w', encoding='utf-8') as f:
            json.dump({
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'total_batches_processed': len(self.history),
                'history': self.history
            }, f, indent=2)
