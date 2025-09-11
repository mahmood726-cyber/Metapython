# metapy - R-like Meta-Analysis Package

A self-contained Python package providing thin, extensible APIs that mirror common workflows from R's `meta` and `metafor` packages.

## Features

### Core Meta-Analysis Functions
- `metagen()` - Generic inverse-variance meta-analysis
- `metacont()` - Continuous outcomes (SMD, MD)
- `metabin()` - Binary outcomes (OR, RR, RD) 
- `metaprop()` - Single-arm proportions
- `rma()` - metafor-like interface

### Statistical Methods
- **Models**: Fixed-effects and random-effects
- **Tau² estimators**: DerSimonian-Laird (DL), Paule-Mandel (PM)
- **Adjustments**: Hartung-Knapp (HK) correction
- **Statistics**: Q, I², H², τ², confidence/prediction intervals

## Quick Start

```python
import metapy
import numpy as np

# Generic meta-analysis
effects = [0.2, 0.4, 0.3, 0.5, 0.1]
ses = [0.1, 0.15, 0.12, 0.18, 0.08]
result = metapy.metagen(effects, ses, method="DL")
print(result)

# Continuous outcomes
result = metapy.metacont(
    m1=[10.2, 12.5], sd1=[2.1, 2.8], n1=[30, 35],
    m2=[8.1, 9.2], sd2=[2.3, 2.5], n2=[32, 33],
    sm="SMD"  # Standardized mean difference
)

# Binary outcomes  
result = metapy.metabin(
    event1=[10, 15], n1=[50, 60],
    event2=[5, 8], n2=[48, 58], 
    sm="OR"  # Odds ratio
)

# With pandas DataFrame
import pandas as pd
df = pd.DataFrame({
    'study': ['A', 'B', 'C'],
    'effect': [0.2, 0.4, 0.3],
    'se': [0.1, 0.15, 0.12]
})

result = metapy.metagen(
    effect='effect', se='se', studlab='study', data=df
)
```

## API Reference

### metagen(effect, se, studlab=None, method="DL", hakn=False)
Generic inverse-variance meta-analysis

### metacont(m1, sd1, n1, m2, sd2, n2, sm="SMD", method="DL", hakn=False)
Meta-analysis of continuous outcomes

### metabin(event1, n1, event2, n2, sm="OR", method="DL", hakn=False)
Meta-analysis of binary outcomes

### metaprop(event, n, method="DL", hakn=False)
Meta-analysis of proportions

### rma(yi, vi=None, sei=None, method="DL", knha=False)
metafor-like interface

## Parameters

- `method`: Tau² estimation method ("DL" or "PM")
- `hakn`/`knha`: Use Hartung-Knapp adjustment (bool)
- `sm`: Summary measure ("SMD", "MD", "OR", "RR", "RD")
- `level`: Confidence level (default 0.95)

## Examples

See `example_metapy.py` for comprehensive examples and `test_metapy.py` for validation tests.

## Compatibility

- Works alongside existing `metapython.py` without conflicts
- Headless plotting compatible (set `MPLBACKEND=Agg`)
- No breaking changes to existing code