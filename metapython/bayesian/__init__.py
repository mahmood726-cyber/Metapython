"""
Bayesian meta-analysis methods using PyMC.

This module provides comprehensive Bayesian meta-analysis functionality,
including hierarchical models, sensitivity analysis, and posterior predictive
checks.
"""

from metapython.core.config import HAS_PYMC

if HAS_PYMC:
    from metapython.bayesian.models import (
        BayesianMetaAnalysis,
        bayesian_meta_analysis,
        bayesian_meta_regression,
        bayesian_network_meta_analysis,
    )

    __all__ = [
        'BayesianMetaAnalysis',
        'bayesian_meta_analysis',
        'bayesian_meta_regression',
        'bayesian_network_meta_analysis',
    ]
else:
    __all__ = []
