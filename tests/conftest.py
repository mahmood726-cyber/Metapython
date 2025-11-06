"""
Pytest configuration and shared fixtures for MetaPython tests.
"""

import pytest
import numpy as np
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def sample_meta_data():
    """
    Create sample meta-analysis data for testing.

    Returns a DataFrame with effect sizes and standard errors.
    """
    data = {
        'study': ['Study1', 'Study2', 'Study3', 'Study4', 'Study5'],
        'effect_size': [0.5, 0.3, 0.7, 0.4, 0.6],
        'se': [0.1, 0.15, 0.12, 0.11, 0.13],
        'n': [100, 150, 120, 110, 130]
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_binary_data():
    """
    Create sample binary outcome data (2x2 table).

    Returns a DataFrame with event counts for treatment and control.
    """
    data = {
        'study': ['Study1', 'Study2', 'Study3'],
        'ai': [10, 15, 12],  # events in treatment
        'bi': [90, 85, 88],  # non-events in treatment
        'ci': [20, 25, 22],  # events in control
        'di': [80, 75, 78],  # non-events in control
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_continuous_data():
    """
    Create sample continuous outcome data.

    Returns a DataFrame with means and standard deviations.
    """
    data = {
        'study': ['Study1', 'Study2', 'Study3'],
        'mean_t': [10.5, 11.2, 10.8],
        'sd_t': [2.0, 2.2, 1.9],
        'n_t': [50, 55, 52],
        'mean_c': [9.5, 10.0, 9.8],
        'sd_c': [2.1, 2.3, 2.0],
        'n_c': [50, 55, 52],
    }
    return pd.DataFrame(data)


@pytest.fixture
def random_seed():
    """Set random seed for reproducibility."""
    np.random.seed(42)
    return 42
