# MetaPython v0.4.0 - Unified Meta-Analysis Platform

A comprehensive, production-ready meta-analysis library that combines PyMeta v2.1 and CBAMM v5.7 capabilities with enhanced robustness for minimal environments.

## 🚀 Key Features

- **Core Meta-Analysis**: Fixed-effects, random-effects, advanced heterogeneity assessment
- **Publication Bias**: Comprehensive bias detection (Egger's, Begg's, PET, PEESE, selection models)
- **Advanced Methods**: Network meta-analysis, diagnostic test accuracy, sequential analysis
- **Sparse Events**: Specialized methods for rare events (Peto OR, Mantel-Haenszel)
- **Bayesian Analysis**: Full Bayesian workflow with PyMC (when available)
- **Living Meta-Analysis**: Automated updates and monitoring
- **Educational Tools**: Simulation and teaching capabilities

## 🛠️ Robust Design for Minimal Environments

MetaPython is specifically designed to work reliably in constrained environments:

- **GitHub Codespaces** - No compilation overhead
- **CI/CD Systems** - Works with static libpython
- **Docker Containers** - Functions without development tools
- **Cloud Notebooks** - Jupyter-compatible with minimal setup

### Robustness Features

1. **Zero-Compilation PyTensor**: Automatically configures PyTensor to avoid C compilation
2. **Graceful Degradation**: Core functionality works with minimal dependencies
3. **Throttled Warnings**: Each missing dependency logs only once per run
4. **Enhanced Error Handling**: Robust fallbacks for environment-specific failures

## 📦 Installation

### Minimal Installation (Core Features)

For basic meta-analysis functionality:

```bash
pip install numpy pandas matplotlib seaborn scipy
```

### Full Installation (All Features)

For complete functionality including Bayesian methods, ML features, and advanced analysis:

```bash
pip install numpy pandas matplotlib seaborn scipy statsmodels scikit-learn pymc arviz spacy cvxpy biopython xgboost shap numba dask joblib streamlit flask pytest pyyaml jinja2
```

## 🔧 Environment Configuration

### For Minimal Environments

If you're running in Codespaces, CI, or containers, MetaPython automatically configures itself for minimal compilation overhead. You can also manually set:

```bash
export PYTENSOR_FLAGS="device=cpu,floatX=float32,optimizer=fast_compile,openmp=False,blas__ldflags="
```

### Why This Matters

- **Prevents long compilation times** in environments without development tools
- **Avoids linking errors** with static libpython
- **Ensures immediate startup** in cloud and container environments
- **Reduces memory usage** by disabling unnecessary optimizations

## 🚀 Quick Start

### Basic Meta-Analysis

```python
import metapython
import numpy as np
import pandas as pd

# Sample data
data = pd.DataFrame({
    'effect': [0.2, 0.5, 0.3, 0.4, 0.1],
    'se': [0.1, 0.15, 0.12, 0.14, 0.09],
    'study': ['Study1', 'Study2', 'Study3', 'Study4', 'Study5']
})

# Create meta-analysis object
meta = metapython.UnifiedMetaAnalysis(data, effect_col='effect', se_col='se')

# Run comprehensive analysis
meta.analyze()

# View results
print(f"Fixed-effects: {meta.results.fixed_effects.effect:.3f} ({meta.results.fixed_effects.ci_low:.3f}, {meta.results.fixed_effects.ci_high:.3f})")
print(f"Random-effects: {meta.results.random_effects.effect:.3f} ({meta.results.random_effects.ci_low:.3f}, {meta.results.random_effects.ci_high:.3f})")
```

### Complete Demo (All Features)

```python
# Run comprehensive demonstration
meta = metapython.run_unified_demo(
    n_studies=25, 
    save_visuals=True, 
    save_text_report=True
)
```

## 📊 Core Dependencies vs Optional Enhancements

### Core Dependencies (Always Required)
- **numpy**: Numerical computations
- **pandas**: Data manipulation
- **matplotlib**: Basic plotting
- **seaborn**: Enhanced visualizations
- **scipy**: Statistical functions

### Optional Enhancements
- **statsmodels**: Advanced regression methods, GLMMs
- **scikit-learn**: Machine learning clustering and classification
- **pymc + arviz**: Bayesian meta-analysis
- **spacy**: NLP-based effect extraction
- **cvxpy**: Transport weighting optimization
- **biopython**: PubMed integration for living meta-analysis
- **xgboost + shap**: ML-based heterogeneity detection
- **numba**: Performance optimization
- **streamlit + flask**: Web interfaces

## 🎯 Graceful Degradation

When optional dependencies are unavailable:

```
INFO:metapython:PyMC/PyTensor not available - Bayesian methods disabled
INFO:metapython:spaCy not available - NLP extraction disabled
INFO:metapython:CVXPY not available - transport weighting disabled
```

- **Core meta-analysis** functions continue to work
- **Alternative methods** are automatically used
- **Clear guidance** provided for installing missing features
- **No crashes or errors** - robust fallback behavior

## 🔍 Troubleshooting

### PyTensor Compilation Issues

If you see compilation errors or long startup times:

```bash
# Set environment variable before running Python
export PYTENSOR_FLAGS="device=cpu,floatX=float32,optimizer=fast_compile,openmp=False,blas__ldflags="
python your_script.py
```

### Missing spaCy Models

For NLP features, install language models:

```bash
python -m spacy download en_core_web_sm
```

The system will show this message only once per run if models are missing.

### Static libpython Environments

In environments with static libpython (common in some CI systems):
- PyTensor automatically uses fast compilation
- C extensions are avoided
- All core functionality remains available

## 📁 File Structure

```
metapython.py          # Main library file
README.md             # This documentation
requirements.txt      # Minimal dependencies
requirements-full.txt # Complete dependencies
meta_pipeline.yaml    # Configuration example
PHASE4_CHANGELOG.md   # Latest updates
```

## 🧪 Testing

Basic functionality test:

```python
import metapython
print("Import successful - core functionality available")

# Test with sample data
meta = metapython.run_unified_demo(n_studies=5, save_visuals=False)
```

## 🤝 Contributing

This is a unified platform combining multiple meta-analysis approaches. The codebase prioritizes:

1. **Robustness** - Works in any Python environment
2. **Clarity** - Clear documentation and examples
3. **Completeness** - Comprehensive meta-analysis toolkit
4. **Performance** - Optimized for large datasets when possible

## 📄 License

MIT License - See LICENSE file for details.

## 🔄 Version History

- **v0.4.0**: Enhanced robustness, sparse events, network inconsistency, diagnostic test accuracy
- **v3.0.0**: Unified PyMeta-CBAMM suite with comprehensive capabilities

---

For complete examples and advanced usage, see the PHASE4_CHANGELOG.md file.