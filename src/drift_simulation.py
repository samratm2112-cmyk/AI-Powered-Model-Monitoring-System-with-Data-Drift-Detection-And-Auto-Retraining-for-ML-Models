import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# ============================================================================
# STEP 1: Load and prepare original data (same as training)
# ============================================================================
data = pd.read_csv("data/creditcard.csv")

# Split features and target
X = data.drop("Class", axis=1)
y = data["Class"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Scale Amount
scaler = StandardScaler()
X_train["Amount"] = scaler.fit_transform(X_train[["Amount"]])
X_test["Amount"] = scaler.transform(X_test[["Amount"]])

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# ============================================================================
# STEP 2: Evaluate on original test data
# ============================================================================
y_prob_original = model.predict_proba(X_test)[:, 1]
threshold = 0.3
y_pred_original = (y_prob_original > threshold).astype(int)

print("="*70)
print("BASELINE MODEL PERFORMANCE (Original Data)")
print("="*70)
print(f"Accuracy: {accuracy_score(y_test, y_pred_original):.4f}")
print(classification_report(y_test, y_pred_original))

# ============================================================================
# STEP 3: Create drifted data
# ============================================================================
print("\n" + "="*70)
print("SIMULATING DATA DRIFT")
print("="*70)

# Split data into old and new
old_data = data[:10000].copy()
new_data = data[10000:20000].copy()

print(f"\nOld data shape: {old_data.shape}")
print(f"New data shape: {new_data.shape}")

# Show original distributions
print(f"\nOld Amount - Mean: {old_data['Amount'].mean():.2f}, Std: {old_data['Amount'].std():.2f}")
print(f"New Amount (before drift) - Mean: {new_data['Amount'].mean():.2f}, Std: {new_data['Amount'].std():.2f}")

# ============================================================================
# STEP 4: Introduce drift (modify multiple features)
# ============================================================================
# Simulate realistic data drift by shifting feature distributions
new_data["Amount"] = new_data["Amount"] * 3  # Larger transaction amounts
new_data["V1"] = new_data["V1"] * 1.5       # Shift V1
new_data["V2"] = new_data["V2"] * 1.5       # Shift V2
new_data["V3"] = new_data["V3"] + 1         # Shift V3

print(f"\nDRIFT INTRODUCED:")
print(f"  - Amount multiplied by 3")
print(f"  - V1, V2 multiplied by 1.5")
print(f"  - V3 shifted by +1")
print(f"New Amount (after drift) - Mean: {new_data['Amount'].mean():.2f}, Std: {new_data['Amount'].std():.2f}")

# ============================================================================
# STEP 5: Prepare drifted data for prediction
# ============================================================================
X_new = new_data.drop("Class", axis=1)
y_new = new_data["Class"]

# Scale Amount using the same scaler (critical for showing drift)
X_new["Amount"] = scaler.transform(X_new[["Amount"]])

# ============================================================================
# STEP 6: Evaluate on drifted data
# ============================================================================
y_prob_drifted = model.predict_proba(X_new)[:, 1]
y_pred_drifted = (y_prob_drifted > threshold).astype(int)

print("\n" + "="*70)
print("MODEL PERFORMANCE ON DRIFTED DATA")
print("="*70)
print(f"Accuracy: {accuracy_score(y_new, y_pred_drifted):.4f}")
print(classification_report(y_new, y_pred_drifted))

# ============================================================================
# STEP 7: Comparison Summary
# ============================================================================
print("\n" + "="*70)
print("DRIFT IMPACT SUMMARY")
print("="*70)

original_accuracy = accuracy_score(y_test, y_pred_original)
drifted_accuracy = accuracy_score(y_new, y_pred_drifted)
accuracy_drop = original_accuracy - drifted_accuracy

print(f"\nOriginal Accuracy: {original_accuracy:.4f} (99.95%)")
print(f"Drifted Accuracy:  {drifted_accuracy:.4f}")
print(f"Accuracy Drop:     {accuracy_drop:.4f} ({accuracy_drop*100:.2f}%)")

if accuracy_drop > 0:
    print("\n✅ DATA DRIFT DETECTED!")
    print("   Model performance degraded after drift injection")
else:
    print("\n⚠️ No significant accuracy drop detected")
