"""
Advanced Bayesian Meta-Analysis

State-of-the-art Bayesian methods:
- INLA (Integrated Nested Laplace Approximation)
- Location-scale models
- Fast alternatives to MCMC
- Network meta-analysis

References:
- Rue et al. (2009). JRSS-B, 71(2), 319-392
- Günhan et al. (2018). Research Synthesis Methods, 9(2), 179-194
"""

from metapython.advanced_bayesian.inla_methods import (
    BayesianResult,
    INLAMetaAnalysis,
    LocationScaleModel,
    bayesian_network_meta_analysis
)

__all__ = [
    'BayesianResult',
    'INLAMetaAnalysis',
    'LocationScaleModel',
    'bayesian_network_meta_analysis'
]
