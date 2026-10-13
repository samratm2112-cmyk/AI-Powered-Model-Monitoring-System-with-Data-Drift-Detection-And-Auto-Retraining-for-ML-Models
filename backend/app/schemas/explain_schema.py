"""
📋 PYDANTIC SCHEMAS FOR SHAP INTERPRETABILITY & LOCAL EXPLANATIONS
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class FeatureShapItem(BaseModel):
    feature: str
    value: float
    shap_value: float
    direction: str = Field(..., example="positive")
    impact: str = Field(..., example="Increases Anomaly Score")
    abs_shap: float
    human_description: Optional[str] = None
    human_sentence: Optional[str] = None

class TopPushItem(BaseModel):
    feature: str
    value: float
    shap_value: float
    human_description: Optional[str] = None
    human_sentence: Optional[str] = None

class SampleTransactionItem(BaseModel):
    id: int
    label: str
    class_label: int
    amount: float

class ExplainTransactionResponse(BaseModel):
    transaction_id: int
    is_target_class: int
    predicted_class: int
    prediction_label: str
    anomaly_score: float
    base_value: float
    model_output: float
    human_explanation: Optional[str] = None
    human_sentences: Optional[List[str]] = None
    features: List[FeatureShapItem]
    top_anomaly_pushes: List[TopPushItem]
    top_legit_pushes: List[TopPushItem]
    sample_ids: List[SampleTransactionItem]
