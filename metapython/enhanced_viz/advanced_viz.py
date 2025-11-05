"""
Advanced Visualizations for Meta-Analysis

3D visualizations, animations, and specialized plots for:
- Network meta-analysis
- Time-varying effects
- Multiverse analysis
- Complex heterogeneity patterns
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import warnings

from metapython.core.config import HAS_PLOTLY, logger

if HAS_PLOTLY:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots


def network_meta_3d(
    treatments: List[str],
    comparison_matrix: np.ndarray,
    effect_sizes: np.ndarray,
    se_matrix: np.ndarray,
    figsize: Tuple[int, int] = (12, 10)
) -> go.Figure:
    """
    Create 3D network meta-analysis visualization.

    Shows treatment network in 3D space with effect sizes and confidence.

    Args:
        treatments: List of treatment names
        comparison_matrix: Binary matrix indicating which comparisons exist
        effect_sizes: Matrix of pairwise effect sizes
        se_matrix: Matrix of standard errors
        figsize: Figure size

    Returns:
        Plotly 3D figure
    """
    if not HAS_PLOTLY:
        raise ImportError("Plotly required for 3D visualizations")

    n_treatments = len(treatments)

    # Create 3D coordinates for treatments (circular layout)
    theta = np.linspace(0, 2 * np.pi, n_treatments, endpoint=False)
    x = np.cos(theta)
    y = np.sin(theta)
    z = np.zeros(n_treatments)

    # Create figure
    fig = go.Figure()

    # Add edges (comparisons)
    for i in range(n_treatments):
        for j in range(i + 1, n_treatments):
            if comparison_matrix[i, j] > 0:
                effect = effect_sizes[i, j]
                se = se_matrix[i, j]

                # Edge width proportional to precision
                width = 1 / (se + 0.1) * 3

                # Edge color based on effect direction
                color = 'red' if effect > 0 else 'blue'
                opacity = min(1.0, abs(effect))

                # Add edge
                fig.add_trace(
                    go.Scatter3d(
                        x=[x[i], x[j]],
                        y=[y[i], y[j]],
                        z=[z[i], z[j]],
                        mode='lines',
                        line=dict(color=color, width=width),
                        opacity=opacity,
                        hovertemplate=(
                            f'<b>{treatments[i]} vs {treatments[j]}</b><br>' +
                            f'Effect: {effect:.3f}<br>' +
                            f'SE: {se:.3f}<br>' +
                            '<extra></extra>'
                        ),
                        showlegend=False
                    )
                )

    # Add nodes (treatments)
    # Node size based on number of comparisons
    node_sizes = np.sum(comparison_matrix, axis=1) * 10 + 20

    fig.add_trace(
        go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode='markers+text',
            marker=dict(
                size=node_sizes,
                color='lightgreen',
                line=dict(color='black', width=2)
            ),
            text=treatments,
            textposition='top center',
            hovertemplate='<b>%{text}</b><br><extra></extra>',
            showlegend=False
        )
    )

    # Update layout
    fig.update_layout(
        title='<b>3D Network Meta-Analysis</b>',
        scene=dict(
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, title=''),
            yaxis=dict(showticklabels=False, showgrid=False, zeroline=False, title=''),
            zaxis=dict(showticklabels=False, showgrid=False, zeroline=False, title=''),
            bgcolor='rgba(240,240,240,0.9)'
        ),
        width=1000,
        height=800,
        hovermode='closest'
    )

    return fig


def animated_cumulative_plot(
    effects: np.ndarray,
    se: np.ndarray,
    years: np.ndarray,
    study_labels: np.ndarray
) -> go.Figure:
    """
    Create animated cumulative meta-analysis plot.

    Shows how evidence accumulates over time with animation.

    Args:
        effects: Effect sizes
        se: Standard errors
        years: Publication years
        study_labels: Study names

    Returns:
        Animated Plotly figure
    """
    if not HAS_PLOTLY:
        raise ImportError("Plotly required for animations")

    # Sort by year
    sort_idx = np.argsort(years)
    effects_sorted = effects[sort_idx]
    se_sorted = se[sort_idx]
    years_sorted = years[sort_idx]
    labels_sorted = study_labels[sort_idx]

    n_studies = len(effects)

    # Calculate cumulative estimates
    frames = []

    for i in range(1, n_studies + 1):
        cum_effects = effects_sorted[:i]
        cum_se = se_sorted[:i]
        cum_weights = 1 / (cum_se ** 2)

        pooled = np.sum(cum_weights * cum_effects) / np.sum(cum_weights)
        pooled_se = np.sqrt(1 / np.sum(cum_weights))
        ci_low = pooled - 1.96 * pooled_se
        ci_high = pooled + 1.96 * pooled_se

        # Create frame
        frame = go.Frame(
            data=[
                # Cumulative effect line
                go.Scatter(
                    x=years_sorted[:i],
                    y=[pooled] * i,
                    mode='lines',
                    line=dict(color='red', width=3),
                    name='Cumulative Effect',
                    showlegend=True
                ),
                # Confidence band
                go.Scatter(
                    x=np.concatenate([years_sorted[:i], years_sorted[:i][::-1]]),
                    y=np.concatenate([[ci_high] * i, [ci_low] * i][::-1]),
                    fill='toself',
                    fillcolor='rgba(255,0,0,0.2)',
                    line=dict(width=0),
                    showlegend=False
                ),
                # Individual studies
                go.Scatter(
                    x=years_sorted[:i],
                    y=cum_effects,
                    mode='markers',
                    marker=dict(size=10, color='steelblue'),
                    text=labels_sorted[:i],
                    hovertemplate='<b>%{text}</b><br>Year: %{x}<br>Effect: %{y:.3f}<extra></extra>',
                    name='Studies',
                    showlegend=True
                )
            ],
            name=str(int(years_sorted[i-1]))
        )
        frames.append(frame)

    # Initial frame
    initial_pooled = effects_sorted[0]
    initial_se = se_sorted[0]
    initial_ci_low = initial_pooled - 1.96 * initial_se
    initial_ci_high = initial_pooled + 1.96 * initial_se

    fig = go.Figure(
        data=[
            go.Scatter(
                x=[years_sorted[0]],
                y=[initial_pooled],
                mode='lines',
                line=dict(color='red', width=3),
                name='Cumulative Effect'
            ),
            go.Scatter(
                x=[years_sorted[0], years_sorted[0]],
                y=[initial_ci_low, initial_ci_high],
                fill='toself',
                fillcolor='rgba(255,0,0,0.2)',
                line=dict(width=0),
                showlegend=False
            ),
            go.Scatter(
                x=[years_sorted[0]],
                y=[effects_sorted[0]],
                mode='markers',
                marker=dict(size=10, color='steelblue'),
                text=[labels_sorted[0]],
                hovertemplate='<b>%{text}</b><br>Year: %{x}<br>Effect: %{y:.3f}<extra></extra>',
                name='Studies'
            )
        ],
        frames=frames
    )

    # Add animation controls
    fig.update_layout(
        title='<b>Animated Cumulative Meta-Analysis</b>',
        xaxis=dict(title='Year', range=[years_sorted[0] - 1, years_sorted[-1] + 1]),
        yaxis=dict(title='Effect Size'),
        hovermode='closest',
        updatemenus=[
            dict(
                type='buttons',
                showactive=False,
                y=1.15,
                x=0.1,
                xanchor='left',
                yanchor='top',
                buttons=[
                    dict(label='Play',
                         method='animate',
                         args=[None, dict(frame=dict(duration=500, redraw=True),
                                        fromcurrent=True)]),
                    dict(label='Pause',
                         method='animate',
                         args=[[None], dict(frame=dict(duration=0, redraw=False),
                                          mode='immediate')])
                ]
            )
        ],
        sliders=[
            dict(
                yanchor='top',
                y=0,
                xanchor='left',
                currentvalue=dict(
                    prefix='Year: ',
                    visible=True,
                    xanchor='right'
                ),
                steps=[
                    dict(
                        args=[[f.name], dict(frame=dict(duration=0, redraw=True),
                                           mode='immediate')],
                        label=f.name,
                        method='animate'
                    ) for f in frames
                ]
            )
        ],
        width=1200,
        height=600
    )

    return fig


def heterogeneity_heatmap(
    effects_matrix: np.ndarray,
    moderator1_labels: List[str],
    moderator2_labels: List[str],
    title: str = "Heterogeneity Heatmap"
) -> go.Figure:
    """
    Create heatmap showing effect sizes across two moderators.

    Args:
        effects_matrix: Matrix of effect sizes (moderator1 × moderator2)
        moderator1_labels: Labels for first moderator (rows)
        moderator2_labels: Labels for second moderator (columns)
        title: Plot title

    Returns:
        Plotly heatmap figure
    """
    if not HAS_PLOTLY:
        raise ImportError("Plotly required for heatmaps")

    fig = go.Figure(
        data=go.Heatmap(
            z=effects_matrix,
            x=moderator2_labels,
            y=moderator1_labels,
            colorscale='RdBu',
            zmid=0,
            text=np.round(effects_matrix, 3),
            texttemplate='%{text}',
            textfont={"size": 12},
            hovertemplate=(
                '<b>%{y} × %{x}</b><br>' +
                'Effect: %{z:.3f}<br>' +
                '<extra></extra>'
            ),
            colorbar=dict(title='Effect Size')
        )
    )

    fig.update_layout(
        title=f'<b>{title}</b>',
        xaxis=dict(title=moderator2_labels[0].split(':')[0] if ':' in moderator2_labels[0] else 'Moderator 2'),
        yaxis=dict(title=moderator1_labels[0].split(':')[0] if ':' in moderator1_labels[0] else 'Moderator 1'),
        width=900,
        height=700
    )

    return fig


def multiverse_analysis_plot(
    analysis_specifications: List[str],
    effect_sizes: np.ndarray,
    ci_low: np.ndarray,
    ci_high: np.ndarray,
    p_values: np.ndarray,
    reference_spec: Optional[int] = None
) -> go.Figure:
    """
    Create multiverse analysis visualization.

    Shows robustness of findings across different analytical choices.

    Args:
        analysis_specifications: Descriptions of each analysis specification
        effect_sizes: Effect sizes for each specification
        ci_low: Lower CI bounds
        ci_high: Upper CI bounds
        p_values: P-values
        reference_spec: Index of reference specification (highlighted)

    Returns:
        Plotly figure
    """
    if not HAS_PLOTLY:
        raise ImportError("Plotly required for multiverse plots")

    n_specs = len(analysis_specifications)

    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Effect Sizes Across Specifications', 'P-value Distribution'),
        vertical_spacing=0.15,
        row_heights=[0.7, 0.3]
    )

    # Sort by effect size
    sort_idx = np.argsort(effect_sizes)

    # Colors based on significance
    colors = ['red' if p < 0.05 else 'blue' for p in p_values[sort_idx]]

    # 1. Effect sizes plot
    for i, idx in enumerate(sort_idx):
        # Highlight reference if provided
        if reference_spec is not None and idx == reference_spec:
            line_width = 3
            marker_size = 12
            color = 'green'
        else:
            line_width = 1.5
            marker_size = 8
            color = colors[i]

        # CI line
        fig.add_trace(
            go.Scatter(
                x=[ci_low[idx], ci_high[idx]],
                y=[i, i],
                mode='lines',
                line=dict(color=color, width=line_width),
                showlegend=False,
                hoverinfo='skip'
            ),
            row=1, col=1
        )

        # Point estimate
        fig.add_trace(
            go.Scatter(
                x=[effect_sizes[idx]],
                y=[i],
                mode='markers',
                marker=dict(size=marker_size, color=color, line=dict(color='black', width=1)),
                text=[analysis_specifications[idx]],
                hovertemplate=(
                    '<b>Specification %{y}</b><br>' +
                    '%{text}<br>' +
                    'Effect: %{x:.3f}<br>' +
                    '<extra></extra>'
                ),
                showlegend=False
            ),
            row=1, col=1
        )

    # Null line
    fig.add_vline(x=0, line_dash="dash", line_color="black", opacity=0.5, row=1, col=1)

    # 2. P-value histogram
    fig.add_trace(
        go.Histogram(
            x=p_values,
            nbinsx=20,
            marker_color='steelblue',
            showlegend=False,
            hovertemplate='P-value: %{x:.3f}<br>Count: %{y}<extra></extra>'
        ),
        row=2, col=1
    )

    # Significance threshold
    fig.add_vline(x=0.05, line_dash="dash", line_color="red",
                 annotation_text="α = 0.05", row=2, col=1)

    # Update layout
    fig.update_xaxes(title_text="Effect Size", row=1, col=1)
    fig.update_yaxes(title_text="Specification Index", row=1, col=1)

    fig.update_xaxes(title_text="P-value", row=2, col=1)
    fig.update_yaxes(title_text="Frequency", row=2, col=1)

    # Add summary stats
    n_sig = np.sum(p_values < 0.05)
    median_effect = np.median(effect_sizes)
    range_effects = np.max(effect_sizes) - np.min(effect_sizes)

    fig.add_annotation(
        text=f"<b>Summary</b><br>" +
             f"Significant: {n_sig}/{n_specs} ({n_sig/n_specs*100:.1f}%)<br>" +
             f"Median effect: {median_effect:.3f}<br>" +
             f"Range: {range_effects:.3f}",
        xref="paper", yref="paper",
        x=0.98, y=0.98,
        xanchor='right', yanchor='top',
        showarrow=False,
        bgcolor="white",
        bordercolor="black",
        borderwidth=2,
        font=dict(size=12)
    )

    fig.update_layout(
        height=900,
        width=1200,
        title_text="<b>Multiverse Analysis</b>",
        title_font_size=20,
        hovermode='closest'
    )

    return fig


__all__ = [
    'network_meta_3d',
    'animated_cumulative_plot',
    'heterogeneity_heatmap',
    'multiverse_analysis_plot',
]
