"""
Test basic MetaPython functionality.
"""

import pytest
import numpy as np
import pandas as pd
import metapython


def test_fixed_effects_results_creation():
    """Test that FixedEffectsResults can be created."""
    result = metapython.FixedEffectsResults(
        effect=0.5,
        se=0.1,
        ci_low=0.3,
        ci_high=0.7,
        z_statistic=5.0,
        p_value=0.001
    )

    assert result.effect == 0.5
    assert result.se == 0.1
    assert result.ci_low == 0.3
    assert result.ci_high == 0.7
    assert result.z_statistic == 5.0
    assert result.p_value == 0.001
    assert result.is_significant(alpha=0.05) == True


def test_random_effects_results_creation():
    """Test that RandomEffectsResults can be created."""
    result = metapython.RandomEffectsResults(
        effect=0.6,
        se=0.15,
        ci_low=0.35,
        ci_high=0.85,
        z_statistic=4.0,
        p_value=0.01,
        tau2=0.05
    )

    assert result.effect == 0.6
    assert result.tau2 == 0.05
    assert result.is_significant(alpha=0.05) == True


def test_heterogeneity_results_creation():
    """Test that HeterogeneityResults can be created."""
    result = metapython.HeterogeneityResults(
        Q=10.5,
        df=4,
        p_value=0.03,
        I2=62.0,
        H2=2.63,
        tau2=0.05
    )

    assert result.Q == 10.5
    assert result.df == 4
    assert result.I2 == 62.0
    assert 0 <= result.I2 <= 100
    assert result.is_significant(alpha=0.05) == True


def test_unified_meta_config_creation():
    """Test that UnifiedMetaConfig can be created with defaults."""
    config = metapython.UnifiedMetaConfig()

    assert config.alpha == 0.05
    assert hasattr(config, 'tau2_method')
    assert config.tau2_method == 'REML'
    assert config.min_studies == 2
    assert config.max_iterations == 1000


def test_unified_meta_config_custom():
    """Test that UnifiedMetaConfig can be customized."""
    config = metapython.UnifiedMetaConfig(
        alpha=0.01,
        tau2_method='DL',
        use_hksj=True,
        min_studies=3
    )

    assert config.alpha == 0.01
    assert config.tau2_method == 'DL'
    assert config.use_hksj == True
    assert config.min_studies == 3


def test_meta_analysis_results_dataclass():
    """Test MetaAnalysisResults structure."""
    # Create minimal result object
    fe_result = metapython.FixedEffectsResults(
        effect=0.5, se=0.1, ci_low=0.3, ci_high=0.7,
        z_statistic=5.0, p_value=0.001
    )

    het_result = metapython.HeterogeneityResults(
        Q=5.0, df=1, p_value=0.025,
        I2=50.0, H2=2.0, tau2=0.02
    )

    result = metapython.MetaAnalysisResults(
        fixed_effects=fe_result,
        heterogeneity=het_result
    )

    assert result.fixed_effects is not None
    assert result.heterogeneity is not None
    assert result.fixed_effects.effect == 0.5
    assert result.heterogeneity.I2 == 50.0


def test_bias_test_results_creation():
    """Test BiasTestResults can be created."""
    result = metapython.BiasTestResults(
        egger_intercept=2.5,
        egger_p_value=0.05,
        egger_significant=False,
        begg_tau=0.3,
        begg_p_value=0.1,
        begg_significant=False
    )

    assert result.egger_intercept == 2.5
    assert result.egger_p_value == 0.05
    assert result.egger_significant == False
    assert result.begg_tau == 0.3
    assert result.begg_p_value == 0.1


def test_tau_squared_estimators_class_exists():
    """Test that TauSquaredEstimators class exists."""
    assert hasattr(metapython, 'TauSquaredEstimators')
    tau_est = metapython.TauSquaredEstimators()
    assert tau_est is not None


def test_unified_meta_analysis_class_exists():
    """Test that UnifiedMetaAnalysis class exists."""
    assert hasattr(metapython, 'UnifiedMetaAnalysis')


def test_error_classes():
    """Test custom exception classes."""
    assert hasattr(metapython, 'UnifiedMetaError')
    assert hasattr(metapython, 'InsufficientDataError')
    assert hasattr(metapython, 'NumericalInstabilityError')

    # Test exception hierarchy
    assert issubclass(metapython.InsufficientDataError, metapython.UnifiedMetaError)
    assert issubclass(metapython.NumericalInstabilityError, metapython.UnifiedMetaError)


def test_insufficient_data_error():
    """Test InsufficientDataError can be raised."""
    with pytest.raises(metapython.InsufficientDataError):
        raise metapython.InsufficientDataError("Test error message")


def test_numerical_instability_error():
    """Test NumericalInstabilityError can be raised."""
    with pytest.raises(metapython.NumericalInstabilityError):
        raise metapython.NumericalInstabilityError("Test numerical error")


def test_prediction_interval_results():
    """Test PredictionIntervalResults creation."""
    result = metapython.PredictionIntervalResults(
        low=-0.2,
        high=0.8,
        se=0.2
    )

    assert result.low == -0.2
    assert result.high == 0.8
    assert result.se == 0.2
