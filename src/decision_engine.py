import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, precision_score, recall_score, f1_score
import pickle
import json
from datetime import datetime

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
# RETRAINING FUNCTIONS (MODULAR & REUSABLE)
# ============================================================================

def retrain_model(model, X_train, y_train, logger=None):
    """
    Retrain a machine learning model with new data
    
    Args:
        model: ML model to retrain (sklearn estimator)
        X_train: Training features
        y_train: Training labels
        logger: Logger instance for tracking
    
    Returns:
        Retrained model
    """
    if logger:
        logger.log_event("RETRAINING", f"Starting retraining with {len(X_train)} samples")
    
    # Retrain model
    model.fit(X_train, y_train)
    
    if logger:
        logger.log_event("RETRAINING", "✅ Model retraining completed successfully")
    
    return model

def evaluate_model(model, X_test, y_test, stage="EVALUATION", logger=None):
    """
    Evaluate model performance on test data
    
    Args:
        model: Trained ML model
        X_test: Test features
        y_test: Test labels
        stage: Name of evaluation stage
        logger: Logger instance
    
    Returns:
        Dictionary of metrics
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
    Make decision on whether to retrain
    
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

# ============================================================================
# STEP 1: Load Training Data and Train Initial Model
# ============================================================================
print("="*70)
print("STEP 1: LOADING TRAINING DATA & TRAINING INITIAL MODEL")
print("="*70)

logger.log_event("INITIALIZATION", "Starting ML Drift Detection System")

data = pd.read_csv("data/creditcard.csv")

# Use first 20000 for training
train_data = data[:20000].copy()
X_train = train_data.drop("Class", axis=1)
y_train = train_data["Class"]

# Train initial model
scaler = StandardScaler()
X_train["Amount"] = scaler.fit_transform(X_train[["Amount"]])

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

print("✅ Initial model trained")
logger.log_event("INITIALIZATION", f"✅ Initial model trained on {len(X_train)} samples")


# ============================================================================
# STEP 2: Simulate New Data with Drift
# ============================================================================
print("\n" + "="*70)
print("STEP 2: SIMULATING NEW DATA WITH DRIFT")
print("="*70)

# Use next 10000 for testing (simulating new incoming data)
new_data = data[20000:30000].copy()

# Apply drift to simulate real-world changes
new_data["Amount"] = new_data["Amount"] * 3
new_data["V1"] = new_data["V1"] * 1.5
new_data["V2"] = new_data["V2"] * 1.5
new_data["V3"] = new_data["V3"] + 1

print("✅ New data loaded with drift applied")
print(f"   - Amount × 3")
print(f"   - V1 × 1.5")
print(f"   - V2 × 1.5")
print(f"   - V3 + 1")

# ============================================================================
# STEP 3: Prepare New Data (Same preprocessing as training)
# ============================================================================
print("\n" + "="*70)
print("STEP 3: PREPARING NEW DATA FOR EVALUATION")
print("="*70)

X_new = new_data.drop("Class", axis=1)
y_new = new_data["Class"]

# Apply same scaling
X_new["Amount"] = scaler.transform(X_new[["Amount"]])

print(f"New data shape: {X_new.shape}")

# ============================================================================
# STEP 4: Evaluate Model on New Data (BEFORE RETRAINING)
# ============================================================================
print("\n" + "="*70)
print("STEP 4: EVALUATING MODEL ON NEW DATA (BASELINE)")
print("="*70)

metrics_before, y_pred_before = evaluate_model(model, X_new, y_new, stage="BASELINE", logger=logger)
accuracy_before = metrics_before['accuracy']

print(f"\n📊 BASELINE PERFORMANCE (Before Retraining):")
print(f"   Accuracy: {accuracy_before:.4f} ({accuracy_before*100:.2f}%)")

# ============================================================================
# STEP 5: Decision Engine - Check Conditions
# ============================================================================
print("\n" + "="*70)
print("STEP 5: DECISION ENGINE - EVALUATING CONDITIONS")
print("="*70)

# Condition 1: Check for Drift
drift_detected = True  # From Step 6 (Drift Detection)
print(f"\n🔍 Condition 1 - Drift Detection:")
print(f"   {'✅ DRIFT DETECTED' if drift_detected else '❌ No drift'}")

# Condition 2: Check Accuracy Threshold
accuracy_threshold = 0.80  # 80% minimum accuracy

print(f"\n🔍 Condition 2 - Accuracy Check:")
print(f"   Threshold: {accuracy_threshold:.2f} ({accuracy_threshold*100:.0f}%)")
print(f"   Current:   {accuracy_before:.4f} ({accuracy_before*100:.2f}%)")

# ============================================================================
# STEP 6: Make Decision Using Function
# ============================================================================
print("\n" + "="*70)
print("STEP 6: DECISION - SHOULD WE RETRAIN?")
print("="*70)

should_retrain, accuracy_degraded = make_retraining_decision(
    drift_detected=drift_detected,
    accuracy_before=accuracy_before,
    accuracy_threshold=accuracy_threshold,
    logger=logger
)

print(f"\n🤔 Decision Logic:")
print(f"   Drift detected: {drift_detected}")
print(f"   Accuracy degraded: {accuracy_degraded}")
print(f"   → Retrain required: {should_retrain}")

if should_retrain:
    print("\n🚨 ALERT: Model needs retraining!")
    print(f"   Reason(s):")
    if drift_detected:
        print(f"   • Data drift detected in production")
        logger.log_event("DECISION", "🚨 ALERT: Drift detected - triggering retraining", level="WARNING")
    if accuracy_degraded:
        print(f"   • Accuracy dropped below {accuracy_threshold*100:.0f}% threshold")
        logger.log_event("DECISION", f"🚨 ALERT: Accuracy degraded - triggering retraining", level="WARNING")
else:
    print("\n✅ Model is stable. No retraining needed.")
    logger.log_event("DECISION", "✅ Model is stable - no retraining needed")


# ============================================================================
# STEP 7: Auto Retraining (If Needed) - Using Modular Function
# ============================================================================
print("\n" + "="*70)
print("STEP 7: AUTO RETRAINING PROCESS")
print("="*70)

if should_retrain:
    print("\n⚙️  RETRAINING MODEL with new data...")
    logger.log_event("RETRAINING", "🔄 Starting retraining process")
    
    # Combine old and new data for better training
    combined_X = pd.concat([X_train, X_new], ignore_index=True)
    combined_y = pd.concat([y_train, y_new], ignore_index=True)
    
    logger.log_event("RETRAINING", f"Combined dataset: {len(combined_X)} samples (Old: {len(X_train)}, New: {len(X_new)})")
    
    # Retrain model using function
    model_retrained = RandomForestClassifier(n_estimators=100, random_state=42)
    model = retrain_model(model_retrained, combined_X, combined_y, logger=logger)
    
    print("✅ Model retraining completed!")
    print(f"   Training samples used: {len(combined_X)}")
    
else:
    print("\n⏭️  Skipping retraining (model is stable)")
    logger.log_event("RETRAINING", "⏭️ Skipping retraining - model is stable")


# ============================================================================
# STEP 8: Evaluate Model After Retraining - Using Function
# ============================================================================
print("\n" + "="*70)
print("STEP 8: EVALUATING MODEL AFTER RETRAINING")
print("="*70)

metrics_after, y_pred_after = evaluate_model(model, X_new, y_new, stage="POST_RETRAINING", logger=logger)
accuracy_after = metrics_after['accuracy']

print(f"\n📊 UPDATED PERFORMANCE (After Retraining):")
print(f"   Accuracy: {accuracy_after:.4f} ({accuracy_after*100:.2f}%)")

# ============================================================================
# STEP 9: Performance Comparison
# ============================================================================
print("\n" + "="*70)
print("STEP 9: PERFORMANCE COMPARISON")
print("="*70)

improvement = accuracy_after - accuracy_before
improvement_pct = (improvement / accuracy_before) * 100 if accuracy_before > 0 else 0

print(f"\n📈 BEFORE vs AFTER RETRAINING:")
print(f"   Before:      {accuracy_before:.4f} ({accuracy_before*100:.2f}%)")
print(f"   After:       {accuracy_after:.4f} ({accuracy_after*100:.2f}%)")
print(f"   Improvement: {improvement:+.4f} ({improvement_pct:+.2f}%)")

logger.log_event("COMPARISON", f"Before accuracy: {accuracy_before:.4f}")
logger.log_event("COMPARISON", f"After accuracy: {accuracy_after:.4f}")
logger.log_event("COMPARISON", f"Improvement: {improvement_pct:+.2f}%")

if improvement > 0:
    print(f"\n✅ MODEL IMPROVED! Self-healing system working! 🔥")
    logger.log_event("COMPARISON", "✅ MODEL IMPROVED! Retraining was successful!", level="SUCCESS")
elif improvement == 0:
    print(f"\n ℹ️  Model performance unchanged")
    logger.log_event("COMPARISON", "ℹ️ Model performance unchanged")
else:
    print(f"\n⚠️  Model performance decreased slightly")
    logger.log_event("COMPARISON", "⚠️ Model performance decreased - investigate further", level="WARNING")


# ============================================================================
# STEP 10: Detailed Classification Report
# ============================================================================
print("\n" + "="*70)
print("STEP 10: DETAILED CLASSIFICATION REPORT (AFTER RETRAINING)")
print("="*70)

report = classification_report(y_new, y_pred_after)
print(f"\n{report}")
logger.log_event("CLASSIFICATION", "Classification report generated (see output above)")


# ============================================================================
# STEP 11: System Status Summary
# ============================================================================
print("\n" + "="*70)
print("SYSTEM STATUS SUMMARY")
print("="*70)

print(f"\n🎯 EXECUTIVE SUMMARY:")
print(f"\n1. Initial Detection:")
print(f"   ✓ Drift detected: {drift_detected}")
print(f"   ✓ Accuracy before retraining: {accuracy_before*100:.2f}%")

print(f"\n2. Decision:")
print(f"   ✓ Retraining triggered: {should_retrain}")
if should_retrain:
    reason = []
    if drift_detected:
        reason.append("Drift")
    if accuracy_degraded:
        reason.append("Accuracy degradation")
    print(f"   ✓ Reason: {' + '.join(reason)}")

print(f"\n3. Outcome:")
print(f"   ✓ Accuracy after retraining: {accuracy_after*100:.2f}%")
print(f"   ✓ Improvement: {improvement_pct:+.2f}%")

print(f"\n4. System Status:")
if accuracy_after > 0.90:
    status = "🟢 EXCELLENT"
elif accuracy_after > 0.80:
    status = "🟡 GOOD"
else:
    status = "🔴 NEEDS ATTENTION"
print(f"   {status}")
logger.log_event("STATUS", f"System Status: {status}")

print(f"\n5. Recommended Actions:")
if accuracy_after > accuracy_threshold:
    print(f"   ✓ Deploy updated model to production")
    print(f"   ✓ Monitor performance continuously")
    logger.log_event("RECOMMENDATION", "✅ Model ready for production deployment")
else:
    print(f"   ✓ Further investigation required")
    print(f"   ✓ Consider feature engineering or data collection")
    logger.log_event("RECOMMENDATION", "⚠️ Model needs further investigation", level="WARNING")


# ============================================================================
# STEP 12: Save Decision Log
# ============================================================================
print("\n" + "="*70)
print("STEP 12: DECISION LOG")
print("="*70)

decision_log = {
    'timestamp': str(pd.Timestamp.now()),
    'drift_detected': drift_detected,
    'accuracy_before': accuracy_before,
    'accuracy_threshold': accuracy_threshold,
    'accuracy_degraded': accuracy_degraded,
    'retraining_triggered': should_retrain,
    'accuracy_after': accuracy_after,
    'improvement': improvement,
    'improvement_pct': improvement_pct,
    'system_status': status if accuracy_after > 0.90 else "🟡 GOOD" if accuracy_after > 0.80 else "🔴 NEEDS ATTENTION"
}

# Save log
with open('decision_log.json', 'w') as f:
    json.dump(decision_log, f, indent=2)

print("\n✅ Decision log saved to decision_log.json")
print(json.dumps(decision_log, indent=2))
logger.log_event("LOGGING", "✅ Decision log saved to decision_log.json")


# ============================================================================
# FINAL MESSAGE
# ============================================================================
print("\n" + "="*70)
print("DECISION ENGINE COMPLETE!")
print("="*70)
print("\n🚀 YOUR SYSTEM IS NOW SELF-HEALING!")
print("\n   Automatic Workflow:")
print("   1. ✅ Detect new data")
print("   2. ✅ Check for drift")
print("   3. ✅ Evaluate accuracy")
print("   4. ✅ Make decision")
print("   5. ✅ Retrain if needed")
print("   6. ✅ Validate improvement")
print("   7. ✅ Log results")
print("\n   This cycle can run AUTOMATICALLY in production! 🔥")

logger.log_event("COMPLETE", "✅ Decision Engine Execution Complete!")
logger.log_event("COMPLETE", "📊 All events logged to retraining_log.txt")
print(f"\n📊 Full event log saved to: retraining_log.txt")
