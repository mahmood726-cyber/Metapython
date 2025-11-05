"""
Advanced Statistical Methods from Top Journals (2023-2024)

Implements cutting-edge methods from:
- Statistics in Medicine
- Biostatistics
- Journal of the American Statistical Association
- Research Synthesis Methods
- Statistical Methods in Medical Research
- BMC Medical Research Methodology

New methods include:
- Robust variance estimation with small sample corrections
- One-stage IPD meta-analysis with complex random effects
- Meta-analysis of prevalence with double arcsine transformation
- Hartung-Knapp-Sidik-Jonkman with ad-hoc variance correction
- Permutation-based inference for meta-analysis
- Empirical Bayes shrinkage estimators
- Machine learning for heterogeneity prediction
- Copula-based models for multivariate meta-analysis
- Measurement error correction models
- Time-varying effect meta-analysis
"""

from metapython.advanced_methods.journal_methods_2024 import (
    robust_variance_meta_analysis,
    one_stage_ipd_meta_analysis,
    prevalence_meta_analysis,
    hksj_improved,
    permutation_meta_analysis,
    empirical_bayes_meta_analysis,
    ml_heterogeneity_prediction,
    copula_meta_analysis,
    measurement_error_correction,
    time_varying_meta_analysis,
)

from metapython.advanced_methods.meta_diagnostics import (
    advanced_influence_diagnostics,
    cook_distance_meta,
    dffits_meta,
    covratio_meta,
    leverage_analysis,
)

from metapython.advanced_methods.robust_methods import (
    robust_meta_regression,
    quantile_meta_analysis,
    winsorized_meta_analysis,
    trimmed_meta_analysis,
)

__all__ = [
    # 2023-2024 Methods
    'robust_variance_meta_analysis',
    'one_stage_ipd_meta_analysis',
    'prevalence_meta_analysis',
    'hksj_improved',
    'permutation_meta_analysis',
    'empirical_bayes_meta_analysis',
    'ml_heterogeneity_prediction',
    'copula_meta_analysis',
    'measurement_error_correction',
    'time_varying_meta_analysis',

    # Diagnostics
    'advanced_influence_diagnostics',
    'cook_distance_meta',
    'dffits_meta',
    'covratio_meta',
    'leverage_analysis',

    # Robust methods
    'robust_meta_regression',
    'quantile_meta_analysis',
    'winsorized_meta_analysis',
    'trimmed_meta_analysis',
]
