"""
Core package for MetaPython.

Contains fundamental data structures, configuration, and utilities.
"""

from metapython.core.config import *
from metapython.core.models import *
from metapython.core.utils import *

__all__ = [
    # From config
    'DEFAULT_ALPHA',
    'Z_CRITICAL_95',
    'Z_CRITICAL_99',
    'MIN_STUDIES_DEFAULT',
    'MAX_ITERATIONS_DEFAULT',
    'CONVERGENCE_TOLERANCE',
    'NUMERICAL_EPSILON',

    # From models
    'FixedEffectsResults',
    'RandomEffectsResults',
    'HeterogeneityResults',
    'PredictionIntervalResults',
    'BiasTestResults',
    'MetaAnalysisResults',
    'UnifiedMetaConfig',
    'UnifiedMetaError',
    'InsufficientDataError',
    'NumericalInstabilityError',

    # From utils
    'calculate_pooled_estimate',
    'calculate_confidence_interval',
    'validate_inputs',
    'safe_solve',
    'safe_matrix_inverse',
]
