"""
⚙️ CENTRALIZED CONFIGURATION FOR ML DRIFT MONITORING PIPELINE
"""

import os

# Base Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "creditcard.csv")
LOG_FILE = os.path.join(BASE_DIR, "retraining_log.txt")
JSON_LOG_FILE = os.path.join(BASE_DIR, "decision_log.json")

# Data Partitioning Settings
HISTORICAL_TRAIN_SIZE = 20000
BATCH_SIZE = 1000  # Configurable batch size (e.g. 500 or 1000 records)

# Model Settings
N_ESTIMATORS = 100
RANDOM_STATE = 42
GLOBAL_WEIGHT = 0.7  # 70% weight to Global Model, 30% to Local Model
CLASSIFICATION_THRESHOLD = 0.3  # Tuned recall threshold for fraud detection
SLIDING_WINDOW_SIZE = 5000  # Local Model max sliding window capacity

# Monitoring & Decision Engine Parameters
KS_ALPHA = 0.05  # Statistical p-value threshold for KS-test drift detection
ACCURACY_THRESHOLD = 0.99  # Retraining triggered if batch accuracy drops below 99%
