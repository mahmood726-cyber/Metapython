# Metapython v0.3.0 - Unified Meta-Analysis Suite

A comprehensive meta-analysis library combining traditional frequentist methods with modern Bayesian engines, automated diagnostics, and interactive visualizations.

## Features

### Core Capabilities
- **Fixed and Random Effects Models**: Multiple tau² estimators (DL, REML, HS, EB)
- **Comprehensive Diagnostics**: Heterogeneity metrics, influence analysis, leave-one-out
- **Publication Bias Assessment**: Egger, Begg, PET-PEESE, trim-and-fill, p-curve analysis
- **Advanced Methods**: Network meta-analysis, dose-response, sequential analysis

### Phase 3 Enhancements (v0.3.0)
- **Optional Bayesian Engines**: PyMC (primary), CmdStanPy/PyStan (fallback)
- **Automated Reporting**: One-liner `meta_auto_report()` function
- **Interactive Visualizations**: Plotly/Altair plots with Matplotlib fallback
- **R Parity Validation**: Automated comparison with metafor/netmeta
- **Performance Optimization**: Numba acceleration, Dask scaling (optional)

## Installation

### Basic Installation
```bash
pip install metapython
```

### With Optional Features
```bash
# Bayesian analysis
pip install metapython[bayes]

# Interactive visualizations  
pip install metapython[viz]

# Performance optimization
pip install metapython[speed]

# R interoperability
pip install metapython[rinterop]

# Big data processing
pip install metapython[dask]

# Everything (except dev tools)
pip install metapython[all]
```

## Quick Start

```python
import metapython as mp
import pandas as pd

# Load your data
data = pd.DataFrame({
    'study': ['Study1', 'Study2', 'Study3'],
    'effect': [0.5, 0.3, 0.7],
    'se': [0.1, 0.15, 0.12]
})

# One-liner automated analysis and report
result = mp.meta_auto_report(data, output_format='html')

# Or detailed analysis
meta = mp.UnifiedMetaAnalysis(data, effect_col='effect', se_col='se')
meta.analyze(include_bias_tests=True, include_bayesian=True)
print(meta.summary())
```

## Documentation

Full documentation available at: https://mahmood726-cyber.github.io/Metapython/

## Citation

If you use Metapython in your research, please cite:

```
PyMeta-CBAMM Development Team. (2025). Metapython: Unified Meta-Analysis Suite v0.3.0. 
GitHub repository: https://github.com/mahmood726-cyber/Metapython
```

## License

MIT License - see LICENSE file for details.