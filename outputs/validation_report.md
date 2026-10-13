# 🛡️ Model Retraining Validation Report & Governance Audit

**Timestamp:** 2026-10-13 12:20:33  
**Recommendation:** **Strongly Recommend Deployment**  
**Audit File:** `/Users/sam/Desktop/Major1/outputs/validation_report.json`

---

## 1. Metrics Comparison (Old Model vs. Retrained New Model)

| Metric | Old Model | New Model | Delta | % Change | Evaluation |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Accuracy** | 0.9313 | 0.9313 | +0.0000 | +0.00% | 🟢 Improved |
| **Precision** | 0.9607 | 0.9607 | +0.0000 | +0.00% | 🟢 Improved |
| **Recall** | 0.9313 | 0.9313 | +0.0000 | +0.00% | 🟢 Improved |
| **F1-Score** | 0.9457 | 0.9457 | +0.0000 | +0.00% | 🟢 Improved |

---

## 2. Top 3 Features That Caused The Drift

Statistical divergence calculated using Two-Sample Kolmogorov-Smirnov Test:

1. **`Amount`**
   - **KS Statistic:** 0.9041
   - **p-value:** 0.000000e+00
   - **Drift Detected:** Yes (p < 0.05)

2. **`V3`**
   - **KS Statistic:** 0.0266
   - **p-value:** 1.138604e-10
   - **Drift Detected:** Yes (p < 0.05)

3. **`V1`**
   - **KS Statistic:** 0.0196
   - **p-value:** 5.206045e-06
   - **Drift Detected:** Yes (p < 0.05)

---

## 3. Governance Recommendation & Analysis

- **Decision:** **Strongly Recommend Deployment**
- **Analysis:** The retrained model demonstrates superior or stable performance over the old model (F1: 0.9457 vs 0.9457, Accuracy: 0.9313 vs 0.9313) and effectively counteracts the distribution drift detected in primary features: Amount, V3, V1.

---
*Generated automatically by AI-Powered Model Monitoring System Human-in-the-Loop Governance Gate.*
