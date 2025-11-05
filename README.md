# MetaPython - Production-Ready Meta-Analysis Library

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive, production-ready Python library for meta-analysis combining state-of-the-art methods with extensive diagnostics, visualizations, and automation capabilities.

## ✨ Key Features

### Core Meta-Analysis
- **Fixed and Random Effects Models** with multiple τ² estimators (DL, REML, Hunter-Schmidt, Hedges, etc.)
- **Heterogeneity Assessment** (Q, I², H², τ²) with comprehensive diagnostics
- **Prediction Intervals** for future studies
- **Subgroup Analysis** with between-group heterogeneity tests

### Advanced Methods
- **Publication Bias Detection**: Egger's test, Begg's test, trim-and-fill, p-curve, PET-PEESE, weight function models
- **Sensitivity Analysis**: Leave-one-out (with 50-100x speedup), influence diagnostics, multiverse analysis
- **Conflict Detection**: ML-based clustering to identify inconsistent evidence
- **Transport Weighting**: External validity assessment for target populations
- **Network Meta-Analysis**: Consistency testing, node-splitting, ranking
- **Diagnostic Test Accuracy**: HSROC models, Fagan nomograms, SROC curves
- **Sparse Event Methods**: Peto OR, refined Mantel-Haenszel
- **Sequential Analysis**: Trial sequential analysis with monitoring boundaries

### Automation & Integration
- **Living Meta-Analysis**: Automated PubMed monitoring and updates
- **CLI & Pipeline Support**: YAML-based workflow automation
- **NLP Extraction**: Automated effect size extraction from abstracts
- **Comprehensive Visualization**: Forest plots, funnel plots, radial plots, Baujat plots

## 🚀 Quick Start

### Installation

```bash
pip install numpy pandas matplotlib seaborn scipy

# Optional dependencies for advanced features
pip install statsmodels scikit-learn pymc arviz
pip install spacy xgboost shap cvxpy pyyaml jinja2
```

### Basic Usage

```python
import pandas as pd
from metapython import UnifiedMetaAnalysis

# Prepare your data
data = pd.DataFrame({
    'study': ['Study 1', 'Study 2', 'Study 3', 'Study 4', 'Study 5'],
    'log_or': [0.2, 0.5, 0.3, 0.6, 0.4],
    'se': [0.1, 0.15, 0.12, 0.18, 0.11]
})

# Run meta-analysis
meta = UnifiedMetaAnalysis(data, effect_col='log_or', se_col='se', label_col='study')
meta.analyze()

# Access results
print(f"Random-effects estimate: {meta.results.random_effects.effect:.3f}")
print(f"95% CI: ({meta.results.random_effects.ci_low:.3f}, "
      f"{meta.results.random_effects.ci_high:.3f})")
print(f"I² = {meta.results.heterogeneity.I2:.1f}%")
print(f"τ² = {meta.results.heterogeneity.tau2:.3f}")

# Create visualizations
meta.create_forest_plot()
meta.create_funnel_plot()

# Sensitivity analysis
loo_results = meta.leave_one_out_analysis(fast=True)  # 50-100x faster!
influential_studies = loo_results[loo_results['influential']]
print(f"Found {len(influential_studies)} influential studies")
```

## 📊 Performance Improvements

Our recent optimizations provide dramatic performance improvements:

### Leave-One-Out Analysis
- **50-100x faster** for large meta-analyses (>20 studies)
- Vectorized computation option (`fast=True`)
- 50 studies: ~0.01s (fast) vs ~0.5s (comprehensive)

### Matrix Operations
- **O(n) memory** instead of O(n²)
- Avoids dense diagonal matrices through broadcasting
- 1000 observations: saves ~8 MB memory, 10x faster

## 🔒 Security Features

Built-in security for file operations:

```python
from metapython import validate_file_path, SecurityError

try:
    # Validates file exists, checks size, prevents path traversal
    safe_path = validate_file_path(
        'data.csv',
        allowed_extensions=['.csv'],
        max_size_mb=100.0
    )
except SecurityError as e:
    print(f"Security validation failed: {e}")
```

## 🎯 Advanced Features

### Comprehensive Publication Bias Assessment

```python
# All major bias tests in one call
meta.analyze(include_bias_tests=True)

# Access individual test results
bias = meta.results.bias_assessment
print(f"Egger's test p-value: {bias['egger']['p_value']:.3f}")
print(f"Trim-and-fill imputed studies: {bias['trim_fill']['n_imputed']}")
print(f"P-curve right-skewed: {bias['p_curve']['right_skewed']}")
```

### Fast Sensitivity Analysis

```python
# Ultra-fast leave-one-out (vectorized)
loo = meta.leave_one_out_analysis(fast=True)

# Identify influential studies
print(loo[loo['influential']])

# Comprehensive diagnostics
diagnostics = meta.influence_diagnostics()
high_influence = diagnostics[diagnostics['influential']]
```

### Living Meta-Analysis

```python
from metapython import PubMedIntegration

# Set up automated monitoring
pubmed = PubMedIntegration(email="your@email.com")
new_studies = pubmed.fetch_studies(
    query="(meta-analysis) AND (hypertension)",
    max_records=100
)

# Update existing meta-analysis
updated_data = pd.concat([existing_data, new_studies])
meta_updated = UnifiedMetaAnalysis(updated_data, 'effect', 'se', 'study')
meta_updated.analyze()
```

### Network Meta-Analysis

```python
from metapython import NetworkMetaRankings

# Test for inconsistency
network_data = pd.DataFrame({
    'treatment': ['A', 'B', 'A', 'B', 'C'],
    'comparator': ['B', 'C', 'C', 'D', 'D'],
    'effect': [0.2, 0.3, 0.6, 0.4, 0.5],
    'se': [0.1, 0.15, 0.2, 0.12, 0.14]
})

# Design-by-treatment inconsistency test
dbt = NetworkMetaRankings.design_by_treatment_inconsistency(network_data)
print(f"Global inconsistency p-value: {dbt['p_value']:.3f}")

# Node-splitting for local inconsistency
node_split = NetworkMetaRankings.node_splitting_inconsistency(network_data)
print(f"Inconsistent comparisons: {node_split['n_inconsistent']}")
```

## 📈 Diagnostic Test Accuracy

```python
from metapython import EnhancedDiagnosticTestAccuracy

# HSROC model for diagnostic accuracy
tp = np.array([85, 90, 78])  # True positives
fn = np.array([15, 10, 22])  # False negatives
fp = np.array([12, 8, 15])   # False positives
tn = np.array([88, 92, 85])  # True negatives

hsroc = EnhancedDiagnosticTestAccuracy.hsroc_model_complete(tp, fn, fp, tn)
print(f"Summary sensitivity: {hsroc['summary_sensitivity']:.3f}")
print(f"Summary specificity: {hsroc['summary_specificity']:.3f}")

# Fagan nomogram
fagan = EnhancedDiagnosticTestAccuracy.fagan_nomogram_helpers(
    pre_test_prob=0.15, plr=5.2, nlr=0.08
)
print(fagan['text_nomogram'])
```

## 🛠️ CLI and Pipeline Automation

### YAML Configuration

```yaml
# config.yaml
data_file: "meta_data.csv"
effect_col: "log_or"
se_col: "se"
label_col: "study"

analysis_options:
  tau2_method: "REML"
  use_hksj: true
  include_bias_tests: true

output_options:
  save_forest_plot: true
  save_funnel_plot: true
  output_dir: "results"
```

### Run from CLI

```python
from metapython import MetaCLI

cli = MetaCLI()
result = cli.run_from_config('config.yaml')

if result['success']:
    print(f"Analysis complete! Results in {result['output_dir']}")
else:
    print(f"Error: {result['error']}")
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python tests/test_metapython.py

# Or with pytest
pip install pytest
pytest tests/
```

## ⚡ Performance Benchmarks

Compare optimizations:

```bash
python benchmarks/performance_benchmarks.py
```

Expected results:
- Leave-one-out (50 studies): 50-100x speedup
- Matrix operations (1000 obs): 10x faster, 8MB memory saved
- Complete workflow: <100ms for 50 studies

## 📚 Documentation

### Key Classes

- `UnifiedMetaAnalysis`: Main meta-analysis class
- `TauSquaredEstimators`: τ² estimation methods
- `NetworkMetaRankings`: Network meta-analysis
- `EnhancedDiagnosticTestAccuracy`: DTA meta-analysis
- `SparseEventMethods`: Rare event methods
- `MetaCLI`: Command-line interface

### Configuration

```python
from metapython import UnifiedMetaConfig

config = UnifiedMetaConfig(
    alpha=0.05,                    # Significance level
    tau2_method='REML',            # DL, REML, HS, Hedges
    use_hksj=False,                # Hartung-Knapp-Sidik-Jonkman
    prediction_interval=True,      # Calculate prediction intervals
    bias_correction=True,          # Small-sample corrections
    min_studies=2,                 # Minimum studies required
    max_iterations=1000,           # Convergence iterations
    convergence_tolerance=1e-6     # Convergence criterion
)

meta = UnifiedMetaAnalysis(data, 'effect', 'se', 'study', config=config)
```

## 🔧 Troubleshooting

### Common Issues

**ImportError: No module named 'statsmodels'**
```bash
pip install statsmodels
```

**PyTensor compilation issues (minimal environments)**
```bash
export PYTENSOR_FLAGS="device=cpu,floatX=float32,optimizer=fast_compile,openmp=False"
python your_script.py
```

**Memory issues with large meta-analyses**
```python
# Use fast mode for leave-one-out
loo = meta.leave_one_out_analysis(fast=True)

# Disable optional analyses
meta.analyze(include_bias_tests=False, include_conflicts=False)
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

Combines best practices from:
- PyMeta v2.1: Core meta-analysis methods
- CBAMM v5.7: Transport weighting and robust methods
- Cochrane Handbook: Gold standard methodology
- R metafor package: Advanced techniques

## 📞 Support

- Issues: https://github.com/mahmood726-cyber/Metapython/issues
- Documentation: See PHASE4_CHANGELOG.md for detailed API reference
- Examples: Check tests/ and benchmarks/ directories

---

**Version 0.4.1** - Production-ready with comprehensive optimizations and security features
