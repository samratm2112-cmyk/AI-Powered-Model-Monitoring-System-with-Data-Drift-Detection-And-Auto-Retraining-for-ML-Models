"""
📥 DATA INGESTION & BATCH STREAM PARTITIONER
Splits raw incoming dataset into historical training set and sequential production batches.
Simulates a realistic production environment with a mixture of normal and drifted batches.
"""

import pandas as pd
import numpy as np

class BatchStreamIngestion:
    """Handles data loading and partition into configurable production batches."""
    
    def __init__(self, data_path, train_size=20000, batch_size=1000):
        self.data_path = data_path
        self.train_size = train_size
        self.batch_size = batch_size
        self.df = None
        self.X_train = None
        self.y_train = None
        self.production_df = None
        self.num_batches = 0
        
    def load_and_split(self):
        """Loads dataset and splits into historical training set and production stream."""
        self.df = pd.read_csv(self.data_path)
        
        # Historical baseline data
        train_df = self.df.iloc[:self.train_size].copy()
        self.X_train = train_df.drop(columns=["Class"])
        self.y_train = train_df["Class"]
        
        # Production stream (remaining records)
        self.production_df = self.df.iloc[self.train_size:].copy()
        self.num_batches = int(np.ceil(len(self.production_df) / self.batch_size))
        
        return self.X_train, self.y_train
        
    def get_batch_iterator(self, apply_drift=True):
        """
        Yields sequential batches (X_batch, y_batch, batch_id, metadata).
        Simulates a realistic production schedule: mixture of normal and drifted batches.
        """
        for i in range(self.num_batches):
            start_idx = i * self.batch_size
            end_idx = min((i + 1) * self.batch_size, len(self.production_df))
            
            batch_df = self.production_df.iloc[start_idx:end_idx].copy()
            batch_id = i + 1
            drift_type = "Normal"
            
            if apply_drift:
                if batch_id in [1, 2, 3, 5, 7, 9]:
                    # Completely Normal Batches (No Drift Injected)
                    drift_type = "Normal"
                elif batch_id == 4:
                    # Mild Distribution Drift
                    drift_type = "Mild Drift"
                    batch_df["Amount"] = batch_df["Amount"] * 1.8
                    batch_df["V1"] = batch_df["V1"] * 1.2
                elif batch_id == 6:
                    # Moderate Distribution Drift
                    drift_type = "Moderate Drift"
                    batch_df["Amount"] = batch_df["Amount"] * 2.5
                    batch_df["V1"] = batch_df["V1"] * 1.5
                    batch_df["V2"] = batch_df["V2"] * 1.5
                elif batch_id == 8:
                    # Novel Fraud Pattern D Attack Vector
                    drift_type = "Novel Fraud Pattern D"
                    fraud_mask = (batch_df["Class"] == 1)
                    batch_df.loc[fraud_mask, "V11"] += 5.0
                    batch_df.loc[fraud_mask, "V12"] -= 6.0
                    batch_df.loc[fraud_mask, "V14"] -= 5.5
                elif batch_id == 10:
                    # Strong Distribution Drift + Novel Fraud Attack
                    drift_type = "Strong Drift + Novel Fraud"
                    batch_df["Amount"] = batch_df["Amount"] * 3.5
                    batch_df["V1"] = batch_df["V1"] * 1.8
                    batch_df["V3"] = batch_df["V3"] + 1.5
                    fraud_mask = (batch_df["Class"] == 1)
                    batch_df.loc[fraud_mask, "V11"] += 5.0
                    batch_df.loc[fraud_mask, "V14"] -= 5.5

            X_batch = batch_df.drop(columns=["Class"])
            y_batch = batch_df["Class"]
            
            metadata = {
                'batch_id': batch_id,
                'start_idx': start_idx,
                'end_idx': end_idx,
                'size': len(batch_df),
                'fraud_count': int(y_batch.sum()),
                'simulated_drift_type': drift_type
            }
            
            yield X_batch, y_batch, metadata
