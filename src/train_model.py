import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load data
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

# Get probabilities instead of direct predictions
y_prob = model.predict_proba(X_test)[:, 1]

# Apply optimal threshold (0.3)
threshold = 0.3
y_pred = (y_prob > threshold).astype(int)

# Evaluation with optimal threshold
print("="*70)
print(f"Model trained with Optimal Threshold: {threshold}")
print("="*70)
print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
