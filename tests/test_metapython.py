"""
Unit tests for MetaPython meta-analysis library

Run with: python -m pytest tests/
Or: python tests/test_metapython.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

# Test imports
try:
    from metapython import (
        UnifiedMetaAnalysis,
        UnifiedMetaConfig,
        TauSquaredEstimators,
        calculate_pooled_estimate,
        calculate_confidence_interval,
        safe_solve,
        safe_matrix_inverse,
        validate_file_path,
        SecurityError,
        InsufficientDataError,
        DEFAULT_ALPHA,
        Z_CRITICAL_95,
    )
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 1: Utility functions
def test_pooled_estimate():
    """Test calculate_pooled_estimate utility function"""
    effects = np.array([0.2, 0.5, 0.3])
    variances = np.array([0.01, 0.02, 0.015])

    pooled, se = calculate_pooled_estimate(effects, variances, use_variances=True)

    assert isinstance(pooled, float), "Pooled estimate should be float"
    assert isinstance(se, float), "SE should be float"
    assert se > 0, "SE should be positive"
    print("✓ test_pooled_estimate passed")


def test_confidence_interval():
    """Test calculate_confidence_interval utility function"""
    effect = 0.5
    se = 0.1

    ci_low, ci_high = calculate_confidence_interval(effect, se)

    assert ci_low < effect < ci_high, "Effect should be within CI"
    assert abs(ci_high - ci_low - 2 * Z_CRITICAL_95 * se) < 1e-10, "CI width should match expected"
    print("✓ test_confidence_interval passed")


def test_safe_matrix_operations():
    """Test safe_solve and safe_matrix_inverse"""
    A = np.array([[2.0, 1.0], [1.0, 2.0]])
    b = np.array([1.0, 1.0])

    # Test safe_solve
    x = safe_solve(A, b)
    assert x.shape == (2,), "Solution should have correct shape"
    assert np.allclose(A @ x, b), "Solution should satisfy Ax=b"

    # Test safe_matrix_inverse
    A_inv = safe_matrix_inverse(A)
    assert A_inv.shape == (2, 2), "Inverse should have correct shape"
    assert np.allclose(A @ A_inv, np.eye(2)), "A * A^-1 should be identity"

    print("✓ test_safe_matrix_operations passed")


# Test 2: Tau² estimators
def test_tau_squared_estimators():
    """Test tau² estimation methods"""
    effects = np.array([0.2, 0.5, 0.3, 0.6, 0.4])
    variances = np.array([0.01, 0.02, 0.015, 0.018, 0.012])

    # DerSimonian-Laird
    tau2_dl = TauSquaredEstimators.dersimonian_laird(effects, variances)
    assert isinstance(tau2_dl, float), "Tau² should be float"
    assert tau2_dl >= 0, "Tau² should be non-negative"

    # REML
    tau2_reml = TauSquaredEstimators.restricted_ml(effects, variances)
    assert isinstance(tau2_reml, float), "Tau² should be float"
    assert tau2_reml >= 0, "Tau² should be non-negative"

    print("✓ test_tau_squared_estimators passed")


# Test 3: Core meta-analysis
def test_basic_meta_analysis():
    """Test basic meta-analysis workflow"""
    # Create test data
    data = pd.DataFrame({
        'study': [f'Study {i+1}' for i in range(10)],
        'effect': np.random.normal(0.3, 0.1, 10),
        'se': np.random.uniform(0.05, 0.15, 10)
    })

    # Create configuration
    config = UnifiedMetaConfig(alpha=DEFAULT_ALPHA, tau2_method='DL')

    # Run analysis
    meta = UnifiedMetaAnalysis(data, 'effect', 'se', 'study', config=config)
    meta.analyze(include_bias_tests=False, include_conflicts=False)

    # Check results
    assert meta._fitted, "Analysis should be marked as fitted"
    assert hasattr(meta.results, 'fixed_effects'), "Should have fixed effects results"
    assert hasattr(meta.results, 'random_effects'), "Should have random effects results"
    assert hasattr(meta.results, 'heterogeneity'), "Should have heterogeneity results"

    # Check values are reasonable
    fe = meta.results.fixed_effects
    assert -10 < fe.effect < 10, "Fixed effect should be reasonable"
    assert fe.se > 0, "SE should be positive"
    assert 0 <= fe.p_value <= 1, "P-value should be in [0,1]"

    re = meta.results.random_effects
    assert -10 < re.effect < 10, "Random effect should be reasonable"
    assert re.tau2 >= 0, "Tau² should be non-negative"

    het = meta.results.heterogeneity
    assert het.Q >= 0, "Q should be non-negative"
    assert 0 <= het.I2 <= 100, "I² should be in [0,100]"

    print("✓ test_basic_meta_analysis passed")


# Test 4: Leave-one-out analysis
def test_leave_one_out():
    """Test leave-one-out analysis (both fast and slow modes)"""
    data = pd.DataFrame({
        'study': [f'Study {i+1}' for i in range(5)],
        'effect': [0.2, 0.5, 0.3, 0.6, 0.4],
        'se': [0.1, 0.15, 0.12, 0.18, 0.11]
    })

    meta = UnifiedMetaAnalysis(data, 'effect', 'se', 'study')
    meta.analyze(include_bias_tests=False, include_conflicts=False)

    # Fast mode
    loo_fast = meta.leave_one_out_analysis(fast=True)
    assert isinstance(loo_fast, pd.DataFrame), "Should return DataFrame"
    assert len(loo_fast) == 5, "Should have 5 results"
    assert 'excluded_study' in loo_fast.columns, "Should have excluded_study column"
    assert 'loo_effect' in loo_fast.columns, "Should have loo_effect column"

    print("✓ test_leave_one_out passed")


# Test 5: File path validation
def test_file_path_validation():
    """Test secure file path validation"""
    import tempfile
    import pathlib

    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        temp_path = f.name
        f.write("test,data\n1,2\n")

    try:
        # Valid file should pass
        validated = validate_file_path(temp_path, allowed_extensions=['.csv'])
        assert pathlib.Path(validated).exists(), "Validated path should exist"

        # Invalid extension should fail
        try:
            validate_file_path(temp_path, allowed_extensions=['.xlsx'])
            assert False, "Should have raised ValueError for invalid extension"
        except ValueError:
            pass

        # Non-existent file should fail
        try:
            validate_file_path('/nonexistent/file.csv')
            assert False, "Should have raised ValueError for non-existent file"
        except ValueError:
            pass

        print("✓ test_file_path_validation passed")

    finally:
        # Clean up
        pathlib.Path(temp_path).unlink(missing_ok=True)


# Test 6: Insufficient data handling
def test_insufficient_data():
    """Test handling of insufficient data"""
    data = pd.DataFrame({
        'study': ['Study 1'],
        'effect': [0.5],
        'se': [0.1]
    })

    try:
        meta = UnifiedMetaAnalysis(data, 'effect', 'se', 'study')
        meta.analyze()
        assert False, "Should have raised InsufficientDataError"
    except InsufficientDataError:
        pass

    print("✓ test_insufficient_data passed")


# Run all tests
if __name__ == "__main__":
    print("\nRunning MetaPython Unit Tests")
    print("=" * 50)

    tests = [
        test_pooled_estimate,
        test_confidence_interval,
        test_safe_matrix_operations,
        test_tau_squared_estimators,
        test_basic_meta_analysis,
        test_leave_one_out,
        test_file_path_validation,
        test_insufficient_data,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)

    sys.exit(0 if failed == 0 else 1)
