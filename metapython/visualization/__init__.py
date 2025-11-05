"""
Visualization tools for meta-analysis.

Provides both static (matplotlib) and interactive (Plotly) visualizations
for meta-analysis results.
"""

from metapython.core.config import HAS_PLOTLY

# Static plots are always available
from metapython.visualization.plots import (
    forest_plot,
    funnel_plot,
    radial_plot,
    baujat_plot,
)

__all__ = [
    'forest_plot',
    'funnel_plot',
    'radial_plot',
    'baujat_plot',
]

# Interactive plots require Plotly
if HAS_PLOTLY:
    from metapython.visualization.interactive import (
        interactive_forest_plot,
        interactive_funnel_plot,
        interactive_network_plot,
        interactive_gosh_plot,
    )

    __all__.extend([
        'interactive_forest_plot',
        'interactive_funnel_plot',
        'interactive_network_plot',
        'interactive_gosh_plot',
    ])
