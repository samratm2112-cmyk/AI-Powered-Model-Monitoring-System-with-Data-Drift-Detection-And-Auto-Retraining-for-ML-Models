"""
🔍 DATA VALIDATOR MODULE
Validates batch schema, missing values, column count, and data integrity.
"""

import pandas as pd

class DataValidator:
    """Validates schema and data quality for incoming production batches."""
    
    def __init__(self, expected_features):
        self.expected_features = list(expected_features)
        
    def validate(self, X_batch):
        """
        Validates batch features.
        Returns (is_valid, validation_details).
        """
        errors = []
        
        # Check column count & match
        missing_cols = set(self.expected_features) - set(X_batch.columns)
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")
            
        extra_cols = set(X_batch.columns) - set(self.expected_features)
        if extra_cols:
            errors.append(f"Unexpected columns: {extra_cols}")
            
        # Check missing values
        null_count = X_batch.isnull().sum().sum()
        if null_count > 0:
            errors.append(f"Found {null_count} null values in batch")
            
        is_valid = len(errors) == 0
        return is_valid, {
            'is_valid': is_valid,
            'errors': errors,
            'num_samples': len(X_batch),
            'num_features': X_batch.shape[1]
        }
