# MetaPython: Unified Meta-Analysis Suite

[![PyPI version](https://badge.fury.io/py/metapython.svg)](https://badge.fury.io/py/metapython)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/metapython/badge/?version=latest)](https://metapython.readthedocs.io/en/latest/?badge=latest)

MetaPython is a comprehensive, production-ready meta-analysis library that combines the power of PyMeta v2.1 and CBAMM v5.7 with extensive Phase 7 enhancements. It provides a unified interface for conducting systematic reviews, meta-analyses, and evidence synthesis with state-of-the-art statistical methods.

## 🚀 Quick Start

### Installation

```bash
# Core installation
pip install metapython

# With statistical analysis extras
pip install metapython[stats]

# With all optional dependencies
pip install metapython[all]

# Development version
pip install metapython[full]
```

### Basic Usage

```python
import metapython as mp
import pandas as pd

# Load your data
data = pd.read_csv('studies.csv')

# Run meta-analysis
meta = mp.UnifiedMetaAnalysis(
    data=data,
    effect_col='effect_size',
    se_col='standard_error',
    label_col='study_name'
)

# Analyze with comprehensive bias assessment
results = meta.analyze(include_bias_tests=True)

# Generate comprehensive report
print(meta.comprehensive_report())
```

### Command Line Interface

```bash
# Run demonstration
metapython demo --studies 25

# Quick analysis from CSV
metapython quick data.csv --effect-col effect --se-col se

# Run pipeline from YAML
metapython pipeline config.yaml

# Show help
metapython --help
```

## 📊 Key Features

### Core Meta-Analysis
- **Fixed and Random Effects Models**: DerSimonian-Laird, REML, Paule-Mandel, empirical Bayes
- **Robust Variance Estimation**: Hartung-Knapp-Sidik-Jonkman (HKSJ) adjustments
- **Heterogeneity Assessment**: I², H², τ², prediction intervals
- **Subgroup Analysis**: Flexible stratification and meta-regression

### Advanced Methods
- **Network Meta-Analysis**: Inconsistency detection, ranking (SUCRA), node-splitting
- **Diagnostic Test Accuracy**: Bivariate random-effects, HSROC, Fagan nomogram
- **Sparse Events Analysis**: Peto odds ratio, Mantel-Haenszel, continuity corrections
- **Bayesian Methods**: PyMC integration, HSROC, model stacking
- **Living Meta-Analysis**: Automated PubMed updates, version control

### Publication Bias Assessment
- **Classical Tests**: Egger, Begg, rank correlation
- **Modern Methods**: PET-PEESE, trim-and-fill, p-curve analysis
- **Advanced Techniques**: Test for excess significance, weight-function models
- **Selection Models**: Vevea-Hedges, three-parameter selection models

### Quality and Reliability
- **Conflict Detection**: ML-based clustering, effect size partitioning
- **Sensitivity Analysis**: Leave-one-out, missing studies, multiverse analysis
- **Diagnostic Tools**: Influence analysis, outlier detection, Cook's distance
- **Reproducibility**: Seed management, provenance tracking, exact replication

### Visualization Suite
- **Forest Plots**: Classic and enhanced with confidence/prediction intervals
- **Funnel Plots**: Asymmetry detection, trim-and-fill visualization
- **Diagnostic Plots**: Baujat, radial, Galbraith, L'Abbé plots
- **Interactive Dashboards**: Streamlit integration, real-time exploration

## 🔧 Installation Options

MetaPython uses an optional dependency system to keep the core lightweight while providing access to advanced features:

```bash
# Core dependencies only (numpy, pandas, matplotlib, seaborn, scipy)
pip install metapython

# Statistical analysis (statsmodels, scikit-learn)
pip install metapython[stats]

# Bayesian methods (PyMC, ArviZ)
pip install metapython[bayesian]

# Pipeline automation (PyYAML, Jinja2, Click)
pip install metapython[pipeline]

# Performance optimization (Numba, Dask, Joblib)
pip install metapython[performance]

# Living meta-analysis (BioPython, requests)
pip install metapython[living]

# Web interfaces (Streamlit, Flask, Plotly)
pip install metapython[web]

# NLP and ML (spaCy, transformers, XGBoost, SHAP)
pip install metapython[ml]

# Mathematical optimization (CVXPY)
pip install metapython[optimization]

# Documentation (Sphinx, Jupyter)
pip install metapython[docs]

# Development tools (pytest, black, mypy)
pip install metapython[dev]

# Everything included
pip install metapython[all]
```

## 📖 Documentation

- **[User Guide](docs/user_guides/)**: Analysis-specific tutorials and best practices
- **[API Reference](docs/api_reference/)**: Complete function and class documentation  
- **[Examples Gallery](examples/)**: Real-world examples with sample datasets
- **[CLI Documentation](docs/cli/)**: Command-line interface guide
- **[Tutorials](docs/tutorials/)**: Step-by-step learning materials

## 🎯 Use Cases

### Clinical Research
- Systematic reviews and meta-analyses
- Individual patient data (IPD) meta-analysis
- Network meta-analysis for treatment comparisons
- Diagnostic test accuracy reviews

### Evidence Synthesis
- Educational intervention effectiveness
- Environmental health studies
- Policy evaluation and social science
- Method comparison studies

### Methodological Research
- Bias detection and correction methods
- Heterogeneity exploration techniques
- Statistical method validation
- Simulation studies

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Setting up the development environment
- Code style and testing requirements
- Submitting bug reports and feature requests
- Contributing documentation and examples

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Citation

If you use MetaPython in your research, please cite:

```bibtex
@software{metapython2024,
  title={MetaPython: Unified Meta-Analysis Suite},
  author={PyMeta-CBAMM Development Team},
  year={2024},
  version={0.6.0},
  url={https://github.com/mahmood726-cyber/Metapython},
  doi={10.5281/zenodo.XXXXXXX}
}
```

## 🆘 Support

- **Documentation**: [https://metapython.readthedocs.io](https://metapython.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/mahmood726-cyber/Metapython/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mahmood726-cyber/Metapython/discussions)
- **Email**: pymeta-cbamm@example.com

## 🗺️ Roadmap

### v0.6.0 (Current Release Candidate)
- ✅ Production hardening and packaging
- ✅ Comprehensive documentation
- ✅ Enhanced CLI and UX improvements
- ✅ Expanded test coverage

### v0.7.0 (Future)
- Individual patient data (IPD) meta-analysis
- Spatial meta-analysis methods
- Time-to-event meta-analysis enhancements  
- Advanced causal inference methods

### v1.0.0 (Stable)
- API stabilization
- Performance optimizations
- Enterprise features
- Certified reproducibility protocols

---

**MetaPython v0.6.0-rc.1** - Combining the best of PyMeta v2.1 and CBAMM v5.7 with production-grade enhancements for the modern evidence synthesis workflow.