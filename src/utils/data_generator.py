"""
📦 DATA GENERATOR UTILITY
Generates synthetic multi-pattern Credit Card dataset (Types A, B, C historical + Type D production stream).
"""

import os
import numpy as np
import pandas as pd
import config

def ensure_dataset_exists(file_path=config.DATA_FILE, n_samples=30000, force_generate=False):
    """Generates synthetic Credit Card dataset enriched with historical and production fraud patterns."""
    if os.path.exists(file_path) and not force_generate:
        return file_path

    print(f"📦 Generating Credit Card dataset with multi-pattern fraud ({n_samples} rows)...")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    np.random.seed(config.RANDOM_STATE)
    
    time_col = np.sort(np.random.uniform(0, 172800, n_samples))
    amount_col = np.random.exponential(scale=88.0, size=n_samples)
    v_cols = {f"V{i}": np.random.normal(loc=0.0, scale=1.0, size=n_samples) for i in range(1, 29)}
    
    n_fraud = int(n_samples * 0.02)
    fraud_indices = np.random.choice(n_samples, size=n_fraud, replace=False)
    classes = np.zeros(n_samples, dtype=int)
    classes[fraud_indices] = 1
    
    type_a, type_b, type_c = np.array_split(fraud_indices, 3)
    
    # Pattern A: High Amount
    amount_col[type_a] += 550.0
    v_cols["V1"][type_a] -= 4.5
    v_cols["V3"][type_a] -= 5.0
    
    # Pattern B: Low Amount Micro Fraud
    amount_col[type_b] = np.random.uniform(1.0, 15.0, size=len(type_b))
    v_cols["V2"][type_b] += 4.0
    v_cols["V4"][type_b] += 3.5
    
    # Pattern C: Velocity Fraud
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
    print(f"✅ Dataset generated at: {file_path}")
    return file_path
