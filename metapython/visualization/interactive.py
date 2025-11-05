"""
Interactive visualizations using Plotly.

Provides modern, interactive plots for meta-analysis that can be embedded
in web applications or Jupyter notebooks.
"""

from typing import Optional, List, Dict, Any, Tuple
import numpy as np
import pandas as pd
from scipy.stats import norm

from metapython.core.config import HAS_PLOTLY

if HAS_PLOTLY:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots


def interactive_forest_plot(
    effects: np.ndarray,
    se: np.ndarray,
    study_labels: np.ndarray,
    pooled_effect: Optional[float] = None,
    pooled_se: Optional[float] = None,
    title: str = "Interactive Forest Plot",
    xlabel: str = "Effect Size",
    alpha: float = 0.05,
    height: int = 600,
) -> go.Figure:
    """
    Create interactive forest plot with Plotly.

    Args:
        effects: Effect sizes
        se: Standard errors
        study_labels: Study names
        pooled_effect: Pooled effect estimate
        pooled_se: Pooled standard error
        title: Plot title
        xlabel: X-axis label
        alpha: Significance level
        height: Figure height in pixels

    Returns:
        Plotly Figure object
    """
    if not HAS_PLOTLY:
        raise ImportError("Plotly required. Install with: pip install 'metapython[full]'")

    z_crit = norm.ppf(1 - alpha / 2)

    # Calculate CIs
    ci_low = effects - z_crit * se
    ci_high = effects + z_crit * se

    # Calculate weights for marker size
    weights = 1 / (se ** 2)
    weights_norm = 15 * weights / np.max(weights)

    # Create figure
    fig = go.Figure()

    # Add individual studies
    for i in range(len(effects)):
        # CI error bars
        fig.add_trace(go.Scatter(
            x=[ci_low[i], ci_high[i]],
            y=[study_labels[i], study_labels[i]],
            mode='lines',
            line=dict(color='gray', width=2),
            showlegend=False,
            hoverinfo='skip'
        ))

        # Point estimate
        fig.add_trace(go.Scatter(
            x=[effects[i]],
            y=[study_labels[i]],
            mode='markers',
            marker=dict(
                size=weights_norm[i],
                color='steelblue',
                line=dict(color='black', width=1)
            ),
            name=study_labels[i],
            hovertemplate=(
                f"<b>{study_labels[i]}</b><br>"
                f"Effect: {effects[i]:.3f}<br>"
                f"95% CI: [{ci_low[i]:.3f}, {ci_high[i]:.3f}]<br>"
                f"SE: {se[i]:.3f}<br>"
                "<extra></extra>"
            )
        ))

    # Add pooled estimate
    if pooled_effect is not None and pooled_se is not None:
        pooled_ci_low = pooled_effect - z_crit * pooled_se
        pooled_ci_high = pooled_effect + z_crit * pooled_se

        # CI line
        fig.add_trace(go.Scatter(
            x=[pooled_ci_low, pooled_ci_high],
            y=['Pooled', 'Pooled'],
            mode='lines',
            line=dict(color='darkred', width=3),
            showlegend=False,
            hoverinfo='skip'
        ))

        # Diamond marker
        fig.add_trace(go.Scatter(
            x=[pooled_effect],
            y=['Pooled'],
            mode='markers',
            marker=dict(
                size=20,
                color='darkred',
                symbol='diamond',
                line=dict(color='black', width=2)
            ),
            name='Pooled Estimate',
            hovertemplate=(
                "<b>Pooled Estimate</b><br>"
                f"Effect: {pooled_effect:.3f}<br>"
                f"95% CI: [{pooled_ci_low:.3f}, {pooled_ci_high:.3f}]<br>"
                f"SE: {pooled_se:.3f}<br>"
                "<extra></extra>"
            )
        ))

    # Add null effect line
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)

    # Update layout
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='black')),
        xaxis_title=xlabel,
        height=height,
        showlegend=False,
        hovermode='closest',
        template='plotly_white'
    )

    return fig


def interactive_funnel_plot(
    effects: np.ndarray,
    se: np.ndarray,
    study_labels: Optional[np.ndarray] = None,
    pooled_effect: Optional[float] = None,
    title: str = "Interactive Funnel Plot",
    xlabel: str = "Effect Size",
    show_contours: bool = True,
) -> go.Figure:
    """
    Create interactive funnel plot with Plotly.

    Args:
        effects: Effect sizes
        se: Standard errors
        study_labels: Optional study labels
        pooled_effect: Pooled effect estimate
        title: Plot title
        xlabel: X-axis label
        show_contours: Show confidence contours

    Returns:
        Plotly Figure object
    """
    if not HAS_PLOTLY:
        raise ImportError("Plotly required. Install with: pip install 'metapython[full]'")

    if pooled_effect is None:
        pooled_effect = np.mean(effects)

    if study_labels is None:
        study_labels = [f"Study {i+1}" for i in range(len(effects))]

    fig = go.Figure()

    # Add contour lines
    if show_contours:
        se_range = np.linspace(0, np.max(se) * 1.1, 100)

        # 95% CI
        ci_95_low = pooled_effect - 1.96 * se_range
        ci_95_high = pooled_effect + 1.96 * se_range
        fig.add_trace(go.Scatter(
            x=ci_95_low,
            y=se_range,
            mode='lines',
            line=dict(color='gray', dash='dash', width=1),
            name='95% CI',
            showlegend=True
        ))
        fig.add_trace(go.Scatter(
            x=ci_95_high,
            y=se_range,
            mode='lines',
            line=dict(color='gray', dash='dash', width=1),
            showlegend=False,
            hoverinfo='skip'
        ))

        # 99% CI
        ci_99_low = pooled_effect - 2.58 * se_range
        ci_99_high = pooled_effect + 2.58 * se_range
        fig.add_trace(go.Scatter(
            x=ci_99_low,
            y=se_range,
            mode='lines',
            line=dict(color='gray', dash='dot', width=1),
            name='99% CI',
            showlegend=True
        ))
        fig.add_trace(go.Scatter(
            x=ci_99_high,
            y=se_range,
            mode='lines',
            line=dict(color='gray', dash='dot', width=1),
            showlegend=False,
            hoverinfo='skip'
        ))

    # Add pooled effect line
    fig.add_vline(
        x=pooled_effect,
        line_dash="solid",
        line_color="darkred",
        line_width=2,
        annotation_text="Pooled Effect"
    )

    # Add studies
    fig.add_trace(go.Scatter(
        x=effects,
        y=se,
        mode='markers',
        marker=dict(
            size=12,
            color='steelblue',
            opacity=0.7,
            line=dict(color='black', width=1)
        ),
        text=study_labels,
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Effect: %{x:.3f}<br>"
            "SE: %{y:.3f}<br>"
            "<extra></extra>"
        ),
        name='Studies'
    ))

    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title=xlabel,
        yaxis_title="Standard Error",
        yaxis=dict(autorange="reversed"),  # Invert y-axis
        height=600,
        template='plotly_white',
        hovermode='closest'
    )

    return fig


def interactive_network_plot(
    treatments: List[str],
    comparisons: List[Tuple[str, str]],
    effects: np.ndarray,
    title: str = "Network Meta-Analysis",
) -> go.Figure:
    """
    Create interactive network plot showing treatment comparisons.

    Args:
        treatments: List of treatment names
        comparisons: List of (treatment_a, treatment_b) tuples
        effects: Effect sizes for each comparison
        title: Plot title

    Returns:
        Plotly Figure object
    """
    if not HAS_PLOTLY:
        raise ImportError("Plotly required. Install with: pip install 'metapython[full]'")

    # Create positions for treatments (circular layout)
    n = len(treatments)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    pos = {
        treatment: (np.cos(angle), np.sin(angle))
        for treatment, angle in zip(treatments, angles)
    }

    fig = go.Figure()

    # Add edges (comparisons)
    for (t1, t2), effect in zip(comparisons, effects):
        x0, y0 = pos[t1]
        x1, y1 = pos[t2]

        # Color by effect size
        color = 'blue' if effect > 0 else 'red'
        width = min(abs(effect) * 5, 10)  # Scale line width by effect size

        fig.add_trace(go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode='lines',
            line=dict(color=color, width=width),
            hovertemplate=f"{t1} vs {t2}<br>Effect: {effect:.3f}<extra></extra>",
            showlegend=False
        ))

    # Add nodes (treatments)
    node_x = [pos[t][0] for t in treatments]
    node_y = [pos[t][1] for t in treatments]

    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(
            size=30,
            color='lightblue',
            line=dict(color='black', width=2)
        ),
        text=treatments,
        textposition='top center',
        hoverinfo='text',
        showlegend=False
    ))

    # Update layout
    fig.update_layout(
        title=title,
        showlegend=False,
        hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600,
        template='plotly_white'
    )

    return fig


def interactive_gosh_plot(
    gosh_results: pd.DataFrame,
    outlier_threshold: float = 2.5,
    title: str = "GOSH Plot (Graphical Display of Heterogeneity)",
) -> go.Figure:
    """
    Create interactive GOSH plot for heterogeneity visualization.

    Args:
        gosh_results: DataFrame with columns ['effect', 'I2', 'subset_indices']
        outlier_threshold: Z-score threshold for outlier detection
        title: Plot title

    Returns:
        Plotly Figure object
    """
    if not HAS_PLOTLY:
        raise ImportError("Plotly required. Install with: pip install 'metapython[full]'")

    # Detect outliers
    effect_z = np.abs((gosh_results['effect'] - gosh_results['effect'].mean()) /
                      gosh_results['effect'].std())
    is_outlier = effect_z > outlier_threshold

    colors = ['red' if outlier else 'blue' for outlier in is_outlier]

    fig = go.Figure()

    # Add scatter plot
    fig.add_trace(go.Scatter(
        x=gosh_results['effect'],
        y=gosh_results['I2'],
        mode='markers',
        marker=dict(
            size=5,
            color=colors,
            opacity=0.5,
            line=dict(width=0)
        ),
        hovertemplate=(
            "Effect: %{x:.3f}<br>"
            "I²: %{y:.1f}%<br>"
            "<extra></extra>"
        ),
        showlegend=False
    ))

    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Effect Size",
        yaxis_title="I² (%)",
        height=600,
        template='plotly_white',
        hovermode='closest'
    )

    return fig


__all__ = [
    'interactive_forest_plot',
    'interactive_funnel_plot',
    'interactive_network_plot',
    'interactive_gosh_plot',
]
