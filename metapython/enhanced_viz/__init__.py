"""
Enhanced Visualization Suite for Meta-Analysis

Publication-quality visualizations with interactive capabilities:
- Advanced forest plots with subgroups and prediction intervals
- Interactive dashboards with drill-down capabilities
- 3D visualizations for network meta-analysis
- Animated plots for time-varying effects
- Comprehensive diagnostic plots
- Publication-ready figures with journal-specific formatting
"""

from metapython.enhanced_viz.publication_plots import (
    advanced_forest_plot,
    cumulative_forest_plot,
    radial_plot,
    labbé_plot,
    contour_enhanced_funnel,
    galbraith_plot,
)

from metapython.enhanced_viz.interactive_dashboards import (
    create_meta_analysis_dashboard,
    interactive_sensitivity_dashboard,
    bias_assessment_dashboard,
)

from metapython.enhanced_viz.advanced_viz import (
    network_meta_3d,
    animated_cumulative_plot,
    heterogeneity_heatmap,
    multiverse_analysis_plot,
)

__all__ = [
    # Publication plots
    'advanced_forest_plot',
    'cumulative_forest_plot',
    'radial_plot',
    'labbé_plot',
    'contour_enhanced_funnel',
    'galbraith_plot',

    # Interactive dashboards
    'create_meta_analysis_dashboard',
    'interactive_sensitivity_dashboard',
    'bias_assessment_dashboard',

    # Advanced visualizations
    'network_meta_3d',
    'animated_cumulative_plot',
    'heterogeneity_heatmap',
    'multiverse_analysis_plot',
]
