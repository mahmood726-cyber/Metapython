"""
Test data structures and validation.
"""

import pytest
import numpy as np
import pandas as pd


def test_sample_meta_data_fixture(sample_meta_data):
    """Test that sample meta data fixture works."""
    assert isinstance(sample_meta_data, pd.DataFrame)
    assert 'effect_size' in sample_meta_data.columns
    assert 'se' in sample_meta_data.columns
    assert len(sample_meta_data) > 0


def test_sample_binary_data_fixture(sample_binary_data):
    """Test that sample binary data fixture works."""
    assert isinstance(sample_binary_data, pd.DataFrame)
    assert 'ai' in sample_binary_data.columns
    assert 'bi' in sample_binary_data.columns
    assert 'ci' in sample_binary_data.columns
    assert 'di' in sample_binary_data.columns
    assert len(sample_binary_data) > 0


def test_sample_continuous_data_fixture(sample_continuous_data):
    """Test that sample continuous data fixture works."""
    assert isinstance(sample_continuous_data, pd.DataFrame)
    assert 'mean_t' in sample_continuous_data.columns
    assert 'sd_t' in sample_continuous_data.columns
    assert 'n_t' in sample_continuous_data.columns
    assert len(sample_continuous_data) > 0


def test_meta_data_validation(sample_meta_data):
    """Test that meta data has valid values."""
    # Effect sizes should be numeric
    assert sample_meta_data['effect_size'].dtype in [np.float64, np.float32, np.int64]

    # Standard errors should be positive
    assert all(sample_meta_data['se'] > 0)

    # Sample sizes should be positive integers
    assert all(sample_meta_data['n'] > 0)


def test_binary_data_validation(sample_binary_data):
    """Test that binary data has valid values."""
    # All counts should be non-negative
    assert all(sample_binary_data['ai'] >= 0)
    assert all(sample_binary_data['bi'] >= 0)
    assert all(sample_binary_data['ci'] >= 0)
    assert all(sample_binary_data['di'] >= 0)

    # Total sample sizes should be positive
    total_t = sample_binary_data['ai'] + sample_binary_data['bi']
    total_c = sample_binary_data['ci'] + sample_binary_data['di']
    assert all(total_t > 0)
    assert all(total_c > 0)


def test_continuous_data_validation(sample_continuous_data):
    """Test that continuous data has valid values."""
    # Sample sizes should be positive
    assert all(sample_continuous_data['n_t'] > 0)
    assert all(sample_continuous_data['n_c'] > 0)

    # Standard deviations should be positive
    assert all(sample_continuous_data['sd_t'] > 0)
    assert all(sample_continuous_data['sd_c'] > 0)


def test_dataframe_creation():
    """Test creating DataFrame from scratch."""
    data = {
        'study': ['A', 'B', 'C'],
        'effect': [0.5, 0.3, 0.7],
        'se': [0.1, 0.12, 0.09]
    }
    df = pd.DataFrame(data)

    assert len(df) == 3
    assert list(df.columns) == ['study', 'effect', 'se']


def test_numpy_array_operations():
    """Test basic numpy operations for meta-analysis."""
    effects = np.array([0.5, 0.3, 0.7, 0.4])
    ses = np.array([0.1, 0.12, 0.09, 0.11])

    # Calculate weights (inverse variance)
    weights = 1 / (ses ** 2)

    assert len(weights) == len(effects)
    assert all(weights > 0)

    # Calculate weighted mean
    weighted_mean = np.average(effects, weights=weights)

    assert isinstance(weighted_mean, (float, np.floating))
    assert 0 <= weighted_mean <= 1  # Should be between min and max effects


def test_statistical_calculations():
    """Test basic statistical calculations."""
    data = np.array([1, 2, 3, 4, 5])

    mean = np.mean(data)
    std = np.std(data)
    var = np.var(data)

    assert mean == 3.0
    assert var == pytest.approx(std ** 2)
    assert std > 0


def test_confidence_interval_calculation():
    """Test confidence interval calculation."""
    estimate = 0.5
    se = 0.1
    z_critical = 1.96  # 95% CI

    ci_lower = estimate - z_critical * se
    ci_upper = estimate + z_critical * se

    assert ci_lower < estimate < ci_upper
    assert ci_upper - ci_lower == pytest.approx(2 * z_critical * se)
