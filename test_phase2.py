"""
Comprehensive tests for Phase 2 R-parity features
================================================

Tests for network meta-analysis, multilevel models, effect size calculators,
and other new functionality introduced in Phase 2.
"""

import numpy as np
import pandas as pd
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import metapython
from example_datasets import get_example_dataset

def test_network_meta_analysis():
    """Test network meta-analysis functionality"""
    print("Testing Network Meta-Analysis...")
    
    # Get example network data
    dataset = get_example_dataset('smoking_network')
    data = dataset['data']
    
    # Create NetworkMetaData
    network_data = metapython.NetworkMetaData(
        study=data['study'].tolist(),
        treatment=data['treatment'].tolist(),
        yi=data['yi'].tolist(),
        sei=data['sei'].tolist(),
        n=data['n'].tolist(),
        events=data['events'].tolist()
    )
    
    # Test fixed-effects analysis
    nma_fixed = metapython.NetworkMetaAnalysis(network_data, method='fixed')
    nma_fixed.fit()
    
    print(f"  Fixed-effects network analysis completed")
    print(f"  Treatments: {nma_fixed.results.geometry.treatments}")
    print(f"  Network connected: {nma_fixed.results.geometry.is_connected}")
    print(f"  P-scores: {nma_fixed.results.p_scores.round(3).to_dict()}")
    
    # Test random-effects analysis
    nma_random = metapython.NetworkMetaAnalysis(network_data, method='random')
    nma_random.fit()
    
    print(f"  Random-effects tau²: {nma_random.results.tau2:.4f}")
    
    # Test league table
    league_table = nma_fixed.results.league_table
    print(f"  League table shape: {league_table.shape}")
    
    return True

def test_multilevel_meta_analysis():
    """Test multilevel/multivariate meta-analysis"""
    print("\nTesting Multilevel Meta-Analysis...")
    
    # Get multilevel example data
    dataset = get_example_dataset('multilevel')
    data = dataset['data']
    
    # Create multilevel analysis
    mma = metapython.MultilevelMetaAnalysis(
        data=data,
        yi_col='yi',
        vi_col='vi', 
        study_col='study',
        outcome_col='outcome'
    )
    
    # Fit model
    mma.fit()
    
    print(f"  Multilevel analysis completed")
    print(f"  Overall effect: {mma.results.effects[0]:.3f} (SE: {mma.results.se[0]:.3f})")
    print(f"  Variance components: {mma.results.variance_components}")
    
    # Test cluster-robust SE
    robust_se = mma.cluster_robust_se()
    print(f"  Robust SE available: {len(robust_se) > 0}")
    
    return True

def test_correlated_effects():
    """Test correlated effects analysis"""
    print("\nTesting Correlated Effects Analysis...")
    
    # Get correlated effects data
    dataset = get_example_dataset('correlated')
    data = dataset['data']
    
    # Create correlated effects analysis
    cea = metapython.CorrelatedEffectsAnalysis(
        data=data,
        yi_col='yi',
        vi_col='vi',
        study_col='study',
        rho=0.8
    )
    
    # Sensitivity analysis
    sensitivity_df = cea.sensitivity_analysis(rho_values=[0.0, 0.5, 0.8])
    
    print(f"  Sensitivity analysis completed")
    print(f"  Rho values tested: {sensitivity_df['rho'].tolist()}")
    print(f"  Effect range: {sensitivity_df['effect'].min():.3f} to {sensitivity_df['effect'].max():.3f}")
    
    return True

def test_effect_size_calculators():
    """Test effect size calculation functions"""
    print("\nTesting Effect Size Calculators...")
    
    # Test binary data calculations
    events1 = np.array([20, 15, 25])
    n1 = np.array([100, 80, 120]) 
    events2 = np.array([10, 12, 18])
    n2 = np.array([100, 80, 120])
    
    # Log odds ratio
    lor, se_lor = metapython.EffectSizeCalculators.log_odds_ratio(events1, n1, events2, n2)
    print(f"  Log OR calculated: {lor.mean():.3f} ± {se_lor.mean():.3f}")
    
    # Log risk ratio
    lrr, se_lrr = metapython.EffectSizeCalculators.log_risk_ratio(events1, n1, events2, n2)
    print(f"  Log RR calculated: {lrr.mean():.3f} ± {se_lrr.mean():.3f}")
    
    # Test continuous data calculations
    mean1 = np.array([10.5, 12.0, 9.8])
    sd1 = np.array([2.1, 2.5, 1.9])
    mean2 = np.array([8.2, 9.5, 8.0])
    sd2 = np.array([2.0, 2.3, 1.8])
    
    # Hedges' g
    g, se_g = metapython.EffectSizeCalculators.hedges_g(mean1, sd1, n1, mean2, sd2, n2)
    print(f"  Hedges' g calculated: {g.mean():.3f} ± {se_g.mean():.3f}")
    
    # Test correlation data
    correlations = np.array([0.3, 0.5, 0.7])
    n_corr = np.array([50, 60, 70])
    
    # Fisher z-transform
    z, se_z = metapython.EffectSizeCalculators.fisher_z_transform(correlations, n_corr)
    print(f"  Fisher z calculated: {z.mean():.3f} ± {se_z.mean():.3f}")
    
    # Test converters
    d_to_r = metapython.EffectSizeConverters.d_to_r(0.5)
    r_to_d = metapython.EffectSizeConverters.r_to_d(0.3)
    print(f"  Conversions: d=0.5 → r={d_to_r:.3f}, r=0.3 → d={r_to_d:.3f}")
    
    return True

def test_selection_models():
    """Test selection model functionality"""
    print("\nTesting Selection Models...")
    
    # Create example data with potential publication bias
    np.random.seed(42)
    n_studies = 20
    true_effect = 0.3
    effects = np.random.normal(true_effect, 0.2, n_studies)
    se_vals = np.random.uniform(0.05, 0.25, n_studies)
    
    # Add publication bias (suppress non-significant negative effects)
    p_values = 2 * (1 - np.abs(effects) / se_vals)  # Approximate p-values
    
    # Vevea-Hedges selection model
    result = metapython.SelectionModels.vevea_hedges_model(effects, se_vals, p_values)
    
    if result['available']:
        print(f"  Selection model available: {result['available']}")
        if result.get('converged'):
            print(f"  Adjusted effect: {result['mu']:.3f}")
        else:
            print(f"  Model did not converge: {result.get('message', 'Unknown reason')}")
    else:
        print(f"  Selection model not available: {result.get('message', 'Unknown')}")
    
    return True

def test_bias_tests():
    """Test additional bias test functions"""
    print("\nTesting Bias Test Suite...")
    
    # Create example data
    effects = np.array([0.2, 0.4, 0.1, 0.6, 0.3, 0.5, 0.25, 0.35])
    se_vals = np.array([0.15, 0.20, 0.12, 0.25, 0.18, 0.22, 0.16, 0.19])
    
    # Peters test
    peters_result = metapython.BiasTestSuite.peters_test(effects, se_vals)
    if peters_result.get('available', True):
        print(f"  Peters test p-value: {peters_result.get('p_value', 'N/A')}")
    
    # Arcsine test
    # Convert effects to proportions for arcsine test
    proportions = 1 / (1 + np.exp(-effects))  # Logistic transform
    arcsine_result = metapython.BiasTestSuite.arcsine_test(proportions, se_vals)
    if arcsine_result.get('available', True):
        print(f"  Arcsine test p-value: {arcsine_result.get('p_value', 'N/A')}")
    
    # Test stubs
    p_curve = metapython.BiasTestSuite.p_curve_stub()
    p_uniform = metapython.BiasTestSuite.p_uniform_stub()
    print(f"  P-curve available: {p_curve['available']}")
    print(f"  P-uniform available: {p_uniform['available']}")
    
    return True

def test_r_compatibility():
    """Test R compatibility functions"""
    print("\nTesting R Compatibility...")
    
    # Test R script generation
    mock_results = {'method': 'REML', 'effect': 0.45, 'tau2': 0.12}
    r_script_path = metapython.RCompatibility.generate_r_script(mock_results, "test_script.R")
    
    if os.path.exists(r_script_path):
        print(f"  R script generated: {r_script_path}")
        with open(r_script_path, 'r') as f:
            content = f.read()
            print(f"  Script length: {len(content)} characters")
        
        # Clean up
        os.remove(r_script_path)
    else:
        print("  R script generation failed")
    
    return True

def test_example_datasets():
    """Test example datasets"""
    print("\nTesting Example Datasets...")
    
    from example_datasets import list_datasets, get_example_dataset
    
    datasets = list_datasets()
    print(f"  Available datasets: {len(datasets)}")
    
    for name, description in datasets.items():
        try:
            dataset = get_example_dataset(name)
            data = dataset['data']
            print(f"  {name}: {len(data)} observations - {description}")
        except Exception as e:
            print(f"  {name}: Error loading - {e}")
    
    return True

def run_parity_tests():
    """Run comprehensive parity tests"""
    print("=" * 60)
    print("PHASE 2 R-PARITY FEATURE TESTS")
    print("=" * 60)
    
    tests = [
        test_network_meta_analysis,
        test_multilevel_meta_analysis,
        test_correlated_effects,
        test_effect_size_calculators,
        test_selection_models,
        test_bias_tests,
        test_r_compatibility,
        test_example_datasets
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"  FAILED: {test_func.__name__}")
        except Exception as e:
            failed += 1
            print(f"  ERROR in {test_func.__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = run_parity_tests()
    sys.exit(0 if success else 1)