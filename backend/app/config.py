"""
⚙️ BACKEND SYSTEM CONFIGURATION
Manages file paths and environment settings for FastAPI service layer.
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JSON_LOG_PATH = os.path.join(BASE_DIR, "decision_log.json")
TEXT_LOG_PATH = os.path.join(BASE_DIR, "retraining_log.txt")
PROJECT_ROOT = BASE_DIR
PROJECT_NAME = "ML Drift Detection & Monitoring System"
PROJECT_VERSION = "1.0"
