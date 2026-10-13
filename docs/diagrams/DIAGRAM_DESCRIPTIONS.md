# Technical Diagram Descriptions & IEEE Documentation

This document provides formal descriptions, component breakdowns, arrow semantics, and suggested IEEE-style research paper captions for the four publication-quality technical diagrams of the **AI-Based Data Drift Detection and Automated Model Retraining System for Credit Card Fraud Detection**.

---

## 1. System Architecture Diagram

### Figure Title
**System Architecture of the AI-Based Data Drift Detection and Automated Model Retraining System**

### File Paths
- **SVG**: `Documentation/diagrams/01_system_architecture.svg`
- **PNG**: `Documentation/diagrams/01_system_architecture.png`

### IEEE Paper Caption
> **Fig. 1.** System architecture illustrating the layered interaction among data ingestion, model monitoring, drift detection, adaptive retraining, backend services, and the React-based monitoring interface.

### Purpose
Communicates the high-level structural organization of the system, illustrating how raw transaction streams are partitioned, preprocessed, monitored for drift, adaptively retrained via a hybrid Global–Local Ensemble, and surfaced through FastAPI REST services to the React frontend.

### Component Explanations

| Layer / Block Name | Module in Code | Function & Technical Role |
| :--- | :--- | :--- |
| **Credit Card Transaction Stream** | External | Incoming production transaction data stream entering the system. |
| **Data Ingestion Layer** | `src/pipeline/ingestion.py` (`BatchStreamIngestion`) | Partitions full dataset into historical baseline training set (20,000 samples) and sequential streaming production batches (1,000 samples/batch). |
| **Data Validation & Feature Preprocessing** | `src/pipeline/validator.py` (`DataValidator`) & `src/pipeline/preprocessor.py` (`FeaturePreprocessor`) | Validates batch schema and missingness; applies baseline `StandardScaler` to non-stationary features (`Amount`). |
| **Historical Training Data** | `data/creditcard.csv` (Baseline Split) | Static baseline dataset used to fit the initial baseline global model. |
| **Production Batch Data** | Streaming Partition | Sequential incoming production transaction batch undergoing active evaluation and drift inspection. |
| **Global Fraud Detection Model** | `src/models/ensemble.py` (`model_global`) | Static Random Forest classifier ($N=100$ trees) representing long-term historical memory. Holds a fixed 70% weight in ensemble predictions. |
| **Model Performance Evaluation** | `src/pipeline/evaluator.py` (`ModelEvaluator`) | Calculates batch-level classification performance metrics: Accuracy, Precision, Recall, and F1-Score. |
| **KS Drift Detection Engine** | `src/pipeline/drift_detector.py` (`KSDriftDetector`) | Performs two-sample Kolmogorov–Smirnov (KS) tests ($\alpha=0.05$) per feature comparing the production batch against baseline reference data (excluding timestamp feature `Time`). |
| **Decision Engine** | `src/pipeline/decision_engine.py` (`RetrainingDecisionEngine`) | Implements a 3-tier production policy evaluating drift alerts ($\ge 3$ shifted features) and performance drops ($\text{Accuracy} < 0.99$). |
| **Local Adaptive Model** | `src/models/ensemble.py` (`model_local`) | Adaptive Random Forest classifier trained dynamically on recent drifted batches using a sliding window buffer ($\le 5,000$ samples). Holds 30% weight in ensemble. |
| **Global–Local Ensemble** | `src/models/ensemble.py` (`GlobalLocalEnsemble`) | Hybrid soft-voting classifier fusing predictions: $P(y|X) = 0.7 \cdot P_{\text{global}}(y|X) + 0.3 \cdot P_{\text{local}}(y|X)$ with decision threshold $\tau = 0.3$. |
| **Prediction & Post-Adaptation Evaluation** | `src/pipeline/evaluator.py` | Runs final ensemble predictions and evaluates post-retraining performance boost on the batch. |
| **Monitoring & Audit Layer** | `src/pipeline/logger.py` (`PipelineLogger`) | Persists timestamped text event logs (`retraining_log.txt`) and structured execution metrics JSON (`decision_log.json`). |
| **FastAPI REST Backend** | `backend/app/main.py` & `backend/app/services/` | Asynchronous REST service layer exposing monitoring endpoints, KPI aggregations, log streams, and custom CSV upload pipeline execution. |
| **React Monitoring Dashboard** | `frontend/src/` | Client-side React single-page application (SPA) rendering real-time KPI cards, batch timeline, drift frequency charts, and accuracy trends. |

### Explanation of Arrows
1. **Transaction Stream $\rightarrow$ Ingestion**: Ingests raw continuous transaction data.
2. **Ingestion $\rightarrow$ Preprocessing**: Passes partitioned batches for schema validation and feature scaling.
3. **Preprocessing $\rightarrow$ Split**:
   - **Left path**: Feeds historical baseline partition to train the static Global Model.
   - **Right path**: Passes live production batches to Evaluation and Drift Detection.
4. **Production Batch $\rightarrow$ Model Evaluation $\rightarrow$ Drift Detection Engine $\rightarrow$ Decision Engine**: Sequential flow of validation, baseline metric calculation, statistical KS drift testing, and policy evaluation.
5. **Decision Engine Branches**:
   - **🟢 GREEN Branch ("No Retrain")**: 0 shifted features and accuracy $\ge 99\%$; bypasses local retraining.
   - **🟡 YELLOW Branch ("Log Warning")**: 1–2 shifted features (minor variation) and accuracy $\ge 99\%$; logs warning, bypasses retraining.
   - **🔴 RED Branch ("Retrain")**: $\ge 3$ shifted features OR accuracy $< 99\%$; triggers local model retraining.
6. **RED Branch $\rightarrow$ Local Model**: Injects shifted batch data into sliding window buffer to fit/update the Local Model.
7. **Global Model & Local Model $\rightarrow$ Global–Local Ensemble**: Fuses prediction probabilities via $70/30$ weighted soft-voting.
8. **Ensemble $\rightarrow$ Post-Adaptation Evaluation $\rightarrow$ Monitoring Layer $\rightarrow$ FastAPI $\rightarrow$ React**: Downstream flow of final predictions, log persistence, API serialization, and dashboard visualization.

---

## 2. Data Flow Diagram (DFD)

### Figure Title
**Data Flow Diagram of the Continuous ML Monitoring Pipeline**

### File Paths
- **SVG**: `Documentation/diagrams/02_data_flow_diagram.svg`
- **PNG**: `Documentation/diagrams/02_data_flow_diagram.png`

### IEEE Paper Caption
> **Fig. 2.** Data flow diagram depicting data transformations, process interactions, data stores, and external entity data movement across the ML monitoring pipeline.

### Purpose
Focuses strictly on **data movement and transformations**, detailing inputs, process nodes (P1–P9), data stores (D1–D3), and output data artifacts across the system.

### Processes, Data Stores, and Entities

| DFD Element | ID | Name | Data Input | Data Output |
| :--- | :--- | :--- | :--- | :--- |
| **External Entity** | Source | Production Transaction Source | Raw transaction stream | `Transaction Batch` |
| **Process** | P1 | Data Ingestion | `Transaction Batch` | `Raw Batch Data` |
| **Process** | P2 | Data Validation | `Raw Batch Data` | `Validated Batch` |
| **Process** | P3 | Feature Preprocessing | `Validated Batch` | `Preprocessed Features` |
| **Process** | P4 | Model Performance Evaluation | `Preprocessed Features`, `Current Model` (from D2) | `Accuracy Metrics` |
| **Process** | P5 | Drift Detection | `Preprocessed Features`, `Reference Data` (from D1) | `Drift Statistics` |
| **Process** | P6 | Retraining Decision | `Accuracy Metrics`, `Drift Statistics` | `Retraining Decision` (`GREEN`/`YELLOW`/`RED`) |
| **Process** | P7 | Local Model Adaptation | `Preprocessed Features`, `RED Decision` | `Updated Local Model` (to D2), `Adapted Model` |
| **Process** | P8 | Ensemble Prediction | `Preprocessed Features`, `Adapted Model`, `Model State` (D2) | `Final Predictions` |
| **Process** | P9 | Monitoring & Reporting | `Final Predictions`, Execution Metrics | `Monitoring Results` (to D3) |
| **Data Store** | D1 | Historical Training Dataset | Split baseline partition | `Reference Data` (for KS-test comparison) |
| **Data Store** | D2 | Model State Store | `Updated Local Model` | `Current Model`, `Model State` |
| **Data Store** | D3 | Monitoring & Audit Store | `Monitoring Results` | `Dashboard Payload` |
| **External Entity** | Sink | FastAPI REST API $\rightarrow$ React Dashboard | `Dashboard Payload` | Client visual UI rendering |

### Explanation of Arrows & Data Labels
- **Transaction Batch**: Raw stream of credit card records ($N=1,000$).
- **Raw Batch Data**: Ingested batch dataframe.
- **Validated Batch**: Batch verified for 31 expected features and zero null values.
- **Preprocessed Features**: Feature matrix with `Amount` scaled via baseline `StandardScaler`.
- **Reference Data**: Baseline feature distributions ($N=20,000$) pulled from D1 for two-sample KS testing.
- **Current Model**: Global model weights loaded from D2 for baseline prediction.
- **Accuracy Metrics & Drift Statistics**: Accuracy/Recall scores and p-value feature shift counts fed into Decision Engine P6.
- **RED: Retrain**: Decision payload triggering local sliding window retrain.
- **GREEN/YELLOW**: Decision payload continuing pipeline without triggering local retrain.
- **Updated Local Model**: Newly fitted Random Forest model saved back to Model State Store D2.
- **Final Predictions**: Weighted ensemble classification predictions ($y_{\text{pred}} \in \{0, 1\}$).
- **Monitoring Results**: Execution record containing metrics, decision level, and drift details written to D3.
- **Dashboard Payload**: Aggregated JSON payload fetched by React dashboard over HTTP REST endpoints.

---

## 3. Control Flow Diagram

### Figure Title
**Control Flow of Continuous Data Drift Monitoring and Model Adaptation**

### File Paths
- **SVG**: `Documentation/diagrams/03_control_flow_diagram.svg`
- **PNG**: `Documentation/diagrams/03_control_flow_diagram.png`

### IEEE Paper Caption
> **Fig. 3.** Control flow diagram of the continuous batch monitoring and adaptive retraining loop.

### Purpose
Illustrates the **program logic, execution branches, decision points, and loop-back mechanisms** governing continuous batch processing and dynamic model adaptation.

### Control Steps & Logic

```
[START]
  │
  ▼
[Load / Generate Dataset]
  │
  ▼
[Ingest & Split Data] ──► Baseline Train (20K) + Stream Batches (1K)
  │
  ▼
[Preprocess Baseline Features]
  │
  ▼
[Train Static Global Model]
  │
  ▼
[Initialize Pipeline Modules]
  │
  ▼
┌─► [Receive Next Production Batch] ◄────────────────────────────────────────┐
│     │                                                                      │
│     ▼                                                                      │
│   / Valid Batch? \ ──(NO)──► [Reject & Log Error] ──(Skip to Next Batch)───┤
│   \              /                                                         │
│     │ (YES)                                                                │
│     ▼                                                                      │
│   [Preprocess Batch]                                                       │
│     │                                                                      │
│     ▼                                                                      │
│   [Pre-Adaptation Evaluation]                                              │
│     │                                                                      │
│     ▼                                                                      │
│   [Perform KS Drift Test]                                                  │
│     │                                                                      │
│     ▼                                                                      │
│   / Decision Engine \                                                      │
│   \  (3-Tier Policy)/                                                      │
│     │      │      │                                                        │
│ GREEN   YELLOW   RED                                                       │
│     │      │      │                                                        │
│     │      │      ▼                                                        │
│     │      │    [Retrain Local Model]                                      │
│     │      │      │                                                        │
│     │      │      ▼                                                        │
│     │      │    [Update Global–Local Ensemble]                             │
│     │      │      │                                                        │
│     └──────┴──────┼────────────────────────────────────────────────────────┘
                    │ (Rejoin)
                    ▼
          [Post-Adaptation Evaluation]
                    │
                    ▼
          [Record Monitoring Results]
                    │
                    ▼
          / More Batches? \ ──(YES)──► (Loop back to Receive Next Batch) ────┘
          \               /
            │ (NO)
            ▼
          [END]
```

### Decision Logic Breakdown
1. **Validation Decision (`Valid?`)**:
   - **NO**: Missing columns or null values detected. Log error and skip directly to the next batch.
   - **YES**: Schema intact. Proceed to feature scaling.
2. **Policy Evaluation (`Decision Engine`)**:
   - **GREEN**: `num_drifted == 0` AND `accuracy >= 0.99`. System stable. No retraining.
   - **YELLOW**: `1 <= num_drifted <= 2` AND `accuracy >= 0.99`. Minor drift warning logged. No retraining.
   - **RED**: `num_drifted >= 3` OR `accuracy < 0.99`. Significant drift / degradation. Trigger local model retrain.
3. **Loop Continuation (`More Batches?`)**:
   - **YES**: Remaining production batches exist in stream. Loop back to `Receive Next Production Batch`.
   - **NO**: Production stream exhausted. Pipeline execution terminates.

---

## 4. Sequence Diagram

### Figure Title
**Sequence Diagram for Batch-Level Drift Detection and Model Adaptation**

### File Paths
- **SVG**: `Documentation/diagrams/04_sequence_diagram.svg`
- **PNG**: `Documentation/diagrams/04_sequence_diagram.png`

### IEEE Paper Caption
> **Fig. 4.** Sequence diagram illustrating component interaction during batch-level drift detection and adaptive model retraining.

### Purpose
Details the **time-ordered object interactions, synchronous call paths, return messages, and conditional execution frames (`alt`)** during a single batch monitoring lifecycle.

### Sequence Participants

1. `Production Data Source`: Stream provider yielding transaction batches.
2. `Ingestion Layer`: `BatchStreamIngestion` partitioner.
3. `Data Validator`: `DataValidator` schema inspector.
4. `Feature Preprocessor`: `FeaturePreprocessor` scaler.
5. `Model Evaluator`: `ModelEvaluator` metrics calculator.
6. `Drift Detection Engine`: `KSDriftDetector` statistical tester.
7. `Decision Engine`: `RetrainingDecisionEngine` policy controller.
8. `Local Model`: `GlobalLocalEnsemble.fit_local()` adaptive RF classifier.
9. `Global–Local Ensemble`: `GlobalLocalEnsemble` hybrid soft-voting classifier.
10. `Monitoring & Audit Layer`: `PipelineLogger` logger.
11. `FastAPI Backend`: `MonitoringService` API layer.
12. `React Dashboard`: Single-Page Application visual dashboard.

---
*All diagrams adhere strictly to publication standards: professional typography, light backgrounds, restrained blue/gray/red color accents, precise directional connectors, zero text overlap, and complete alignment with the verified project source code.*
