"""
Multivariate Meta-Analysis

Meta-analysis of multiple correlated outcomes:
- Random-effects multivariate models
- Missing correlation imputation
- Joint hypothesis testing
- Dose-response extensions

References:
- Jackson et al. (2011). Statistics in Medicine, 30(20), 2481-2498
- White (2011). The Stata Journal, 11(2), 255-270
- Wei & Higgins (2013). Statistics in Medicine, 32(7), 1191-1205
"""

from metapython.multivariate_meta.multivariate_analysis import (
    MultivariateResult,
    MultivariateMetaAnalysis,
    impute_missing_correlations,
    dose_response_multivariate
)

__all__ = [
    'MultivariateResult',
    'MultivariateMetaAnalysis',
    'impute_missing_correlations',
    'dose_response_multivariate'
]
