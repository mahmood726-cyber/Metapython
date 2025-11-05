"""
Advanced Diagnostic Methods for Meta-Analysis

Implements cutting-edge diagnostic and influence analysis methods from:
- Viechtbauer & Cheung (2010). "Outlier and influence diagnostics"
  Research Synthesis Methods, 1(2), 112-125.
- Baujat et al. (2002). "A graphical method for exploring heterogeneity"
  Statistics in Medicine, 21(18), 2641-2652.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from scipy import stats
import warnings

from metapython.core.config import logger


def advanced_influence_diagnostics(
    effects: np.ndarray,
    variances: np.ndarray,
    study_labels: Optional[np.ndarray] = None
) -> Dict[str, Any]:
    """
    Comprehensive influence diagnostics for meta-analysis.

    Calculates multiple influence measures:
    - Cook's distance
    - DFFITS
    - COVRATIO
    - Hat values (leverage)
    - Studentized residuals
    - DFBETAS

    Implements methods from:
    Viechtbauer & Cheung (2010). Research Synthesis Methods, 1(2), 112-125.

    Args:
        effects: Effect sizes
        variances: Within-study variances
        study_labels: Optional study labels

    Returns:
        Comprehensive diagnostics for each study
    """
    n_studies = len(effects)

    if study_labels is None:
        study_labels = np.array([f"Study {i+1}" for i in range(n_studies)])

    # Fit full model
    weights = 1 / variances
    pooled = np.sum(weights * effects) / np.sum(weights)

    # Estimate tau² (DerSimonian-Laird)
    Q = np.sum(weights * (effects - pooled) ** 2)
    C = np.sum(weights) - np.sum(weights ** 2) / np.sum(weights)
    tau2 = max(0, (Q - (n_studies - 1)) / C)

    # Random-effects weights
    re_weights = 1 / (variances + tau2)
    pooled_re = np.sum(re_weights * effects) / np.sum(re_weights)

    # Initialize diagnostic arrays
    cook_d = np.zeros(n_studies)
    dffits = np.zeros(n_studies)
    covratio = np.zeros(n_studies)
    hat_values = np.zeros(n_studies)
    studentized_resid = np.zeros(n_studies)
    dfbetas = np.zeros(n_studies)

    # Calculate diagnostics
    for i in range(n_studies):
        # Leave-one-out analysis
        mask = np.ones(n_studies, dtype=bool)
        mask[i] = False

        loo_effects = effects[mask]
        loo_variances = variances[mask]
        loo_weights = 1 / loo_variances

        # Leave-one-out pooled estimate
        loo_pooled = np.sum(loo_weights * loo_effects) / np.sum(loo_weights)

        # Leave-one-out tau²
        loo_Q = np.sum(loo_weights * (loo_effects - loo_pooled) ** 2)
        loo_C = np.sum(loo_weights) - np.sum(loo_weights ** 2) / np.sum(loo_weights)
        loo_tau2 = max(0, (loo_Q - (n_studies - 2)) / loo_C)

        loo_re_weights = 1 / (loo_variances + loo_tau2)
        loo_pooled_re = np.sum(loo_re_weights * loo_effects) / np.sum(loo_re_weights)

        # Hat value (leverage)
        hat_values[i] = re_weights[i] / np.sum(re_weights)

        # Residual
        residual = effects[i] - pooled_re

        # Studentized residual
        se_residual = np.sqrt(variances[i] + tau2 - 1/np.sum(re_weights))
        studentized_resid[i] = residual / se_residual

        # Cook's distance
        cook_d[i] = (pooled_re - loo_pooled_re) ** 2 / (1 / np.sum(re_weights))

        # DFFITS
        dffits[i] = (pooled_re - loo_pooled_re) / np.sqrt(1 / np.sum(loo_re_weights))

        # COVRATIO
        covratio[i] = (1 / np.sum(loo_re_weights)) / (1 / np.sum(re_weights))

        # DFBETAS
        dfbetas[i] = (pooled_re - loo_pooled_re) / np.sqrt(1 / np.sum(re_weights))

    # Identify influential studies (using standard thresholds)
    influential_cook = cook_d > 4 / n_studies
    influential_dffits = np.abs(dffits) > 2 * np.sqrt(1 / n_studies)
    influential_covratio = (covratio < 1 - 3 * 1 / n_studies) | (covratio > 1 + 3 * 1 / n_studies)
    influential_dfbetas = np.abs(dfbetas) > 2 / np.sqrt(n_studies)

    # Overall influence score (composite)
    overall_influence = (influential_cook.astype(int) +
                        influential_dffits.astype(int) +
                        influential_covratio.astype(int) +
                        influential_dfbetas.astype(int))

    # Identify highly influential studies (flagged by 3+ measures)
    highly_influential = overall_influence >= 3

    return {
        'cook_distance': cook_d.tolist(),
        'dffits': dffits.tolist(),
        'covratio': covratio.tolist(),
        'hat_values': hat_values.tolist(),
        'studentized_residuals': studentized_resid.tolist(),
        'dfbetas': dfbetas.tolist(),
        'influential_studies': {
            'cook': np.where(influential_cook)[0].tolist(),
            'dffits': np.where(influential_dffits)[0].tolist(),
            'covratio': np.where(influential_covratio)[0].tolist(),
            'dfbetas': np.where(influential_dfbetas)[0].tolist(),
            'highly_influential': np.where(highly_influential)[0].tolist(),
        },
        'study_labels': study_labels.tolist(),
        'pooled_effect': float(pooled_re),
        'tau2': float(tau2),
        'n_studies': n_studies,
        'method': 'Advanced influence diagnostics',
        'reference': 'Viechtbauer & Cheung (2010), Research Synthesis Methods'
    }


def cook_distance_meta(
    effects: np.ndarray,
    variances: np.ndarray,
    threshold: Optional[float] = None
) -> Dict[str, Any]:
    """
    Calculate Cook's distance for meta-analysis.

    Measures the influence of each study on the pooled estimate.

    Args:
        effects: Effect sizes
        variances: Within-study variances
        threshold: Custom threshold (default: 4/n)

    Returns:
        Cook's distances and influential studies
    """
    n_studies = len(effects)

    if threshold is None:
        threshold = 4 / n_studies

    weights = 1 / variances
    pooled = np.sum(weights * effects) / np.sum(weights)

    # Estimate tau²
    Q = np.sum(weights * (effects - pooled) ** 2)
    C = np.sum(weights) - np.sum(weights ** 2) / np.sum(weights)
    tau2 = max(0, (Q - (n_studies - 1)) / C)

    re_weights = 1 / (variances + tau2)
    pooled_re = np.sum(re_weights * effects) / np.sum(re_weights)

    cook_d = np.zeros(n_studies)

    for i in range(n_studies):
        mask = np.ones(n_studies, dtype=bool)
        mask[i] = False

        loo_effects = effects[mask]
        loo_variances = variances[mask]
        loo_weights = 1 / loo_variances

        loo_pooled = np.sum(loo_weights * loo_effects) / np.sum(loo_weights)
        loo_Q = np.sum(loo_weights * (loo_effects - loo_pooled) ** 2)
        loo_C = np.sum(loo_weights) - np.sum(loo_weights ** 2) / np.sum(loo_weights)
        loo_tau2 = max(0, (loo_Q - (n_studies - 2)) / loo_C)

        loo_re_weights = 1 / (loo_variances + loo_tau2)
        loo_pooled_re = np.sum(loo_re_weights * loo_effects) / np.sum(loo_re_weights)

        cook_d[i] = (pooled_re - loo_pooled_re) ** 2 / (1 / np.sum(re_weights))

    influential = cook_d > threshold

    return {
        'cook_distance': cook_d.tolist(),
        'threshold': float(threshold),
        'influential_studies': np.where(influential)[0].tolist(),
        'max_influence': float(np.max(cook_d)),
        'mean_influence': float(np.mean(cook_d)),
        'n_influential': int(np.sum(influential)),
        'pooled_effect': float(pooled_re),
        'n_studies': n_studies,
        'method': "Cook's distance",
        'reference': 'Viechtbauer & Cheung (2010), Research Synthesis Methods'
    }


def dffits_meta(
    effects: np.ndarray,
    variances: np.ndarray,
    threshold: Optional[float] = None
) -> Dict[str, Any]:
    """
    Calculate DFFITS for meta-analysis.

    Measures the influence of each study on its own fitted value.

    Args:
        effects: Effect sizes
        variances: Within-study variances
        threshold: Custom threshold (default: 2*sqrt(1/n))

    Returns:
        DFFITS values and influential studies
    """
    n_studies = len(effects)

    if threshold is None:
        threshold = 2 * np.sqrt(1 / n_studies)

    weights = 1 / variances
    pooled = np.sum(weights * effects) / np.sum(weights)

    Q = np.sum(weights * (effects - pooled) ** 2)
    C = np.sum(weights) - np.sum(weights ** 2) / np.sum(weights)
    tau2 = max(0, (Q - (n_studies - 1)) / C)

    re_weights = 1 / (variances + tau2)
    pooled_re = np.sum(re_weights * effects) / np.sum(re_weights)

    dffits_vals = np.zeros(n_studies)

    for i in range(n_studies):
        mask = np.ones(n_studies, dtype=bool)
        mask[i] = False

        loo_effects = effects[mask]
        loo_variances = variances[mask]
        loo_weights = 1 / loo_variances

        loo_pooled = np.sum(loo_weights * loo_effects) / np.sum(loo_weights)
        loo_Q = np.sum(loo_weights * (loo_effects - loo_pooled) ** 2)
        loo_C = np.sum(loo_weights) - np.sum(loo_weights ** 2) / np.sum(loo_weights)
        loo_tau2 = max(0, (loo_Q - (n_studies - 2)) / loo_C)

        loo_re_weights = 1 / (loo_variances + loo_tau2)
        loo_pooled_re = np.sum(loo_re_weights * loo_effects) / np.sum(loo_re_weights)

        dffits_vals[i] = (pooled_re - loo_pooled_re) / np.sqrt(1 / np.sum(loo_re_weights))

    influential = np.abs(dffits_vals) > threshold

    return {
        'dffits': dffits_vals.tolist(),
        'threshold': float(threshold),
        'influential_studies': np.where(influential)[0].tolist(),
        'max_dffits': float(np.max(np.abs(dffits_vals))),
        'mean_dffits': float(np.mean(np.abs(dffits_vals))),
        'n_influential': int(np.sum(influential)),
        'pooled_effect': float(pooled_re),
        'n_studies': n_studies,
        'method': 'DFFITS',
        'reference': 'Viechtbauer & Cheung (2010), Research Synthesis Methods'
    }


def covratio_meta(
    effects: np.ndarray,
    variances: np.ndarray
) -> Dict[str, Any]:
    """
    Calculate COVRATIO for meta-analysis.

    Measures the impact of each study on the precision of the pooled estimate.

    Args:
        effects: Effect sizes
        variances: Within-study variances

    Returns:
        COVRATIO values and influential studies
    """
    n_studies = len(effects)

    # Thresholds for influence
    lower_threshold = 1 - 3 * (1 / n_studies)
    upper_threshold = 1 + 3 * (1 / n_studies)

    weights = 1 / variances
    pooled = np.sum(weights * effects) / np.sum(weights)

    Q = np.sum(weights * (effects - pooled) ** 2)
    C = np.sum(weights) - np.sum(weights ** 2) / np.sum(weights)
    tau2 = max(0, (Q - (n_studies - 1)) / C)

    re_weights = 1 / (variances + tau2)
    pooled_re = np.sum(re_weights * effects) / np.sum(re_weights)
    full_var = 1 / np.sum(re_weights)

    covratio_vals = np.zeros(n_studies)

    for i in range(n_studies):
        mask = np.ones(n_studies, dtype=bool)
        mask[i] = False

        loo_effects = effects[mask]
        loo_variances = variances[mask]
        loo_weights = 1 / loo_variances

        loo_pooled = np.sum(loo_weights * loo_effects) / np.sum(loo_weights)
        loo_Q = np.sum(loo_weights * (loo_effects - loo_pooled) ** 2)
        loo_C = np.sum(loo_weights) - np.sum(loo_weights ** 2) / np.sum(loo_weights)
        loo_tau2 = max(0, (loo_Q - (n_studies - 2)) / loo_C)

        loo_re_weights = 1 / (loo_variances + loo_tau2)
        loo_var = 1 / np.sum(loo_re_weights)

        covratio_vals[i] = loo_var / full_var

    influential = (covratio_vals < lower_threshold) | (covratio_vals > upper_threshold)

    return {
        'covratio': covratio_vals.tolist(),
        'lower_threshold': float(lower_threshold),
        'upper_threshold': float(upper_threshold),
        'influential_studies': np.where(influential)[0].tolist(),
        'n_influential': int(np.sum(influential)),
        'pooled_effect': float(pooled_re),
        'pooled_variance': float(full_var),
        'n_studies': n_studies,
        'method': 'COVRATIO',
        'reference': 'Viechtbauer & Cheung (2010), Research Synthesis Methods'
    }


def leverage_analysis(
    effects: np.ndarray,
    variances: np.ndarray,
    threshold: float = 0.2
) -> Dict[str, Any]:
    """
    Analyze leverage (hat values) in meta-analysis.

    High leverage indicates studies with unusual weight in the analysis.

    Args:
        effects: Effect sizes
        variances: Within-study variances
        threshold: Leverage threshold for flagging studies

    Returns:
        Leverage values and high-leverage studies
    """
    n_studies = len(effects)

    weights = 1 / variances
    pooled = np.sum(weights * effects) / np.sum(weights)

    Q = np.sum(weights * (effects - pooled) ** 2)
    C = np.sum(weights) - np.sum(weights ** 2) / np.sum(weights)
    tau2 = max(0, (Q - (n_studies - 1)) / C)

    re_weights = 1 / (variances + tau2)

    # Calculate hat values (leverage)
    hat_values = re_weights / np.sum(re_weights)

    # Flag high leverage studies
    high_leverage = hat_values > threshold

    # Average leverage
    avg_leverage = 1 / n_studies

    return {
        'hat_values': hat_values.tolist(),
        'threshold': float(threshold),
        'average_leverage': float(avg_leverage),
        'high_leverage_studies': np.where(high_leverage)[0].tolist(),
        'n_high_leverage': int(np.sum(high_leverage)),
        'max_leverage': float(np.max(hat_values)),
        'min_leverage': float(np.min(hat_values)),
        'n_studies': n_studies,
        'method': 'Leverage analysis',
        'reference': 'Viechtbauer & Cheung (2010), Research Synthesis Methods'
    }


__all__ = [
    'advanced_influence_diagnostics',
    'cook_distance_meta',
    'dffits_meta',
    'covratio_meta',
    'leverage_analysis',
]
