"""
Test statistical methods and calculations.
"""

import pytest
import numpy as np
from scipy import stats


def test_normal_distribution():
    """Test normal distribution calculations."""
    # Test z-score calculation
    z = stats.norm.ppf(0.975)  # 95% CI critical value
    assert z == pytest.approx(1.96, rel=0.01)

    # Test p-value calculation
    p = stats.norm.sf(1.96)  # One-tailed p-value
    assert p == pytest.approx(0.025, rel=0.01)


def test_t_distribution():
    """Test t-distribution calculations."""
    # Test t-critical value
    df = 10
    t_crit = stats.t.ppf(0.975, df)
    assert t_crit > 1.96  # Should be larger than z for small df


def test_chi_square_distribution():
    """Test chi-square distribution calculations."""
    # Test chi-square critical value
    df = 5
    chi2_crit = stats.chi2.ppf(0.95, df)
    assert chi2_crit > 0

    # Test p-value calculation
    chi2_stat = 10.0
    p = stats.chi2.sf(chi2_stat, df)
    assert 0 <= p <= 1


def test_heterogeneity_i_squared():
    """Test I-squared calculation."""
    q = 10.0
    df = 4

    # I² = max(0, (Q - df) / Q * 100)
    i_squared = max(0, (q - df) / q * 100)

    assert 0 <= i_squared <= 100
    assert i_squared == pytest.approx(60.0)


def test_inverse_variance_weights():
    """Test inverse variance weighting."""
    ses = np.array([0.1, 0.2, 0.15])
    variances = ses ** 2

    weights = 1 / variances
    normalized_weights = weights / np.sum(weights)

    assert len(normalized_weights) == len(ses)
    assert np.sum(normalized_weights) == pytest.approx(1.0)
    assert all(normalized_weights > 0)

    # Smaller SE should have larger weight
    assert normalized_weights[0] > normalized_weights[1]


def test_pooled_estimate():
    """Test pooled effect size calculation."""
    effects = np.array([0.5, 0.3, 0.7])
    ses = np.array([0.1, 0.2, 0.15])

    weights = 1 / (ses ** 2)
    pooled = np.average(effects, weights=weights)

    assert isinstance(pooled, (float, np.floating))
    assert min(effects) <= pooled <= max(effects)


def test_pooled_standard_error():
    """Test pooled standard error calculation."""
    ses = np.array([0.1, 0.2, 0.15])
    weights = 1 / (ses ** 2)

    pooled_se = np.sqrt(1 / np.sum(weights))

    assert pooled_se > 0
    assert pooled_se < min(ses)  # Pooled SE should be smaller


def test_q_statistic_calculation():
    """Test Cochran's Q statistic."""
    effects = np.array([0.5, 0.3, 0.7])
    ses = np.array([0.1, 0.2, 0.15])

    weights = 1 / (ses ** 2)
    pooled = np.average(effects, weights=weights)

    q = np.sum(weights * (effects - pooled) ** 2)

    assert q >= 0  # Q is always non-negative
    assert isinstance(q, (float, np.floating))


def test_confidence_interval_coverage():
    """Test that confidence intervals have proper coverage."""
    estimate = 0.5
    se = 0.1
    z_critical = 1.96

    ci_lower = estimate - z_critical * se
    ci_upper = estimate + z_critical * se

    # The true value should be within the CI
    assert ci_lower <= estimate <= ci_upper

    # CI width should be 2 * z * SE
    width = ci_upper - ci_lower
    expected_width = 2 * z_critical * se
    assert width == pytest.approx(expected_width)


def test_z_test():
    """Test z-test calculation."""
    estimate = 0.5
    se = 0.1
    null_value = 0.0

    z = (estimate - null_value) / se
    p_value = 2 * stats.norm.sf(abs(z))  # Two-tailed

    assert z == 5.0
    assert p_value < 0.05  # Should be significant


def test_effect_size_transformation():
    """Test effect size transformations."""
    # Test odds ratio to log odds ratio
    or_value = 2.0
    log_or = np.log(or_value)
    assert log_or > 0

    # Transform back
    or_back = np.exp(log_or)
    assert or_back == pytest.approx(or_value)


def test_correlation_coefficient():
    """Test correlation coefficient calculation."""
    x = np.array([1, 2, 3, 4, 5])
    y = np.array([2, 4, 6, 8, 10])

    r, p = stats.pearsonr(x, y)

    assert r == pytest.approx(1.0)  # Perfect correlation
    assert -1 <= r <= 1
    assert p < 0.05  # Should be significant
