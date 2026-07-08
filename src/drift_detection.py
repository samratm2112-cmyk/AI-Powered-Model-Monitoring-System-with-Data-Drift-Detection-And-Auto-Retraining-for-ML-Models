import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# ============================================================================
# STEP 1: Load Data
# ============================================================================
data = pd.read_csv("data/creditcard.csv")

print("="*70)
print("STEP 1: LOADING DATA")
print("="*70)
print(f"Total data shape: {data.shape}")

# ============================================================================
# STEP 2: Create Old Data (Reference)
# ============================================================================
old_data = data[:10000].copy()
print(f"\nOld data (reference) shape: {old_data.shape}")
print(f"Old data - Amount Mean: {old_data['Amount'].mean():.2f}")

# ============================================================================
# STEP 3: Create New Data and Apply Drift
# ============================================================================
new_data = data[10000:20000].copy()
print(f"\nNew data (before drift) shape: {new_data.shape}")
print(f"New data - Amount Mean (before): {new_data['Amount'].mean():.2f}")

# Apply SAME DRIFT as Step 5
new_data["Amount"] = new_data["Amount"] * 3
new_data["V1"] = new_data["V1"] * 1.5
new_data["V2"] = new_data["V2"] * 1.5
new_data["V3"] = new_data["V3"] + 1

print(f"\nNew data - Amount Mean (after drift): {new_data['Amount'].mean():.2f}")
print("\n✅ DRIFT APPLIED:")
print("   - Amount × 3")
print("   - V1 × 1.5")
print("   - V2 × 1.5")
print("   - V3 + 1")

# ============================================================================
# STEP 4: Run Drift Detection (Using Statistical Tests)
# ============================================================================
print("\n" + "="*70)
print("STEP 2: RUNNING DRIFT DETECTION")
print("="*70)
print("Comparing old_data vs new_data using Kolmogorov-Smirnov Test...\n")

# Statistical drift detection
drift_results = {}
features_to_check = [col for col in old_data.columns if col not in ['Time', 'Class']]

drift_detected_count = 0

for feature in features_to_check:
    # Kolmogorov-Smirnov Test
    statistic, p_value = stats.ks_2samp(old_data[feature], new_data[feature])
    
    # If p-value < 0.05, drift is detected
    is_drift = p_value < 0.05
    
    drift_results[feature] = {
        'ks_statistic': statistic,
        'p_value': p_value,
        'drift_detected': is_drift,
        'mean_old': old_data[feature].mean(),
        'mean_new': new_data[feature].mean(),
        'std_old': old_data[feature].std(),
        'std_new': new_data[feature].std()
    }
    
    if is_drift:
        drift_detected_count += 1

# ============================================================================
# STEP 5: Display Results
# ============================================================================
print("="*70)
print("STEP 3: DRIFT DETECTION RESULTS")
print("="*70)

print(f"\n📊 OVERALL DRIFT STATUS: {'✅ DRIFT DETECTED' if drift_detected_count > 0 else '❌ NO DRIFT'}")
print(f"\nFeatures with drift: {drift_detected_count} / {len(features_to_check)}")

print("\n" + "="*70)
print("FEATURE-WISE DRIFT ANALYSIS")
print("="*70)

for feature in list(drift_results.keys())[:10]:  # Show first 10
    result = drift_results[feature]
    status = "✅ DRIFT" if result['drift_detected'] else "❌ NO DRIFT"
    
    print(f"\n{feature}:")
    print(f"  Status: {status}")
    print(f"  KS Statistic: {result['ks_statistic']:.4f}")
    print(f"  P-value: {result['p_value']:.6f}")
    print(f"  Mean (Old | New): {result['mean_old']:.4f} | {result['mean_new']:.4f}")
    print(f"  Std (Old | New): {result['std_old']:.4f} | {result['std_new']:.4f}")

# ============================================================================
# STEP 6: Create Visualization
# ============================================================================
print("\n" + "="*70)
print("STEP 4: GENERATING VISUALIZATIONS")
print("="*70)

# Create comparison plots for top drifted features
drifted_features = [f for f in drift_results if drift_results[f]['drift_detected']]

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('Data Drift Detection - Distribution Comparison', fontsize=16, fontweight='bold')

# Plot Amount (biggest drift)
ax = axes[0, 0]
ax.hist(old_data['Amount'], bins=50, alpha=0.6, label='Old Data', color='blue')
ax.hist(new_data['Amount'], bins=50, alpha=0.6, label='New Data (Drifted)', color='red')
ax.set_title('Amount Distribution (× 3 Multiplied)')
ax.set_xlabel('Amount')
ax.set_ylabel('Frequency')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot V1
ax = axes[0, 1]
ax.hist(old_data['V1'], bins=50, alpha=0.6, label='Old Data', color='blue')
ax.hist(new_data['V1'], bins=50, alpha=0.6, label='New Data (Drifted)', color='red')
ax.set_title('V1 Distribution (× 1.5 Multiplied)')
ax.set_xlabel('V1')
ax.set_ylabel('Frequency')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot V2
ax = axes[1, 0]
ax.hist(old_data['V2'], bins=50, alpha=0.6, label='Old Data', color='blue')
ax.hist(new_data['V2'], bins=50, alpha=0.6, label='New Data (Drifted)', color='red')
ax.set_title('V2 Distribution (× 1.5 Multiplied)')
ax.set_xlabel('V2')
ax.set_ylabel('Frequency')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot V3
ax = axes[1, 1]
ax.hist(old_data['V3'], bins=50, alpha=0.6, label='Old Data', color='blue')
ax.hist(new_data['V3'], bins=50, alpha=0.6, label='New Data (Drifted)', color='red')
ax.set_title('V3 Distribution (+ 1 Added)')
ax.set_xlabel('V3')
ax.set_ylabel('Frequency')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('drift_report.png', dpi=300, bbox_inches='tight')
print("✅ Visualization saved as: drift_report.png")

# ============================================================================
# STEP 7: Summary
# ============================================================================
print("\n" + "="*70)
print("DRIFT DETECTION COMPLETE!")
print("="*70)

print(f"\n📊 Summary:")
print(f"  ✅ Features with drift detected: {drift_detected_count}")
print(f"  ✅ Drift detection method: Kolmogorov-Smirnov Test")
print(f"  ✅ Visualization saved: drift_report.png")
print(f"\n🎯 Interpretation:")
print(f"  • KS Statistic > 0.1 and P-value < 0.05 = Significant drift")
print(f"  • P-value indicates probability that distributions are same")
print(f"  • P-value < 0.05 = Strong evidence of drift")
