"""
🧠 SHAP EXPLAINABILITY SERVICE
Computes local feature attributions using shap.TreeExplainer on the Stage 2 Classifier.
Returns JSON-serializable payloads for dynamic interactive UI rendering.
"""

import os
import sys
import pickle
import pandas as pd
import numpy as np
import shap
from sklearn.preprocessing import StandardScaler
from fastapi import HTTPException
from backend.app import config

# Ensure src is in sys.path so pickled models can resolve
_src_dir = os.path.join(config.PROJECT_ROOT, "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)


class ExplainabilityService:
    """Service providing SHAP explanations for transactions."""

    _df = None
    _model = None
    _scaler = None
    _explainer = None
    _samples = None

    @classmethod
    def _init_resources(cls):
        """Lazy-loads and caches dataset, model, scaler, and SHAP TreeExplainer."""
        if cls._explainer is not None and cls._df is not None:
            return

        # 1. Load dataset
        data_path = os.path.join(config.PROJECT_ROOT, "data", "creditcard.csv")
        if not os.path.exists(data_path):
            raise HTTPException(status_code=404, detail="Dataset not found at data/creditcard.csv")

        cls._df = pd.read_csv(data_path)
        
        # 2. Setup baseline Amount scaler
        cls._scaler = StandardScaler()
        cls._scaler.fit(cls._df[["Amount"]])

        # 3. Load deployed model
        model_path = os.path.join(config.PROJECT_ROOT, "models", "deployed_model.pkl")
        if not os.path.exists(model_path):
            # Fallback to model_latest.pkl
            model_path = os.path.join(config.PROJECT_ROOT, "models", "model_latest.pkl")

        if os.path.exists(model_path):
            try:
                with open(model_path, "rb") as f:
                    loaded_obj = pickle.load(f)
                    
                # If GlobalLocalEnsemble, extract the Stage 2 XGBoost expert classifier
                if hasattr(loaded_obj, "model_global") and hasattr(loaded_obj.model_global, "stage2_classifier"):
                    cls._model = loaded_obj.model_global.stage2_classifier
                elif hasattr(loaded_obj, "stage2_classifier"):
                    cls._model = loaded_obj.stage2_classifier
                else:
                    cls._model = loaded_obj
            except Exception as e:
                print(f"Warning: Failed to load deployed model for SHAP: {e}")
                cls._model = None

        # 4. If no model found or unpickling failed, train a lightweight fallback classifier for SHAP
        if cls._model is None:
            from sklearn.ensemble import RandomForestClassifier
            sample_df = cls._df.sample(n=min(5000, len(cls._df)), random_state=42)
            X_temp = sample_df.drop("Class", axis=1).copy()
            X_temp["Amount"] = cls._scaler.transform(X_temp[["Amount"]])
            y_temp = sample_df["Class"]
            cls._model = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
            cls._model.fit(X_temp, y_temp)

        # 5. Initialize shap.TreeExplainer
        cls._explainer = shap.TreeExplainer(cls._model)

        # 6. Precompute authentic sample transactions for easy selection
        fraud_indices = cls._df[cls._df["Class"] == 1].index.tolist()[:4]
        legit_indices = cls._df[cls._df["Class"] == 0].index.tolist()[:3]
        
        cls._samples = []
        for idx in legit_indices:
            row = cls._df.iloc[idx]
            cls._samples.append({
                "id": int(idx),
                "label": f"Transaction #{idx} (Legitimate - ${float(row['Amount']):.2f})",
                "class_label": 0,
                "amount": round(float(row["Amount"]), 2)
            })
        for idx in fraud_indices:
            row = cls._df.iloc[idx]
            cls._samples.append({
                "id": int(idx),
                "label": f"Transaction #{idx} (Flagged Anomaly - ${float(row['Amount']):.2f})",
                "class_label": 1,
                "amount": round(float(row["Amount"]), 2)
            })

    @classmethod
    def get_sample_list(cls):
        cls._init_resources()
        return cls._samples

    @classmethod
    def explain_transaction(cls, transaction_id: int):
        """Computes SHAP explanation for a specific transaction row index."""
        cls._init_resources()

        # Ensure transaction_id is converted to an integer
        transaction_id = int(transaction_id)
        X_test = cls._df.drop("Class", axis=1) if "Class" in cls._df.columns else cls._df

        total_rows = len(X_test)
        if transaction_id < 0 or transaction_id >= total_rows:
            raise HTTPException(
                status_code=404,
                detail=f"Transaction ID {transaction_id} not found. Valid index range: 0 to {total_rows - 1}."
            )

        # Crucially: Use this integer to slice the specific row from the dataset
        sample = X_test.iloc[int(transaction_id)]
        print(f"SENSING REQUEST: Explaining transaction index {transaction_id} with values {sample.values}", flush=True)

        is_target_class = int(cls._df.iloc[transaction_id].get("Class", 0)) if "Class" in cls._df.columns else 0

        # Prepare feature vector for the specific sliced transaction
        features_df = pd.DataFrame([sample], columns=X_test.columns)
        
        # Scale Amount feature using the pre-fit scaler
        features_scaled = features_df.copy()
        if "Amount" in features_scaled.columns:
            features_scaled["Amount"] = cls._scaler.transform(features_scaled[["Amount"]])

        # Predict probability for the specific transaction
        if hasattr(cls._model, "predict_proba"):
            probs = cls._model.predict_proba(features_scaled)[0]
            anomaly_prob = float(probs[1]) if len(probs) > 1 else float(probs[0])
        else:
            anomaly_prob = float(cls._model.predict(features_scaled)[0])

        predicted_class = int(anomaly_prob >= 0.3)
        prediction_label = "ANOMALOUS 🔴" if predicted_class == 1 else "BASELINE 🟢"

        # Pass the specific row to TreeExplainer to get local values for that exact user
        shap_values = cls._explainer(features_scaled)
        single_exp = shap_values[0]

        base_val = float(single_exp.base_values)
        if isinstance(base_val, (list, np.ndarray)):
            base_val = float(base_val[1] if len(base_val) > 1 else base_val[0])

        shap_array = single_exp.values
        if len(shap_array.shape) > 1 and shap_array.shape[1] > 1:
            shap_array = shap_array[:, 1]  # Class 1 (Target/Anomalous)

        # Import human explanation helpers from root_cause
        try:
            from src.root_cause import (
                get_human_explanation,
                get_single_feature_sentence,
                get_feature_description,
            )
        except ImportError:
            from root_cause import (
                get_human_explanation,
                get_single_feature_sentence,
                get_feature_description,
            )

        cols = features_df.columns.tolist()
        shap_dict = {col: float(shap_array[idx]) for idx, col in enumerate(cols)}
        feature_vals_dict = {col: float(sample[col]) for col in cols}

        # Synthesize overall and feature-level natural language explanations
        human_explanation = get_human_explanation(
            shap_dict,
            feature_values=feature_vals_dict,
            top_k=3,
            as_string=True
        )
        human_details = get_human_explanation(
            shap_dict,
            feature_values=feature_vals_dict,
            top_k=5,
            as_string=False
        )
        human_sentences = human_details.get("sentences", []) if isinstance(human_details, dict) else []

        feature_items = []
        top_fraud = []
        top_legit = []

        for idx, col in enumerate(cols):
            raw_val = round(float(sample[col]), 4)
            s_val = round(float(shap_array[idx]), 4)
            direction = "positive" if s_val > 0 else "negative"
            impact = "Increases Anomaly Score" if s_val > 0 else "Pushes Towards Baseline"
            desc = get_feature_description(col)
            sentence = get_single_feature_sentence(col, s_val, raw_val)

            item = {
                "feature": col,
                "value": raw_val,
                "shap_value": s_val,
                "direction": direction,
                "impact": impact,
                "abs_shap": abs(s_val),
                "human_description": desc,
                "human_sentence": sentence,
            }
            feature_items.append(item)

            if s_val > 0:
                top_fraud.append({
                    "feature": col,
                    "value": raw_val,
                    "shap_value": s_val,
                    "human_description": desc,
                    "human_sentence": sentence,
                })
            else:
                top_legit.append({
                    "feature": col,
                    "value": raw_val,
                    "shap_value": s_val,
                    "human_description": desc,
                    "human_sentence": sentence,
                })

        # Sort features by absolute SHAP magnitude descending
        feature_items.sort(key=lambda x: x["abs_shap"], reverse=True)
        top_fraud.sort(key=lambda x: x["shap_value"], reverse=True)
        top_legit.sort(key=lambda x: x["shap_value"])  # Most negative first

        model_output = round(base_val + float(shap_array.sum()), 4)

        return {
            "transaction_id": transaction_id,
            "is_target_class": is_target_class,
            "predicted_class": predicted_class,
            "prediction_label": prediction_label,
            "anomaly_score": round(anomaly_prob, 4),
            "base_value": round(base_val, 4),
            "model_output": model_output,
            "human_explanation": human_explanation,
            "human_sentences": human_sentences,
            "features": feature_items,
            "top_anomaly_pushes": top_fraud[:5],
            "top_legit_pushes": top_legit[:5],
            "sample_ids": cls._samples
        }
