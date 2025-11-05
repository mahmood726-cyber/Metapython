"""
MetaPython - Professional Meta-Analysis Platform
=================================================

A comprehensive, production-ready meta-analysis library implementing
cutting-edge methods from top statistics journals.

Key Features:
- Fixed and random effects meta-analysis
- Publication bias assessment (P-uniform, Selection models, Limit meta-analysis)
- Network meta-analysis
- Bayesian meta-analysis
- Diagnostic test accuracy
- Bootstrap methods (BCa, percentile, studentized)
- GOSH plots for heterogeneity visualization
- Restricted cubic splines for dose-response
- Advanced meta-regression
- Interactive visualizations

Version: 0.5.0
License: MIT
"""

__version__ = '0.5.0'
__author__ = 'MetaPython Development Team'
__license__ = 'MIT'

# Core imports
from metapython.core.config import (
    DEFAULT_ALPHA,
    MIN_STUDIES_DEFAULT,
    HAS_PYMC,
    HAS_STATSMODELS,
)

from metapython.core.models import (
    FixedEffectsResults,
    RandomEffectsResults,
    HeterogeneityResults,
    PredictionIntervalResults,
    BiasTestResults,
    MetaAnalysisResults,
    UnifiedMetaConfig,
    UnifiedMetaError,
    InsufficientDataError,
    NumericalInstabilityError,
)

from metapython.core.utils import (
    calculate_pooled_estimate,
    calculate_confidence_interval,
    validate_inputs,
    safe_solve,
    safe_matrix_inverse,
)

# Import advanced methods from legacy files
try:
    from advanced_methods import PUniformMethods, SelectionModels, LimitMetaAnalysis
    from advanced_methods_part2 import GOSHAnalysis, BootstrapMethods, DoseResponseSplines
    HAS_ADVANCED_METHODS = True
except ImportError:
    HAS_ADVANCED_METHODS = False

__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__license__',

    # Configuration
    'DEFAULT_ALPHA',
    'MIN_STUDIES_DEFAULT',
    'HAS_PYMC',
    'HAS_STATSMODELS',
    'UnifiedMetaConfig',

    # Models
    'FixedEffectsResults',
    'RandomEffectsResults',
    'HeterogeneityResults',
    'PredictionIntervalResults',
    'BiasTestResults',
    'MetaAnalysisResults',

    # Exceptions
    'UnifiedMetaError',
    'InsufficientDataError',
    'NumericalInstabilityError',

    # Utilities
    'calculate_pooled_estimate',
    'calculate_confidence_interval',
    'validate_inputs',
    'safe_solve',
    'safe_matrix_inverse',
]

# Advanced methods
if HAS_ADVANCED_METHODS:
    __all__.extend([
        'PUniformMethods',
        'SelectionModels',
        'LimitMetaAnalysis',
        'GOSHAnalysis',
        'BootstrapMethods',
        'DoseResponseSplines',
    ])
