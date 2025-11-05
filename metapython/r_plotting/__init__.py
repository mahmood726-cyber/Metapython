"""
R-Based Publication-Quality Plotting Module

This module provides world-class meta-analysis visualizations using
R's metafor and meta packages - the gold standard in the field.

Available Plot Types:
- Forest plots (metafor and meta styles)
- Funnel plots with trim-and-fill
- Baujat plots (outlier detection)
- Radial/Galbraith plots
- GOSH plots (heterogeneity exploration)
- L'Abbé plots (binary data)
- Cumulative forest plots
- Leave-one-out plots

All plots are publication-ready and can be exported as PNG, SVG, or PDF.
"""

from .metafor_plots import (
    RMetaPlotter,
    create_forest_plot,
    create_funnel_plot,
)

__all__ = [
    'RMetaPlotter',
    'create_forest_plot',
    'create_funnel_plot',
]
