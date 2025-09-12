# Metapython v0.8 🧬

[![Version](https://img.shields.io/badge/version-0.8.0-blue.svg)](https://github.com/mahmood726-cyber/Metapython/releases)
[![API Stability](https://img.shields.io/badge/API-stable-green.svg)](API_DEPRECATION_MATRIX.md)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Production-ready meta-analysis platform with observability, distributed computing, and plugin marketplace.**

## 🚀 Quick Start

```bash
# Core installation
pip install metapython

# With optional features
pip install metapython[distributed,gpu,web,all]
```

```python
import metapython
import numpy as np

# Simple meta-analysis
effects = np.array([0.5, 0.3, 0.7])
variances = np.array([0.1, 0.2, 0.15])

result = metapython.quick_meta(effects, variances)
print(f"Pooled effect: {result['pooled_effect']:.3f}")
```

## ✨ What's New in v0.8

### 🔒 API Stabilization
- **Stable API guarantee** for all public interfaces
- **Deprecation framework** with migration tools
- **Backward compatibility** maintained

### 📊 Observability & Telemetry
- **Structured logging** with OpenTelemetry support
- **Opt-in telemetry** with privacy controls
- **Run health tracking** and retry mechanisms

### ⚡ Distributed Computing
- **Dask and Ray** executors for parallel analysis
- **JAX GPU acceleration** for Bayesian methods
- **Spark integration** improvements

### 🛡️ Security & Supply Chain
- **SBOM generation** (SPDX format)
- **SLSA provenance** attestation
- **Reproducible builds** across platforms

### 🌍 Accessibility & i18n
- **Multi-language support** (EN, ES, ZH, FR, DE, JA)
- **Right-to-left layouts** ready
- **Screen reader compatibility**
- **High contrast mode**

### 🔌 Plugin Marketplace (GA)
- **Verified publishers** with trust scoring
- **Search and discovery** with quality filters
- **CLI marketplace** integration

## 📖 Documentation

- **[Migration Guide](MIGRATION_GUIDE.md)** - Upgrade from v0.7
- **[API Stability](API_DEPRECATION_MATRIX.md)** - Compatibility guarantees
- **[Plugin Development](https://metapython.readthedocs.io/plugins/)** - Extend functionality
- **[Security Policy](https://metapython.readthedocs.io/security/)** - Report vulnerabilities

## 🎯 Core Features

### Meta-Analysis Methods
- **Fixed & Random Effects** models
- **Network Meta-Analysis** with inconsistency testing
- **Diagnostic Test Accuracy** (DTA) with HSROC
- **Publication Bias** assessment and correction
- **Trial Sequential Analysis** (TSA)
- **Sparse Events** handling (Peto OR, M-H)

### Advanced Analytics
- **Bayesian Methods** with PyMC integration
- **Machine Learning** heterogeneity detection
- **Multivariate Structures** (unstructured, factor-analytic)
- **Living Meta-Analysis** with transport weighting
- **Influence Diagnostics** and outlier detection

### Integration & Automation
- **CLI Interface** with YAML workflows
- **Web Dashboard** (Streamlit/Flask)
- **PubMed Integration** for automated extraction
- **Export Formats** (CSV, JSON, HTML, PDF)

## 🔧 Installation Options

### Core Package
```bash
pip install metapython
```

### Optional Extras
```bash
# Distributed computing
pip install metapython[distributed]  # Dask + Ray
pip install metapython[gpu]          # JAX GPU acceleration
pip install metapython[spark]        # Spark integration

# Advanced analytics
pip install metapython[bayesian]     # PyMC + ArviZ
pip install metapython[advanced]     # Statsmodels + Scikit-learn
pip install metapython[nlp]          # spaCy + Transformers

# Web interfaces
pip install metapython[web]          # Streamlit + Flask + FastAPI
pip install metapython[cli]          # Enhanced CLI tools

# Development
pip install metapython[dev]          # Testing + Linting

# Everything
pip install metapython[all]
```

## 💻 Usage Examples

### Basic Meta-Analysis
```python
import metapython as mp
import pandas as pd

# Load data
df = pd.read_csv("studies.csv")

# Configure analysis
config = mp.UnifiedMetaConfig(
    method="random_effects",
    heterogeneity_estimator="DL"
)

# Run analysis
analysis = mp.UnifiedMetaAnalysis(config)
result = analysis.analyze(
    effect_sizes=df['effect'], 
    variances=df['variance']
)

print(result.summary())
```

### Distributed Computing
```python
# Check available compute resources
compute = mp.get_compute_manager()
available = compute.get_available_executors()
print(f"Available: {available}")

# Use JAX acceleration for Bayesian analysis
if "jax" in available:
    jax_accel = mp.JAXAccelerator()
    result = jax_accel.accelerated_bayesian_fit(data)
```

### Plugin Marketplace
```python
# Search plugins
registry = mp.get_marketplace_registry()
plugins = registry.search_plugins(
    query="visualization", 
    min_trust_score=0.7
)

# Install via CLI
cli = mp.get_marketplace_cli()
cli.install("advanced-forest-plots")
```

### Observability
```python
# Enable structured logging
import os
os.environ["METAPYTHON_TELEMETRY"] = "true"

logger = mp.get_logger()
health = mp.get_run_health()

# Track analysis
health.start_run()
logger.log_analysis_start("network-meta", study_count=25)

try:
    # Your analysis here
    result = analysis.run()
    logger.log_analysis_complete("network-meta", duration_ms=1500)
    health.complete_run(success=True)
except Exception as e:
    health.complete_run(success=False)
    raise
```

### Internationalization
```python
# Set locale
mp.set_locale("es")  # Spanish

# Get translated messages
message = mp._("analysis.starting")
print(message)  # "Iniciando meta-análisis..."

# Accessibility support
a11y = mp.get_accessibility_helper()
a11y.enable_high_contrast()
formatted = a11y.format_cli_output("Complete", level="success")
```

## 🏗️ Architecture

```
metapython/
├── 🧠 Core Analysis Engine
│   ├── Fixed/Random Effects
│   ├── Network Meta-Analysis  
│   ├── Bayesian Methods
│   └── Diagnostic Accuracy
├── ⚡ Distributed Computing
│   ├── Dask Executor
│   ├── Ray Executor
│   ├── JAX Acceleration
│   └── Spark Integration
├── 📊 Observability
│   ├── Structured Logging
│   ├── Health Monitoring
│   └── Telemetry (opt-in)
├── 🔌 Plugin Marketplace
│   ├── Registry & Discovery
│   ├── Trust & Verification
│   └── CLI Integration
└── 🌍 Accessibility
    ├── i18n Framework
    ├── Screen Reader Support
    └── High Contrast Mode
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md).

### Development Setup
```bash
git clone https://github.com/mahmood726-cyber/Metapython.git
cd Metapython
pip install -e .[dev,all]
pytest
```

### Plugin Development
```python
from metapython import PluginMetadata

plugin = PluginMetadata(
    name="my-plugin",
    version="1.0.0", 
    capabilities=["visualization"],
    # ... other metadata
)
```

## 📊 Performance

| Dataset Size | Method | CPU Time | Memory | Distributed |
|-------------|--------|----------|---------|-------------|
| 10 studies | Fixed Effects | <1s | 50MB | No |
| 100 studies | Random Effects | 2s | 100MB | Optional |
| 1,000 studies | Network MA | 30s | 500MB | Recommended |
| 10,000+ studies | Bayesian | 10min | 2GB | Required |

## 🔒 Security

- **SLSA Level 3** supply chain security
- **SBOM generation** for transparency
- **Reproducible builds** across platforms  
- **Security scanning** in CI/CD
- **Vulnerability reporting**: security@metapython.example.com

## 📜 License

MIT License - see [LICENSE](LICENSE) file.

## 🙋 Support

- **Documentation**: https://metapython.readthedocs.io
- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Community Q&A and design feedback
- **Email**: pymeta-cbamm@example.com

## 🗺️ Roadmap

- **v0.9.0** (Q2 2024): Enhanced plugin ecosystem, more executors
- **v1.0.0** (Q4 2024): LTS release, full API stability
- **v1.1.0+**: Continuous feature additions, no breaking changes

---

**Built with ❤️ by the PyMeta-CBAMM Development Team**