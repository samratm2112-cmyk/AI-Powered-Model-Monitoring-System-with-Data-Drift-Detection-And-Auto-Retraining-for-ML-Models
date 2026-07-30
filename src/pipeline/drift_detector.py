"""
🔎 STATISTICAL DRIFT DETECTOR MODULE
Executes Kolmogorov-Smirnov (KS) two-sample tests comparing batch features vs baseline reference.
Ignores non-stationary timestamp features (e.g., 'Time') from statistical drift calculations.
"""

from scipy.stats import ks_2samp
import pandas as pd

class KSDriftDetector:
    """Detects feature distribution drift using two-sample Kolmogorov-Smirnov test."""
    
    def __init__(self, reference_data, alpha=0.05, exclude_features=None):
        self.reference_data = reference_data.copy()
        self.alpha = alpha
        # Exclude monotonically increasing timestamps ('Time') from statistical drift checks
        self.exclude_features = set(exclude_features) if exclude_features is not None else {"Time"}
        
    def detect_drift(self, X_batch):
        """
        Runs KS-test for every feature in batch against baseline reference data (excluding timestamp/ID features).
        Returns drift summary dict.
        """
        drift_results = {}
        p_values = {}
        
        for col in self.reference_data.columns:
            # Skip excluded non-stationary features like 'Time'
            if col in self.exclude_features:
                continue
                
            if col in X_batch.columns:
                stat, pval = ks_2samp(self.reference_data[col], X_batch[col])
                p_values[col] = float(pval)
                drift_results[col] = bool(pval < self.alpha)
                
        drifted_features = [col for col, drifted in drift_results.items() if drifted]
        num_drifted = len(drifted_features)
        drift_detected = num_drifted > 0
        
        return {
            'drift_detected': drift_detected,
            'num_drifted': num_drifted,
            'total_features': len(drift_results),
            'drifted_features': drifted_features,
            'p_values': p_values,
            'excluded_features': list(self.exclude_features)
        }
