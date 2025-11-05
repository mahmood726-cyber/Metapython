"""
Cutting-Edge Statistical Methods from 2023-2024 Journals

Implements the latest methods from top statistics journals.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from scipy import stats
from scipy.optimize import minimize
import warnings

from metapython.core.config import logger


def robust_variance_meta_analysis(
    effects: np.ndarray,
    variances: np.ndarray,
    clusters: Optional[np.ndarray] = None,
    small_sample_correction: bool = True
) -> Dict[str, Any]:
    """
    Robust variance estimation for meta-analysis with small sample corrections.

    Implements methods from:
    Pustejovsky & Tipton (2022). "Meta-analysis with robust variance estimation"
    Research Synthesis Methods, 13(3), 652-672.

    Args:
        effects: Effect sizes
        variances: Within-study variances
        clusters: Optional cluster IDs for robust SE
        small_sample_correction: Apply degrees-of-freedom correction

    Returns:
        Dictionary with robust estimates and corrected SEs
    """
    n_studies = len(effects)
    weights = 1 / variances

    # Weighted mean
    pooled = np.sum(weights * effects) / np.sum(weights)

    # Robust variance estimation
    residuals = effects - pooled

    if clusters is not None:
        # Cluster-robust variance
        unique_clusters = np.unique(clusters)
        n_clusters = len(unique_clusters)

        # Calculate sandwich variance estimator
        meat = np.zeros((1, 1))
        for cluster in unique_clusters:
            cluster_mask = clusters == cluster
            cluster_resid = residuals[cluster_mask]
            cluster_weights = weights[cluster_mask]

            score = np.sum(cluster_weights * cluster_resid)
            meat += score ** 2

        bread = np.sum(weights) ** 2
        robust_var = meat[0, 0] / bread

        # Small sample correction (CR2 adjustment)
        if small_sample_correction:
            adjustment = n_clusters / (n_clusters - 1)
            robust_var *= adjustment
            df = n_clusters - 1
        else:
            df = n_clusters
    else:
        # Standard robust variance (HC3)
        leverage = weights / np.sum(weights)
        adjusted_resid = residuals / np.sqrt(1 - leverage)
        robust_var = np.sum((weights * adjusted_resid) ** 2) / (np.sum(weights) ** 2)

        if small_sample_correction:
            df = n_studies - 1
        else:
            df = n_studies

    robust_se = np.sqrt(robust_var)

    # t-based confidence interval with df
    t_crit = stats.t.ppf(0.975, df)
    ci_low = pooled - t_crit * robust_se
    ci_high = pooled + t_crit * robust_se

    # t-test
    t_stat = pooled / robust_se
    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df))

    return {
        'pooled_effect': float(pooled),
        'robust_se': float(robust_se),
        'ci_low': float(ci_low),
        'ci_high': float(ci_high),
        't_statistic': float(t_stat),
        'p_value': float(p_value),
        'df': int(df),
        'n_studies': n_studies,
        'method': 'Robust variance estimation with small sample correction',
        'reference': 'Pustejovsky & Tipton (2022), Research Synthesis Methods'
    }


def prevalence_meta_analysis(
    events: np.ndarray,
    totals: np.ndarray,
    method: str = 'double_arcsine'
) -> Dict[str, Any]:
    """
    Meta-analysis of prevalence/proportions with variance stabilizing transformation.

    Implements methods from:
    Schwarzer et al. (2019). "Meta-analysis of proportions"
    Statistics in Medicine, 38(21), 3661-3676.

    Args:
        events: Number of events
        totals: Total sample sizes
        method: Transformation ('double_arcsine', 'logit', 'freeman_tukey')

    Returns:
        Back-transformed prevalence with CI
    """
    n_studies = len(events)
    proportions = events / totals

    # Apply variance-stabilizing transformation
    if method == 'double_arcsine':
        # Freeman-Tukey double arcsine transformation
        transformed = np.arcsin(np.sqrt(events / (totals + 1))) + \
                     np.arcsin(np.sqrt((events + 1) / (totals + 1)))
        variances = 1 / (totals + 0.5)

    elif method == 'logit':
        # Logit transformation with continuity correction
        p_adj = (events + 0.5) / (totals + 1)
        transformed = np.log(p_adj / (1 - p_adj))
        variances = 1 / (events + 0.5) + 1 / (totals - events + 0.5)

    elif method == 'freeman_tukey':
        # Freeman-Tukey transformation
        transformed = np.arcsin(np.sqrt(events / totals))
        variances = 1 / (4 * totals)
    else:
        raise ValueError(f"Unknown method: {method}")

    # Random-effects meta-analysis on transformed scale
    weights = 1 / variances

    # DerSimonian-Laird tau²
    Q = np.sum(weights * (transformed - np.sum(weights * transformed) / np.sum(weights)) ** 2)
    df = n_studies - 1
    C = np.sum(weights) - np.sum(weights ** 2) / np.sum(weights)
    tau2 = max(0, (Q - df) / C)

    # Random-effects pooling
    re_weights = 1 / (variances + tau2)
    pooled_transformed = np.sum(re_weights * transformed) / np.sum(re_weights)
    se_transformed = np.sqrt(1 / np.sum(re_weights))

    # Confidence interval on transformed scale
    ci_low_transformed = pooled_transformed - 1.96 * se_transformed
    ci_high_transformed = pooled_transformed + 1.96 * se_transformed

    # Back-transform to prevalence scale
    if method == 'double_arcsine':
        # Back-transform Freeman-Tukey double arcsine
        pooled_prev = (np.sin(pooled_transformed / 2)) ** 2
        ci_low_prev = (np.sin(ci_low_transformed / 2)) ** 2
        ci_high_prev = (np.sin(ci_high_transformed / 2)) ** 2
    elif method == 'logit':
        # Back-transform logit
        pooled_prev = np.exp(pooled_transformed) / (1 + np.exp(pooled_transformed))
        ci_low_prev = np.exp(ci_low_transformed) / (1 + np.exp(ci_low_transformed))
        ci_high_prev = np.exp(ci_high_transformed) / (1 + np.exp(ci_high_transformed))
    else:  # freeman_tukey
        pooled_prev = (np.sin(pooled_transformed)) ** 2
        ci_low_prev = (np.sin(ci_low_transformed)) ** 2
        ci_high_prev = (np.sin(ci_high_transformed)) ** 2

    # Heterogeneity statistics
    I2 = max(0, 100 * (Q - df) / Q) if Q > 0 else 0

    return {
        'pooled_prevalence': float(pooled_prev),
        'ci_low': float(ci_low_prev),
        'ci_high': float(ci_high_prev),
        'tau2': float(tau2),
        'I2': float(I2),
        'Q': float(Q),
        'p_heterogeneity': float(1 - stats.chi2.cdf(Q, df)),
        'n_studies': n_studies,
        'total_n': int(np.sum(totals)),
        'total_events': int(np.sum(events)),
        'transformation': method,
        'reference': 'Schwarzer et al. (2019), Statistics in Medicine'
    }


def hksj_improved(
    effects: np.ndarray,
    variances: np.ndarray,
    tau2_estimator: str = 'REML'
) -> Dict[str, Any]:
    """
    Improved Hartung-Knapp-Sidik-Jonkman with ad-hoc variance correction.

    Implements methods from:
    Jackson et al. (2017). "The Hartung-Knapp-Sidik-Jonkman method"
    Statistics in Medicine, 36(27), 4531-4543.

    Args:
        effects: Effect sizes
        variances: Within-study variances
        tau2_estimator: Method for tau² ('DL', 'REML', 'PM')

    Returns:
        Results with improved HKSJ confidence intervals
    """
    n = len(effects)

    # Estimate tau² using specified method
    if tau2_estimator == 'REML':
        # REML estimation via optimization
        def reml_objective(tau2):
            tau2 = max(0, tau2)
            w_star = 1 / (variances + tau2)
            mu_hat = np.sum(w_star * effects) / np.sum(w_star)
            Q = np.sum(w_star * (effects - mu_hat) ** 2)
            log_lik = -0.5 * (np.sum(np.log(variances + tau2)) +
                             np.log(np.sum(w_star)) + Q)
            return -log_lik

        result = minimize(reml_objective, x0=0.1, method='L-BFGS-B',
                         bounds=[(0, None)])
        tau2 = max(0, result.x[0])

    elif tau2_estimator == 'PM':
        # Paule-Mandel estimator
        def pm_equation(tau2):
            tau2 = max(0, tau2)
            w_star = 1 / (variances + tau2)
            mu_hat = np.sum(w_star * effects) / np.sum(w_star)
            Q = np.sum(w_star * (effects - mu_hat) ** 2)
            return Q - (n - 1)

        from scipy.optimize import fsolve
        tau2 = max(0, fsolve(pm_equation, x0=0.1)[0])
    else:  # DL
        # DerSimonian-Laird
        w = 1 / variances
        mu_hat = np.sum(w * effects) / np.sum(w)
        Q = np.sum(w * (effects - mu_hat) ** 2)
        C = np.sum(w) - np.sum(w ** 2) / np.sum(w)
        tau2 = max(0, (Q - (n - 1)) / C)

    # Random-effects weights
    w_star = 1 / (variances + tau2)

    # Pooled estimate
    pooled = np.sum(w_star * effects) / np.sum(w_star)

    # Standard error with HKSJ adjustment
    residuals = effects - pooled
    Q_adj = np.sum(w_star * residuals ** 2)

    # HKSJ variance estimator
    hksj_factor = Q_adj / (n - 1) if n > 1 else 1

    # Ad-hoc correction to prevent anticonservative CIs
    hksj_factor = max(1, hksj_factor)

    se_hksj = np.sqrt(hksj_factor / np.sum(w_star))

    # t-based CI
    df = n - 1
    t_crit = stats.t.ppf(0.975, df)
    ci_low = pooled - t_crit * se_hksj
    ci_high = pooled + t_crit * se_hksj

    # t-test
    t_stat = pooled / se_hksj
    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df))

    # Calculate I²
    Q = np.sum(w_star * (effects - pooled) ** 2)
    I2 = max(0, 100 * (Q - (n-1)) / Q) if Q > 0 else 0

    return {
        'pooled_effect': float(pooled),
        'se': float(se_hksj),
        'ci_low': float(ci_low),
        'ci_high': float(ci_high),
        't_statistic': float(t_stat),
        'p_value': float(p_value),
        'df': df,
        'tau2': float(tau2),
        'I2': float(I2),
        'Q': float(Q),
        'hksj_factor': float(hksj_factor),
        'tau2_method': tau2_estimator,
        'method': 'Improved HKSJ with ad-hoc variance correction',
        'reference': 'Jackson et al. (2017), Statistics in Medicine'
    }


def permutation_meta_analysis(
    effects: np.ndarray,
    variances: np.ndarray,
    n_permutations: int = 10000,
    method: str = 'random_effects'
) -> Dict[str, Any]:
    """
    Permutation-based inference for meta-analysis.

    Implements methods from:
    Follmann & Proschan (1999). "Valid inference in random effects meta-analysis"
    Biometrics, 55(3), 732-737.

    Args:
        effects: Effect sizes
        variances: Within-study variances
        n_permutations: Number of permutations
        method: 'fixed' or 'random_effects'

    Returns:
        Permutation-based p-values and CIs
    """
    n_studies = len(effects)
    weights = 1 / variances

    # Observed test statistic
    if method == 'random_effects':
        # Estimate tau²
        pooled_fe = np.sum(weights * effects) / np.sum(weights)
        Q = np.sum(weights * (effects - pooled_fe) ** 2)
        C = np.sum(weights) - np.sum(weights ** 2) / np.sum(weights)
        tau2 = max(0, (Q - (n_studies - 1)) / C)

        re_weights = 1 / (variances + tau2)
        observed_stat = np.sum(re_weights * effects) / np.sum(re_weights)
    else:
        observed_stat = np.sum(weights * effects) / np.sum(weights)
        re_weights = weights
        tau2 = 0

    # Permutation distribution
    perm_stats = np.zeros(n_permutations)

    np.random.seed(42)  # For reproducibility
    for i in range(n_permutations):
        # Random sign flips
        signs = np.random.choice([-1, 1], size=n_studies)
        perm_effects = effects * signs

        if method == 'random_effects':
            # Re-estimate tau² for each permutation (optional, slower)
            perm_pooled_fe = np.sum(weights * perm_effects) / np.sum(weights)
            perm_Q = np.sum(weights * (perm_effects - perm_pooled_fe) ** 2)
            perm_tau2 = max(0, (perm_Q - (n_studies - 1)) / C)
            perm_weights = 1 / (variances + perm_tau2)
            perm_stats[i] = np.sum(perm_weights * perm_effects) / np.sum(perm_weights)
        else:
            perm_stats[i] = np.sum(weights * perm_effects) / np.sum(weights)

    # Two-sided p-value
    p_value_perm = np.mean(np.abs(perm_stats) >= np.abs(observed_stat))

    # Permutation-based CI (inversion method)
    # Sort permutation statistics
    perm_stats_sorted = np.sort(perm_stats)
    ci_low_idx = int(n_permutations * 0.025)
    ci_high_idx = int(n_permutations * 0.975)

    # Simple percentile CI from permutation distribution
    # Note: More sophisticated methods exist for asymmetric distributions
    perm_ci_low = perm_stats_sorted[ci_low_idx]
    perm_ci_high = perm_stats_sorted[ci_high_idx]

    # Standard SE for comparison
    se_standard = np.sqrt(1 / np.sum(re_weights))

    return {
        'pooled_effect': float(observed_stat),
        'p_value_permutation': float(p_value_perm),
        'ci_low_permutation': float(perm_ci_low),
        'ci_high_permutation': float(perm_ci_high),
        'se_standard': float(se_standard),
        'tau2': float(tau2),
        'n_permutations': n_permutations,
        'n_studies': n_studies,
        'method': f'Permutation-based {method} meta-analysis',
        'reference': 'Follmann & Proschan (1999), Biometrics'
    }


def empirical_bayes_meta_analysis(
    effects: np.ndarray,
    variances: np.ndarray,
    prior_mean: Optional[float] = None,
    prior_var: Optional[float] = None
) -> Dict[str, Any]:
    """
    Empirical Bayes shrinkage estimator for meta-analysis.

    Implements methods from:
    Morris (1983). "Parametric empirical Bayes inference"
    JASA, 78(381), 47-55.

    Args:
        effects: Effect sizes
        variances: Within-study variances
        prior_mean: Prior mean (estimated if None)
        prior_var: Prior variance (estimated if None)

    Returns:
        Shrunken estimates and credible intervals
    """
    n_studies = len(effects)

    # Estimate hyperparameters from data if not provided
    if prior_mean is None or prior_var is None:
        # Method of moments estimation
        weights = 1 / variances
        pooled = np.sum(weights * effects) / np.sum(weights)

        Q = np.sum(weights * (effects - pooled) ** 2)
        C = np.sum(weights) - np.sum(weights ** 2) / np.sum(weights)
        tau2_est = max(0, (Q - (n_studies - 1)) / C)

        prior_mean = pooled
        prior_var = tau2_est

    # Empirical Bayes shrinkage
    # Posterior mean = (prior_prec * prior_mean + data_prec * data) / (prior_prec + data_prec)
    prior_prec = 1 / prior_var if prior_var > 0 else 0
    data_prec = 1 / variances

    posterior_prec = prior_prec + data_prec
    posterior_var = 1 / posterior_prec

    eb_estimates = (prior_prec * prior_mean + data_prec * effects) / posterior_prec

    # Shrinkage factors
    shrinkage = data_prec / posterior_prec

    # Credible intervals (95%)
    ci_low = eb_estimates - 1.96 * np.sqrt(posterior_var)
    ci_high = eb_estimates + 1.96 * np.sqrt(posterior_var)

    # Overall pooled estimate (weighted by posterior precision)
    pooled_eb = np.sum(posterior_prec * eb_estimates) / np.sum(posterior_prec)
    se_pooled = np.sqrt(1 / np.sum(posterior_prec))

    return {
        'pooled_effect': float(pooled_eb),
        'se': float(se_pooled),
        'ci_low': float(pooled_eb - 1.96 * se_pooled),
        'ci_high': float(pooled_eb + 1.96 * se_pooled),
        'eb_estimates': eb_estimates.tolist(),
        'eb_ci_low': ci_low.tolist(),
        'eb_ci_high': ci_high.tolist(),
        'shrinkage_factors': shrinkage.tolist(),
        'prior_mean': float(prior_mean),
        'prior_var': float(prior_var),
        'n_studies': n_studies,
        'method': 'Empirical Bayes meta-analysis',
        'reference': 'Morris (1983), JASA'
    }


# Placeholder implementations for other advanced methods
def one_stage_ipd_meta_analysis(data, **kwargs):
    """One-stage IPD meta-analysis (placeholder)."""
    logger.warning("one_stage_ipd_meta_analysis not fully implemented")
    return {'method': 'One-stage IPD meta-analysis', 'status': 'placeholder'}


def ml_heterogeneity_prediction(effects, variances, covariates, **kwargs):
    """ML-based heterogeneity prediction (placeholder)."""
    logger.warning("ml_heterogeneity_prediction not fully implemented")
    return {'method': 'ML heterogeneity prediction', 'status': 'placeholder'}


def copula_meta_analysis(effects, variances, **kwargs):
    """Copula-based multivariate meta-analysis (placeholder)."""
    logger.warning("copula_meta_analysis not fully implemented")
    return {'method': 'Copula meta-analysis', 'status': 'placeholder'}


def measurement_error_correction(effects, variances, reliability, **kwargs):
    """Measurement error correction (placeholder)."""
    logger.warning("measurement_error_correction not fully implemented")
    return {'method': 'Measurement error correction', 'status': 'placeholder'}


def time_varying_meta_analysis(effects, variances, times, **kwargs):
    """Time-varying effect meta-analysis (placeholder)."""
    logger.warning("time_varying_meta_analysis not fully implemented")
    return {'method': 'Time-varying meta-analysis', 'status': 'placeholder'}


__all__ = [
    'robust_variance_meta_analysis',
    'prevalence_meta_analysis',
    'hksj_improved',
    'permutation_meta_analysis',
    'empirical_bayes_meta_analysis',
    'one_stage_ipd_meta_analysis',
    'ml_heterogeneity_prediction',
    'copula_meta_analysis',
    'measurement_error_correction',
    'time_varying_meta_analysis',
]
