"""
⚙️ BACKEND SYSTEM CONFIGURATION
Manages file paths and environment settings for FastAPI service layer.
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = BASE_DIR
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
MODELS_DIR = os.path.join(BASE_DIR, "models")
JSON_LOG_PATH = os.path.join(OUTPUTS_DIR, "decision_log.json") if os.path.exists(os.path.join(OUTPUTS_DIR, "decision_log.json")) else os.path.join(BASE_DIR, "decision_log.json")
TEXT_LOG_PATH = os.path.join(OUTPUTS_DIR, "retraining_log.txt") if os.path.exists(os.path.join(OUTPUTS_DIR, "retraining_log.txt")) else os.path.join(BASE_DIR, "retraining_log.txt")
PROJECT_NAME = "ML Drift Detection & Monitoring System"
PROJECT_VERSION = "1.0"

# CSV Upload Configuration
TEMPLATE_CSV_PATH = os.path.join(BASE_DIR, "data", "creditcard.csv")
DATA_FILE = TEMPLATE_CSV_PATH
USER_UPLOAD_PATH = os.path.join(BASE_DIR, "data", "user_upload.csv")
MAX_UPLOAD_SIZE_MB = 300
TEMPLATE_COLUMNS = [
    "Time", "V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9",
    "V10", "V11", "V12", "V13", "V14", "V15", "V16", "V17", "V18", "V19",
    "V20", "V21", "V22", "V23", "V24", "V25", "V26", "V27", "V28", "Amount", "Class"
]
BASELINE_TRAIN_SIZE = 20000
