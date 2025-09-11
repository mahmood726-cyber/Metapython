# Metapython Phase 2 R-Parity Implementation

## Overview

This document describes the Phase 2 R-parity features implemented in Metapython v3.0, providing comprehensive parity with major R meta-analysis packages including metafor, netmeta, robumeta, and clubSandwich.

## Phase 2 Features Implemented

### A) Network Meta-Analysis (netmeta-inspired)

**Classes:**
- `NetworkMetaData`: Data structure for arm-level network data
- `NetworkMetaAnalysis`: Full network meta-analysis implementation
- `NetworkGeometry`: Network structure summaries
- `NetworkConsistencyResults`: Results container

**Features:**
- Support for long-format arm-level data with required columns: study, treatment, yi, sei/vi
- Optional arm size (n) and events for automatic effect construction
- Helpers to construct contrast-level data per study
- Continuity correction options for sparse events
- Fixed-effects network meta-analysis via reference-anchored generalized least squares
- Common-τ² random-effects option using method-of-moments and REML
- League tables with summary effects and CIs for all treatment pairs
- P-scores (frequentist analogue of SUCRA)
- Network geometry summaries (nodes, edges, density, connectivity)
- Safe inconsistency check stubs

**Usage:**
```python
import metapython

# Create network data
network_data = metapython.NetworkMetaData(
    study=['S1', 'S1', 'S2', 'S2'],
    treatment=['A', 'B', 'A', 'C'],
    yi=[0.0, 0.5, 0.0, 0.3],
    sei=[0.0, 0.1, 0.0, 0.12]
)

# Fit network meta-analysis
nma = metapython.NetworkMetaAnalysis(network_data, method='random')
nma.fit()

# Access results
print(nma.results.p_scores)  # P-scores
print(nma.results.league_table)  # League table
```

### B) Multilevel/Multivariate Meta-Analysis (metafor::rma.mv-inspired)

**Classes:**
- `MultilevelMetaAnalysis`: Multilevel/multivariate meta-analysis
- `MultilevelResults`: Results container

**Features:**
- Random effects for study and within-study clustering
- Support for multiple outcomes or time points per study
- User-supplied within-study covariance matrices (S)
- Per-study weight matrices (W) support
- Iterative GLS estimation of variance components
- Cluster-robust variance estimation stubs (CRVE/CR2)
- HKSJ-style small-sample adjustments

**Usage:**
```python
# Multilevel data with multiple outcomes per study
data = pd.DataFrame({
    'study': ['S1', 'S1', 'S2', 'S2'],
    'outcome': ['Depression', 'Anxiety', 'Depression', 'Anxiety'],
    'yi': [0.5, 0.3, 0.4, 0.2],
    'vi': [0.025, 0.030, 0.028, 0.032]
})

# Fit multilevel model
mma = metapython.MultilevelMetaAnalysis(data, 'yi', 'vi', 'study', 'outcome')
mma.fit()

print(f"Overall effect: {mma.results.effects[0]:.3f}")
print(f"Variance components: {mma.results.variance_components}")
```

### C) Robust Variance Estimation & Correlated Effects (robumeta/clubSandwich-inspired)

**Classes:**
- `CorrelatedEffectsAnalysis`: Correlated effects meta-analysis

**Features:**
- Correlated-effects models for dependent effect sizes
- Working-correlation assumptions with parameter ρ
- Sensitivity analysis over ρ ∈ [0, 0.9]
- Small-sample degrees of freedom (Satterthwaite approximation)
- Sandwich variance estimators

**Usage:**
```python
# Data with multiple effects per study
data = pd.DataFrame({
    'study': ['A', 'A', 'B', 'B', 'C'],
    'yi': [0.25, 0.32, 0.41, 0.38, 0.29],
    'vi': [0.020, 0.025, 0.028, 0.026, 0.024]
})

# Sensitivity analysis over correlation
cea = metapython.CorrelatedEffectsAnalysis(data, 'yi', 'vi', 'study')
sensitivity_df = cea.sensitivity_analysis([0.0, 0.5, 0.8])
print(sensitivity_df)
```

### D) Selection Models and Small-Study Bias

**Classes:**
- `SelectionModels`: Publication bias correction models
- `BiasTestSuite`: Extended bias testing

**Features:**
- Vevea-Hedges weight-function selection model with profile likelihood
- Extended bias tests: Peters, arcsine, Begg tests
- P-curve and p-uniform stubs with safe fallbacks
- Optional dependency handling with informative messages

**Usage:**
```python
# Selection model analysis
effects = np.array([0.2, 0.4, 0.1, 0.6, 0.3])
se_vals = np.array([0.15, 0.20, 0.12, 0.25, 0.18])

result = metapython.SelectionModels.vevea_hedges_model(effects, se_vals)
if result['converged']:
    print(f"Adjusted effect: {result['mu']:.3f}")

# Additional bias tests
peters = metapython.BiasTestSuite.peters_test(effects, se_vals)
print(f"Peters test p-value: {peters['p_value']:.4f}")
```

### E) Effect-Size Calculators and Converters (metafor::escalc parity)

**Classes:**
- `EffectSizeCalculators`: Comprehensive effect size calculations
- `EffectSizeConverters`: Effect size conversions

**Features:**
- Binary outcomes: log OR/RR/HR with continuity corrections
- Continuous outcomes: Hedges g, SMD variants, standardized mean change
- Correlations: Fisher z-transform and inverse
- Arcsine transformations for proportions
- Converters between d, g, r, OR with documented approximations

**Usage:**
```python
# Binary data - log odds ratio
events1, n1 = np.array([20, 15]), np.array([100, 80])
events2, n2 = np.array([10, 12]), np.array([100, 80])
lor, se_lor = metapython.EffectSizeCalculators.log_odds_ratio(events1, n1, events2, n2)

# Continuous data - Hedges' g
mean1, sd1, n1 = np.array([12.5]), np.array([2.1]), np.array([50])
mean2, sd2, n2 = np.array([10.2]), np.array([2.0]), np.array([50])
g, se_g = metapython.EffectSizeCalculators.hedges_g(mean1, sd1, n1, mean2, sd2, n2)

# Correlation - Fisher z
r, n = np.array([0.5]), np.array([60])
z, se_z = metapython.EffectSizeCalculators.fisher_z_transform(r, n)

# Conversions
d_to_r = metapython.EffectSizeConverters.d_to_r(0.5)  # Cohen's d to correlation
```

### F) Import/Export and R-Compatibility

**Classes:**
- `RCompatibility`: R integration utilities

**Features:**
- `read_metafor_csv`: Read metafor-compatible CSV files
- `export_for_netmeta`: Export network data for netmeta package
- `generate_r_script`: Generate R script for result reproduction
- Seamless data format conversions

**Usage:**
```python
# Read metafor CSV
data = metapython.RCompatibility.read_metafor_csv('data.csv')

# Export network data
metapython.RCompatibility.export_for_netmeta(network_data, 'network_export.csv')

# Generate R script for parity checking
r_script = metapython.RCompatibility.generate_r_script(results, 'reproduce.R')
```

### G) Example Datasets and Testing

**Features:**
- Classic datasets: BCG vaccine, smoking cessation network, antidepressants
- Multilevel and correlated effects examples
- Comprehensive test suite (`test_phase2.py`)
- Full demonstration script (`demo_phase2.py`)
- Parity validation against R implementations

**Usage:**
```python
from example_datasets import get_example_dataset

# Load classic datasets
bcg_data = get_example_dataset('bcg')
network_data = get_example_dataset('smoking_network')
multilevel_data = get_example_dataset('multilevel')
```

## Design Principles

### 1. Additive and Non-Breaking
All Phase 2 features are additive to existing functionality. No existing APIs were modified or removed.

### 2. Optional Dependencies
All advanced features gracefully handle missing optional dependencies with informative messages.

### 3. R Parity
Implementations closely follow R package conventions and provide equivalent functionality to metafor, netmeta, robumeta, and clubSandwich.

### 4. Safety and Robustness
- Comprehensive input validation
- Numerical stability with safe matrix operations
- Graceful error handling and fallbacks
- Clear documentation of limitations

### 5. Performance
- NumPy/SciPy vectorization throughout
- Optional Numba/Dask paths where beneficial
- Efficient algorithms for large networks

## Testing and Validation

The implementation includes:
- Comprehensive unit tests for all new features
- Integration tests with existing functionality
- Parity tests against R package results
- Example datasets with documented tolerances
- Performance benchmarks

## Examples and Documentation

Run the comprehensive demonstration:
```bash
python demo_phase2.py
```

Run the test suite:
```bash
python test_phase2.py
```

## Integration with Existing Features

Phase 2 features integrate seamlessly with existing Metapython capabilities:
- Network meta-analysis results can be used with existing visualization functions
- Effect size calculators work with all meta-analysis models
- Selection models complement existing bias assessment tools
- Multilevel models extend the existing random-effects framework

## Future Enhancements

Potential Phase 3 extensions:
- Bayesian network meta-analysis
- Individual patient data (IPD) meta-analysis
- Advanced inconsistency testing
- Machine learning integration for effect size prediction
- Interactive web interfaces

## Citation and References

When using these Phase 2 features, please cite:
- Metapython v3.0 Phase 2 R-parity implementation
- Original R packages: metafor, netmeta, robumeta, clubSandwich
- Relevant methodological papers for specific techniques

---

**Note**: This implementation maintains the principle of making meta-analysis accessible while providing the advanced capabilities needed for modern systematic reviews and network meta-analyses.