import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

class GlobalLocalEnsemble:
    """
    Global-Local Ensemble (Hybrid Classifier) for ML Drift Adaptability.
    
    Architecture:
    - Global Model (Veteran Guard): Static model trained on baseline historical data (Long-term memory).
    - Local Model (Rookie Guard): Adaptive model trained on recent drifted data batches using sliding window (Short-term adaptability).
    - Soft Voting Fusion: Fuses probabilities using a weighted average.
    """
    
    def __init__(self, global_weight=0.7, threshold=0.3, n_estimators=100, window_size=5000, random_state=42):
        """
        Args:
            global_weight: Weight assigned to Global Model (0.0 to 1.0). Local weight will be 1 - global_weight.
            threshold: Classification decision threshold for positive class probability.
            n_estimators: Number of decision trees in RandomForest models.
            window_size: Maximum samples retained for Local Model training (Sliding window).
            random_state: Random state seed.
        """
        self.global_weight = global_weight
        self.local_weight = 1.0 - global_weight
        self.threshold = threshold
        self.n_estimators = n_estimators
        self.window_size = window_size
        self.random_state = random_state
        
        self.model_global = None
        self.model_local = None
        self.local_buffer_X = None
        self.local_buffer_y = None
        self.is_global_fitted = False
        self.is_local_fitted = False

    def fit_global(self, X_train, y_train):
        """Train the static Global Model on historical baseline data."""
        self.model_global = RandomForestClassifier(
            n_estimators=self.n_estimators,
            random_state=self.random_state
        )
        self.model_global.fit(X_train, y_train)
        self.is_global_fitted = True
        return self

    def fit_local(self, X_new, y_new):
        """
        Train/Update the Local Model using a sliding window buffer of recent data.
        
        Args:
            X_new: New incoming feature DataFrame/Array.
            y_new: New incoming target Series/Array.
        """
        # Convert to pandas DataFrame/Series if needed
        if not isinstance(X_new, pd.DataFrame):
            X_new = pd.DataFrame(X_new)
        if not isinstance(y_new, pd.Series):
            y_new = pd.Series(y_new)
            
        # Append to sliding window buffer
        if self.local_buffer_X is None:
            self.local_buffer_X = X_new.copy()
            self.local_buffer_y = y_new.copy()
        else:
            self.local_buffer_X = pd.concat([self.local_buffer_X, X_new], ignore_index=True)
            self.local_buffer_y = pd.concat([self.local_buffer_y, y_new], ignore_index=True)
            
        # Enforce sliding window capacity (Keep only last `window_size` samples)
        if len(self.local_buffer_X) > self.window_size:
            self.local_buffer_X = self.local_buffer_X.iloc[-self.window_size:].reset_index(drop=True)
            self.local_buffer_y = self.local_buffer_y.iloc[-self.window_size:].reset_index(drop=True)
            
        # Train fresh Local Model on sliding window buffer
        self.model_local = RandomForestClassifier(
            n_estimators=self.n_estimators,
            random_state=self.random_state
        )
        self.model_local.fit(self.local_buffer_X, self.local_buffer_y)
        self.is_local_fitted = True
        return self

    def predict_proba(self, X):
        """Calculate weighted soft-voting probability fusion."""
        if not self.is_global_fitted:
            raise ValueError("Global model must be fitted before running predictions.")
            
        proba_global = self.model_global.predict_proba(X)
        
        # Fall back to 100% Global Model if Local Model is not fitted yet
        if not self.is_local_fitted:
            return proba_global
            
        proba_local = self.model_local.predict_proba(X)
        
        # Ensure class shape alignment
        if proba_global.shape != proba_local.shape:
            # Fallback if class set differs in small local batch
            return proba_global
            
        fused_proba = (self.global_weight * proba_global) + (self.local_weight * proba_local)
        return fused_proba

    def predict(self, X):
        """Predict binary class labels based on classification threshold."""
        proba = self.predict_proba(X)
        if proba.shape[1] == 2:
            return (proba[:, 1] >= self.threshold).astype(int)
        return np.argmax(proba, axis=1)

    def get_status(self):
        """Returns ensemble status dictionary."""
        return {
            'global_fitted': self.is_global_fitted,
            'local_fitted': self.is_local_fitted,
            'global_weight': self.global_weight,
            'local_weight': self.local_weight,
            'local_buffer_size': len(self.local_buffer_X) if self.local_buffer_X is not None else 0,
            'threshold': self.threshold
        }
