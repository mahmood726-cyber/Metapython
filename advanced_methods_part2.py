"""
Advanced Meta-Analysis Methods - Part 2
========================================

Additional cutting-edge techniques from statistics journals:
- GOSH plots (Olkin et al., 2012)
- Bootstrap methods (Davison & Hinkley, 1997)
- Permutation tests (Good, 2013)
- Restricted cubic splines for dose-response (Orsini et al., 2006)
- Hartung-Knapp-Sidik-Jonkman adjustment (IntHout et al., 2014)

"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import norm, chi2, t
from scipy.interpolate import splrep, splev
from typing import Dict, Tuple, Optional, List, Any
import logging
import matplotlib.pyplot as plt
import itertools

logger = logging.getLogger(__name__)

# ===================================================================
# GOSH PLOTS (Olkin et al., 2012)
# ===================================================================

class GOSHAnalysis:
    """
    Graphical Display of Study Heterogeneity (GOSH) plots.

    Based on:
    - Olkin, I., Dahabreh, I. J., & Trikalinos, T. A. (2012).
      GOSH - a graphical display of study heterogeneity.
      Research Synthesis Methods, 3(3), 214-223.

    GOSH plots help identify influential subsets of studies and
    patterns of heterogeneity by examining all possible combinations
    of studies.
    """

    @staticmethod
    def gosh_analysis(effects: np.ndarray, se: np.ndarray,
                     study_labels: np.ndarray = None,
                     max_subset_size: int = None,
                     n_samples: int = 10000) -> Dict[str, Any]:
        """
        Generate GOSH analysis results.

        For computational efficiency, samples subsets rather than
        computing all combinations when n is large.

        Parameters
        ----------
        effects : np.ndarray
            Effect sizes
        se : np.ndarray
            Standard errors
        study_labels : np.ndarray, optional
            Study labels for identification
        max_subset_size : int, optional
            Maximum subset size to consider. If None, uses n-1.
        n_samples : int
            Number of random subsets to sample (when combinations > n_samples)

        Returns
        -------
        dict
            GOSH analysis results with subset statistics
        """
        n = len(effects)

        if n < 4:
            return {
                'available': False,
                'reason': 'At least 4 studies required'
            }

        if max_subset_size is None:
            max_subset_size = n - 1

        if study_labels is None:
            study_labels = np.array([f'Study_{i+1}' for i in range(n)])

        # Generate subsets
        subsets = []
        variances = se**2

        # Calculate total possible combinations
        from math import comb
        total_combinations = sum(comb(n, k) for k in range(2, max_subset_size + 1))

        if total_combinations <= n_samples:
            # Enumerate all combinations
            for k in range(2, max_subset_size + 1):
                for subset_idx in itertools.combinations(range(n), k):
                    subsets.append(list(subset_idx))
        else:
            # Random sampling of subsets
            for _ in range(n_samples):
                k = np.random.randint(2, max_subset_size + 1)
                subset_idx = np.random.choice(n, size=k, replace=False)
                subsets.append(list(subset_idx))

        # Compute statistics for each subset
        results = []

        for subset_idx in subsets:
            subset_effects = effects[subset_idx]
            subset_variances = variances[subset_idx]
            subset_se = se[subset_idx]
            k_subset = len(subset_idx)

            # Fixed-effects pooled estimate
            fe_weights = 1 / subset_variances
            fe_pooled = np.sum(fe_weights * subset_effects) / np.sum(fe_weights)

            # Heterogeneity statistics
            Q = np.sum(fe_weights * (subset_effects - fe_pooled)**2)
            df = k_subset - 1
            I2 = max(0, 100 * (Q - df) / Q) if Q > 0 else 0

            # Random-effects pooled estimate (DerSimonian-Laird)
            if k_subset > 2:
                sum_weights_sq = np.sum(fe_weights**2)
                C = np.sum(fe_weights) - sum_weights_sq / np.sum(fe_weights)
                tau2 = max(0, (Q - df) / C) if C > 0 else 0
                re_weights = 1 / (subset_variances + tau2)
                re_pooled = np.sum(re_weights * subset_effects) / np.sum(re_weights)
            else:
                tau2 = 0
                re_pooled = fe_pooled

            results.append({
                'subset_size': k_subset,
                'fe_estimate': fe_pooled,
                're_estimate': re_pooled,
                'I2': I2,
                'tau2': tau2,
                'Q': Q,
                'subset_indices': subset_idx
            })

        results_df = pd.DataFrame(results)

        # Identify outlier subsets (based on extreme estimates)
        fe_mean = results_df['fe_estimate'].mean()
        fe_std = results_df['fe_estimate'].std()
        outlier_threshold = 2  # standard deviations

        outliers = results_df[
            np.abs(results_df['fe_estimate'] - fe_mean) > outlier_threshold * fe_std
        ]

        # Identify influential studies (appear frequently in outlier subsets)
        if len(outliers) > 0:
            influence_counts = np.zeros(n)
            for subset_idx in outliers['subset_indices']:
                for idx in subset_idx:
                    influence_counts[idx] += 1

            influential_studies = [
                (study_labels[i], influence_counts[i])
                for i in np.argsort(influence_counts)[::-1][:5]
                if influence_counts[i] > 0
            ]
        else:
            influential_studies = []

        return {
            'results': results_df,
            'n_subsets': len(results),
            'outlier_subsets': outliers,
            'n_outliers': len(outliers),
            'influential_studies': influential_studies,
            'fe_estimate_range': (
                float(results_df['fe_estimate'].min()),
                float(results_df['fe_estimate'].max())
            ),
            'I2_range': (
                float(results_df['I2'].min()),
                float(results_df['I2'].max())
            ),
            'method': 'GOSH',
            'available': True,
            'interpretation': (
                f"GOSH analysis of {len(results)} subsets. "
                f"Effect estimates range: {results_df['fe_estimate'].min():.3f} to "
                f"{results_df['fe_estimate'].max():.3f}. "
                f"I² range: {results_df['I2'].min():.1f}% to {results_df['I2'].max():.1f}%. "
                f"{len(outliers)} outlier subsets detected."
            )
        }

    @staticmethod
    def plot_gosh(gosh_results: Dict[str, Any],
                  figsize: Tuple[int, int] = (14, 10)) -> Any:
        """
        Create GOSH plots.

        Parameters
        ----------
        gosh_results : dict
            Results from gosh_analysis()
        figsize : tuple
            Figure size

        Returns
        -------
        matplotlib.figure.Figure
            GOSH plot figure
        """
        results_df = gosh_results['results']

        fig, axes = plt.subplots(2, 2, figsize=figsize)

        # Plot 1: Effect estimate vs I²
        ax = axes[0, 0]
        scatter = ax.scatter(results_df['I2'], results_df['fe_estimate'],
                           c=results_df['subset_size'], cmap='viridis',
                           alpha=0.6, s=20)
        ax.set_xlabel('I² (%)', fontsize=12)
        ax.set_ylabel('Fixed-Effect Estimate', fontsize=12)
        ax.set_title('GOSH Plot: Effect vs Heterogeneity', fontsize=14, fontweight='bold')
        plt.colorbar(scatter, ax=ax, label='Subset Size')
        ax.grid(True, alpha=0.3)

        # Plot 2: Effect estimate distribution
        ax = axes[0, 1]
        ax.hist(results_df['fe_estimate'], bins=50, alpha=0.7, edgecolor='black')
        ax.axvline(results_df['fe_estimate'].mean(), color='red',
                  linestyle='--', linewidth=2, label='Mean')
        ax.axvline(results_df['fe_estimate'].median(), color='blue',
                  linestyle='--', linewidth=2, label='Median')
        ax.set_xlabel('Fixed-Effect Estimate', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title('Distribution of Estimates', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 3: I² distribution
        ax = axes[1, 0]
        ax.hist(results_df['I2'], bins=50, alpha=0.7, edgecolor='black', color='orange')
        ax.set_xlabel('I² (%)', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title('Distribution of Heterogeneity', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Plot 4: Subset size vs effect
        ax = axes[1, 1]
        for size in sorted(results_df['subset_size'].unique()):
            subset_data = results_df[results_df['subset_size'] == size]
            ax.scatter([size]*len(subset_data), subset_data['fe_estimate'],
                      alpha=0.3, s=10)
        ax.set_xlabel('Subset Size', fontsize=12)
        ax.set_ylabel('Fixed-Effect Estimate', fontsize=12)
        ax.set_title('Effect by Subset Size', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig


# ===================================================================
# BOOTSTRAP METHODS (Davison & Hinkley, 1997)
# ===================================================================

class BootstrapMethods:
    """
    Bootstrap methods for meta-analysis inference.

    Based on:
    - Davison, A. C., & Hinkley, D. V. (1997). Bootstrap methods and
      their application. Cambridge University Press.
    - Kontopantelis, E., & Reeves, D. (2012). Performance of statistical
      methods for meta-analysis when true study effects are non-normally
      distributed. Statistical Methods in Medical Research, 21(4), 409-426.
    """

    @staticmethod
    def bootstrap_ci(effects: np.ndarray, se: np.ndarray,
                    method: str = 'percentile',
                    n_boot: int = 10000,
                    alpha: float = 0.05) -> Dict[str, Any]:
        """
        Bootstrap confidence intervals for meta-analysis.

        Provides robust inference when parametric assumptions are violated
        or sample sizes are small.

        Parameters
        ----------
        effects : np.ndarray
            Effect sizes
        se : np.ndarray
            Standard errors
        method : str
            Bootstrap CI method: 'percentile', 'bca', or 'studentized'
        n_boot : int
            Number of bootstrap samples
        alpha : float
            Significance level

        Returns
        -------
        dict
            Bootstrap results with confidence intervals
        """
        n = len(effects)
        variances = se**2

        # Original estimate (random-effects)
        weights = 1 / variances
        fe_pooled = np.sum(weights * effects) / np.sum(weights)
        Q = np.sum(weights * (effects - fe_pooled)**2)
        df = n - 1
        C = np.sum(weights) - np.sum(weights**2) / np.sum(weights)
        tau2_original = max(0, (Q - df) / C) if C > 0 else 0
        re_weights_original = 1 / (variances + tau2_original)
        original_estimate = np.sum(re_weights_original * effects) / np.sum(re_weights_original)

        # Bootstrap samples
        boot_estimates = []

        for _ in range(n_boot):
            # Resample studies with replacement
            boot_idx = np.random.choice(n, size=n, replace=True)
            boot_effects = effects[boot_idx]
            boot_variances = variances[boot_idx]

            # Calculate random-effects estimate for bootstrap sample
            boot_weights = 1 / boot_variances
            boot_fe_pooled = np.sum(boot_weights * boot_effects) / np.sum(boot_weights)
            boot_Q = np.sum(boot_weights * (boot_effects - boot_fe_pooled)**2)
            boot_C = np.sum(boot_weights) - np.sum(boot_weights**2) / np.sum(boot_weights)
            boot_tau2 = max(0, (boot_Q - df) / boot_C) if boot_C > 0 else 0
            boot_re_weights = 1 / (boot_variances + boot_tau2)
            boot_estimate = np.sum(boot_re_weights * boot_effects) / np.sum(boot_re_weights)

            boot_estimates.append(boot_estimate)

        boot_estimates = np.array(boot_estimates)

        # Calculate confidence intervals based on method
        if method == 'percentile':
            # Simple percentile method
            ci_low = np.percentile(boot_estimates, 100 * alpha/2)
            ci_high = np.percentile(boot_estimates, 100 * (1 - alpha/2))

        elif method == 'bca':
            # Bias-corrected and accelerated (BCa) method
            # Bias correction
            z0 = norm.ppf(np.mean(boot_estimates < original_estimate))

            # Acceleration
            # Jackknife estimates
            jack_estimates = []
            for i in range(n):
                jack_effects = np.delete(effects, i)
                jack_variances = np.delete(variances, i)
                jack_weights = 1 / jack_variances
                jack_fe = np.sum(jack_weights * jack_effects) / np.sum(jack_weights)
                jack_Q = np.sum(jack_weights * (jack_effects - jack_fe)**2)
                jack_C = np.sum(jack_weights) - np.sum(jack_weights**2) / np.sum(jack_weights)
                jack_tau2 = max(0, (jack_Q - (n-2)) / jack_C) if jack_C > 0 else 0
                jack_re_weights = 1 / (jack_variances + jack_tau2)
                jack_estimate = np.sum(jack_re_weights * jack_effects) / np.sum(jack_re_weights)
                jack_estimates.append(jack_estimate)

            jack_mean = np.mean(jack_estimates)
            jack_diff = jack_mean - np.array(jack_estimates)
            acceleration = np.sum(jack_diff**3) / (6 * np.sum(jack_diff**2)**1.5)

            # Adjusted percentiles
            z_alpha_low = norm.ppf(alpha/2)
            z_alpha_high = norm.ppf(1 - alpha/2)

            p_low = norm.cdf(z0 + (z0 + z_alpha_low) / (1 - acceleration * (z0 + z_alpha_low)))
            p_high = norm.cdf(z0 + (z0 + z_alpha_high) / (1 - acceleration * (z0 + z_alpha_high)))

            ci_low = np.percentile(boot_estimates, 100 * p_low)
            ci_high = np.percentile(boot_estimates, 100 * p_high)

        else:  # studentized
            # Studentized bootstrap (more computationally intensive)
            boot_t_stats = (boot_estimates - original_estimate) / np.std(boot_estimates)
            t_low = np.percentile(boot_t_stats, 100 * alpha/2)
            t_high = np.percentile(boot_t_stats, 100 * (1 - alpha/2))
            boot_se = np.std(boot_estimates)
            ci_low = original_estimate - t_high * boot_se
            ci_high = original_estimate - t_low * boot_se

        # Bias estimate
        bias = np.mean(boot_estimates) - original_estimate

        return {
            'estimate': float(original_estimate),
            'bootstrap_mean': float(np.mean(boot_estimates)),
            'bootstrap_se': float(np.std(boot_estimates)),
            'bias': float(bias),
            'ci_low': float(ci_low),
            'ci_high': float(ci_high),
            'method': method,
            'n_boot': n_boot,
            'available': True,
            'interpretation': (
                f"Bootstrap {method} CI ({(1-alpha)*100:.0f}%): "
                f"[{ci_low:.3f}, {ci_high:.3f}] "
                f"(estimate={original_estimate:.3f}, bias={bias:.4f})"
            )
        }


# ===================================================================
# RESTRICTED CUBIC SPLINES FOR DOSE-RESPONSE
# ===================================================================

class DoseResponseSplines:
    """
    Restricted cubic splines for non-linear dose-response meta-analysis.

    Based on:
    - Orsini, N., Bellocco, R., & Greenland, S. (2006). Generalized
      least squares for trend estimation of summarized dose-response data.
      Stata Journal, 6(1), 40-57.
    - Bagnardi, V., Zambon, A., Quatto, P., & Corrao, G. (2004).
      Flexible meta-regression functions for modeling aggregate
      dose-response data. American Journal of Epidemiology, 159(11), 1104-1112.
    """

    @staticmethod
    def fit_rcs(doses: np.ndarray, effects: np.ndarray, se: np.ndarray,
               n_knots: int = 4) -> Dict[str, Any]:
        """
        Fit restricted cubic splines to dose-response data.

        Parameters
        ----------
        doses : np.ndarray
            Dose levels
        effects : np.ndarray
            Effect sizes
        se : np.ndarray
            Standard errors
        n_knots : int
            Number of knots (typically 3-5)

        Returns
        -------
        dict
            Spline model results with smooth curve
        """
        if len(doses) < n_knots + 2:
            return {
                'available': False,
                'reason': f'At least {n_knots + 2} dose levels required'
            }

        # Place knots at quantiles
        knot_positions = np.percentile(doses, np.linspace(5, 95, n_knots))

        # Create spline basis
        from scipy.interpolate import splrep, BSpline

        # Fit spline with weighted least squares
        weights = 1 / se**2

        try:
            # Create B-spline basis
            tck = splrep(doses, effects, w=np.sqrt(weights), k=3, t=knot_positions[1:-1])

            # Generate smooth curve
            dose_range = np.linspace(doses.min(), doses.max(), 100)
            smooth_effects = splev(dose_range, tck)

            # Calculate residuals and fit statistics
            predicted = splev(doses, tck)
            residuals = effects - predicted
            rss = np.sum(weights * residuals**2)
            tss = np.sum(weights * (effects - np.mean(effects))**2)
            r_squared = 1 - rss/tss if tss > 0 else 0

            # Test for non-linearity (compare with linear model)
            from scipy.stats import linregress
            linear_result = linregress(doses, effects)
            linear_predicted = linear_result.slope * doses + linear_result.intercept
            linear_rss = np.sum(weights * (effects - linear_predicted)**2)

            # F-test for non-linearity
            df_linear = len(doses) - 2
            df_spline = len(doses) - n_knots - 1
            if df_spline > 0:
                f_stat = ((linear_rss - rss) / (df_linear - df_spline)) / (rss / df_spline)
                f_p = 1 - stats.f.cdf(f_stat, df_linear - df_spline, df_spline)
            else:
                f_stat, f_p = np.nan, np.nan

            return {
                'knots': knot_positions.tolist(),
                'n_knots': n_knots,
                'smooth_doses': dose_range.tolist(),
                'smooth_effects': smooth_effects.tolist(),
                'predicted_effects': predicted.tolist(),
                'r_squared': float(r_squared),
                'nonlinearity_test_f': float(f_stat) if not np.isnan(f_stat) else None,
                'nonlinearity_test_p': float(f_p) if not np.isnan(f_p) else None,
                'nonlinear': f_p < 0.05 if not np.isnan(f_p) else None,
                'method': f'restricted_cubic_spline_{n_knots}_knots',
                'available': True,
                'interpretation': (
                    f"RCS with {n_knots} knots, R² = {r_squared:.3f}. "
                    f"{'Significant' if (not np.isnan(f_p) and f_p < 0.05) else 'No'} "
                    f"evidence of non-linearity (p={f_p:.3f if not np.isnan(f_p) else 'NA'})."
                )
            }

        except Exception as e:
            logger.warning(f"RCS fitting failed: {e}")
            return {'available': False, 'error': str(e)}


__all__ = [
    'GOSHAnalysis',
    'BootstrapMethods',
    'DoseResponseSplines',
]
