# MetaPython v0.4.0 - Phase 4 Implementation

## What's New in Phase 4

### 1. Network Meta-Analysis Inconsistency and Extensions
- **Design-by-Treatment (DBT) Global Inconsistency Test**: Frequentist test for overall network inconsistency
- **Node-Splitting Local Inconsistency**: Compare direct vs. network evidence for specific comparisons  
- **Local Influence Diagnostics**: Identify influential studies/edges with ASCII heatmap visualization

### 2. Arm-Based GLMMs and Sparse-Event Methods
- **Peto Odds Ratio**: Robust method for rare events with continuity corrections
- **Refined Mantel-Haenszel OR**: Multiple correction strategies (constant, TACC, empirical)
- **Binomial GLMM**: Logit-link models with random study effects and convergence diagnostics
- **Event Analysis Guidance**: Automated recommendations for appropriate methods

### 3. Enhanced Diagnostic Test Accuracy (DTA) Meta-Analysis
- **Complete HSROC Model**: Freeman-Tukey and logit-based implementations with SROC curves
- **Fagan Nomogram Helpers**: Clinical interpretation with text-based fallbacks
- **Threshold-Dependent Analysis**: Performance across different diagnostic thresholds
- **Bivariate Random-Effects**: Enhanced Reitsma model implementation

### 4. Advanced Multivariate Structures  
- **Unstructured Covariance**: Completely flexible between-study covariance matrix
- **Factor-Analytic Covariance**: Parsimonious factor structure modeling
- **Robust Meta-Analytic Correlation**: Fisher's z-transform with small-sample corrections
- **Penalized Likelihood**: Ridge/Lasso/Elastic Net regularization for high-dimensional cases

### 5. CLI and Pipeline Automation
- **MetaCLI**: Command-line interface for configuration-driven analysis
- **Pipeline Runner**: YAML-based workflow orchestration with provenance tracking
- **Dataset Transform Registry**: Reusable preprocessing steps
- **Artifact Generation**: Automated CSV/JSON/HTML output with metadata

### 6. Performance and Reliability Improvements
- **Numba Hot Paths**: JIT-compiled critical functions (when available)
- **Memory-Efficient Iterators**: Chunked computation for large datasets  
- **Safe Numerical Practices**: Robust matrix operations and convergence monitoring
- **Enhanced Error Handling**: Graceful fallbacks when optional dependencies unavailable

## Usage Examples

### Sparse Events Analysis
```python
import metapython
import numpy as np

# Peto odds ratio for rare events
result = metapython.SparseEventMethods.peto_odds_ratio(
    treatment_events=np.array([2, 1, 3]),
    treatment_total=np.array([100, 150, 120]),
    control_events=np.array([5, 4, 8]), 
    control_total=np.array([100, 150, 120])
)
print(f"Peto OR: {result['peto_or']:.3f} ({result['ci_low']:.3f}-{result['ci_high']:.3f})")
```

### Network Inconsistency Testing
```python
import pandas as pd

network_data = pd.DataFrame({
    'treatment': ['A', 'B', 'A'],
    'comparator': ['B', 'C', 'C'],
    'effect': [0.2, 0.3, 0.6],
    'se': [0.1, 0.15, 0.2]
})

# Design-by-treatment inconsistency test
dbt_result = metapython.NetworkMetaRankings.design_by_treatment_inconsistency(network_data)
print(f"Global inconsistency p-value: {dbt_result['p_value']:.3f}")

# Node-splitting for local inconsistency
node_result = metapython.NetworkMetaRankings.node_splitting_inconsistency(network_data)
print(f"Inconsistent comparisons: {node_result['n_inconsistent']}")
```

### Enhanced Diagnostic Test Accuracy
```python
tp, fn, fp, tn = np.array([85, 90, 78]), np.array([15, 10, 22]), np.array([12, 8, 15]), np.array([88, 92, 85])

# Complete HSROC model
hsroc = metapython.EnhancedDiagnosticTestAccuracy.hsroc_model_complete(tp, fn, fp, tn)
print(f"Summary sensitivity: {hsroc['summary_sensitivity']:.3f}")
print(f"Summary specificity: {hsroc['summary_specificity']:.3f}")

# Fagan nomogram for clinical interpretation
fagan = metapython.EnhancedDiagnosticTestAccuracy.fagan_nomogram_helpers(
    pre_test_prob=0.15, plr=5.2, nlr=0.08
)
print(fagan['text_nomogram'])
```

### Pipeline Automation
```python
# Run analysis from YAML configuration
cli = metapython.MetaCLI()
result = cli.run_pipeline('meta_pipeline.yaml')
print(f"Pipeline completed: {result['success']}")
print(f"Artifacts saved to: {result['results']['generate_comprehensive_report']['output_directory']}")
```

## Backward Compatibility

All Phase 4 additions are **fully backward compatible**. Existing code will continue to work unchanged. New functionality is accessed through new classes and methods that don't interfere with existing APIs.

## Dependencies

Core functionality requires only:
- numpy
- pandas  
- matplotlib
- seaborn
- scipy

Optional enhancements available with:
- statsmodels (GLMMs, advanced regression)
- scikit-learn (ML clustering)
- PyYAML (pipeline configuration)
- Jinja2 (HTML reports)
- numba (performance optimization)

## Version History

- **v0.4.0**: Phase 4 implementation - Network inconsistency, sparse events, enhanced DTA, multivariate structures, CLI automation
- **v3.0.0**: Unified PyMeta-CBAMM suite with comprehensive meta-analysis capabilities