"""
📈 PERFORMANCE EVALUATOR MODULE
Calculates classification metrics (Accuracy, Precision, Recall, F1) for models and ensembles.
"""

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

class ModelEvaluator:
    """Evaluates classification model / ensemble performance metrics."""
    
    @staticmethod
    def evaluate(model, X_batch, y_batch, stage="EVALUATION"):
        """
        Runs model predictions on batch and computes standard metrics.
        Returns metrics dict and prediction array.
        """
        y_pred = model.predict(X_batch)
        
        metrics = {
            'accuracy': float(accuracy_score(y_batch, y_pred)),
            'precision': float(precision_score(y_batch, y_pred, average='weighted', zero_division=0)),
            'recall': float(recall_score(y_batch, y_pred, average='weighted', zero_division=0)),
            'f1': float(f1_score(y_batch, y_pred, average='weighted', zero_division=0))
        }
        
        return metrics, y_pred
