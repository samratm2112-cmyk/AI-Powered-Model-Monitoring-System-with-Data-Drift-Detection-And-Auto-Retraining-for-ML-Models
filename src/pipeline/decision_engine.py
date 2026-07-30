"""
🤔 DECISION ENGINE MODULE
Automated controller evaluating statistical drift alerts and performance degradation criteria.
Implements a 3-tier production decision policy (GREEN, YELLOW, RED).
"""

class RetrainingDecisionEngine:
    """
    Evaluates whether to trigger Local Model retraining on incoming stream batches
    using a production-grade 3-tier policy (GREEN, YELLOW, RED).
    """
    
    def __init__(self, accuracy_threshold=0.99, min_drift_features_threshold=3):
        """
        Args:
            accuracy_threshold: Minimum acceptable model accuracy (e.g., 0.99).
            min_drift_features_threshold: Minimum shifted features required for 'significant drift' (default: 3).
        """
        self.accuracy_threshold = accuracy_threshold
        self.min_drift_features_threshold = min_drift_features_threshold
        
    def evaluate_decision(self, drift_result, current_accuracy):
        """
        Determines the decision level (GREEN, YELLOW, RED) and whether retraining is required.
        
        Policy Rules:
        - GREEN: 0 drifted features AND accuracy >= threshold -> No Retraining.
        - YELLOW: 1 to 2 drifted features (minor variation) AND accuracy >= threshold -> Warning Logged, No Retraining.
        - RED: >= 3 drifted features (significant drift) OR accuracy < threshold -> Local Model Retraining Triggered.
        """
        num_drifted = drift_result['num_drifted']
        accuracy_degraded = current_accuracy < self.accuracy_threshold
        significant_drift = num_drifted >= self.min_drift_features_threshold
        
        reasons = []
        
        if significant_drift or accuracy_degraded:
            # RED LEVEL: Trigger Retraining
            decision_level = "RED"
            should_retrain = True
            if significant_drift:
                reasons.append(f"Significant drift in {num_drifted} features (>= threshold {self.min_drift_features_threshold})")
            if accuracy_degraded:
                reasons.append(f"Accuracy ({current_accuracy:.4f}) dropped below threshold ({self.accuracy_threshold:.4f})")
                
        elif num_drifted > 0 and not accuracy_degraded:
            # YELLOW LEVEL: Minor Variation - Warning Only, No Retraining
            decision_level = "YELLOW"
            should_retrain = False
            reasons.append(f"Minor variation in {num_drifted} features (< threshold {self.min_drift_features_threshold}) - Accuracy ({current_accuracy:.4f}) stable")
            
        else:
            # GREEN LEVEL: Fully Stable System - No Retraining
            decision_level = "GREEN"
            should_retrain = False
            reasons.append("System stable: 0 features drifted and accuracy is above threshold")
            
        return {
            'decision_level': decision_level,
            'should_retrain': should_retrain,
            'drift_detected': drift_result['drift_detected'],
            'significant_drift': significant_drift,
            'accuracy_degraded': accuracy_degraded,
            'num_drifted_features': num_drifted,
            'current_accuracy': current_accuracy,
            'accuracy_threshold': self.accuracy_threshold,
            'reasons': reasons
        }
