"""
Advanced Meta-Analysis Methods from Statistics Journals
=======================================================

State-of-the-art techniques from:
- Statistics in Medicine
- Journal of the American Statistical Association (JASA)
- BMJ
- Biometrics
- Research Synthesis Methods

Author: PyMeta-CBAMM Development Team
Version: 0.5.0
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import norm, chi2, t
from typing import Dict, Tuple, Optional, List, Any
import logging

logger = logging.getLogger(__name__)

# ===================================================================
# P-UNIFORM METHODS (van Assen et al., 2015)
# ===================================================================

class PUniformMethods:
    """
    P-uniform and P-uniform* methods for publication bias.

    Based on:
    - van Assen, M. A., van Aert, R. C., & Wicherts, J. M. (2015).
      Meta-analysis using effect size distributions of only statistically
      significant studies. Psychological Methods, 20(3), 293.
    - van Aert, R. C., Wicherts, J. M., & van Assen, M. A. (2016).
      Conducting meta-analyses based on p values: Reservations and
      recommendations for applying p-uniform and p-curve.
      Perspectives on Psychological Science, 11(5), 713-729.
    """

    @staticmethod
    def p_uniform(effects: np.ndarray, se: np.ndarray,
                  alpha: float = 0.05) -> Dict[str, Any]:
        """
        P-uniform method for estimating effect size corrected for publication bias.

        Uses only statistically significant studies and tests if their p-values
        are uniformly distributed under the null hypothesis.

        Parameters
        ----------
        effects : np.ndarray
            Effect sizes
        se : np.ndarray
            Standard errors
        alpha : float
            Significance level (default 0.05)

        Returns
        -------
        dict
            P-uniform results including corrected effect estimate
        """
        # Select significant studies
        z_scores = np.abs(effects / se)
        sig_mask = z_scores > norm.ppf(1 - alpha/2)

        if np.sum(sig_mask) < 2:
            return {
                'available': False,
                'reason': 'Fewer than 2 significant studies'
            }

        sig_effects = effects[sig_mask]
        sig_se = se[sig_mask]
        k_sig = len(sig_effects)

        # Transform to p-values (one-tailed, assuming positive effects)
        p_values = 1 - norm.cdf(sig_effects / sig_se)

        # Estimate effect size that makes p-values uniform
        def negative_log_likelihood(theta):
            """Negative log-likelihood for p-uniform"""
            if theta <= 0:
                return 1e10
            # Expected p-values under effect size theta
            expected_z = theta / sig_se
            expected_p = 1 - norm.cdf(expected_z)
            # Transform observed p-values to uniform scale
            transformed_p = p_values / expected_p
            # Log-likelihood of uniform distribution
            ll = -np.sum(np.log(np.clip(transformed_p, 1e-10, 1)))
            return ll

        # Optimize to find effect estimate
        from scipy.optimize import minimize_scalar
        result = minimize_scalar(negative_log_likelihood,
                                bounds=(0, 5 * np.max(sig_effects)),
                                method='bounded')

        p_uniform_estimate = result.x

        # Calculate confidence interval via profile likelihood
        def profile_ll_diff(theta, target_ll_diff=chi2.ppf(0.95, 1)/2):
            return abs(negative_log_likelihood(theta) - result.fun - target_ll_diff)

        # Find CI bounds
        from scipy.optimize import brentq
        try:
            ci_low = brentq(profile_ll_diff, 0, p_uniform_estimate, xtol=1e-6)
            ci_high = brentq(profile_ll_diff, p_uniform_estimate, 5*p_uniform_estimate, xtol=1e-6)
        except:
            ci_low, ci_high = np.nan, np.nan

        # Test for publication bias (uniformity test)
        # Transform p-values assuming estimated effect
        expected_z_est = p_uniform_estimate / sig_se
        expected_p_est = 1 - norm.cdf(expected_z_est)
        transformed_p_est = p_values / expected_p_est

        # Kolmogorov-Smirnov test for uniformity
        ks_stat, ks_p = stats.kstest(transformed_p_est, 'uniform')

        return {
            'estimate': float(p_uniform_estimate),
            'ci_low': float(ci_low),
            'ci_high': float(ci_high),
            'k_significant': int(k_sig),
            'k_total': len(effects),
            'publication_bias_test_p': float(ks_p),
            'publication_bias_detected': ks_p < 0.05,
            'method': 'p-uniform',
            'available': True,
            'interpretation': (
                f"P-uniform estimate = {p_uniform_estimate:.3f} "
                f"(based on {k_sig}/{len(effects)} significant studies). "
                f"Publication bias {'detected' if ks_p < 0.05 else 'not detected'} (p={ks_p:.3f})"
            )
        }

    @staticmethod
    def p_uniform_star(effects: np.ndarray, se: np.ndarray,
                       alpha: float = 0.05) -> Dict[str, Any]:
        """
        P-uniform* method - extension that uses all studies.

        Improvement over p-uniform that includes non-significant studies.
        More efficient and less biased than original p-uniform.

        Based on:
        van Aert, R. C., & van Assen, M. A. (2018). p-uniform* :
        Publication bias examined and corrected with p-values.
        """
        if len(effects) < 3:
            return {
                'available': False,
                'reason': 'Fewer than 3 studies required'
            }

        # Calculate z-scores
        z_scores = effects / se

        # Likelihood function using all studies
        def negative_log_likelihood_star(theta):
            """Negative log-likelihood for p-uniform*"""
            if theta <= 0:
                return 1e10

            ll = 0
            for z, s in zip(z_scores, se):
                # Expected z under effect theta
                expected_z = theta / s
                # p-value under H0: theta=0
                p_obs = 2 * (1 - norm.cdf(abs(z)))
                # p-value under H1: theta=theta
                p_exp = 2 * (1 - norm.cdf(abs(z - expected_z)))

                # Avoid log(0)
                p_exp = max(p_exp, 1e-10)
                ll += np.log(p_exp / max(p_obs, 1e-10))

            return -ll

        # Optimize
        from scipy.optimize import minimize_scalar
        result = minimize_scalar(negative_log_likelihood_star,
                                bounds=(0, 5 * np.max(np.abs(effects))),
                                method='bounded')

        p_uniform_star_estimate = result.x

        # Confidence interval via profile likelihood
        def profile_ll_diff(theta, target_ll_diff=chi2.ppf(0.95, 1)/2):
            return abs(negative_log_likelihood_star(theta) - result.fun - target_ll_diff)

        try:
            ci_low = brentq(profile_ll_diff, 0, p_uniform_star_estimate, xtol=1e-6)
            ci_high = brentq(profile_ll_diff, p_uniform_star_estimate,
                           5*p_uniform_star_estimate, xtol=1e-6)
        except:
            ci_low, ci_high = np.nan, np.nan

        # Likelihood ratio test for publication bias
        # Compare with naive random-effects estimate
        naive_pooled = np.sum(effects / se**2) / np.sum(1 / se**2)
        ll_naive = -negative_log_likelihood_star(naive_pooled)
        ll_punif = -result.fun
        lr_stat = 2 * (ll_punif - ll_naive)
        lr_p = 1 - chi2.cdf(lr_stat, 1) if lr_stat > 0 else 1.0

        return {
            'estimate': float(p_uniform_star_estimate),
            'ci_low': float(ci_low),
            'ci_high': float(ci_high),
            'k_studies': len(effects),
            'naive_estimate': float(naive_pooled),
            'publication_bias_test_p': float(lr_p),
            'publication_bias_detected': lr_p < 0.05,
            'method': 'p-uniform*',
            'available': True,
            'interpretation': (
                f"P-uniform* estimate = {p_uniform_star_estimate:.3f} "
                f"(vs naive {naive_pooled:.3f}). "
                f"Publication bias {'detected' if lr_p < 0.05 else 'not detected'} (p={lr_p:.3f})"
            )
        }


# ===================================================================
# SELECTION MODELS (Vevea & Hedges, 1995; Hedges & Vevea, 2005)
# ===================================================================

class SelectionModels:
    """
    Selection models for publication bias.

    Based on:
    - Vevea, J. L., & Hedges, L. V. (1995). A general linear model for
      estimating effect size in the presence of publication bias.
      Psychometrika, 60(3), 419-435.
    - Hedges, L. V., & Vevea, J. L. (2005). Selection method approaches.
      In H. R. Rothstein, A. J. Sutton, & M. Borenstein (Eds.),
      Publication bias in meta-analysis (pp. 145-174).
    """

    @staticmethod
    def three_parameter_selection_model(effects: np.ndarray, se: np.ndarray,
                                       alpha: float = 0.05) -> Dict[str, Any]:
        """
        3-parameter selection model (3PSM).

        Models probability of publication as a function of p-value.
        Divides p-value space into regions with different selection probabilities.

        Parameters
        ----------
        effects : np.ndarray
            Effect sizes
        se : np.ndarray
            Standard errors
        alpha : float
            Significance threshold

        Returns
        -------
        dict
            Selection model results
        """
        if len(effects) < 5:
            return {
                'available': False,
                'reason': 'At least 5 studies required'
            }

        # Calculate p-values (two-tailed)
        z_scores = np.abs(effects / se)
        p_values = 2 * (1 - norm.cdf(z_scores))

        # Classify studies by p-value region
        # Region 1: p < alpha (significant)
        # Region 2: alpha <= p < 0.50
        # Region 3: p >= 0.50
        region_1 = p_values < alpha
        region_2 = (p_values >= alpha) & (p_values < 0.50)
        region_3 = p_values >= 0.50

        n_region = [np.sum(region_1), np.sum(region_2), np.sum(region_3)]

        if n_region[0] < 2:
            return {
                'available': False,
                'reason': 'Too few significant studies'
            }

        # Maximum likelihood estimation
        def negative_log_likelihood(params):
            """
            Negative log-likelihood for 3PSM.

            params: [mu, tau, w1, w2]
            - mu: mean effect
            - tau: between-study heterogeneity
            - w1: selection weight for region 2 relative to region 1
            - w2: selection weight for region 3 relative to region 1
            """
            mu, tau, w1, w2 = params

            if tau < 0 or w1 < 0 or w2 < 0:
                return 1e10

            ll = 0
            for i, (y, v) in enumerate(zip(effects, se**2)):
                # Total variance
                total_var = v + tau**2

                # Likelihood of observing this effect
                likelihood_y = norm.pdf(y, mu, np.sqrt(total_var))

                # Selection probability based on p-value region
                if region_1[i]:
                    weight = 1.0
                elif region_2[i]:
                    weight = w1
                else:
                    weight = w2

                # Contribution to log-likelihood
                ll += np.log(likelihood_y * weight + 1e-10)

            return -ll

        # Initial values
        naive_effect = np.mean(effects)
        naive_tau = np.std(effects) if len(effects) > 1 else 0.1
        initial = [naive_effect, naive_tau, 0.5, 0.1]

        # Optimize
        from scipy.optimize import minimize
        result = minimize(negative_log_likelihood, initial,
                         bounds=[(-5, 5), (0, 2), (0, 1), (0, 1)],
                         method='L-BFGS-B')

        mu_est, tau_est, w1_est, w2_est = result.x

        # Calculate standard errors via Hessian
        try:
            from scipy.optimize import approx_fprime
            hessian = np.zeros((4, 4))
            eps = np.sqrt(np.finfo(float).eps)
            for i in range(4):
                for j in range(4):
                    def f1(x):
                        p = result.x.copy()
                        p[i] += eps
                        return negative_log_likelihood(p)
                    def f2(x):
                        p = result.x.copy()
                        p[j] += eps
                        return negative_log_likelihood(p)
                    hessian[i, j] = (f1(0) + f2(0) - 2*negative_log_likelihood(result.x)) / eps**2

            cov_matrix = np.linalg.inv(hessian)
            se_mu = np.sqrt(cov_matrix[0, 0])
        except:
            se_mu = np.nan

        # Confidence interval
        ci_low = mu_est - 1.96 * se_mu if not np.isnan(se_mu) else np.nan
        ci_high = mu_est + 1.96 * se_mu if not np.isnan(se_mu) else np.nan

        # Interpret selection weights
        bias_severity = 'severe' if w1_est < 0.3 else 'moderate' if w1_est < 0.6 else 'mild'

        return {
            'estimate': float(mu_est),
            'tau': float(tau_est),
            'se': float(se_mu) if not np.isnan(se_mu) else None,
            'ci_low': float(ci_low) if not np.isnan(ci_low) else None,
            'ci_high': float(ci_high) if not np.isnan(ci_high) else None,
            'weight_moderate': float(w1_est),  # p in [0.05, 0.50]
            'weight_high': float(w2_est),      # p >= 0.50
            'n_regions': n_region,
            'bias_severity': bias_severity,
            'method': '3PSM',
            'available': True,
            'interpretation': (
                f"3PSM estimate = {mu_est:.3f}, τ = {tau_est:.3f}. "
                f"Selection weights: sig=1.00, moderate={w1_est:.2f}, "
                f"non-sig={w2_est:.2f}. {bias_severity.capitalize()} publication bias."
            )
        }


# ===================================================================
# LIMIT META-ANALYSIS (Rücker et al., 2011)
# ===================================================================

class LimitMetaAnalysis:
    """
    Limit meta-analysis for detecting small-study effects.

    Based on:
    - Rücker, G., Schwarzer, G., Carpenter, J., & Olkin, I. (2011).
      Why add anything to nothing? The arcsine difference as a measure of
      treatment effect in meta-analysis with zero cells.
      Statistics in Medicine, 30(7), 721-734.
    """

    @staticmethod
    def limit_meta_analysis(effects: np.ndarray, se: np.ndarray) -> Dict[str, Any]:
        """
        Limit meta-analysis extrapolates to infinite precision.

        Estimates effect size at the limit of infinite precision (SE → 0),
        which corresponds to an unbiased estimate if small-study effects
        are present.

        Parameters
        ----------
        effects : np.ndarray
            Effect sizes
        se : np.ndarray
            Standard errors

        Returns
        -------
        dict
            Limit meta-analysis results
        """
        if len(effects) < 5:
            return {
                'available': False,
                'reason': 'At least 5 studies required'
            }

        # Weight by inverse variance
        weights = 1 / se**2

        # Regress effect on SE
        from scipy.stats import linregress
        slope, intercept, r_value, p_value, std_err = linregress(se, effects)

        # Limit estimate is the intercept (effect when SE = 0)
        limit_estimate = intercept
        limit_se = std_err

        # Confidence interval
        df = len(effects) - 2
        t_crit = t.ppf(0.975, df)
        ci_low = limit_estimate - t_crit * limit_se
        ci_high = limit_estimate + t_crit * limit_se

        # Compare with naive random-effects
        naive_estimate = np.sum(weights * effects) / np.sum(weights)
        difference = abs(limit_estimate - naive_estimate)

        # Test for small-study effects
        small_study_effect_detected = p_value < 0.10  # Slope significantly different from 0

        return {
            'limit_estimate': float(limit_estimate),
            'limit_se': float(limit_se),
            'ci_low': float(ci_low),
            'ci_high': float(ci_high),
            'naive_estimate': float(naive_estimate),
            'difference': float(difference),
            'slope': float(slope),
            'slope_p_value': float(p_value),
            'small_study_effect_detected': small_study_effect_detected,
            'r_squared': float(r_value**2),
            'method': 'limit_meta_analysis',
            'available': True,
            'interpretation': (
                f"Limit estimate (SE→0) = {limit_estimate:.3f} "
                f"(vs naive {naive_estimate:.3f}, diff={difference:.3f}). "
                f"Small-study effects {'detected' if small_study_effect_detected else 'not detected'} "
                f"(slope p={p_value:.3f})."
            )
        }


# Helper function for brentq import
from scipy.optimize import brentq

__all__ = [
    'PUniformMethods',
    'SelectionModels',
    'LimitMetaAnalysis',
]
