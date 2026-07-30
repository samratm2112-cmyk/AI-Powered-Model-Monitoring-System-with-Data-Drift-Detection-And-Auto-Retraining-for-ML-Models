#!/usr/bin/env python
"""
🚀 CONTINUOUS ML DRIFT MONITORING PIPELINE ORCHESTRATOR
Sequentially ingests, validates, preprocesses, monitors drift, evaluates, decides, retrains, and logs batch-by-batch.
"""

import sys
import os
import pandas as pd

# Add src and base directory to sys.path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import config
from src.utils.data_generator import ensure_dataset_exists
from src.models.ensemble import GlobalLocalEnsemble
from src.pipeline.ingestion import BatchStreamIngestion
from src.pipeline.validator import DataValidator
from src.pipeline.preprocessor import FeaturePreprocessor
from src.pipeline.drift_detector import KSDriftDetector
from src.pipeline.evaluator import ModelEvaluator
from src.pipeline.decision_engine import RetrainingDecisionEngine
from src.pipeline.logger import PipelineLogger

def main():
    print("=" * 80)
    print("🚀 CONTINUOUS ML DRIFT MONITORING PIPELINE - INITIALIZING")
    print("=" * 80)
    
    logger = PipelineLogger(text_log_path=config.LOG_FILE, json_log_path=config.JSON_LOG_FILE)
    logger.log_event("PIPELINE", "Starting Continuous ML Drift Monitoring Pipeline", "INFO")
    
    # 1. Dataset Generation / Checks
    data_path = ensure_dataset_exists(file_path=config.DATA_FILE, force_generate=True)
    
    # 2. Ingestion Setup & Baseline Train Split
    ingestion = BatchStreamIngestion(
        data_path=data_path,
        train_size=config.HISTORICAL_TRAIN_SIZE,
        batch_size=config.BATCH_SIZE
    )
    X_train, y_train = ingestion.load_and_split()
    
    print(f"📊 Dataset Loaded: {len(ingestion.df)} total records")
    print(f"   Historical Baseline Train Set: {len(X_train)} samples ({y_train.sum()} fraud events)")
    print(f"   Production Stream Remaining:  {len(ingestion.production_df)} samples")
    print(f"   Configured Batch Size:        {config.BATCH_SIZE} records/batch ({ingestion.num_batches} total batches)")
    
    # 3. Preprocessing Setup & Baseline Model Training
    preprocessor = FeaturePreprocessor()
    X_train_scaled = preprocessor.fit_transform_baseline(X_train)
    
    print("\n🏋️  Training static Global Model (Veteran Expert - Long-Term Historical Memory)...")
    ensemble = GlobalLocalEnsemble(
        global_weight=config.GLOBAL_WEIGHT,
        threshold=config.CLASSIFICATION_THRESHOLD,
        n_estimators=config.N_ESTIMATORS,
        window_size=config.SLIDING_WINDOW_SIZE,
        random_state=config.RANDOM_STATE
    )
    ensemble.fit_global(X_train_scaled, y_train)
    print(f"✅ Global Model training complete (Weight: {ensemble.global_weight * 100:.0f}%)")
    logger.log_event("INITIALIZATION", "Global baseline model training completed successfully", "INFO")
    
    # 4. Pipeline Modules Setup
    validator = DataValidator(expected_features=X_train.columns)
    drift_detector = KSDriftDetector(reference_data=X_train_scaled, alpha=config.KS_ALPHA)
    decision_engine = RetrainingDecisionEngine(accuracy_threshold=config.ACCURACY_THRESHOLD, min_drift_features_threshold=3)
    
    # 5. Continuous Batch Monitoring Loop
    print("\n" + "=" * 80)
    print("🔁 CONTINUOUS BATCH MONITORING STREAM STARTED")
    print("=" * 80)
    
    batch_records = []
    
    for X_batch, y_batch, meta in ingestion.get_batch_iterator(apply_drift=True):
        batch_id = meta['batch_id']
        print(f"\n────────────────────────────────────────────────────────────────────────────────")
        print(f"📦 PROCESSING BATCH {batch_id} / {ingestion.num_batches} | Size: {meta['size']} records | Traffic: {meta['simulated_drift_type']}")
        print(f"────────────────────────────────────────────────────────────────────────────────")
        
        # Step A: Data Validation
        is_valid, val_info = validator.validate(X_batch)
        if not is_valid:
            logger.log_event("VALIDATION", f"Batch {batch_id} failed validation: {val_info['errors']}", "ERROR")
            continue
        print(f"   ✓ Data Validation: PASSED ({val_info['num_features']} features, 0 nulls)")
        
        # Step B: Preprocessing
        X_batch_scaled = preprocessor.transform_batch(X_batch)
        print(f"   ✓ Preprocessing: Applied baseline Amount feature scaling")
        
        # Step C: Pre-Adaptation Ensemble Evaluation
        metrics_pre, _ = ModelEvaluator.evaluate(ensemble, X_batch_scaled, y_batch, stage="PRE_ADAPTATION")
        print(f"   ✓ Pre-Adaptation Metrics: Accuracy = {metrics_pre['accuracy']:.4f} | Recall = {metrics_pre['recall']:.4f}")
        
        # Step D: Statistical Drift Detection (KS-Test)
        drift_res = drift_detector.detect_drift(X_batch_scaled)
        print(f"   ✓ Drift Detection: {'⚠️ DRIFT DETECTED' if drift_res['drift_detected'] else '✅ No drift'} ({drift_res['num_drifted']}/{drift_res['total_features']} features shifted)")
        if drift_res['drift_detected']:
            print(f"     Shifted features: {drift_res['drifted_features'][:5]}")
            
        # Step E: Decision Engine Criteria Evaluation (3-Tier Policy: GREEN, YELLOW, RED)
        decision = decision_engine.evaluate_decision(drift_res, metrics_pre['accuracy'])
        level_icon = "🟢" if decision['decision_level'] == "GREEN" else "🟡" if decision['decision_level'] == "YELLOW" else "🔴"
        print(f"   ✓ Decision Engine Status: {level_icon} {decision['decision_level']} | Retrain Local Expert = {decision['should_retrain']}")
        print(f"     Reasons: {', '.join(decision['reasons'])}")
        
        if decision['decision_level'] == "RED":
            logger.log_event("DECISION", f"Batch {batch_id} [RED]: Retraining triggered -> {', '.join(decision['reasons'])}", "WARNING")
        elif decision['decision_level'] == "YELLOW":
            logger.log_event("DECISION", f"Batch {batch_id} [YELLOW]: Warning logged -> {', '.join(decision['reasons'])}", "INFO")
        else:
            logger.log_event("DECISION", f"Batch {batch_id} [GREEN]: System stable -> {', '.join(decision['reasons'])}", "INFO")
            
        # Step F: Local Model Retraining (Conditional - RED Level Only)
        if decision['should_retrain']:
            print(f"   🏋️ Retraining Local Model (Rookie Expert) on Batch {batch_id} stream...")
            ensemble.fit_local(X_batch_scaled, y_batch)
            status = ensemble.get_status()
            print(f"   ✅ Local Model updated (Sliding Window Buffer: {status['local_buffer_size']} records)")
            logger.log_event("RETRAINING", f"Batch {batch_id}: Local Model updated (Buffer: {status['local_buffer_size']})", "SUCCESS")
            
        # Step G: Post-Adaptation Evaluation
        metrics_post, _ = ModelEvaluator.evaluate(ensemble, X_batch_scaled, y_batch, stage="POST_ADAPTATION")
        improvement = (metrics_post['accuracy'] - metrics_pre['accuracy']) * 100
        print(f"   ✓ Post-Adaptation Metrics: Accuracy = {metrics_post['accuracy']:.4f} (Boost: {improvement:+.2f}%)")
        
        # Step H: Log Record Assembly
        record = {
            'batch_id': batch_id,
            'num_samples': meta['size'],
            'fraud_count': meta['fraud_count'],
            'simulated_drift_type': meta['simulated_drift_type'],
            'validation_passed': is_valid,
            'drift_detected': drift_res['drift_detected'],
            'drifted_feature_count': drift_res['num_drifted'],
            'accuracy_before': metrics_pre['accuracy'],
            'decision_level': decision['decision_level'],
            'retraining_triggered': decision['should_retrain'],
            'accuracy_after': metrics_post['accuracy'],
            'improvement_pct': improvement,
            'local_buffer_size': ensemble.get_status()['local_buffer_size']
        }
        batch_records.append(record)
        logger.log_batch_record(record)
        
    # 6. Final Pipeline Execution Summary
    print("\n" + "=" * 80)
    print("📊 CONTINUOUS MONITORING PIPELINE EXECUTION SUMMARY")
    print("=" * 80)
    
    total_batches = len(batch_records)
    green_count = sum(1 for r in batch_records if r['decision_level'] == "GREEN")
    yellow_count = sum(1 for r in batch_records if r['decision_level'] == "YELLOW")
    red_count = sum(1 for r in batch_records if r['decision_level'] == "RED")
    
    avg_pre_acc = sum(r['accuracy_before'] for r in batch_records) / total_batches
    avg_post_acc = sum(r['accuracy_after'] for r in batch_records) / total_batches
    
    print(f"""
🎯 PIPELINE EXECUTION COMPLETE

📊 3-TIER DECISION BREAKDOWN:
   • Total Batches Processed:      {total_batches} ({config.BATCH_SIZE} records/batch)
   • 🟢 GREEN (Stable / No Drift):  {green_count} / {total_batches} (No Retraining)
   • 🟡 YELLOW (Minor Variation):   {yellow_count} / {total_batches} (Warning Only, No Retraining)
   • 🔴 RED (Significant Drift/Drop):{red_count} / {total_batches} (Local Model Retrained)

📈 ACCURACY SUMMARY:
   • Average Pre-Adaptation Acc:  {avg_pre_acc:.4f} ({avg_pre_acc*100:.2f}%)
   • Average Post-Adaptation Acc: {avg_post_acc:.4f} ({avg_post_acc*100:.2f}%)
   • Net Average Accuracy Boost:  +{ (avg_post_acc - avg_pre_acc)*100:.2f}%

📝 ARTIFACTS SAVED:
   ✅ Text Log: {config.LOG_FILE}
   ✅ JSON Log: {config.JSON_LOG_FILE}

🎓 SYSTEM STATUS: ✅ CONTINUOUS MONITORING ACTIVE & STABLE
""")
    print("=" * 80)
    logger.log_event("PIPELINE", f"Pipeline finished: GREEN={green_count}, YELLOW={yellow_count}, RED={red_count}", "SUCCESS")

if __name__ == "__main__":
    main()
