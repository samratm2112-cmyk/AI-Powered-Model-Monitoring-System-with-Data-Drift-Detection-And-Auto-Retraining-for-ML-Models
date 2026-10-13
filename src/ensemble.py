"""
🧠 TWO-STAGE HYBRID PIPELINE & GLOBAL-LOCAL ENSEMBLE MODULE
Architecture:
- Stage 1 (Anomaly Filter): Unsupervised Isolation Forest learning normal transaction behavior.
  Flags distribution weirdness and zero-day anomalies.
- Stage 2 (Expert Classifier): High-performance supervised XGBoost classifier.
  Processes flagged transactions to verify if they are actually fraud.
- GlobalLocalEnsemble: Hybrid fusion combining static long-term historical memory
  with adaptive short-term sliding window updates.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


class TwoStagePipeline:
    """
    Two-Stage Hybrid Anomaly Filter & Expert Classifier Pipeline.
    
    Stage 1 (Anomaly Filter - Unsupervised):
    - Models the distribution of normal transactions using an Isolation Forest.
    - Filters out normal traffic and flags distribution weirdness/zero-day anomalies.
    
    Stage 2 (Expert Classifier - Supervised):
    - Employs an XGBoost classifier trained on known fraud patterns.
    - Evaluates transactions flagged by Stage 1 to confirm fraud classification.
    """
    
    def __init__(
        self,
        contamination=0.08,
        n_estimators_stage1=100,
        n_estimators_stage2=100,
        max_depth=5,
        learning_rate=0.1,
        threshold=0.3,
        random_state=42
    ):
        self.contamination = contamination
        self.n_estimators_stage1 = n_estimators_stage1
        self.n_estimators_stage2 = n_estimators_stage2
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.threshold = threshold
        self.random_state = random_state
        
        self.stage1_filter = None
        self.stage2_classifier = None
        self.is_fitted = False

    def fit(self, X, y):
        """
        Fits both pipeline stages:
        1. Stage 1 (Unsupervised): Trains Isolation Forest on normal transactions (y == 0).
        2. Stage 2 (Supervised): Trains XGBoost classifier on all labeled transactions.
        """
        X_df = X if isinstance(X, pd.DataFrame) else pd.DataFrame(X)
        y_sr = y if isinstance(y, pd.Series) else pd.Series(y)
        
        # Stage 1: Unsupervised Isolation Forest learning normal behavior
        normal_mask = (y_sr == 0)
        X_normal = X_df[normal_mask] if normal_mask.sum() > 50 else X_df
        
        self.stage1_filter = IsolationForest(
            contamination=self.contamination,
            n_estimators=self.n_estimators_stage1,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.stage1_filter.fit(X_normal)
        
        # Stage 2: Supervised XGBoost classifier
        self.stage2_classifier = XGBClassifier(
            n_estimators=self.n_estimators_stage2,
            max_depth=self.max_depth,
            learning_rate=self.learning_rate,
            random_state=self.random_state,
            eval_metric='logloss',
            n_jobs=-1
        )
        self.stage2_classifier.fit(X_df, y_sr)
        
        self.is_fitted = True
        return self

    def predict_proba(self, X):
        """
        Two-stage prediction flow:
        - Stage 1 flags anomalous transactions.
        - Stage 2 evaluates flagged transactions to assess fraud likelihood.
        - Extreme zero-day anomalies receive an anomaly boost so novel attacks are caught.
        """
        if not self.is_fitted:
            raise ValueError("TwoStagePipeline must be fitted before predict_proba.")
            
        X_df = X if isinstance(X, pd.DataFrame) else pd.DataFrame(X)
        n_samples = len(X_df)
        
        # Stage 1: Anomaly Filtering
        anomaly_scores = self.stage1_filter.decision_function(X_df)
        is_anomaly = (anomaly_scores < 0.05)
        
        proba = np.zeros((n_samples, 2))
        proba[:, 0] = 1.0  # Default to normal (0)
        
        if np.any(is_anomaly):
            X_flagged = X_df[is_anomaly]
            stage2_probs = self.stage2_classifier.predict_proba(X_flagged)
            
            # Anomaly intensity metric for novel zero-day attacks
            anomaly_intensity = np.clip(-anomaly_scores[is_anomaly] / 0.10, 0.0, 1.0)
            
            # Fuse supervised confidence with anomaly score boost
            boosted_fraud_prob = np.maximum(stage2_probs[:, 1], 0.35 * anomaly_intensity)
            boosted_fraud_prob = np.clip(boosted_fraud_prob, 0.0, 1.0)
            
            proba[is_anomaly, 1] = boosted_fraud_prob
            proba[is_anomaly, 0] = 1.0 - boosted_fraud_prob
            
        return proba

    def predict(self, X):
        """Binary predictions using classification threshold (default: 0.3)."""
        proba = self.predict_proba(X)
        return (proba[:, 1] >= self.threshold).astype(int)

    @property
    def feature_importances_(self):
        """Expose Stage 2 XGBoost feature importances for analysis & backward compatibility."""
        if self.stage2_classifier is not None and hasattr(self.stage2_classifier, 'feature_importances_'):
            return self.stage2_classifier.feature_importances_
        return None


class GlobalLocalEnsemble:
    """
    Global-Local Hybrid Ensemble managing Two-Stage Pipelines.
    
    Architecture:
    - Global Model (Veteran Expert): Static Two-Stage Pipeline trained on historical data.
    - Local Model (Rookie Expert): Adaptive Two-Stage Pipeline updated via sliding window on recent stream.
    - Probability Fusion: Weighted average of Global and Local predictions.
    """
    
    def __init__(
        self,
        global_weight=0.7,
        threshold=0.3,
        n_estimators=100,
        window_size=5000,
        random_state=42
    ):
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
        """Train static Global Two-Stage Pipeline on historical baseline data."""
        self.model_global = TwoStagePipeline(
            contamination=0.08,
            n_estimators_stage1=self.n_estimators,
            n_estimators_stage2=self.n_estimators,
            threshold=self.threshold,
            random_state=self.random_state
        )
        self.model_global.fit(X_train, y_train)
        self.is_global_fitted = True
        return self

    def fit_local(self, X_new, y_new):
        """
        Train/Update Local Two-Stage Pipeline on sliding window buffer of recent data.
        """
        if not isinstance(X_new, pd.DataFrame):
            X_new = pd.DataFrame(X_new)
        if not isinstance(y_new, pd.Series):
            y_new = pd.Series(y_new)
            
        if self.local_buffer_X is None:
            self.local_buffer_X = X_new.copy()
            self.local_buffer_y = y_new.copy()
        else:
            self.local_buffer_X = pd.concat([self.local_buffer_X, X_new], ignore_index=True)
            self.local_buffer_y = pd.concat([self.local_buffer_y, y_new], ignore_index=True)
            
        # Enforce sliding window capacity
        if len(self.local_buffer_X) > self.window_size:
            self.local_buffer_X = self.local_buffer_X.iloc[-self.window_size:].reset_index(drop=True)
            self.local_buffer_y = self.local_buffer_y.iloc[-self.window_size:].reset_index(drop=True)
            
        self.model_local = TwoStagePipeline(
            contamination=0.08,
            n_estimators_stage1=self.n_estimators,
            n_estimators_stage2=self.n_estimators,
            threshold=self.threshold,
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
        
        if not self.is_local_fitted:
            return proba_global
            
        proba_local = self.model_local.predict_proba(X)
        
        if proba_global.shape != proba_local.shape:
            return proba_global
            
        fused_proba = (self.global_weight * proba_global) + (self.local_weight * proba_local)
        return fused_proba

    def predict(self, X):
        """Predict binary class labels based on classification threshold (default: 0.3)."""
        proba = self.predict_proba(X)
        if proba.shape[1] == 2:
            return (proba[:, 1] >= self.threshold).astype(int)
        return np.argmax(proba, axis=1)

    def get_status(self):
        """Returns ensemble status dictionary."""
        return {
            'architecture': 'Two-Stage Hybrid Pipeline (Stage 1: IsolationForest + Stage 2: XGBoost)',
            'global_fitted': self.is_global_fitted,
            'local_fitted': self.is_local_fitted,
            'global_weight': self.global_weight,
            'local_weight': self.local_weight,
            'local_buffer_size': len(self.local_buffer_X) if self.local_buffer_X is not None else 0,
            'threshold': self.threshold
        }
