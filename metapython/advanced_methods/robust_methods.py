"""
Robust Statistical Methods for Meta-Analysis

Implements robust alternatives to standard meta-analysis methods from:
- Hedges & Olkin (1985). Statistical Methods for Meta-Analysis
- Baker & Jackson (2013). "A new approach to outliers in meta-analysis"
  Research Synthesis Methods, 4(3), 220-242.
- Sanchez-Meca & Marin-Martinez (1998). "Weighting by inverse variance
  or by sample size in meta-analysis" Educational and Psychological
  Measurement, 58(2), 211-220.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from scipy import stats
from scipy.optimize import minimize
import warnings

from metapython.core.config import logger


def robust_meta_regression(
    effects: np.ndarray,
    variances: np.ndarray,
    moderators: np.ndarray,
    method: str = 'huber',
    k: float = 1.345
) -> Dict[str, Any]:
    """
    Robust meta-regression using M-estimators.

    Downweights outliers using robust loss functions.

    Implements methods from:
    Hedges & Olkin (1985). Statistical Methods for Meta-Analysis.

    Args:
        effects: Effect sizes
        variances: Within-study variances
        moderators: Moderator variables (n_studies × n_moderators)
        method: Robust method ('huber', 'bisquare', 'cauchy')
        k: Tuning constant for robust estimator

    Returns:
        Robust regression coefficients and statistics
    """
    n_studies = len(effects)

    # Ensure moderators is 2D
    if moderators.ndim == 1:
        moderators = moderators.reshape(-1, 1)

    n_moderators = moderators.shape[1]

    # Add intercept
    X = np.column_stack([np.ones(n_studies), moderators])

    # Initial weights (inverse variance)
    weights = 1 / variances

    # Initial weighted least squares estimate
    W = np.diag(weights)
    beta = np.linalg.solve(X.T @ W @ X, X.T @ W @ effects)

    # Iteratively reweighted least squares
    max_iter = 50
    tol = 1e-6

    for iteration in range(max_iter):
        # Calculate residuals
        fitted = X @ beta
        residuals = effects - fitted

        # Robust scale estimate (MAD)
        mad = np.median(np.abs(residuals - np.median(residuals)))
        scale = 1.4826 * mad  # Consistent estimator of SD

        if scale < 1e-10:
            scale = np.std(residuals)

        # Standardized residuals
        std_resid = residuals / scale

        # Calculate robust weights based on method
        if method == 'huber':
            # Huber weights
            robust_weights = np.where(
                np.abs(std_resid) <= k,
                1.0,
                k / np.abs(std_resid)
            )
        elif method == 'bisquare':
            # Tukey bisquare weights
            robust_weights = np.where(
                np.abs(std_resid) <= k,
                (1 - (std_resid / k) ** 2) ** 2,
                0.0
            )
        elif method == 'cauchy':
            # Cauchy weights
            robust_weights = 1 / (1 + (std_resid / k) ** 2)
        else:
            raise ValueError(f"Unknown method: {method}")

        # Combine with inverse variance weights
        combined_weights = weights * robust_weights

        # Update estimates
        W = np.diag(combined_weights)
        beta_new = np.linalg.solve(X.T @ W @ X, X.T @ W @ effects)

        # Check convergence
        if np.max(np.abs(beta_new - beta)) < tol:
            beta = beta_new
            break

        beta = beta_new

    # Final fitted values and residuals
    fitted = X @ beta
    residuals = effects - fitted

    # Robust covariance matrix
    bread = np.linalg.inv(X.T @ W @ X)
    meat = X.T @ np.diag(combined_weights * residuals ** 2) @ X
    robust_cov = bread @ meat @ bread

    # Standard errors
    se = np.sqrt(np.diag(robust_cov))

    # Test statistics
    z_stats = beta / se
    p_values = 2 * (1 - stats.norm.cdf(np.abs(z_stats)))

    # Confidence intervals
    ci_low = beta - 1.96 * se
    ci_high = beta + 1.96 * se

    # Identify downweighted studies
    downweighted = robust_weights < 0.5

    return {
        'coefficients': beta.tolist(),
        'se': se.tolist(),
        'z_statistics': z_stats.tolist(),
        'p_values': p_values.tolist(),
        'ci_low': ci_low.tolist(),
        'ci_high': ci_high.tolist(),
        'robust_weights': robust_weights.tolist(),
        'downweighted_studies': np.where(downweighted)[0].tolist(),
        'n_downweighted': int(np.sum(downweighted)),
        'residuals': residuals.tolist(),
        'fitted': fitted.tolist(),
        'n_studies': n_studies,
        'n_moderators': n_moderators,
        'method': f'Robust meta-regression ({method})',
        'reference': 'Hedges & Olkin (1985)'
    }


def quantile_meta_analysis(
    effects: np.ndarray,
    variances: np.ndarray,
    quantiles: List[float] = [0.25, 0.5, 0.75]
) -> Dict[str, Any]:
    """
    Quantile-based meta-analysis.

    Estimates different quantiles of the effect size distribution.

    Args:
        effects: Effect sizes
        variances: Within-study variances
        quantiles: Quantiles to estimate

    Returns:
        Quantile estimates with CIs
    """
    n_studies = len(effects)

    results = {}

    for q in quantiles:
        # Quantile regression objective
        def quantile_loss(theta):
            residuals = effects - theta
            return np.sum(
                np.where(residuals >= 0,
                        q * residuals * (1 / variances),
                        (q - 1) * residuals * (1 / variances))
            )

        # Optimize
        result = minimize(quantile_loss, x0=np.median(effects),
                         method='Nelder-Mead')
        quantile_est = result.x[0]

        # Bootstrap CI
        n_boot = 1000
        boot_estimates = np.zeros(n_boot)

        np.random.seed(42)
        for b in range(n_boot):
            boot_idx = np.random.choice(n_studies, size=n_studies, replace=True)
            boot_effects = effects[boot_idx]
            boot_variances = variances[boot_idx]

            def boot_loss(theta):
                residuals = boot_effects - theta
                return np.sum(
                    np.where(residuals >= 0,
                            q * residuals * (1 / boot_variances),
                            (q - 1) * residuals * (1 / boot_variances))
                )

            boot_result = minimize(boot_loss, x0=quantile_est,
                                 method='Nelder-Mead')
            boot_estimates[b] = boot_result.x[0]

        ci_low = np.percentile(boot_estimates, 2.5)
        ci_high = np.percentile(boot_estimates, 97.5)

        results[f'Q{int(q*100)}'] = {
            'estimate': float(quantile_est),
            'ci_low': float(ci_low),
            'ci_high': float(ci_high),
        }

    return {
        'quantile_estimates': results,
        'n_studies': n_studies,
        'method': 'Quantile meta-analysis',
        'reference': 'Baker & Jackson (2013), Research Synthesis Methods'
    }


def winsorized_meta_analysis(
    effects: np.ndarray,
    variances: np.ndarray,
    percentile: float = 0.1
) -> Dict[str, Any]:
    """
    Meta-analysis with winsorized effect sizes.

    Replaces extreme values with less extreme percentiles.

    Args:
        effects: Effect sizes
        variances: Within-study variances
        percentile: Percentile for winsorization (0-0.5)

    Returns:
        Meta-analysis results with winsorized data
    """
    n_studies = len(effects)

    # Calculate winsorization thresholds
    lower_threshold = np.percentile(effects, percentile * 100)
    upper_threshold = np.percentile(effects, (1 - percentile) * 100)

    # Winsorize effects
    effects_winsorized = np.clip(effects, lower_threshold, upper_threshold)

    # Count winsorized studies
    n_winsorized = np.sum((effects < lower_threshold) | (effects > upper_threshold))

    # Perform meta-analysis on winsorized data
    weights = 1 / variances
    pooled = np.sum(weights * effects_winsorized) / np.sum(weights)

    # Estimate tau²
    Q = np.sum(weights * (effects_winsorized - pooled) ** 2)
    C = np.sum(weights) - np.sum(weights ** 2) / np.sum(weights)
    tau2 = max(0, (Q - (n_studies - 1)) / C)

    # Random-effects meta-analysis
    re_weights = 1 / (variances + tau2)
    pooled_re = np.sum(re_weights * effects_winsorized) / np.sum(re_weights)
    se_re = np.sqrt(1 / np.sum(re_weights))

    # Confidence interval
    ci_low = pooled_re - 1.96 * se_re
    ci_high = pooled_re + 1.96 * se_re

    # Test statistic
    z_stat = pooled_re / se_re
    p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))

    # Heterogeneity
    I2 = max(0, 100 * (Q - (n_studies - 1)) / Q) if Q > 0 else 0

    return {
        'pooled_effect': float(pooled_re),
        'se': float(se_re),
        'ci_low': float(ci_low),
        'ci_high': float(ci_high),
        'z_statistic': float(z_stat),
        'p_value': float(p_value),
        'tau2': float(tau2),
        'I2': float(I2),
        'Q': float(Q),
        'winsorized_effects': effects_winsorized.tolist(),
        'original_effects': effects.tolist(),
        'n_winsorized': int(n_winsorized),
        'lower_threshold': float(lower_threshold),
        'upper_threshold': float(upper_threshold),
        'percentile': percentile,
        'n_studies': n_studies,
        'method': 'Winsorized meta-analysis',
        'reference': 'Baker & Jackson (2013), Research Synthesis Methods'
    }


def trimmed_meta_analysis(
    effects: np.ndarray,
    variances: np.ndarray,
    trim_proportion: float = 0.1
) -> Dict[str, Any]:
    """
    Meta-analysis with trimmed effect sizes.

    Removes extreme values before analysis.

    Args:
        effects: Effect sizes
        variances: Within-study variances
        trim_proportion: Proportion to trim from each tail (0-0.5)

    Returns:
        Meta-analysis results with trimmed data
    """
    n_studies = len(effects)

    # Calculate trim thresholds
    n_trim = int(n_studies * trim_proportion)

    # Sort by effect size
    sort_idx = np.argsort(effects)
    effects_sorted = effects[sort_idx]
    variances_sorted = variances[sort_idx]

    # Trim extremes
    if n_trim > 0:
        effects_trimmed = effects_sorted[n_trim:-n_trim]
        variances_trimmed = variances_sorted[n_trim:-n_trim]
        trimmed_idx = sort_idx[n_trim:-n_trim]
    else:
        effects_trimmed = effects_sorted
        variances_trimmed = variances_sorted
        trimmed_idx = sort_idx

    n_remaining = len(effects_trimmed)

    # Perform meta-analysis on trimmed data
    weights = 1 / variances_trimmed
    pooled = np.sum(weights * effects_trimmed) / np.sum(weights)

    # Estimate tau²
    Q = np.sum(weights * (effects_trimmed - pooled) ** 2)
    C = np.sum(weights) - np.sum(weights ** 2) / np.sum(weights)
    tau2 = max(0, (Q - (n_remaining - 1)) / C)

    # Random-effects meta-analysis
    re_weights = 1 / (variances_trimmed + tau2)
    pooled_re = np.sum(re_weights * effects_trimmed) / np.sum(re_weights)
    se_re = np.sqrt(1 / np.sum(re_weights))

    # Confidence interval
    ci_low = pooled_re - 1.96 * se_re
    ci_high = pooled_re + 1.96 * se_re

    # Test statistic
    z_stat = pooled_re / se_re
    p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))

    # Heterogeneity
    I2 = max(0, 100 * (Q - (n_remaining - 1)) / Q) if Q > 0 else 0

    return {
        'pooled_effect': float(pooled_re),
        'se': float(se_re),
        'ci_low': float(ci_low),
        'ci_high': float(ci_high),
        'z_statistic': float(z_stat),
        'p_value': float(p_value),
        'tau2': float(tau2),
        'I2': float(I2),
        'Q': float(Q),
        'trimmed_effects': effects_trimmed.tolist(),
        'original_effects': effects.tolist(),
        'n_trimmed': int(n_studies - n_remaining),
        'n_remaining': int(n_remaining),
        'trim_proportion': trim_proportion,
        'trimmed_indices': trimmed_idx.tolist(),
        'n_studies': n_studies,
        'method': 'Trimmed meta-analysis',
        'reference': 'Baker & Jackson (2013), Research Synthesis Methods'
    }


__all__ = [
    'robust_meta_regression',
    'quantile_meta_analysis',
    'winsorized_meta_analysis',
    'trimmed_meta_analysis',
]
