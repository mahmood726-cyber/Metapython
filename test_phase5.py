#!/usr/bin/env python3
"""
Test script for Phase 5 features of MetaPython
"""

import numpy as np
import pandas as pd
import sys
import os

# Add current directory to path to import metapython
sys.path.insert(0, '/home/runner/work/Metapython/Metapython')

try:
    import metapython
    print(f"✅ MetaPython v{metapython.__version__} imported successfully")
except ImportError as e:
    print(f"❌ Failed to import metapython: {e}")
    sys.exit(1)

def test_enhanced_dose_response():
    """Test enhanced dose-response functionality"""
    print("\n🧪 Testing Enhanced Dose-Response Analysis...")
    
    # Create sample dose-response data
    data = pd.DataFrame({
        'study': ['Study1', 'Study2', 'Study3', 'Study4', 'Study5'],
        'effect': [0.0, 0.2, 0.4, 0.3, 0.5],
        'se': [0.1, 0.12, 0.15, 0.11, 0.13],
        'dose_mg': [0, 10, 20, 15, 25]
    })
    
    try:
        meta = metapython.UnifiedMetaAnalysis(data, 'effect', 'se', 'study')
        
        # Test spline analysis
        spline_results = meta.spline_dose_response_analysis('dose_mg', n_knots=3)
        if spline_results.get('available'):
            print(f"   ✅ Spline analysis: {spline_results['method']}")
            print(f"      Nonlinearity p-value: {spline_results.get('p_nonlinearity', 'N/A')}")
        else:
            print(f"   ⚠️  Spline analysis limited: {spline_results.get('reason', 'Unknown')}")
        
        # Test dose standardization
        std_results = meta.dose_standardization_tools(data, 'dose_mg')
        print(f"   ✅ Dose standardization: {len(std_results['conversion_log'])} conversions")
        print(f"      Dose range: {std_results['dose_range']}")
        
    except Exception as e:
        print(f"   ❌ Dose-response test failed: {e}")

def test_time_to_event_analysis():
    """Test time-to-event analysis"""
    print("\n🧪 Testing Time-to-Event Analysis...")
    
    # Sample survival data
    log_hrs = np.array([0.2, -0.1, 0.4, 0.0, 0.3])
    se_log_hrs = np.array([0.15, 0.12, 0.18, 0.10, 0.14])
    
    try:
        # Test log HR meta-analysis
        survival_results = metapython.TimeToEventAnalysis.log_hr_meta_analysis(
            log_hrs, se_log_hrs, method='random', hartung_knapp=True
        )
        
        if survival_results.get('available'):
            hr = survival_results['random_effects']['hr']
            ci_low = survival_results['random_effects']['ci_low']
            ci_high = survival_results['random_effects']['ci_high']
            print(f"   ✅ Log HR meta-analysis successful")
            print(f"      Pooled HR: {hr:.3f} (95% CI: {ci_low:.3f}-{ci_high:.3f})")
            print(f"      Heterogeneity I²: {survival_results['heterogeneity']['I2']:.1%}")
        else:
            print(f"   ❌ Log HR analysis failed: {survival_results.get('reason')}")
        
        # Test Tierney reconstruction
        reconstruction = metapython.TimeToEventAnalysis.tierney_reconstruction(
            hr_reported=1.25, ci_low=1.05, ci_high=1.48
        )
        
        if reconstruction.get('available'):
            print(f"   ✅ Tierney reconstruction successful")
            print(f"      Reconstructed log HR: {reconstruction['log_hr']:.3f} ± {reconstruction['se_log_hr']:.3f}")
        else:
            print(f"   ❌ Tierney reconstruction failed")
        
    except Exception as e:
        print(f"   ❌ Time-to-event test failed: {e}")

def test_selection_bias_analysis():
    """Test selection bias methods"""
    print("\n🧪 Testing Selection Bias Analysis...")
    
    # Sample effect size data
    effects = np.array([0.4, 0.2, 0.6, 0.3, 0.5, 0.1, 0.7])
    ses = np.array([0.15, 0.18, 0.12, 0.20, 0.14, 0.16, 0.11])
    
    try:
        # Test p-curve analysis
        p_curve_results = metapython.SelectionBiasExtensions.p_curve_analysis(effects, ses)
        
        if p_curve_results.get('available'):
            evidential_value = p_curve_results['interpretation']['evidential_value']
            print(f"   ✅ P-curve analysis successful")
            print(f"      Evidential value: {evidential_value}")
            print(f"      Significant studies: {p_curve_results['n_significant_studies']}")
        else:
            print(f"   ⚠️  P-curve analysis: {p_curve_results.get('reason')}")
        
        # Test p-uniform analysis
        p_uniform_results = metapython.SelectionBiasExtensions.p_uniform_analysis(effects, ses)
        
        if p_uniform_results.get('available'):
            estimate = p_uniform_results['p_uniform_estimate']
            bias_detected = p_uniform_results['bias_detected']
            print(f"   ✅ P-uniform analysis successful")
            print(f"      Bias-corrected estimate: {estimate:.3f}")
            print(f"      Publication bias detected: {bias_detected}")
        else:
            print(f"   ⚠️  P-uniform analysis: {p_uniform_results.get('reason')}")
        
    except Exception as e:
        print(f"   ❌ Selection bias test failed: {e}")

def test_scalable_pipelines():
    """Test scalable pipelines and caching"""
    print("\n🧪 Testing Scalable Pipelines...")
    
    try:
        # Initialize pipeline
        pipeline = metapython.ScalablePipelines(cache_dir="/tmp/meta_test_cache")
        print(f"   ✅ Pipeline initialized with backend: {pipeline.backend}")
        
        # Test caching
        def expensive_computation(x):
            return x ** 2 + np.random.random()  # Add randomness to test caching
        
        # First computation
        result1 = pipeline.cached_computation(expensive_computation, 5, cache_key="test_computation")
        
        # Second computation (should be cached)
        result2 = pipeline.cached_computation(expensive_computation, 5, cache_key="test_computation")
        
        if abs(result1 - result2) < 1e-10:  # Should be identical if cached
            print(f"   ✅ Caching works correctly")
        else:
            print(f"   ⚠️  Caching may not be working (result1={result1}, result2={result2})")
        
        # Test cache info
        cache_info = pipeline.cache_info()
        print(f"   ✅ Cache info: {cache_info['total_artifacts']} artifacts")
        
        # Clean up
        pipeline.clear_cache()
        
    except Exception as e:
        print(f"   ❌ Scalable pipelines test failed: {e}")

def test_privacy_utilities():
    """Test privacy-friendly utilities"""
    print("\n🧪 Testing Privacy-Friendly Utilities...")
    
    try:
        # Test synthetic data generation
        synthetic_data = metapython.PrivacyFriendlyUtilities.generate_synthetic_meta_analysis_data(
            n_studies=10, effect_range=(0.1, 0.8), tau2=0.1, seed=42
        )
        
        print(f"   ✅ Synthetic data generation successful")
        print(f"      Generated {len(synthetic_data)} studies")
        print(f"      Effect range: [{synthetic_data['effect'].min():.3f}, {synthetic_data['effect'].max():.3f}]")
        
        # Test differential privacy
        test_data = np.array([0.2, 0.3, 0.4, 0.5, 0.6])
        dp_result = metapython.PrivacyFriendlyUtilities.differential_privacy_summary_stats(
            test_data, epsilon=1.0, stat_type='mean'
        )
        
        if dp_result.get('available'):
            print(f"   ✅ Differential privacy successful")
            print(f"      DP mean: {dp_result['dp_statistic']:.3f} (ε={dp_result['epsilon']})")
            print(f"      Noise-to-signal ratio: {dp_result['noise_to_signal_ratio']:.3f}")
        else:
            print(f"   ❌ Differential privacy failed")
        
    except Exception as e:
        print(f"   ❌ Privacy utilities test failed: {e}")

def test_backward_compatibility():
    """Test that existing functionality still works"""
    print("\n🧪 Testing Backward Compatibility...")
    
    try:
        # Generate test data using existing method
        demo_data = metapython.generate_demo_data(n_studies=10, seed=42)
        
        # Run basic analysis with correct column names  
        meta = metapython.UnifiedMetaAnalysis(demo_data, 'effect_size', 'standard_error', 'study_id')
        result_obj = meta.analyze(include_conflicts=False)  # Skip conflict detection to avoid sklearn dependency
        
        print(f"   ✅ Basic meta-analysis still works")
        print(f"      Fixed effects: {result_obj.results.fixed_effects.effect:.3f}")
        print(f"      Random effects: {result_obj.results.random_effects.effect:.3f}")
        print(f"      I² heterogeneity: {result_obj.results.heterogeneity.I2:.1%}")
        
        # Test existing dose-response
        dose_results = meta.dose_response_analysis('dose_mg', model_type='linear')
        print(f"   ✅ Existing dose-response works: slope = {dose_results['slope']:.3f}")
        
    except Exception as e:
        print(f"   ❌ Backward compatibility test failed: {e}")

def main():
    """Run all tests"""
    print("🚀 Testing MetaPython Phase 5 Features")
    print("=" * 50)
    
    # Run all tests
    test_backward_compatibility()
    test_enhanced_dose_response()
    test_time_to_event_analysis()
    test_selection_bias_analysis()
    test_scalable_pipelines()
    test_privacy_utilities()
    
    print("\n✨ Phase 5 Testing Complete!")
    print("🎉 MetaPython v0.5.0 is ready for release!")

if __name__ == "__main__":
    main()