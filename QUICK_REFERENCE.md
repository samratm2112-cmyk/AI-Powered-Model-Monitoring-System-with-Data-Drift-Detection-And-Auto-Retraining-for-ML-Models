# 📚 QUICK REFERENCE: Using Your Professional ML System

## 🚀 How to Use Your System (5 Minutes)

### PART 1: Basic Usage

```python
# ============================================
# 1. Import required modules
# ============================================
from src.decision_engine import (
    logger,
    evaluate_model,
    make_retraining_decision,
    retrain_model
)
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# ============================================
# 2. Load your data
# ============================================
new_data = pd.read_csv("production_data.csv")
X_new = new_data.drop("Class", axis=1)
y_new = new_data["Class"]

# ============================================
# 3. Evaluate baseline
# ============================================
metrics_before, predictions = evaluate_model(
    model=your_model,
    X_test=X_new,
    y_test=y_new,
    stage="PRODUCTION_CHECK",
    logger=logger
)

print(f"Baseline Accuracy: {metrics_before['accuracy']:.4f}")

# ============================================
# 4. Make decision
# ============================================
should_retrain, accuracy_degraded = make_retraining_decision(
    drift_detected=check_if_drifted(X_new),
    accuracy_before=metrics_before['accuracy'],
    accuracy_threshold=0.80,
    logger=logger
)

# ============================================
# 5. Retrain if needed
# ============================================
if should_retrain:
    combined_X = pd.concat([X_old, X_new])
    combined_y = pd.concat([y_old, y_new])
    
    your_model = retrain_model(
        model=your_model,
        X_train=combined_X,
        y_train=combined_y,
        logger=logger
    )

# ============================================
# 6. Verify improvement
# ============================================
metrics_after, _ = evaluate_model(
    model=your_model,
    X_test=X_new,
    y_test=y_new,
    stage="POST_RETRAIN",
    logger=logger
)

print(f"New Accuracy: {metrics_after['accuracy']:.4f}")
print(f"Improvement: {(metrics_after['accuracy'] - metrics_before['accuracy'])*100:.2f}%")

# ============================================
# ✅ Everything is logged automatically!
# ✅ Check retraining_log.txt for full history
# ✅ Check decision_log.json for metrics
# ============================================
```

---

## 📊 Output Files Reference

### File 1: `retraining_log.txt` (Event History)

**Purpose:** Complete audit trail of all decisions

**Format:**
```
[TIMESTAMP] [LEVEL] [STAGE] MESSAGE
```

**Example:**
```
[2026-04-21 15:38:31] [INFO] [INITIALIZATION] Starting ML Drift Detection System
[2026-04-21 15:38:49] [INFO] [BASELINE] accuracy: 0.9993
[2026-04-21 15:38:49] [WARNING] [DECISION] 🚨 ALERT: Drift detected - triggering retraining
[2026-04-21 15:39:12] [SUCCESS] [COMPARISON] ✅ MODEL IMPROVED! Retraining was successful!
```

**How to read:**
- `[INFO]` = Normal operation
- `[WARNING]` = Alert needed attention
- `[SUCCESS]` = Positive outcome
- `[ERROR]` = Problem occurred

**Usage:**
```bash
# View last 20 lines
tail -20 retraining_log.txt

# Find all warnings
grep "WARNING" retraining_log.txt

# Find all retrain events
grep "RETRAINING" retraining_log.txt
```

### File 2: `decision_log.json` (Metrics)

**Purpose:** Machine-readable metrics for integration

**Format:**
```json
{
  "timestamp": "ISO-8601 timestamp",
  "drift_detected": boolean,
  "accuracy_before": float,
  "accuracy_after": float,
  "improvement_pct": float,
  "system_status": "string"
}
```

**Example:**
```json
{
  "timestamp": "2026-04-21 15:39:12.596496",
  "drift_detected": true,
  "accuracy_before": 0.9993,
  "accuracy_threshold": 0.8,
  "accuracy_degraded": false,
  "retraining_triggered": true,
  "accuracy_after": 1.0,
  "improvement": 0.0007,
  "improvement_pct": 0.07,
  "system_status": "🟢 EXCELLENT"
}
```

**Usage:**
```python
# Read metrics into Python
import json

with open('decision_log.json', 'r') as f:
    metrics = json.load(f)

print(f"Improvement: {metrics['improvement_pct']}%")
print(f"Status: {metrics['system_status']}")

# Send to dashboard
send_to_dashboard(metrics)

# Store in database
db.insert_one(metrics)
```

---

## 🔧 Functions Quick Reference

### Function 1: `evaluate_model()`

**What it does:** Evaluate model and return metrics

**Signature:**
```python
def evaluate_model(model, X_test, y_test, stage="EVALUATION", logger=None)
```

**Parameters:**
- `model`: Trained sklearn model
- `X_test`: Test features
- `y_test`: Test labels
- `stage`: Name for logging (e.g., "BASELINE", "POST_RETRAIN")
- `logger`: RetrainingLogger instance (optional)

**Returns:**
```python
metrics = {
    'accuracy': float,
    'precision': float,
    'recall': float,
    'f1': float
}
predictions = numpy array
```

**Example:**
```python
metrics, preds = evaluate_model(model, X_test, y_test, 
                                stage="EVALUATION", logger=logger)
print(f"Accuracy: {metrics['accuracy']:.4f}")
```

### Function 2: `retrain_model()`

**What it does:** Retrain model with new data

**Signature:**
```python
def retrain_model(model, X_train, y_train, logger=None)
```

**Parameters:**
- `model`: Model to retrain
- `X_train`: Training features
- `y_train`: Training labels
- `logger`: RetrainingLogger instance (optional)

**Returns:**
- Updated model

**Example:**
```python
model = retrain_model(model, X_train, y_train, logger=logger)
```

### Function 3: `make_retraining_decision()`

**What it does:** Decide if retraining is needed

**Signature:**
```python
def make_retraining_decision(drift_detected, accuracy_before, 
                            accuracy_threshold, logger=None)
```

**Parameters:**
- `drift_detected`: Boolean (was drift detected?)
- `accuracy_before`: Float (current accuracy)
- `accuracy_threshold`: Float (minimum acceptable accuracy)
- `logger`: RetrainingLogger instance (optional)

**Returns:**
```python
should_retrain = boolean
accuracy_degraded = boolean
```

**Example:**
```python
should_retrain, acc_deg = make_retraining_decision(
    drift_detected=True,
    accuracy_before=0.95,
    accuracy_threshold=0.80,
    logger=logger
)

if should_retrain:
    model = retrain_model(model, X_new, y_new, logger=logger)
```

### Class: `RetrainingLogger`

**What it does:** Log all events and metrics

**Signature:**
```python
logger = RetrainingLogger(log_file="retraining_log.txt")
```

**Methods:**

#### `log_event(stage, message, level="INFO")`
```python
logger.log_event("DECISION", "Drift detected - triggering retrain", level="WARNING")
# Output: [2026-04-21 15:38:49] [WARNING] [DECISION] Drift detected...
```

#### `log_metrics(stage, metrics)`
```python
logger.log_metrics("EVALUATION", metrics)
# Logs all metrics: accuracy, precision, recall, f1
```

---

## 💻 Common Scenarios

### Scenario 1: Daily Batch Processing

```python
import schedule
import time
from datetime import datetime

def daily_drift_check():
    # Load production data
    prod_data = fetch_from_database(date=datetime.today())
    X_prod = prod_data.drop("Class", axis=1)
    y_prod = prod_data["Class"]
    
    # Evaluate
    metrics, _ = evaluate_model(model, X_prod, y_prod, 
                                stage="DAILY_CHECK", logger=logger)
    
    # Decide
    should_retrain, _ = make_retraining_decision(
        drift_detected=has_drift(X_prod),
        accuracy_before=metrics['accuracy'],
        accuracy_threshold=0.80,
        logger=logger
    )
    
    # Retrain if needed
    if should_retrain:
        print("🔄 Retraining initiated...")
        model = retrain_model(model, X_prod, y_prod, logger=logger)
        save_model(model, f"models/model_{datetime.now().date()}.pkl")

# Schedule daily at 2 AM
schedule.every().day.at("02:00").do(daily_drift_check)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Scenario 2: Real-time Monitoring

```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer('model_data', value_deserializer=lambda m: json.loads(m.decode('utf-8')))

for message in consumer:
    # Process each new data point
    features = message['features']
    prediction = model.predict([features])
    
    # Track for batch decisions
    batch.append(features)
    
    if len(batch) >= 1000:  # Every 1000 records
        X_batch = pd.DataFrame(batch)
        
        metrics, _ = evaluate_model(model, X_batch, logger=logger)
        
        should_retrain, _ = make_retraining_decision(
            drift_detected=has_drift(X_batch),
            accuracy_before=metrics['accuracy'],
            accuracy_threshold=0.80,
            logger=logger
        )
        
        if should_retrain:
            model = retrain_model(model, X_batch, logger=logger)
        
        batch = []
```

### Scenario 3: Flask REST API

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/evaluate', methods=['POST'])
def evaluate_endpoint():
    data = request.json
    X_new = pd.DataFrame([data['features']])
    y_new = pd.Series([data['label']])
    
    # Evaluate
    metrics, _ = evaluate_model(model, X_new, y_new, 
                                stage="API_REQUEST", logger=logger)
    
    return jsonify({
        'status': 'evaluated',
        'metrics': metrics
    })

@app.route('/api/retrain', methods=['POST'])
def retrain_endpoint():
    data = request.json
    
    # Make decision
    should_retrain, _ = make_retraining_decision(
        drift_detected=data.get('drift_detected', False),
        accuracy_before=data.get('accuracy_before', 0.9),
        accuracy_threshold=0.80,
        logger=logger
    )
    
    if should_retrain:
        # Retrain
        new_data = fetch_new_training_data()
        X_train = new_data.drop("label", axis=1)
        y_train = new_data["label"]
        
        model = retrain_model(model, X_train, y_train, logger=logger)
        
        return jsonify({
            'status': 'retraining_completed',
            'message': 'Model has been retrained'
        })
    else:
        return jsonify({
            'status': 'no_retrain_needed',
            'message': 'Model is performing well'
        })

if __name__ == '__main__':
    app.run(debug=False)
```

---

## ⚡ Quick Troubleshooting

### Problem: "Module not found" error

**Solution:**
```bash
# Make sure you're in the right directory
cd C:\Users\manas\OneDrive\Desktop\ML_Drift_Project

# Run with full path
python src/decision_engine.py
```

### Problem: Unicode errors in log file

**Solution:** Already fixed! Using UTF-8 encoding.

### Problem: Model performance degraded after retraining

**Solution:** Check the logs!
```bash
grep "WARNING" retraining_log.txt
grep "ERROR" retraining_log.txt
```

### Problem: Logs not being created

**Solution:** Check directory permissions
```bash
# Make sure you have write permissions
ls -la retraining_log.txt
```

---

## 📈 Monitoring Dashboard Integration

### Extract metrics for your dashboard

```python
import json
import pandas as pd

# Read decision log
with open('decision_log.json') as f:
    decision = json.load(f)

# Create dashboard data
dashboard_data = {
    'timestamp': decision['timestamp'],
    'current_accuracy': decision['accuracy_after'],
    'improvement': f"{decision['improvement_pct']:.2f}%",
    'status': decision['system_status'],
    'next_retrain': 'If drift detected' if decision['drift_detected'] else 'Not needed'
}

# Send to your dashboard
import requests
requests.post('https://your-dashboard.com/api/metrics', json=dashboard_data)
```

---

## ✅ Checklist for Production Deployment

```
Before deploying:

[ ] All functions tested individually
[ ] Error handling verified
[ ] Logs being created correctly
[ ] Metrics exported to JSON
[ ] Database connection working (if used)
[ ] Alerts configured (if needed)
[ ] Scheduled jobs configured
[ ] Monitoring dashboard updated
[ ] Documentation reviewed
[ ] Team trained on new system

After deployment:

[ ] Monitor logs daily
[ ] Check for warnings/errors
[ ] Review metrics dashboard
[ ] Verify model performance
[ ] Document any issues
[ ] Update runbooks as needed
```

---

## 🎓 Key Takeaways

✅ Your system is **modular** - easy to extend  
✅ Your system is **reusable** - use in other projects  
✅ Your system is **logged** - full audit trail  
✅ Your system is **professional** - enterprise-grade  
✅ Your system is **production-ready** - deploy with confidence  

**You've built an ML Ops system!** 🚀
