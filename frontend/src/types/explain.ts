export interface FeatureShapItem {
  feature: string;
  value: number;
  shap_value: number;
  direction: 'positive' | 'negative';
  impact: string;
  abs_shap: number;
  human_description?: string;
  human_sentence?: string;
}

export interface TopPushItem {
  feature: string;
  value: number;
  shap_value: number;
  human_description?: string;
  human_sentence?: string;
}

export interface SampleTransactionItem {
  id: number;
  label: string;
  class_label: number;
  amount: number;
}

export interface ExplainTransactionResponse {
  transaction_id: number;
  is_target_class: number;
  predicted_class: number;
  prediction_label: string;
  anomaly_score: number;
  base_value: number;
  model_output: number;
  human_explanation?: string;
  human_sentences?: string[];
  features: FeatureShapItem[];
  top_anomaly_pushes: TopPushItem[];
  top_legit_pushes: TopPushItem[];
  sample_ids: SampleTransactionItem[];
}
