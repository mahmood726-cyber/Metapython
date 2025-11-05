"""
Unit Tests for Advanced Meta-Analysis Methods
==============================================

Tests for cutting-edge methods from statistics journals.

Run with:
    python tests/test_advanced_methods.py
    pytest tests/test_advanced_methods.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

# Test imports
try:
    from advanced_methods import PUniformMethods, SelectionModels, LimitMetaAnalysis
    from advanced_methods_part2 import GOSHAnalysis, BootstrapMethods, DoseResponseSplines
    print("✓ All advanced method imports successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Set random seed
np.random.seed(42)

# ===================================================================
# TEST 1: P-UNIFORM
# ===================================================================

def test_p_uniform():
    """Test P-uniform method for publication bias"""
    print("\n" + "="*60)
    print("TEST 1: P-uniform Method")
    print("="*60)

    # Generate data with publication bias
    n_studies = 30
    true_effect = 0.30
    se = np.random.uniform(0.05, 0.20, n_studies)
    effects = np.random.normal(true_effect, 0.15, n_studies)

    # Keep only significant studies (simulated publication bias)
    z_scores = np.abs(effects / se)
    sig_mask = z_scores > 1.96
    effects_published = effects[sig_mask]
    se_published = se[sig_mask]

    print(f"Total studies: {n_studies}")
    print(f"Published (significant): {len(effects_published)}")

    # Run p-uniform
    result = PUniformMethods.p_uniform(effects_published, se_published)

    assert result['available'], "P-uniform should be available"
    assert isinstance(result['estimate'], float), "Estimate should be float"
    assert isinstance(result['ci_low'], float), "CI_low should be float"
    assert isinstance(result['ci_high'], float), "CI_high should be float"
    assert result['ci_low'] < result['estimate'] < result['ci_high'], "Estimate should be within CI"
    assert 0 <= result['publication_bias_test_p'] <= 1, "P-value should be in [0,1]"

    print(f"✓ P-uniform estimate: {result['estimate']:.3f}")
    print(f"✓ 95% CI: [{result['ci_low']:.3f}, {result['ci_high']:.3f}]")
    print(f"✓ Publication bias detected: {result['publication_bias_detected']}")
    print("✓ test_p_uniform passed")


# ===================================================================
# TEST 2: P-UNIFORM*
# ===================================================================

def test_p_uniform_star():
    """Test P-uniform* method"""
    print("\n" + "="*60)
    print("TEST 2: P-uniform* Method")
    print("="*60)

    # Generate data
    n_studies = 20
    effects = np.random.normal(0.40, 0.12, n_studies)
    se = np.random.uniform(0.08, 0.18, n_studies)

    # Run p-uniform*
    result = PUniformMethods.p_uniform_star(effects, se)

    assert result['available'], "P-uniform* should be available"
    assert isinstance(result['estimate'], float), "Estimate should be float"
    assert isinstance(result['naive_estimate'], float), "Naive estimate should be float"
    assert result['k_studies'] == n_studies, "Should use all studies"

    print(f"✓ P-uniform* estimate: {result['estimate']:.3f}")
    print(f"✓ Naive estimate: {result['naive_estimate']:.3f}")
    print(f"✓ Test p-value: {result['publication_bias_test_p']:.4f}")
    print("✓ test_p_uniform_star passed")


# ===================================================================
# TEST 3: 3-PARAMETER SELECTION MODEL
# ===================================================================

def test_selection_model():
    """Test 3-parameter selection model"""
    print("\n" + "="*60)
    print("TEST 3: 3-Parameter Selection Model")
    print("="*60)

    # Generate data with selection
    n_studies = 25
    effects = np.random.normal(0.35, 0.15, n_studies)
    se = np.random.uniform(0.06, 0.20, n_studies)

    # Run selection model
    result = SelectionModels.three_parameter_selection_model(effects, se)

    assert result['available'], "Selection model should be available"
    assert isinstance(result['estimate'], float), "Estimate should be float"
    assert isinstance(result['tau'], float), "Tau should be float"
    assert 0 <= result['weight_moderate'] <= 1, "Weight should be in [0,1]"
    assert 0 <= result['weight_high'] <= 1, "Weight should be in [0,1]"
    assert result['bias_severity'] in ['mild', 'moderate', 'severe'], "Should have bias severity"

    print(f"✓ Estimate: {result['estimate']:.3f}")
    print(f"✓ Tau: {result['tau']:.3f}")
    print(f"✓ Selection weights: moderate={result['weight_moderate']:.2f}, "
          f"high={result['weight_high']:.2f}")
    print(f"✓ Bias severity: {result['bias_severity']}")
    print("✓ test_selection_model passed")


# ===================================================================
# TEST 4: LIMIT META-ANALYSIS
# ===================================================================

def test_limit_meta_analysis():
    """Test limit meta-analysis"""
    print("\n" + "="*60)
    print("TEST 4: Limit Meta-Analysis")
    print("="*60)

    # Generate data with small-study effects
    n_studies = 20
    se = np.random.uniform(0.05, 0.40, n_studies)
    effects = 0.30 + 0.4 * se + np.random.normal(0, 0.08, n_studies)

    # Run limit meta-analysis
    result = LimitMetaAnalysis.limit_meta_analysis(effects, se)

    assert result['available'], "Limit MA should be available"
    assert isinstance(result['limit_estimate'], float), "Limit estimate should be float"
    assert isinstance(result['naive_estimate'], float), "Naive estimate should be float"
    assert isinstance(result['slope'], float), "Slope should be float"
    assert isinstance(result['slope_p_value'], float), "P-value should be float"

    print(f"✓ Limit estimate: {result['limit_estimate']:.3f}")
    print(f"✓ Naive estimate: {result['naive_estimate']:.3f}")
    print(f"✓ Difference: {result['difference']:.3f}")
    print(f"✓ Small-study effects: {result['small_study_effect_detected']}")
    print("✓ test_limit_meta_analysis passed")


# ===================================================================
# TEST 5: GOSH ANALYSIS
# ===================================================================

def test_gosh_analysis():
    """Test GOSH analysis"""
    print("\n" + "="*60)
    print("TEST 5: GOSH Analysis")
    print("="*60)

    # Generate data with outliers
    n_studies = 12
    effects = np.random.normal(0.50, 0.10, n_studies)
    effects[0] = 1.20  # Add outlier
    se = np.random.uniform(0.08, 0.16, n_studies)
    labels = np.array([f"Study_{i+1}" for i in range(n_studies)])

    # Run GOSH analysis (sample fewer subsets for speed)
    result = GOSHAnalysis.gosh_analysis(effects, se, labels, n_samples=1000)

    assert result['available'], "GOSH should be available"
    assert isinstance(result['results'], pd.DataFrame), "Results should be DataFrame"
    assert len(result['results']) > 0, "Should have results"
    assert 'fe_estimate' in result['results'].columns, "Should have fe_estimate column"
    assert 'I2' in result['results'].columns, "Should have I2 column"
    assert isinstance(result['n_subsets'], int), "n_subsets should be int"
    assert isinstance(result['fe_estimate_range'], tuple), "Effect range should be tuple"

    print(f"✓ Subsets analyzed: {result['n_subsets']}")
    print(f"✓ Effect range: {result['fe_estimate_range'][0]:.3f} to "
          f"{result['fe_estimate_range'][1]:.3f}")
    print(f"✓ I² range: {result['I2_range'][0]:.1f}% to {result['I2_range'][1]:.1f}%")
    print(f"✓ Outlier subsets: {result['n_outliers']}")
    print("✓ test_gosh_analysis passed")


# ===================================================================
# TEST 6: BOOTSTRAP METHODS
# ===================================================================

def test_bootstrap_methods():
    """Test bootstrap confidence intervals"""
    print("\n" + "="*60)
    print("TEST 6: Bootstrap Methods")
    print("="*60)

    # Generate data
    n_studies = 15
    effects = np.random.normal(0.40, 0.15, n_studies)
    se = np.random.uniform(0.10, 0.25, n_studies)

    # Test percentile bootstrap
    result_pct = BootstrapMethods.bootstrap_ci(
        effects, se, method='percentile', n_boot=1000
    )

    assert result_pct['available'], "Bootstrap should be available"
    assert isinstance(result_pct['estimate'], float), "Estimate should be float"
    assert isinstance(result_pct['bootstrap_se'], float), "Bootstrap SE should be float"
    assert result_pct['ci_low'] < result_pct['estimate'] < result_pct['ci_high'], \
        "Estimate should be within CI"
    assert result_pct['method'] == 'percentile', "Method should be percentile"

    print(f"✓ Percentile bootstrap estimate: {result_pct['estimate']:.3f}")
    print(f"✓ Bootstrap SE: {result_pct['bootstrap_se']:.3f}")
    print(f"✓ 95% CI: [{result_pct['ci_low']:.3f}, {result_pct['ci_high']:.3f}]")
    print(f"✓ Bias: {result_pct['bias']:.4f}")

    # Test BCa bootstrap
    result_bca = BootstrapMethods.bootstrap_ci(
        effects, se, method='bca', n_boot=1000
    )

    assert result_bca['available'], "BCa bootstrap should be available"
    assert result_bca['method'] == 'bca', "Method should be bca"

    print(f"✓ BCa bootstrap estimate: {result_bca['estimate']:.3f}")
    print(f"✓ BCa 95% CI: [{result_bca['ci_low']:.3f}, {result_bca['ci_high']:.3f}]")
    print("✓ test_bootstrap_methods passed")


# ===================================================================
# TEST 7: RESTRICTED CUBIC SPLINES
# ===================================================================

def test_restricted_cubic_splines():
    """Test restricted cubic splines for dose-response"""
    print("\n" + "="*60)
    print("TEST 7: Restricted Cubic Splines")
    print("="*60)

    # Generate non-linear dose-response data
    doses = np.array([0, 10, 20, 30, 40, 50, 60, 80, 100])
    true_rr = 1.0 - 0.02 * doses + 0.0006 * doses**2
    effects = np.log(true_rr) + np.random.normal(0, 0.05, len(doses))
    se = np.random.uniform(0.08, 0.15, len(doses))

    # Fit RCS
    result = DoseResponseSplines.fit_rcs(doses, effects, se, n_knots=4)

    assert result['available'], "RCS should be available"
    assert result['n_knots'] == 4, "Should have 4 knots"
    assert len(result['knots']) == 4, "Should have 4 knot positions"
    assert isinstance(result['r_squared'], float), "R² should be float"
    assert 0 <= result['r_squared'] <= 1, "R² should be in [0,1]"
    assert isinstance(result['smooth_doses'], list), "Smooth doses should be list"
    assert isinstance(result['smooth_effects'], list), "Smooth effects should be list"
    assert len(result['smooth_doses']) == len(result['smooth_effects']), \
        "Smooth arrays should have same length"

    print(f"✓ Number of knots: {result['n_knots']}")
    print(f"✓ R²: {result['r_squared']:.3f}")
    if result['nonlinearity_test_p'] is not None:
        print(f"✓ Non-linearity p-value: {result['nonlinearity_test_p']:.4f}")
        print(f"✓ Non-linear: {result['nonlinear']}")
    print(f"✓ Smooth curve points: {len(result['smooth_doses'])}")
    print("✓ test_restricted_cubic_splines passed")


# ===================================================================
# TEST 8: INSUFFICIENT DATA HANDLING
# ===================================================================

def test_insufficient_data():
    """Test handling of insufficient data"""
    print("\n" + "="*60)
    print("TEST 8: Insufficient Data Handling")
    print("="*60)

    # Too few studies for various methods
    effects_few = np.array([0.3, 0.5])
    se_few = np.array([0.1, 0.15])

    # P-uniform (needs significant studies)
    result_punif = PUniformMethods.p_uniform(effects_few, se_few)
    assert not result_punif['available'], "P-uniform should fail with few studies"
    print(f"✓ P-uniform correctly rejects: {result_punif['reason']}")

    # Selection model (needs >= 5)
    result_psm = SelectionModels.three_parameter_selection_model(effects_few, se_few)
    assert not result_psm['available'], "Selection model should fail with few studies"
    print(f"✓ Selection model correctly rejects: {result_psm['reason']}")

    # Limit MA (needs >= 5)
    result_lim = LimitMetaAnalysis.limit_meta_analysis(effects_few, se_few)
    assert not result_lim['available'], "Limit MA should fail with few studies"
    print(f"✓ Limit MA correctly rejects: {result_lim['reason']}")

    print("✓ test_insufficient_data passed")


# ===================================================================
# RUN ALL TESTS
# ===================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("RUNNING ADVANCED METHODS UNIT TESTS")
    print("="*70)

    tests = [
        test_p_uniform,
        test_p_uniform_star,
        test_selection_model,
        test_limit_meta_analysis,
        test_gosh_analysis,
        test_bootstrap_methods,
        test_restricted_cubic_splines,
        test_insufficient_data,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*70)

    if failed == 0:
        print("\n✓ All advanced methods tests passed!")
        print("✓ Ready for production use")
    else:
        print(f"\n✗ {failed} test(s) failed")

    sys.exit(0 if failed == 0 else 1)
