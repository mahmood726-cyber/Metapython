"""
Diagnostic Test Accuracy Meta-Analysis

Specialized methods for diagnostic studies:
- Bivariate random-effects model
- Hierarchical Summary ROC (HSROC)
- Summary operating points
- Diagnostic odds ratios

References:
- Reitsma et al. (2005). JCE, 58(10), 982-990
- Rutter & Gatsonis (2001). Statistics in Medicine, 20(19), 2865-2884
- Guo & Riebler (2018). Journal of Statistical Software, 83(1)
"""

from metapython.diagnostic_meta.diagnostic_accuracy import (
    DiagnosticData,
    DiagnosticMAResult,
    BivariateModel,
    HSROCModel,
    diagnostic_forest_plot_data,
    wilson_score_interval
)

__all__ = [
    'DiagnosticData',
    'DiagnosticMAResult',
    'BivariateModel',
    'HSROCModel',
    'diagnostic_forest_plot_data',
    'wilson_score_interval'
]
