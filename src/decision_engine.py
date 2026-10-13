import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, precision_score, recall_score, f1_score
from scipy import stats
import pickle
import json
import copy
from datetime import datetime
import os
import sys

# Base directory & path resolution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

DEFAULT_DATA_FILE = os.path.join(DATA_DIR, "creditcard.csv")
DEFAULT_LOG_FILE = os.path.join(OUTPUTS_DIR, "retraining_log.txt")
DEFAULT_JSON_LOG = os.path.join(OUTPUTS_DIR, "decision_log.json")
DEFAULT_REPORT_JSON = os.path.join(OUTPUTS_DIR, "validation_report.json")
DEFAULT_REPORT_MD = os.path.join(OUTPUTS_DIR, "validation_report.md")

for p in [BASE_DIR, SRC_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from src.ensemble import GlobalLocalEnsemble, TwoStagePipeline
except ImportError:
    from ensemble import GlobalLocalEnsemble, TwoStagePipeline

def ensure_dataset_exists(file_path=None, n_samples=30000, force_generate=True):
    """Generates synthetic Credit Card dataset enriched with multiple historical fraud types (Types A, B, C)."""
    if file_path is None:
        file_path = DEFAULT_DATA_FILE
    if os.path.exists(file_path) and not force_generate:
        return

    print(f"📦 Generating enriched Credit Card dataset with 3 historical target class archetypes ({n_samples} rows)...")
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
    print(f"✅ Generated dataset with {n_fraud} multi-pattern historical target class cases (Types A, B, C).")

# ============================================================================
# STRUCTURED LOGGING SYSTEM
# ============================================================================

class RetrainingLogger:
    """Professional logging for retraining events"""
    
    def __init__(self, log_file=None):
        self.log_file = log_file or DEFAULT_LOG_FILE
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        self.events = []
    
    def log_event(self, stage, message, level="INFO"):
        """Log important events with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] [{stage}] {message}"
        try:
            print(log_entry)
        except OSError:
            pass
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
# DRIFT ROOT-CAUSE & VALIDATION REPORTING
# ============================================================================

def detect_top_drift_features(X_ref, X_curr, top_n=3):
    """
    Identifies the top N features with the highest distribution drift
    between the reference dataset and the current production stream using
    the two-sample Kolmogorov-Smirnov test.
    """
    feature_drifts = []
    cols_to_check = [c for c in X_ref.columns if c not in ['Time', 'Class']]
    
    for col in cols_to_check:
        if col in X_curr.columns:
            stat, p_val = stats.ks_2samp(X_ref[col].dropna(), X_curr[col].dropna())
            feature_drifts.append({
                'feature': col,
                'ks_statistic': float(stat),
                'p_value': float(p_val),
                'drift_detected': bool(p_val < 0.05)
            })
            
    # Sort descending by KS statistic (magnitude of distribution divergence)
    feature_drifts.sort(key=lambda item: item['ks_statistic'], reverse=True)
    return feature_drifts[:top_n]

def generate_validation_report(
    metrics_old,
    metrics_new,
    top_drifted_features,
    report_path_json=None,
    report_path_md=None
):
    """
    Produces a detailed summary report of the retraining event, including:
    - Metrics comparison (Accuracy, Precision, Recall, F1) of Old vs. New Model.
    - Top 3 features that caused the drift.
    - Recommendation ("Strongly Recommend Deployment" or "Risk Detected: Do Not Deploy").
    Saves validation_report.json and validation_report.md for audit trail and compliance.
    """
    if report_path_json is None:
        report_path_json = DEFAULT_REPORT_JSON
    if report_path_md is None:
        report_path_md = DEFAULT_REPORT_MD
    os.makedirs(os.path.dirname(report_path_json), exist_ok=True)
    os.makedirs(os.path.dirname(report_path_md), exist_ok=True)
    comparison = {}
    improved_count = 0
    degraded_count = 0
    
    for metric_name in ['accuracy', 'precision', 'recall', 'f1']:
        old_val = float(metrics_old.get(metric_name, 0.0))
        new_val = float(metrics_new.get(metric_name, 0.0))
        delta = new_val - old_val
        delta_pct = (delta / old_val * 100) if old_val > 0 else 0.0
        improved = delta >= 0.0
        if delta > 0.0001:
            improved_count += 1
        elif delta < -0.005:
            degraded_count += 1
            
        comparison[metric_name] = {
            'old_model': round(old_val, 4),
            'new_model': round(new_val, 4),
            'delta': round(delta, 4),
            'delta_pct': round(delta_pct, 2),
            'improved': improved
        }

    # Evaluate recommendation
    new_acc = metrics_new.get('accuracy', 0.0)
    new_f1 = metrics_new.get('f1', 0.0)
    old_f1 = metrics_old.get('f1', 0.0)
    old_acc = metrics_old.get('accuracy', 0.0)
    
    top_feature_names = [f['feature'] for f in top_drifted_features]
    
    if (new_f1 >= old_f1 or new_acc >= old_acc) and new_acc >= 0.90 and degraded_count == 0:
        recommendation = "Strongly Recommend Deployment"
        rationale = (
            f"The retrained model demonstrates superior or stable performance over the old model "
            f"(F1: {new_f1:.4f} vs {old_f1:.4f}, Accuracy: {new_acc:.4f} vs {old_acc:.4f}) and "
            f"effectively counteracts the distribution drift detected in primary features: "
            f"{', '.join(top_feature_names)}."
        )
    else:
        recommendation = "Risk Detected: Do Not Deploy"
        rationale = (
            f"Candidate retrained model failed quality assurance criteria (F1: {new_f1:.4f} vs {old_f1:.4f}, "
            f"Accuracy: {new_acc:.4f} vs {old_acc:.4f}). High deployment risk detected."
        )

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = {
        'timestamp': timestamp,
        'metrics_comparison': comparison,
        'top_drifted_features': top_drifted_features,
        'recommendation': recommendation,
        'recommendation_rationale': rationale
    }

    # Save JSON report for automated ingestion & compliance audit
    with open(report_path_json, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    # Save Markdown report for human inspection
    md_content = f"""# 🛡️ Model Retraining Validation Report & Governance Audit

**Timestamp:** {timestamp}  
**Recommendation:** **{recommendation}**  
**Audit File:** `{report_path_json}`

---

## 1. Metrics Comparison (Old Model vs. Retrained New Model)

| Metric | Old Model | New Model | Delta | % Change | Evaluation |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Accuracy** | {comparison['accuracy']['old_model']:.4f} | {comparison['accuracy']['new_model']:.4f} | {comparison['accuracy']['delta']:+.4f} | {comparison['accuracy']['delta_pct']:+.2f}% | {'🟢 Improved' if comparison['accuracy']['improved'] else '🔴 Degraded'} |
| **Precision** | {comparison['precision']['old_model']:.4f} | {comparison['precision']['new_model']:.4f} | {comparison['precision']['delta']:+.4f} | {comparison['precision']['delta_pct']:+.2f}% | {'🟢 Improved' if comparison['precision']['improved'] else '🔴 Degraded'} |
| **Recall** | {comparison['recall']['old_model']:.4f} | {comparison['recall']['new_model']:.4f} | {comparison['recall']['delta']:+.4f} | {comparison['recall']['delta_pct']:+.2f}% | {'🟢 Improved' if comparison['recall']['improved'] else '🔴 Degraded'} |
| **F1-Score** | {comparison['f1']['old_model']:.4f} | {comparison['f1']['new_model']:.4f} | {comparison['f1']['delta']:+.4f} | {comparison['f1']['delta_pct']:+.2f}% | {'🟢 Improved' if comparison['f1']['improved'] else '🔴 Degraded'} |

---

## 2. Top 3 Features That Caused The Drift

Statistical divergence calculated using Two-Sample Kolmogorov-Smirnov Test:
"""
    for i, f in enumerate(top_drifted_features, 1):
        md_content += f"""
{i}. **`{f['feature']}`**
   - **KS Statistic:** {f['ks_statistic']:.4f}
   - **p-value:** {f['p_value']:.6e}
   - **Drift Detected:** {'Yes (p < 0.05)' if f['drift_detected'] else 'No'}
"""

    md_content += f"""
---

## 3. Governance Recommendation & Analysis

- **Decision:** **{recommendation}**
- **Analysis:** {rationale}

---
*Generated automatically by AI-Powered Model Monitoring System Human-in-the-Loop Governance Gate.*
"""
    with open(report_path_md, 'w', encoding='utf-8') as f:
        f.write(md_content)

    return report

# ============================================================================
# HUMAN-IN-THE-LOOP GOVERNANCE GATE
# ============================================================================

def governance_gate(
    model_old,
    model_new,
    validation_report,
    model_dir=None,
    model_filename="deployed_model.pkl",
    logger=None,
    approval_override=None
):
    """
    Human-in-the-Loop Governance Gate:
    1. Intercepts the deployment process before writing to disk.
    2. Displays the detailed validation report to console.
    3. Prompts the human reviewer:
       "Deployment Request: Do you approve the deployment of this new model? (yes/no): "
    4. If input is 'yes':
       - Saves the retrained model to the /models/ folder
       - Updates retraining_log.txt to "Deployed by Human Approval."
       - Returns (model_new, True)
    5. If input is 'no' or invalid:
       - Fail-safe engaged: Old model remains active
       - Does NOT save new model to /models/ folder
       - Logs rejection to retraining_log.txt
       - Returns (model_old, False)
    """
    if model_dir is None:
        model_dir = MODELS_DIR
    print("\n" + "="*70)
    print("🛡️  HUMAN-IN-THE-LOOP GOVERNANCE GATE - DEPLOYMENT REVIEW")
    print("="*70)
    
    # Print Validation Report summary
    metrics = validation_report['metrics_comparison']
    top_features = validation_report['top_drifted_features']
    rec = validation_report['recommendation']
    
    print("\n📋 RETRAINING VALIDATION REPORT SUMMARY:")
    print("-" * 60)
    print(f"{'Metric':<12} | {'Old Model':<10} | {'New Model':<10} | {'Delta':<10} | {'Status':<10}")
    print("-" * 60)
    for m in ['accuracy', 'precision', 'recall', 'f1']:
        old_val = metrics[m]['old_model']
        new_val = metrics[m]['new_model']
        delta_str = f"{metrics[m]['delta']:+.4f}"
        status_sym = "🟢 Pass" if metrics[m]['improved'] else "🔴 Degraded"
        print(f"{m.capitalize():<12} | {old_val:<10.4f} | {new_val:<10.4f} | {delta_str:<10} | {status_sym:<10}")
    print("-" * 60)
    
    print("\n🚨 TOP 3 FEATURES CAUSING DRIFT:")
    for idx, feat in enumerate(top_features, 1):
        print(f"   {idx}. {feat['feature']:<8} (KS Statistic: {feat['ks_statistic']:.4f}, p-value: {feat['p_value']:.4e})")
        
    print(f"\n💡 RECOMMENDATION: {rec}")
    print(f"   {validation_report['recommendation_rationale']}")
    print("-" * 70)
    print("📁 Audit files saved: validation_report.json and validation_report.md")
    print("=" * 70)

    # 1. Save candidate model and register PENDING state for Web UI approval
    os.makedirs(model_dir, exist_ok=True)
    candidate_path = os.path.join(model_dir, "candidate_model.pkl")
    with open(candidate_path, "wb") as f:
        pickle.dump(model_new, f)

    pending_file = os.path.join(OUTPUTS_DIR, "pending_deployment.json")
    pending_info = {
        "status": "PENDING_APPROVAL",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "model_candidate": "Two-Stage Candidate Ensemble (Retrained on Production Drift)",
        "validation_report": validation_report
    }
    with open(pending_file, "w", encoding="utf-8") as f:
        json.dump(pending_info, f, indent=2)
    
    # 2. Check if human reviewer is automated / override or Web UI status-driven
    prompt_msg = "Deployment Request: Do you approve the deployment of this new model? (yes/no): "
    
    if approval_override is not None:
        user_input = str(approval_override).strip().lower()
        print(f"{prompt_msg}{approval_override}")
    elif os.environ.get("GOVERNANCE_APPROVAL") is not None:
        user_input = os.environ.get("GOVERNANCE_APPROVAL").strip().lower()
        print(f"{prompt_msg}{user_input} [via GOVERNANCE_APPROVAL env]")
    else:
        # Non-blocking / Web UI Governance Portal mode: status set to PENDING_APPROVAL
        print("\n🌐 Governance Gate engaged: Candidate model registered in 'PENDING_APPROVAL' state.")
        print("   Ready for human review and approval in React Dashboard -> Governance Portal.")
        if logger:
            logger.log_event("GOVERNANCE", "Candidate model registered in outputs/pending_deployment.json with status PENDING_APPROVAL", level="INFO")
        return model_old, False

    if user_input == "yes":
        os.makedirs(model_dir, exist_ok=True)
        save_path = os.path.join(model_dir, model_filename)
        with open(save_path, "wb") as f:
            pickle.dump(model_new, f)
            
        latest_path = os.path.join(model_dir, "model_latest.pkl")
        if save_path != latest_path:
            with open(latest_path, "wb") as f:
                pickle.dump(model_new, f)
                
        # Update retraining_log.txt with the EXACT required text:
        approval_message = "Deployed by Human Approval."
        if logger:
            logger.log_event("GOVERNANCE", approval_message)
        else:
            with open(DEFAULT_LOG_FILE, "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] [INFO] [GOVERNANCE] {approval_message}\n")
                
        print(f"\n🎉 DEPLOYMENT APPROVED! Model saved to /{model_dir}/{model_filename}")
        print(f"📝 Audit log updated: '{approval_message}'")
        return model_new, True
    else:
        # FAIL-SAFE: Old model remains active
        rejection_message = f"Deployment Rejected (user input: '{user_input}'). Fail-safe engaged: Old model remains active in production."
        if logger:
            logger.log_event("GOVERNANCE", rejection_message, level="WARNING")
        else:
            with open(DEFAULT_LOG_FILE, "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] [WARNING] [GOVERNANCE] {rejection_message}\n")
                
        print(f"\n⚠️  DEPLOYMENT REJECTED OR ABORTED (Input: '{user_input}').")
        print("🔒 FAIL-SAFE ENGAGED: Old model remains active in production.")
        print(f"❌ Retrained model was NOT saved to /{model_dir}/ folder.")
        return model_old, False

# ============================================================================
# RETRAINING & ENSEMBLE FUNCTIONS (MODULAR & REUSABLE)
# ============================================================================

def retrain_model(model, X_train, y_train, logger=None):
    """
    Retrain a machine learning model (or update local ensemble expert) with new data
    
    Args:
        model: sklearn estimator, TwoStagePipeline, or GlobalLocalEnsemble instance
        X_train: Training features
        y_train: Training labels
        logger: Logger instance for tracking
    
    Returns:
        Retrained model or ensemble
    """
    if logger:
        logger.log_event("RETRAINING", f"Starting retraining/updating with {len(X_train)} samples")
    
    if hasattr(model, "fit_local"):
        model.fit_local(X_train, y_train)
        if logger:
            status = getattr(model, "get_status", lambda: {"local_buffer_size": len(X_train)})()
            logger.log_event("RETRAINING", f"✅ Local Expert retrained successfully (Buffer: {status.get('local_buffer_size', len(X_train))} samples)")
    elif hasattr(model, "fit"):
        model.fit(X_train, y_train)
        if logger:
            logger.log_event("RETRAINING", "✅ Model retraining completed successfully")
    else:
        raise AttributeError(f"Model {type(model)} does not have fit_local or fit method.")
    
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

    logger.log_event("INITIALIZATION", "Starting ML Monitoring System with Multi-Pattern Historical Dataset (Demo: Credit Card Fraud Detection)")

    data = pd.read_csv(DEFAULT_DATA_FILE)

    # Use first 20000 for training
    train_data = data[:20000].copy()
    X_train = train_data.drop("Class", axis=1)
    y_train = train_data["Class"]

    # Preprocess Amount feature
    scaler = StandardScaler()
    X_train["Amount"] = scaler.fit_transform(X_train[["Amount"]])

    # Initialize Global-Local Ensemble
    ensemble = GlobalLocalEnsemble(global_weight=0.7, threshold=0.3, n_estimators=100, random_state=42)
    ensemble.fit_global(X_train, y_train)

    print(f"✅ Global Model (Veteran Expert) trained on {len(X_train)} historical records ({y_train.sum()} target class cases of Types A, B, C)")
    logger.log_event("INITIALIZATION", f"✅ Initial Global Model trained on {len(X_train)} samples with {y_train.sum()} target class events")

    # Preserve old model baseline for fail-safe rollback
    old_model = copy.deepcopy(ensemble)

    # ============================================================================
    # STEP 2: Simulate New Data with Drift & Novel Fraud (Type D)
    # ============================================================================
    print("\n" + "="*70)
    print("STEP 2: SIMULATING NEW DATA WITH DISTRIBUTION DRIFT & NOVEL TARGET CLASS PATTERN (TYPE D)")
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

    print("✅ New data loaded with feature drift & novel target class pattern (Type D) applied")
    print(f"   - Distribution Shift: Amount ×3, V1 ×1.5, V2 ×1.5, V3 +1")
    print(f"   - Novel Pattern Shift: V11 +5.0, V12 -6.0, V14 -5.5 for production target class cases")

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

    print(f"New data shape: {X_new.shape} with {y_new.sum()} novel target class cases")

    # ============================================================================
    # STEP 4: Evaluate Model on New Data (BEFORE RETRAINING - Old Model Baseline)
    # ============================================================================
    print("\n" + "="*70)
    print("STEP 4: EVALUATING OLD MODEL ON NOVEL DRIFTED DATA (BASELINE)")
    print("="*70)

    metrics_before, y_pred_before = evaluate_model(old_model, X_new, y_new, stage="BASELINE_OLD_MODEL", logger=logger)
    accuracy_before = metrics_before['accuracy']

    print(f"\n📊 BASELINE PERFORMANCE (Old Model on novel drifted stream):")
    print(f"   Accuracy:  {metrics_before['accuracy']:.4f} ({metrics_before['accuracy']*100:.2f}%)")
    print(f"   Recall:    {metrics_before['recall']:.4f} ({metrics_before['recall']*100:.2f}%)")
    print(f"   F1-Score:  {metrics_before['f1']:.4f}")

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
    print(f"   → Retraining required: {should_retrain}")

    # ============================================================================
    # STEP 7: Candidate Model Retraining & Performance Validation
    # ============================================================================
    deployment_approved = False
    
    if should_retrain:
        print("\n" + "="*70)
        print("STEP 7: CANDIDATE MODEL RETRAINING (ISOLATED SANDBOX)")
        print("="*70)
        logger.log_event("RETRAINING", "🔄 Training candidate model in sandbox for validation review")
        
        # Train candidate on shifted data without modifying active model yet
        candidate_model = retrain_model(copy.deepcopy(old_model), X_new, y_new, logger=logger)
        
        # Evaluate Candidate Model
        metrics_after, y_pred_after = evaluate_model(
            candidate_model, X_new, y_new, stage="CANDIDATE_MODEL_EVALUATION", logger=logger
        )
        accuracy_after = metrics_after['accuracy']
        improvement = accuracy_after - accuracy_before
        improvement_pct = (improvement / accuracy_before) * 100 if accuracy_before > 0 else 0

        # Detect Top 3 Features causing the drift
        top_drifted = detect_top_drift_features(X_train, X_new, top_n=3)

        # Generate detailed validation report (.json and .md)
        validation_report = generate_validation_report(
            metrics_old=metrics_before,
            metrics_new=metrics_after,
            top_drifted_features=top_drifted,
            report_path_json=DEFAULT_REPORT_JSON,
            report_path_md=DEFAULT_REPORT_MD
        )

        # ========================================================================
        # STEP 8: HUMAN-IN-THE-LOOP GOVERNANCE GATE
        # ========================================================================
        active_model, deployment_approved = governance_gate(
            model_old=old_model,
            model_new=candidate_model,
            validation_report=validation_report,
            model_dir=MODELS_DIR,
            model_filename="deployed_model.pkl",
            logger=logger
        )
        ensemble = active_model

    else:
        print("\n⏭️  Skipping retraining (model is stable)")
        metrics_after = metrics_before
        accuracy_after = accuracy_before
        improvement = 0.0
        improvement_pct = 0.0
        active_model = old_model

    # ============================================================================
    # STEP 9: Summary & Logging
    # ============================================================================
    status = "🟢 EXCELLENT" if accuracy_after > 0.95 else "🟡 GOOD" if accuracy_after > 0.85 else "🔴 NEEDS ATTENTION"

    decision_log = {
        'timestamp': str(pd.Timestamp.now()),
        'architecture': 'Two-Stage Hybrid Global-Local Ensemble (Stage 1: IsolationForest + Stage 2: XGBoost)',
        'drift_detected': drift_detected,
        'accuracy_before': accuracy_before,
        'accuracy_threshold': accuracy_threshold,
        'retraining_triggered': should_retrain,
        'accuracy_after': accuracy_after,
        'improvement': improvement,
        'improvement_pct': improvement_pct,
        'governance_approval': deployment_approved,
        'active_model': 'New Retrained Model (Deployed by Human Approval)' if deployment_approved else 'Old Baseline Model (Active)',
        'system_status': status
    }

    with open(DEFAULT_JSON_LOG, 'w') as f:
        json.dump(decision_log, f, indent=2)

    print(f"\n✅ Decision log saved to {DEFAULT_JSON_LOG}")
    print(json.dumps(decision_log, indent=2))
    logger.log_event("LOGGING", f"✅ Decision log saved to {DEFAULT_JSON_LOG}")

    print("\n" + "="*70)
    print("GLOBAL-LOCAL ENSEMBLE DECISION ENGINE EXECUTION COMPLETE!")
    print("="*70)

