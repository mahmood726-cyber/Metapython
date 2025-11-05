"""
MetaPython - Modular Meta-Analysis Library
==========================================

A production-ready meta-analysis library with comprehensive features:
- Core meta-analysis with advanced diagnostics
- Transport weighting and robust methods
- NLP extraction and ML-based conflict detection
- Publication bias assessment
- Network and sequential meta-analysis
- Diagnostic test accuracy analysis
- Sparse event methods
- GRADE assessment
- CLI and pipeline automation

Author: PyMeta-CBAMM Development Team
License: MIT
Version: 0.4.1
"""

# Core configuration and utilities
from .config import (
    # Constants
    DEFAULT_ALPHA,
    Z_CRITICAL_95,
    Z_CRITICAL_99,
    OUTLIER_Z_THRESHOLD,
    MIN_STUDIES_DEFAULT,
    MIN_SAMPLE_SIZE_PER_ARM,
    NUMERICAL_EPSILON,
    CONVERGENCE_TOLERANCE,
    MAX_ITERATIONS_DEFAULT,
    DEFAULT_EFFECT_SIZE,
    DEFAULT_SE,

    # Dataclasses
    FixedEffectsResults,
    RandomEffectsResults,
    HeterogeneityResults,
    PredictionIntervalResults,
    BiasTestResults,
    ConflictResults,
    MetaAnalysisResults,

    # Configuration
    UnifiedMetaConfig,

    # Exceptions
    UnifiedMetaError,
    InsufficientDataError,
    NumericalInstabilityError,

    # Utility functions
    validate_inputs,
    safe_solve,
    safe_matrix_inverse,
    calculate_pooled_estimate,
    calculate_confidence_interval,
    get_spacy_model,
)

# Estimators
from .estimators import TauSquaredEstimators

# Main analysis class
from .analysis import UnifiedMetaAnalysis

# Specialized analyses
from .diagnostic_accuracy import EnhancedDiagnosticTestAccuracy
from .network import NetworkMetaRankings
from .sparse_events import SparseEventMethods
from .grade import EnhancedGRADE

# CLI
from .cli import MetaCLI

__version__ = "0.4.1"
__all__ = [
    # Core classes
    "UnifiedMetaAnalysis",
    "TauSquaredEstimators",

    # Specialized analyses
    "EnhancedDiagnosticTestAccuracy",
    "NetworkMetaRankings",
    "SparseEventMethods",
    "EnhancedGRADE",

    # Configuration
    "UnifiedMetaConfig",

    # Results
    "MetaAnalysisResults",
    "FixedEffectsResults",
    "RandomEffectsResults",
    "HeterogeneityResults",

    # CLI
    "MetaCLI",

    # Utilities
    "calculate_pooled_estimate",
    "calculate_confidence_interval",
]
