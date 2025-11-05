"""
Specialized Permutation Tests for Meta-Analysis

Comprehensive permutation tests for:
- Effect size estimation
- Heterogeneity assessment
- Publication bias detection
- Subgroup differences
- Meta-regression
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from scipy import stats

from metapython.permutations.permutation_engine import PermutationEngine, PermutationResult


def permutation_meta_analysis(
    effects: np.ndarray,
    variances: np.ndarray,
    n_permutations: int = 10000,
    method: str = 'sign_flip',
    alternative: str = 'two-sided'
) -> Dict[str, Any]:
    """
    Permutation test for pooled effect in meta-analysis.

    Args:
        effects: Effect sizes
        variances: Within-study variances
        n_permutations: Number of permutations
        method: Permutation method
        alternative: Alternative hypothesis

    Returns:
        Permutation test results
    """
    engine = PermutationEngine(n_permutations=n_permutations)

    def pooled_effect_statistic(data, **kwargs):
        weights = 1 / data['variances']
        return np.sum(weights * data['effects']) / np.sum(weights)

    data = {'effects': effects, 'variances': variances}
    result = engine.run_test(data, pooled_effect_statistic, method)

    return {
        'pooled_effect': result.observed_statistic,
        'p_value': result.p_value_two_sided if alternative == 'two-sided' else result.p_value,
        'ci_lower': result.ci_lower,
        'ci_upper': result.ci_upper,
        'permutation_distribution': result.permutation_distribution,
        'n_permutations': result.n_permutations,
        'method': 'Permutation test for pooled effect'
    }


def permutation_heterogeneity_test(
    effects: np.ndarray,
    variances: np.ndarray,
    n_permutations: int = 10000,
    statistic: str = 'Q'
) -> Dict[str, Any]:
    """
    Permutation test for heterogeneity.

    Tests whether observed heterogeneity exceeds that expected by chance.

    Args:
        effects: Effect sizes
        variances: Within-study variances
        n_permutations: Number of permutations
        statistic: Heterogeneity statistic ('Q', 'I2', 'tau2')

    Returns:
        Permutation test results
    """
    engine = PermutationEngine(n_permutations=n_permutations)

    if statistic == 'Q':
        def hetero_statistic(data, **kwargs):
            weights = 1 / data['variances']
            pooled = np.sum(weights * data['effects']) / np.sum(weights)
            Q = np.sum(weights * (data['effects'] - pooled) ** 2)
            return Q

    elif statistic == 'I2':
        def hetero_statistic(data, **kwargs):
            weights = 1 / data['variances']
            pooled = np.sum(weights * data['effects']) / np.sum(weights)
            Q = np.sum(weights * (data['effects'] - pooled) ** 2)
            df = len(data['effects']) - 1
            I2 = max(0, 100 * (Q - df) / Q) if Q > 0 else 0
            return I2

    elif statistic == 'tau2':
        def hetero_statistic(data, **kwargs):
            weights = 1 / data['variances']
            pooled = np.sum(weights * data['effects']) / np.sum(weights)
            Q = np.sum(weights * (data['effects'] - pooled) ** 2)
            C = np.sum(weights) - np.sum(weights ** 2) / np.sum(weights)
            tau2 = max(0, (Q - (len(data['effects']) - 1)) / C)
            return tau2

    else:
        raise ValueError(f"Unknown heterogeneity statistic: {statistic}")

    data = {'effects': effects, 'variances': variances}
    result = engine.run_test(data, hetero_statistic, 'sign_flip')

    return {
        'observed_statistic': result.observed_statistic,
        'p_value': result.p_value,
        'permutation_distribution': result.permutation_distribution,
        'n_permutations': result.n_permutations,
        'statistic_type': statistic,
        'method': f'Permutation test for heterogeneity ({statistic})'
    }


def permutation_publication_bias_test(
    effects: np.ndarray,
    variances: np.ndarray,
    n_permutations: int = 10000,
    test_type: str = 'egger'
) -> Dict[str, Any]:
    """
    Permutation test for publication bias.

    Args:
        effects: Effect sizes
        variances: Within-study variances
        n_permutations: Number of permutations
        test_type: Type of test ('egger', 'begg', 'trim_fill')

    Returns:
        Permutation test results
    """
    engine = PermutationEngine(n_permutations=n_permutations)

    if test_type == 'egger':
        def bias_statistic(data, **kwargs):
            # Egger's regression: intercept from regression of standardized effect on precision
            precision = 1 / np.sqrt(data['variances'])
            std_effect = data['effects'] / np.sqrt(data['variances'])

            # Simple linear regression
            X = np.column_stack([np.ones(len(precision)), precision])
            try:
                beta = np.linalg.lstsq(X, std_effect, rcond=None)[0]
                return beta[0]  # Intercept
            except:
                return 0.0

    elif test_type == 'begg':
        def bias_statistic(data, **kwargs):
            # Begg's test: rank correlation between effect and variance
            from scipy.stats import kendalltau
            tau, _ = kendalltau(data['effects'], data['variances'])
            return tau

    elif test_type == 'trim_fill':
        def bias_statistic(data, **kwargs):
            # Simplified trim-and-fill statistic
            weights = 1 / data['variances']
            pooled = np.sum(weights * data['effects']) / np.sum(weights)
            residuals = data['effects'] - pooled
            # Count studies on left vs right of pooled estimate
            n_left = np.sum(residuals < 0)
            n_right = np.sum(residuals > 0)
            return abs(n_left - n_right)

    else:
        raise ValueError(f"Unknown publication bias test: {test_type}")

    data = {'effects': effects, 'variances': variances}
    result = engine.run_test(data, bias_statistic, 'shuffle')

    return {
        'observed_statistic': result.observed_statistic,
        'p_value': result.p_value_two_sided,
        'permutation_distribution': result.permutation_distribution,
        'n_permutations': result.n_permutations,
        'test_type': test_type,
        'method': f'Permutation test for publication bias ({test_type})'
    }


def permutation_subgroup_test(
    effects: np.ndarray,
    variances: np.ndarray,
    groups: np.ndarray,
    n_permutations: int = 10000
) -> Dict[str, Any]:
    """
    Permutation test for subgroup differences.

    Tests whether effect sizes differ across subgroups beyond chance.

    Args:
        effects: Effect sizes
        variances: Within-study variances
        groups: Group labels
        n_permutations: Number of permutations

    Returns:
        Permutation test results
    """
    engine = PermutationEngine(n_permutations=n_permutations)

    def subgroup_statistic(data, **kwargs):
        # Q between-groups statistic
        groups_data = kwargs.get('groups', groups)
        unique_groups = np.unique(groups_data)

        # Overall pooled estimate
        weights_overall = 1 / data['variances']
        pooled_overall = np.sum(weights_overall * data['effects']) / np.sum(weights_overall)

        # Calculate Q between
        Q_between = 0
        for group in unique_groups:
            mask = groups_data == group
            group_weights = weights_overall[mask]
            group_effects = data['effects'][mask]

            group_pooled = np.sum(group_weights * group_effects) / np.sum(group_weights)
            Q_between += np.sum(group_weights) * (group_pooled - pooled_overall) ** 2

        return Q_between

    # Create permutation data with group shuffling
    data = {'effects': effects, 'variances': variances, 'groups': groups}

    def subgroup_permutation(d, method='shuffle'):
        """Shuffle group labels."""
        perm_data = d.copy()
        perm_data['groups'] = np.random.permutation(d['groups'])
        return perm_data

    # Manual permutation loop for subgroup test
    observed = subgroup_statistic(data, groups=groups)
    perm_stats = np.zeros(n_permutations)

    for i in range(n_permutations):
        perm_data = subgroup_permutation(data)
        perm_stats[i] = subgroup_statistic(perm_data, groups=perm_data['groups'])

    p_value = np.mean(perm_stats >= observed)

    # Asymptotic p-value for comparison (chi-square)
    df = len(np.unique(groups)) - 1
    asymp_p = 1 - stats.chi2.cdf(observed, df)

    return {
        'Q_between': float(observed),
        'p_value_permutation': float(p_value),
        'p_value_asymptotic': float(asymp_p),
        'df': df,
        'permutation_distribution': perm_stats,
        'n_permutations': n_permutations,
        'method': 'Permutation test for subgroup differences'
    }


def permutation_meta_regression(
    effects: np.ndarray,
    variances: np.ndarray,
    moderators: np.ndarray,
    n_permutations: int = 10000,
    coefficient_index: int = 1
) -> Dict[str, Any]:
    """
    Permutation test for meta-regression coefficient.

    Args:
        effects: Effect sizes
        variances: Within-study variances
        moderators: Moderator variable(s)
        n_permutations: Number of permutations
        coefficient_index: Index of coefficient to test (0=intercept, 1=first moderator, etc.)

    Returns:
        Permutation test results
    """
    engine = PermutationEngine(n_permutations=n_permutations)

    # Ensure moderators is 2D
    if moderators.ndim == 1:
        moderators = moderators.reshape(-1, 1)

    def regression_statistic(data, **kwargs):
        # Weighted least squares meta-regression
        X = np.column_stack([np.ones(len(data['effects'])), kwargs['moderators']])
        weights = 1 / data['variances']
        W = np.diag(weights)

        try:
            beta = np.linalg.solve(X.T @ W @ X, X.T @ W @ data['effects'])
            return beta[coefficient_index]
        except:
            return 0.0

    data = {'effects': effects, 'variances': variances}

    # Permute by shuffling moderators
    observed = regression_statistic(data, moderators=moderators)
    perm_stats = np.zeros(n_permutations)

    for i in range(n_permutations):
        perm_moderators = np.random.permutation(moderators)
        perm_stats[i] = regression_statistic(data, moderators=perm_moderators)

    p_value_two_sided = 2 * min(
        np.mean(perm_stats >= observed),
        np.mean(perm_stats <= observed)
    )

    ci_lower = np.percentile(perm_stats, 2.5)
    ci_upper = np.percentile(perm_stats, 97.5)

    return {
        'coefficient': float(observed),
        'p_value': float(p_value_two_sided),
        'ci_lower': float(ci_lower),
        'ci_upper': float(ci_upper),
        'permutation_distribution': perm_stats,
        'n_permutations': n_permutations,
        'coefficient_index': coefficient_index,
        'method': 'Permutation test for meta-regression'
    }


def permutation_influence_test(
    effects: np.ndarray,
    variances: np.ndarray,
    study_index: int,
    n_permutations: int = 10000
) -> Dict[str, Any]:
    """
    Permutation test for study influence.

    Tests whether a specific study has undue influence on the pooled estimate.

    Args:
        effects: Effect sizes
        variances: Within-study variances
        study_index: Index of study to test
        n_permutations: Number of permutations

    Returns:
        Permutation test results
    """
    engine = PermutationEngine(n_permutations=n_permutations)

    def influence_statistic(data, **kwargs):
        idx = kwargs['study_index']
        weights = 1 / data['variances']

        # Full pooled estimate
        pooled_full = np.sum(weights * data['effects']) / np.sum(weights)

        # Leave-one-out estimate
        mask = np.ones(len(data['effects']), dtype=bool)
        mask[idx] = False
        weights_loo = weights[mask]
        effects_loo = data['effects'][mask]
        pooled_loo = np.sum(weights_loo * effects_loo) / np.sum(weights_loo)

        # Influence = difference
        return abs(pooled_full - pooled_loo)

    data = {'effects': effects, 'variances': variances}
    result = engine.run_test(data, influence_statistic, 'shuffle', study_index=study_index)

    return {
        'influence': result.observed_statistic,
        'p_value': result.p_value,
        'permutation_distribution': result.permutation_distribution,
        'n_permutations': result.n_permutations,
        'study_index': study_index,
        'method': 'Permutation test for study influence'
    }


__all__ = [
    'permutation_meta_analysis',
    'permutation_heterogeneity_test',
    'permutation_publication_bias_test',
    'permutation_subgroup_test',
    'permutation_meta_regression',
    'permutation_influence_test',
]
