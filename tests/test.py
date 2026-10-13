"""
🧪 SYSTEM SETUP & INTEGRATION VERIFICATION TEST
Verifies the directory structure, module imports, data paths, model paths, and output paths.
"""

import os
import sys
import pandas as pd

# Setup project root in sys.path
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_DIR)
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

for p in [PROJECT_ROOT, SRC_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)


def test_directory_structure():
    """Verify that all standard directories exist."""
    print("📁 Checking directory structure...")
    required_dirs = ["data", "docs", "models", "outputs", "src", "tests"]
    for d in required_dirs:
        dir_path = os.path.join(PROJECT_ROOT, d)
        assert os.path.isdir(dir_path), f"Missing required directory: {d}"
        print(f"   ✓ /{d} exists")


def test_data_paths():
    """Verify data loading from /data."""
    print("\n📊 Checking dataset loading...")
    data_file = os.path.join(PROJECT_ROOT, "data", "creditcard.csv")
    assert os.path.exists(data_file), f"Dataset not found at {data_file}"
    df = pd.read_csv(data_file, nrows=10)
    assert not df.empty, "Dataset read error: DataFrame is empty"
    assert "Class" in df.columns, "Target column 'Class' missing from dataset"
    print(f"   ✓ Dataset loaded successfully ({len(df.columns)} columns verified)")


def test_model_paths():
    """Verify /models directory and saved models."""
    print("\n🤖 Checking model files in /models...")
    models_dir = os.path.join(PROJECT_ROOT, "models")
    assert os.path.isdir(models_dir), f"Models directory not found: {models_dir}"
    expected_models = ["deployed_model.pkl", "model_latest.pkl"]
    found = [m for m in expected_models if os.path.exists(os.path.join(models_dir, m))]
    print(f"   ✓ Found {len(found)}/{len(expected_models)} model artifact(s): {found}")


def test_output_paths():
    """Verify /outputs directory and artifact persistence."""
    print("\n📦 Checking /outputs directory...")
    outputs_dir = os.path.join(PROJECT_ROOT, "outputs")
    assert os.path.isdir(outputs_dir), f"Outputs directory not found: {outputs_dir}"
    
    test_file = os.path.join(outputs_dir, ".test_write.tmp")
    with open(test_file, "w") as f:
        f.write("test")
    assert os.path.exists(test_file), "Failed to write to /outputs"
    os.remove(test_file)
    print("   ✓ Write permissions verified for /outputs")


def test_module_imports():
    """Verify internal module imports."""
    print("\n🧩 Checking core module imports...")
    import config
    from src.ensemble import GlobalLocalEnsemble, TwoStagePipeline
    from src.models.ensemble import GlobalLocalEnsemble as ReExportEnsemble
    from src.pipeline.ingestion import BatchStreamIngestion
    from src.pipeline.validator import DataValidator
    from src.pipeline.preprocessor import FeaturePreprocessor
    from src.pipeline.drift_detector import KSDriftDetector
    from src.pipeline.evaluator import ModelEvaluator
    from src.pipeline.decision_engine import RetrainingDecisionEngine
    from src.pipeline.logger import PipelineLogger
    from src.decision_engine import RetrainingLogger, ensure_dataset_exists
    
    print("   ✓ All core logic & pipeline modules imported successfully")


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 RUNNING PROJECT VERIFICATION SUITE")
    print("=" * 70)
    
    test_directory_structure()
    test_data_paths()
    test_model_paths()
    test_output_paths()
    test_module_imports()
    
    print("\n" + "=" * 70)
    print("Setup successful")
    print("=" * 70)
