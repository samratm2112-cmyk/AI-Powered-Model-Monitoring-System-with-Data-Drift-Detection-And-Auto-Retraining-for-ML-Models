import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, precision_score, recall_score, f1_score
import pickle
import json
from datetime import datetime
import os
import sys

# Ensure src directory is in path
sys.path.insert(0, os.path.dirname(__file__))
from ensemble import GlobalLocalEnsemble

def ensure_dataset_exists(file_path="data/creditcard.csv", n_samples=30000, force_generate=True):
    """Generates synthetic Credit Card dataset enriched with multiple historical fraud types (Types A, B, C)."""
    if os.path.exists(file_path) and not force_generate:
        return

    print(f"📦 Generating enriched Credit Card dataset with 3 historical fraud archetypes ({n_samples} rows)...")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    np.random.seed(42)
    
    time_col = np.sort(np.random.uniform(0, 172800, n_samples))
    amount_col = np.random.exponential(scale=88.0, size=n_samples)
    v_cols = {f"V{i}": np.random.normal(loc=0.0, scale=1.0, size=n_samples) for i in range(1, 29)}
    
    # 2% Fraud representation across 3 distinct historical fraud archetypes
    n_fraud = int(n_samples * 0.02)
    fraud_indices = np.random.choice(n_samples, size=n_fraud, replace=False)
    classes = np.zeros(n_samples, dtype=int)
    classes[fraud_indices] = 1
    
    # Split fraud into 3 historical types:
    # Pattern A: High-Amount Large Transactions
    # Pattern B: Low-Amount Micro Skimming Fraud
    # Pattern C: Behavioral Velocity Fraud
    type_a, type_b, type_c = np.array_split(fraud_indices, 3)
    
    # Pattern A
    amount_col[type_a] += 550.0
    v_cols["V1"][type_a] -= 4.5
    v_cols["V3"][type_a] -= 5.0
    
    # Pattern B
    amount_col[type_b] = np.random.uniform(1.0, 15.0, size=len(type_b))
    v_cols["V2"][type_b] += 4.0
    v_cols["V4"][type_b] += 3.5
    
    # Pattern C
    v_cols["V5"][type_c] -= 3.5
    v_cols["V7"][type_c] -= 4.0
    v_cols["V10"][type_c] -= 4.5
    amount_col[type_c] += 120.0

    df_dict = {"Time": time_col}
    df_dict.update(v_cols)
    df_dict["Amount"] = amount_col
    df_dict["Class"] = classes

    df = pd.DataFrame(df_dict)
    df.to_csv(file_path, index=False)
    print(f"✅ Generated dataset with {n_fraud} multi-pattern historical fraud cases (Types A, B, C).")

# ============================================================================
# STRUCTURED LOGGING SYSTEM
# ============================================================================

class RetrainingLogger:
    """Professional logging for retraining events"""
    
    def __init__(self, log_file="retraining_log.txt"):
        self.log_file = log_file
        self.events = []
    
    def log_event(self, stage, message, level="INFO"):
        """Log important events with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] [{stage}] {message}"
        print(log_entry)
        self.events.append(log_entry)
        
        # Write to file with UTF-8 encoding
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def log_metrics(self, stage, metrics):
        """Log performance metrics"""
        for key, value in metrics.items():
            self.log_event(stage, f"{key}: {value:.4f}")

# Initialize logger
logger = RetrainingLogger()

# ============================================================================
# RETRAINING & ENSEMBLE FUNCTIONS (MODULAR & REUSABLE)
# ============================================================================

def retrain_model(model, X_train, y_train, logger=None):
    """
    Retrain a machine learning model (or update local ensemble expert) with new data
    
    Args:
        model: sklearn estimator or GlobalLocalEnsemble instance
        X_train: Training features
        y_train: Training labels
        logger: Logger instance for tracking
    
    Returns:
        Retrained model or ensemble
    """
    if logger:
        logger.log_event("RETRAINING", f"Starting retraining/updating with {len(X_train)} samples")
    
    if isinstance(model, GlobalLocalEnsemble):
        model.fit_local(X_train, y_train)
        if logger:
            status = model.get_status()
            logger.log_event("RETRAINING", f"✅ Local Expert retrained successfully (Buffer: {status['local_buffer_size']} samples)")
    else:
        model.fit(X_train, y_train)
        if logger:
            logger.log_event("RETRAINING", "✅ Model retraining completed successfully")
    
    return model

def evaluate_model(model, X_test, y_test, stage="EVALUATION", logger=None):
    """
    Evaluate model performance on test data
    
    Args:
        model: Trained ML model or GlobalLocalEnsemble instance
        X_test: Test features
        y_test: Test labels
        stage: Name of evaluation stage
        logger: Logger instance
    
    Returns:
        Dictionary of metrics, predictions array
    """
    y_pred = model.predict(X_test)
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
        'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
        'f1': f1_score(y_test, y_pred, average='weighted', zero_division=0)
    }
    
    if logger:
        logger.log_event(stage, f"Evaluation completed:")
        logger.log_metrics(stage, metrics)
    
    return metrics, y_pred

def make_retraining_decision(drift_detected, accuracy_before, accuracy_threshold, logger=None):
    """
    Make decision on whether to retrain / update local model
    
    Args:
        drift_detected: Boolean indicating if drift was detected
        accuracy_before: Current model accuracy
        accuracy_threshold: Minimum acceptable accuracy
        logger: Logger instance
    
    Returns:
        Boolean decision to retrain
    """
    accuracy_degraded = accuracy_before < accuracy_threshold
    should_retrain = drift_detected or accuracy_degraded
    
    if logger:
        logger.log_event("DECISION", f"Drift detected: {drift_detected}")
        logger.log_event("DECISION", f"Accuracy degraded: {accuracy_degraded} ({accuracy_before:.4f} vs threshold {accuracy_threshold:.4f})")
        logger.log_event("DECISION", f"Retrain decision: {should_retrain}")
    
    return should_retrain, accuracy_degraded


if __name__ == "__main__":
    # Ensure multi-pattern historical dataset exists
    ensure_dataset_exists(force_generate=True)

    # ============================================================================
    # STEP 1: Load Training Data and Train Initial Global Model (Ensemble)
    # ============================================================================
    print("="*70)
    print("STEP 1: LOADING MULTI-PATTERN HISTORICAL DATA & TRAINING GLOBAL MODEL")
    print("="*70)

    logger.log_event("INITIALIZATION", "Starting ML Drift System with Multi-Pattern Historical Fraud Dataset")

    data = pd.read_csv("data/creditcard.csv")

    # Use first 20000 for training
    train_data = data[:20000].copy()
    X_train = train_data.drop("Class", axis=1)
    y_train = train_data["Class"]

    # Preprocess Amount feature
    scaler = StandardScaler()
    X_train["Amount"] = scaler.fit_transform(X_train[["Amount"]])

    # Initialize Global-Local Ensemble (Option 3: Hybrid Classifier)
    ensemble = GlobalLocalEnsemble(global_weight=0.7, threshold=0.3, n_estimators=100, random_state=42)
    ensemble.fit_global(X_train, y_train)

    print(f"✅ Global Model (Veteran Expert) trained on {len(X_train)} historical transactions ({y_train.sum()} fraud cases of Types A, B, C)")
    logger.log_event("INITIALIZATION", f"✅ Initial Global Model trained on {len(X_train)} samples with {y_train.sum()} fraud events")

    # ============================================================================
    # STEP 2: Simulate New Data with Drift & Novel Fraud (Type D)
    # ============================================================================
    print("\n" + "="*70)
    print("STEP 2: SIMULATING NEW DATA WITH DRIFT & NOVEL FRAUD (TYPE D)")
    print("="*70)

    # Use next 10000 for testing (simulating new incoming data stream)
    new_data = data[20000:30000].copy()

    # Apply distribution drift
    new_data["Amount"] = new_data["Amount"] * 3
    new_data["V1"] = new_data["V1"] * 1.5
    new_data["V2"] = new_data["V2"] * 1.5
    new_data["V3"] = new_data["V3"] + 1

    # Introduce Novel Fraud Vector (Type D - Hacking / Skimming) in production stream
    fraud_mask = (new_data["Class"] == 1)
    new_data.loc[fraud_mask, "V11"] += 5.0
    new_data.loc[fraud_mask, "V12"] -= 6.0
    new_data.loc[fraud_mask, "V14"] -= 5.5

    print("✅ New data loaded with feature drift & novel fraud pattern (Type D) applied")
    print(f"   - Distribution Shift: Amount ×3, V1 ×1.5, V2 ×1.5, V3 +1")
    print(f"   - Novel Attack Shift: V11 +5.0, V12 -6.0, V14 -5.5 for production fraud cases")

    # ============================================================================
    # STEP 3: Prepare New Data
    # ============================================================================
    print("\n" + "="*70)
    print("STEP 3: PREPARING NEW DATA FOR EVALUATION")
    print("="*70)

    X_new = new_data.drop("Class", axis=1)
    y_new = new_data["Class"]

    # Apply same scaling
    X_new["Amount"] = scaler.transform(X_new[["Amount"]])

    print(f"New data shape: {X_new.shape} with {y_new.sum()} novel fraud cases")

    # ============================================================================
    # STEP 4: Evaluate Model on New Data (BEFORE RETRAINING - Pure Global Model)
    # ============================================================================
    print("\n" + "="*70)
    print("STEP 4: EVALUATING PURE GLOBAL MODEL ON NOVEL DRIFTED DATA (BASELINE)")
    print("="*70)

    metrics_before, y_pred_before = evaluate_model(ensemble, X_new, y_new, stage="BASELINE_GLOBAL", logger=logger)
    accuracy_before = metrics_before['accuracy']

    print(f"\n📊 BASELINE PERFORMANCE (Global Model alone on novel attack):")
    print(f"   Accuracy:  {metrics_before['accuracy']:.4f} ({metrics_before['accuracy']*100:.2f}%)")
    print(f"   Recall:    {metrics_before['recall']:.4f} ({metrics_before['recall']*100:.2f}%)")

    # ============================================================================
    # STEP 5 & 6: Decision Engine - Check Conditions & Decide
    # ============================================================================
    print("\n" + "="*70)
    print("STEP 5 & 6: DECISION ENGINE - EVALUATING DRIFT & PERFORMANCE")
    print("="*70)

    drift_detected = True
    accuracy_threshold = 0.99

    should_retrain, accuracy_degraded = make_retraining_decision(
        drift_detected=drift_detected,
        accuracy_before=accuracy_before,
        accuracy_threshold=accuracy_threshold,
        logger=logger
    )

    print(f"\n🤔 Decision Logic:")
    print(f"   Drift detected: {drift_detected}")
    print(f"   Accuracy degraded: {accuracy_degraded}")
    print(f"   → Local Expert Retraining required: {should_retrain}")

    # ============================================================================
    # STEP 7: Local Model Adaptation (Fast Retraining on Drifted Data)
    # ============================================================================
    print("\n" + "="*70)
    print("STEP 7: LOCAL MODEL ADAPTATION (FAST RETRAINING ON NOVEL STREAM)")
    print("="*70)

    if should_retrain:
        print("\n⚙️  RETRAINING LOCAL MODEL (Rookie Expert) on shifted data batch...")
        logger.log_event("RETRAINING", "🔄 Retraining Local Expert on novel drifted stream")
        
        # Fast local retrain on drifted stream using sliding window
        ensemble = retrain_model(ensemble, X_new, y_new, logger=logger)
        
        print("✅ Local Model retrained and integrated into Global-Local Ensemble!")
        print(f"   Ensemble Config: Global Weight={ensemble.global_weight}, Local Weight={ensemble.local_weight}")
        
    else:
        print("\n⏭️  Skipping retraining (model is stable)")

    # ============================================================================
    # STEP 8 & 9: Evaluate Global-Local Ensemble & Compare
    # ============================================================================
    print("\n" + "="*70)
    print("STEP 8 & 9: EVALUATING HYBRID ENSEMBLE AFTER LOCAL ADAPTATION")
    print("="*70)

    metrics_after, y_pred_after = evaluate_model(ensemble, X_new, y_new, stage="POST_ENSEMBLE_ADAPTATION", logger=logger)
    accuracy_after = metrics_after['accuracy']

    improvement = accuracy_after - accuracy_before
    improvement_pct = (improvement / accuracy_before) * 100 if accuracy_before > 0 else 0

    print(f"\n📈 BEFORE vs AFTER HYBRID ENSEMBLE ADAPTATION:")
    print(f"   Pure Global Model: {accuracy_before:.4f} ({accuracy_before*100:.2f}%)")
    print(f"   Hybrid Ensemble:   {accuracy_after:.4f} ({accuracy_after*100:.2f}%)")
    print(f"   Improvement:       {improvement:+.4f} ({improvement_pct:+.2f}%)")

    # ============================================================================
    # STEP 10, 11, 12: Classification Report, Summary & Logging
    # ============================================================================
    status = "🟢 EXCELLENT" if accuracy_after > 0.95 else "🟡 GOOD" if accuracy_after > 0.85 else "🔴 NEEDS ATTENTION"

    decision_log = {
        'timestamp': str(pd.Timestamp.now()),
        'architecture': 'Global-Local Ensemble (Hybrid Classifier)',
        'drift_detected': drift_detected,
        'accuracy_before': accuracy_before,
        'accuracy_threshold': accuracy_threshold,
        'retraining_triggered': should_retrain,
        'accuracy_after': accuracy_after,
        'improvement': improvement,
        'improvement_pct': improvement_pct,
        'global_weight': ensemble.global_weight,
        'local_weight': ensemble.local_weight,
        'system_status': status
    }

    with open('decision_log.json', 'w') as f:
        json.dump(decision_log, f, indent=2)

    print("\n✅ Decision log saved to decision_log.json")
    print(json.dumps(decision_log, indent=2))
    logger.log_event("LOGGING", "✅ Decision log saved to decision_log.json")

    print("\n" + "="*70)
    print("GLOBAL-LOCAL ENSEMBLE DECISION ENGINE COMPLETE!")
    print("="*70)
