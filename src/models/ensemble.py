"""
🧠 TWO-STAGE HYBRID PIPELINE & GLOBAL-LOCAL ENSEMBLE MODULE
Architecture Re-Export:
Points directly to core logic in src/ensemble.py to prevent code duplication
while preserving compatibility with existing module imports.
"""

import sys
import os

# Ensure src directory is in sys.path
_src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

try:
    from src.ensemble import TwoStagePipeline, GlobalLocalEnsemble
except ImportError:
    from ensemble import TwoStagePipeline, GlobalLocalEnsemble

__all__ = ["TwoStagePipeline", "GlobalLocalEnsemble"]
