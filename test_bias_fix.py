#!/usr/bin/env python3
"""
Test script to verify the bias assessment fix for missing dependencies.

This test specifically reproduces the original crash scenario described in the issue:
- Running in a minimal environment without optional dependencies (statsmodels, sklearn)
- The unified demo completes core analysis but should not crash in the bias section
- Tests that p-values and other metrics are properly handled when missing or non-numeric
"""

import numpy as np
import pandas as pd
from metapython import UnifiedMetaAnalysis

def test_bias_assessment_without_dependencies():
    """Test bias assessment handling when dependencies are unavailable"""
    print("Testing bias assessment robustness without optional dependencies...")
    
    # Create test data
    np.random.seed(42)
    data = pd.DataFrame({
        'effect_size': np.random.normal(0.5, 0.3, 10),
        'standard_error': np.random.uniform(0.1, 0.3, 10),
        'study_id': [f'Study_{i}' for i in range(10)]
    })
    
    try:
        # This should not crash
        meta = UnifiedMetaAnalysis(data, 'effect_size', 'standard_error', 'study_id')
        meta.analyze(include_bias_tests=True)
        
        # Check bias assessment results structure
        bias = meta.results.bias_assessment
        
        # Verify Egger test handles missing statsmodels gracefully
        egger = bias.egger
        assert 'available' in egger
        assert 'success' in egger
        assert egger['available'] == False  # Should be False without statsmodels
        assert egger['success'] == False
        assert egger['p_value'] is None
        print("✓ Egger test properly handles missing statsmodels")
        
        # Verify PET-PEESE handles missing statsmodels gracefully
        pet_peese = bias.pet_peese
        assert 'available' in pet_peese
        assert 'success' in pet_peese
        assert 'corrected_effect' in pet_peese
        assert pet_peese['available'] == False  # Should be False without statsmodels
        assert pet_peese['success'] == False
        assert pet_peese['corrected_effect'] is None
        print("✓ PET-PEESE properly handles missing statsmodels")
        
        # Verify trim-and-fill works without dependencies
        trim_fill = bias.trim_fill
        assert 'available' in trim_fill
        assert 'success' in trim_fill
        assert 'n_imputed' in trim_fill
        print("✓ Trim-and-fill works without dependencies")
        
        # Test visualization doesn't crash
        fig = meta.create_funnel_plot(enhanced=True, include_bias_methods=True)
        print("✓ Funnel plot creation works with missing bias metrics")
        
        # Test report generation doesn't crash
        report = meta.comprehensive_report()
        assert 'PET-PEESE: N/A' in report
        assert 'Egger' in report and 'N/A' in report
        print("✓ Report generation works with missing bias metrics")
        
        print("\n🎉 SUCCESS: All bias assessment methods properly handle missing dependencies!")
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_bias_assessment_without_dependencies()
    if success:
        print("\nThe fix successfully prevents crashes when p-values or other bias metrics are missing.")
    else:
        print("\nThe fix did not work properly.")
        exit(1)