"""
🔧 PREPROCESSOR TRANSFORMER MODULE
Scales Amount feature consistently using fitted baseline StandardScaler.
"""

from sklearn.preprocessing import StandardScaler

class FeaturePreprocessor:
    """Handles feature scaling for baseline training and streaming batches."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.is_fitted = False
        
    def fit_transform_baseline(self, X_train):
        """Fits scaler on baseline training set and transforms Amount."""
        X_scaled = X_train.copy()
        X_scaled["Amount"] = self.scaler.fit_transform(X_train[["Amount"]])
        self.is_fitted = True
        return X_scaled
        
    def transform_batch(self, X_batch):
        """Transforms incoming batch using fitted baseline scaler."""
        if not self.is_fitted:
            raise ValueError("Preprocessor must be fitted on baseline training data first.")
        X_scaled = X_batch.copy()
        X_scaled["Amount"] = self.scaler.transform(X_batch[["Amount"]])
        return X_scaled
