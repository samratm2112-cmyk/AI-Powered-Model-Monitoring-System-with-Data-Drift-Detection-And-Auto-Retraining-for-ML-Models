import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

# ============================================================================
# STEP 1: Load and Prepare Data (Using Sample for Speed)
# ============================================================================
print("="*70)
print("STEP 1: LOADING AND PREPARING DATA")
print("="*70)

data = pd.read_csv("data/creditcard.csv")
print(f"Full data shape: {data.shape}")

# Use a smaller sample for faster training
data_sample = data.sample(n=50000, random_state=42)
print(f"Using sample: {data_sample.shape} for faster analysis")

# Split features and target
X = data_sample.drop("Class", axis=1)
y = data_sample["Class"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Scale Amount
scaler = StandardScaler()
X_train["Amount"] = scaler.fit_transform(X_train[["Amount"]])
X_test["Amount"] = scaler.transform(X_test[["Amount"]])

print(f"Training set size: {X_train.shape[0]}")
print(f"Test set size: {X_test.shape[0]}")

# ============================================================================
# STEP 2: Train Model
# ============================================================================
print("\n" + "="*70)
print("STEP 2: TRAINING MODEL")
print("="*70)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
print("✅ Model trained successfully")

# ============================================================================
# STEP 3: Extract Feature Importance (Built-in from Random Forest)
# ============================================================================
print("\n" + "="*70)
print("STEP 3: EXTRACTING FEATURE IMPORTANCE")
print("="*70)

# Get feature importance from the trained model
feature_importance = model.feature_importances_
feature_names = X_train.columns

# Create dataframe for better visualization
importance_df = pd.DataFrame({
    'Feature': feature_names,
    'Importance': feature_importance
}).sort_values('Importance', ascending=False)

print("✅ Feature importance extracted from Random Forest model")

# ============================================================================
# STEP 4: Feature Importance Analysis
# ============================================================================
print("\n" + "="*70)
print("STEP 4: TOP 15 MOST IMPORTANT FEATURES")
print("="*70)

print("\n🔥 RANKING:")
for idx, (_, row) in enumerate(importance_df.head(15).iterrows(), 1):
    print(f"  #{idx:2d}. {row['Feature']:6s} - Importance: {row['Importance']:.6f}")

# ============================================================================
# STEP 5: Connect with Drift Detection
# ============================================================================
print("\n" + "="*70)
print("STEP 5: ROOT CAUSE ANALYSIS - DRIFT CONNECTION")
print("="*70)

# Identify features that drifted significantly
drifted_features = ['Amount', 'V1', 'V2', 'V3']  # From drift detection step

print("\n📊 ANALYZING DRIFTED FEATURES:")
drifted_with_importance = []

for feature in drifted_features:
    imp_row = importance_df[importance_df['Feature'] == feature]
    if len(imp_row) > 0:
        importance = imp_row.iloc[0]['Importance']
        rank = imp_row.index[0] + 1
        drifted_with_importance.append({
            'Feature': feature,
            'Importance': importance,
            'Rank': rank
        })
        print(f"\n  ✓ {feature}:")
        print(f"    - Importance Rank: #{rank}")
        print(f"    - Importance Score: {importance:.6f}")
        
        # Classify importance level
        if importance > 0.1:
            level = "🔴 CRITICAL"
        elif importance > 0.05:
            level = "🟠 HIGH"
        elif importance > 0.01:
            level = "🟡 MEDIUM"
        else:
            level = "🟢 LOW"
        
        print(f"    - Importance Level: {level}")

# ============================================================================
# STEP 6: ROOT CAUSE INSIGHTS
# ============================================================================
print("\n" + "="*70)
print("ROOT CAUSE ANALYSIS - KEY INSIGHTS")
print("="*70)

print("\n💡 IMPACT ANALYSIS:")

# Find high-importance drifted features
high_impact_drifts = [d for d in drifted_with_importance if d['Importance'] > 0.05]

if high_impact_drifts:
    print(f"\n  ⚠️  CRITICAL ALERT: {len(high_impact_drifts)} important feature(s) have drifted!")
    for item in high_impact_drifts:
        print(f"     • {item['Feature']}: Rank #{item['Rank']} (Importance: {item['Importance']:.6f})")
    print(f"\n  ➜ These drifts are PRIMARY causes of model performance degradation")
else:
    print("\n  ✅ Drifted features have LOW importance")
    print("  ➜ Model should be relatively robust to detected drift")

# ============================================================================
# STEP 7: Generate Visualizations
# ============================================================================
print("\n" + "="*70)
print("STEP 7: GENERATING VISUALIZATIONS")
print("="*70)

fig, axes = plt.subplots(2, 1, figsize=(12, 10))
fig.suptitle('Root Cause Analysis - Feature Importance & Drift Impact', 
             fontsize=16, fontweight='bold')

# Plot 1: Top 20 Features with Drift Highlighting
ax = axes[0]
top_n = 20
top_features = importance_df.head(top_n)

colors = ['#FF6B6B' if f in drifted_features else '#4ECDC4' 
          for f in top_features['Feature']]
bars = ax.barh(range(len(top_features)), top_features['Importance'], 
               color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)

ax.set_yticks(range(len(top_features)))
ax.set_yticklabels(top_features['Feature'], fontsize=10)
ax.set_xlabel('Feature Importance (from Random Forest)', fontweight='bold', fontsize=11)
ax.set_title('Top 20 Most Important Features - Drifted Features Highlighted', fontsize=12)
ax.invert_yaxis()
ax.grid(True, alpha=0.3, axis='x')

# Add legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#FF6B6B', alpha=0.8, label='Drifted Features', edgecolor='black'),
                   Patch(facecolor='#4ECDC4', alpha=0.8, label='Normal Features', edgecolor='black')]
ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

# Add value labels
for i, (_, row) in enumerate(top_features.iterrows()):
    ax.text(row['Importance'], i, f" {row['Importance']:.4f}", 
            va='center', fontsize=8, fontweight='bold')

# Plot 2: Drifted Features Importance Breakdown
ax = axes[1]

if drifted_with_importance:
    drifted_sorted = sorted(drifted_with_importance, 
                           key=lambda x: x['Importance'], 
                           reverse=True)
    features = [d['Feature'] for d in drifted_sorted]
    importance = [d['Importance'] for d in drifted_sorted]
    
    colors_drift = ['#FF6B6B' if imp > 0.05 else '#FFD93D' if imp > 0.01 else '#6BCB77' 
                    for imp in importance]
    
    bars = ax.bar(features, importance, color=colors_drift, 
                  alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax.set_ylabel('Importance Score', fontweight='bold', fontsize=11)
    ax.set_title('Feature Importance of DRIFTED Features - ROOT CAUSE IMPACT', 
                fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add horizontal line for medium importance threshold
    ax.axhline(y=0.05, color='red', linestyle='--', linewidth=2, alpha=0.7, 
              label='Critical Threshold (0.05)')
    
    # Add value labels on bars
    for bar, val in zip(bars, importance):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{val:.4f}',
               ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    ax.legend(fontsize=9)
else:
    ax.text(0.5, 0.5, 'No drifted features found', 
           ha='center', va='center', transform=ax.transAxes, fontsize=14)

plt.tight_layout()
plt.savefig('root_cause_analysis.png', dpi=300, bbox_inches='tight')
print("✅ Visualization saved as: root_cause_analysis.png")

# ============================================================================
# STEP 8: Final Summary and Recommendations
# ============================================================================
print("\n" + "="*70)
print("ROOT CAUSE ANALYSIS SUMMARY & RECOMMENDATIONS")
print("="*70)

print("\n📋 EXECUTIVE SUMMARY:")
print(f"\n1. Total Features Analyzed: {len(importance_df)}")
print(f"2. Features with Drift: {len(drifted_features)}")
print(f"3. Drifted Features with HIGH Importance: {len(high_impact_drifts)}")

print(f"\n4. Top 3 Most Important Features:")
for idx, (_, row) in enumerate(importance_df.head(3).iterrows(), 1):
    drift_status = "🔴 DRIFTED" if row['Feature'] in drifted_features else "✅ STABLE"
    print(f"   #{idx}. {row['Feature']:6s} (Importance: {row['Importance']:.6f}) {drift_status}")

print("\n5. 🎯 KEY FINDINGS:")
if len(high_impact_drifts) > 0:
    print(f"   ⚠️  ALERT: Critical drift detected in important features!")
    for item in high_impact_drifts:
        print(f"      • {item['Feature']} is BOTH drifted AND highly important")
    print(f"\n   Impact: Model performance WILL degrade significantly")
    print(f"   Action: Requires IMMEDIATE retraining")
else:
    print(f"   ✅ Drifted features have LOW importance")
    print(f"\n   Impact: Model performance should remain stable")
    print(f"   Action: Continuous monitoring recommended, retraining not urgent")

print("\n6. 📌 RECOMMENDED ACTIONS:")
print("   • Monitor Amount, V1, V2, V3 in production")
print("   • Set up alerts for drift in top-10 important features")
print("   • Plan monthly retraining cycles")
print("   • Implement automated drift detection (already done! ✅)")

print("\n" + "="*70)
print("ROOT CAUSE ANALYSIS COMPLETE!")
print("="*70)
