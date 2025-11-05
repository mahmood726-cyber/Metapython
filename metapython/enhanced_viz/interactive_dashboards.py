"""
Interactive Dashboards for Meta-Analysis

Create comprehensive interactive visualizations with Plotly for:
- Drill-down exploration of meta-analysis results
- Sensitivity analysis visualization
- Publication bias assessment
- Real-time parameter adjustment
"""

from typing import Dict, List, Any, Optional
import numpy as np
import warnings

from metapython.core.config import HAS_PLOTLY, logger

if HAS_PLOTLY:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.express as px


def create_meta_analysis_dashboard(
    effects: np.ndarray,
    se: np.ndarray,
    study_labels: np.ndarray,
    pooled_effect: float,
    pooled_se: float,
    heterogeneity: Dict[str, float],
    influence_diagnostics: Optional[Dict[str, Any]] = None
) -> go.Figure:
    """
    Create comprehensive interactive meta-analysis dashboard.

    Features:
    - Interactive forest plot with hover details
    - Funnel plot with contours
    - Influence diagnostics
    - Heterogeneity visualization

    Args:
        effects: Effect sizes
        se: Standard errors
        study_labels: Study names
        pooled_effect: Pooled effect estimate
        pooled_se: SE of pooled effect
        heterogeneity: Dict with I2, Q, tau2
        influence_diagnostics: Optional influence measures

    Returns:
        Plotly figure with subplots
    """
    if not HAS_PLOTLY:
        logger.error("Plotly not available. Install with: pip install plotly")
        raise ImportError("Plotly required for interactive dashboards")

    n_studies = len(effects)

    # Calculate CIs
    ci_low = effects - 1.96 * se
    ci_high = effects + 1.96 * se

    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Interactive Forest Plot',
            'Funnel Plot',
            'Influence Diagnostics',
            'Heterogeneity Assessment'
        ),
        specs=[
            [{"type": "scatter"}, {"type": "scatter"}],
            [{"type": "bar"}, {"type": "scatter"}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.10
    )

    # 1. Interactive Forest Plot
    # Error bars for CIs
    for i in range(n_studies):
        fig.add_trace(
            go.Scatter(
                x=[ci_low[i], ci_high[i]],
                y=[i, i],
                mode='lines',
                line=dict(color='gray', width=2),
                showlegend=False,
                hoverinfo='skip'
            ),
            row=1, col=1
        )

    # Effect sizes
    fig.add_trace(
        go.Scatter(
            x=effects,
            y=np.arange(n_studies),
            mode='markers',
            marker=dict(
                size=12,
                color='steelblue',
                line=dict(color='black', width=1)
            ),
            text=study_labels,
            customdata=np.column_stack([effects, ci_low, ci_high, se]),
            hovertemplate=(
                '<b>%{text}</b><br>' +
                'Effect: %{customdata[0]:.3f}<br>' +
                '95% CI: [%{customdata[1]:.3f}, %{customdata[2]:.3f}]<br>' +
                'SE: %{customdata[3]:.3f}<br>' +
                '<extra></extra>'
            ),
            name='Studies'
        ),
        row=1, col=1
    )

    # Pooled estimate
    fig.add_trace(
        go.Scatter(
            x=[pooled_effect],
            y=[n_studies + 1],
            mode='markers',
            marker=dict(
                symbol='diamond',
                size=15,
                color='darkred',
                line=dict(color='black', width=2)
            ),
            hovertemplate=(
                '<b>Pooled Estimate</b><br>' +
                f'Effect: {pooled_effect:.3f}<br>' +
                f'SE: {pooled_se:.3f}<br>' +
                '<extra></extra>'
            ),
            name='Pooled'
        ),
        row=1, col=1
    )

    # Null line
    fig.add_vline(x=0, line_dash="dash", line_color="black", opacity=0.5, row=1, col=1)

    # 2. Funnel Plot
    # Contour regions
    se_range = np.linspace(0, np.max(se) * 1.2, 50)

    # 95% CI funnel
    ci_lower = pooled_effect - 1.96 * se_range
    ci_upper = pooled_effect + 1.96 * se_range

    fig.add_trace(
        go.Scatter(
            x=np.concatenate([ci_lower, ci_upper[::-1]]),
            y=np.concatenate([se_range, se_range[::-1]]),
            fill='toself',
            fillcolor='rgba(0,100,200,0.2)',
            line=dict(color='rgba(0,100,200,0.5)', width=1),
            name='95% CI',
            hoverinfo='skip'
        ),
        row=1, col=2
    )

    # Studies
    fig.add_trace(
        go.Scatter(
            x=effects,
            y=se,
            mode='markers',
            marker=dict(
                size=10,
                color='steelblue',
                line=dict(color='black', width=1)
            ),
            text=study_labels,
            hovertemplate=(
                '<b>%{text}</b><br>' +
                'Effect: %{x:.3f}<br>' +
                'SE: %{y:.3f}<br>' +
                '<extra></extra>'
            ),
            name='Studies',
            showlegend=False
        ),
        row=1, col=2
    )

    # Pooled estimate line
    fig.add_vline(x=pooled_effect, line_dash="dash", line_color="red",
                 annotation_text=f"Pooled: {pooled_effect:.3f}",
                 row=1, col=2)

    # 3. Influence Diagnostics
    if influence_diagnostics is not None:
        cook_d = np.array(influence_diagnostics.get('cook_distance', []))
        if len(cook_d) > 0:
            fig.add_trace(
                go.Bar(
                    x=study_labels,
                    y=cook_d,
                    marker_color='indianred',
                    text=[f"{d:.3f}" for d in cook_d],
                    textposition='outside',
                    hovertemplate=(
                        '<b>%{x}</b><br>' +
                        "Cook's D: %{y:.4f}<br>" +
                        '<extra></extra>'
                    ),
                    name="Cook's Distance"
                ),
                row=2, col=1
            )

            # Threshold line
            threshold = 4 / n_studies
            fig.add_hline(y=threshold, line_dash="dash", line_color="red",
                         annotation_text=f"Threshold: {threshold:.3f}",
                         row=2, col=1)

    # 4. Heterogeneity Visualization
    I2 = heterogeneity.get('I2', 0)
    tau2 = heterogeneity.get('tau2', 0)
    Q = heterogeneity.get('Q', 0)

    # Create a visualization of study-level vs. pooled effects
    fig.add_trace(
        go.Scatter(
            x=np.arange(n_studies),
            y=effects,
            mode='markers+lines',
            marker=dict(size=10, color='steelblue'),
            line=dict(color='lightgray', width=1),
            error_y=dict(
                type='data',
                array=1.96 * se,
                visible=True,
                color='gray'
            ),
            text=study_labels,
            hovertemplate=(
                '<b>%{text}</b><br>' +
                'Effect: %{y:.3f}<br>' +
                '<extra></extra>'
            ),
            name='Study Effects'
        ),
        row=2, col=2
    )

    # Pooled estimate line
    fig.add_hline(y=pooled_effect, line_dash="dash", line_color="red",
                 annotation_text=f"Pooled: {pooled_effect:.3f}",
                 row=2, col=2)

    # Add heterogeneity annotation
    fig.add_annotation(
        text=f"I² = {I2:.1f}%<br>τ² = {tau2:.3f}<br>Q = {Q:.2f}",
        xref="x4", yref="y4",
        x=0.95, y=0.95,
        xanchor='right', yanchor='top',
        showarrow=False,
        bgcolor="white",
        bordercolor="black",
        borderwidth=1,
        row=2, col=2
    )

    # Update layout
    fig.update_xaxes(title_text="Effect Size", row=1, col=1)
    fig.update_yaxes(title_text="Study", row=1, col=1, showticklabels=False)

    fig.update_xaxes(title_text="Effect Size", row=1, col=2)
    fig.update_yaxes(title_text="Standard Error", row=1, col=2, autorange="reversed")

    fig.update_xaxes(title_text="Study", row=2, col=1, tickangle=-45)
    fig.update_yaxes(title_text="Cook's Distance", row=2, col=1)

    fig.update_xaxes(title_text="Study Index", row=2, col=2)
    fig.update_yaxes(title_text="Effect Size", row=2, col=2)

    fig.update_layout(
        height=1000,
        width=1400,
        title_text="<b>Meta-Analysis Dashboard</b>",
        title_font_size=20,
        showlegend=False,
        hovermode='closest'
    )

    return fig


def interactive_sensitivity_dashboard(
    effects: np.ndarray,
    se: np.ndarray,
    study_labels: np.ndarray,
    leave_one_out_results: Dict[str, List[float]]
) -> go.Figure:
    """
    Create interactive sensitivity analysis dashboard.

    Shows impact of removing each study on pooled estimate.

    Args:
        effects: Effect sizes
        se: Standard errors
        study_labels: Study names
        leave_one_out_results: Dict with 'effects', 'ci_low', 'ci_high'

    Returns:
        Plotly figure
    """
    if not HAS_PLOTLY:
        raise ImportError("Plotly required for interactive dashboards")

    n_studies = len(effects)

    loo_effects = np.array(leave_one_out_results['effects'])
    loo_ci_low = np.array(leave_one_out_results['ci_low'])
    loo_ci_high = np.array(leave_one_out_results['ci_high'])

    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(
            'Leave-One-Out Sensitivity Analysis',
            'Impact on Pooled Estimate'
        ),
        vertical_spacing=0.15,
        row_heights=[0.6, 0.4]
    )

    # 1. Leave-one-out estimates
    for i in range(n_studies):
        # CI lines
        fig.add_trace(
            go.Scatter(
                x=[loo_ci_low[i], loo_ci_high[i]],
                y=[i, i],
                mode='lines',
                line=dict(color='gray', width=2),
                showlegend=False,
                hoverinfo='skip'
            ),
            row=1, col=1
        )

    # Effect estimates
    fig.add_trace(
        go.Scatter(
            x=loo_effects,
            y=np.arange(n_studies),
            mode='markers',
            marker=dict(size=10, color='steelblue', line=dict(color='black', width=1)),
            text=study_labels,
            customdata=np.column_stack([loo_effects, loo_ci_low, loo_ci_high]),
            hovertemplate=(
                '<b>Excluding: %{text}</b><br>' +
                'Pooled Effect: %{customdata[0]:.3f}<br>' +
                '95% CI: [%{customdata[1]:.3f}, %{customdata[2]:.3f}]<br>' +
                '<extra></extra>'
            ),
            name='Leave-One-Out'
        ),
        row=1, col=1
    )

    # 2. Impact visualization
    weights = 1 / (se ** 2)
    pooled_full = np.sum(weights * effects) / np.sum(weights)

    impact = np.abs(loo_effects - pooled_full)

    fig.add_trace(
        go.Bar(
            x=study_labels,
            y=impact,
            marker_color='indianred',
            text=[f"{i:.3f}" for i in impact],
            textposition='outside',
            hovertemplate=(
                '<b>%{x}</b><br>' +
                'Impact: %{y:.3f}<br>' +
                '<extra></extra>'
            ),
            name='Impact'
        ),
        row=2, col=1
    )

    # Update layout
    fig.update_xaxes(title_text="Pooled Effect", row=1, col=1)
    fig.update_yaxes(title_text="Excluded Study", row=1, col=1, showticklabels=False)

    fig.update_xaxes(title_text="Excluded Study", row=2, col=1, tickangle=-45)
    fig.update_yaxes(title_text="Absolute Impact", row=2, col=1)

    fig.update_layout(
        height=900,
        width=1200,
        title_text="<b>Sensitivity Analysis Dashboard</b>",
        title_font_size=20,
        showlegend=False,
        hovermode='closest'
    )

    return fig


def bias_assessment_dashboard(
    effects: np.ndarray,
    se: np.ndarray,
    study_labels: np.ndarray,
    bias_tests: Dict[str, Any]
) -> go.Figure:
    """
    Create interactive publication bias assessment dashboard.

    Args:
        effects: Effect sizes
        se: Standard errors
        study_labels: Study names
        bias_tests: Dict with bias test results (egger, begg, trim_fill, etc.)

    Returns:
        Plotly figure
    """
    if not HAS_PLOTLY:
        raise ImportError("Plotly required for interactive dashboards")

    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Funnel Plot',
            'Egger Regression',
            'Trim-and-Fill',
            'P-Curve'
        ),
        specs=[
            [{"type": "scatter"}, {"type": "scatter"}],
            [{"type": "scatter"}, {"type": "histogram"}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.10
    )

    # 1. Funnel Plot
    weights = 1 / (se ** 2)
    pooled = np.sum(weights * effects) / np.sum(weights)

    # 95% CI funnel
    se_range = np.linspace(0, np.max(se) * 1.2, 50)
    ci_lower = pooled - 1.96 * se_range
    ci_upper = pooled + 1.96 * se_range

    fig.add_trace(
        go.Scatter(
            x=np.concatenate([ci_lower, ci_upper[::-1]]),
            y=np.concatenate([se_range, se_range[::-1]]),
            fill='toself',
            fillcolor='rgba(0,100,200,0.2)',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=effects,
            y=se,
            mode='markers',
            marker=dict(size=10, color='steelblue'),
            text=study_labels,
            hovertemplate='<b>%{text}</b><br>Effect: %{x:.3f}<br>SE: %{y:.3f}<extra></extra>',
            showlegend=False
        ),
        row=1, col=1
    )

    # 2. Egger Regression
    if 'egger' in bias_tests:
        precision = 1 / se
        egger_result = bias_tests['egger']

        fig.add_trace(
            go.Scatter(
                x=precision,
                y=effects / se,
                mode='markers',
                marker=dict(size=10, color='steelblue'),
                text=study_labels,
                hovertemplate='<b>%{text}</b><br>Precision: %{x:.2f}<br>Std Effect: %{y:.3f}<extra></extra>',
                showlegend=False
            ),
            row=1, col=2
        )

        # Regression line
        intercept = egger_result.get('intercept', 0)
        slope = egger_result.get('slope', 0)
        x_reg = np.linspace(np.min(precision), np.max(precision), 100)
        y_reg = intercept + slope * x_reg

        fig.add_trace(
            go.Scatter(
                x=x_reg,
                y=y_reg,
                mode='lines',
                line=dict(color='red', dash='dash'),
                name='Regression',
                showlegend=False
            ),
            row=1, col=2
        )

    # 3. Trim-and-Fill
    if 'trim_fill' in bias_tests:
        tf_result = bias_tests['trim_fill']
        imputed_effects = tf_result.get('imputed_effects', [])
        imputed_se = tf_result.get('imputed_se', [])

        # Original studies
        fig.add_trace(
            go.Scatter(
                x=effects,
                y=se,
                mode='markers',
                marker=dict(size=10, color='steelblue'),
                name='Observed',
                text=study_labels,
                hovertemplate='<b>%{text}</b><br>Effect: %{x:.3f}<br>SE: %{y:.3f}<extra></extra>'
            ),
            row=2, col=1
        )

        # Imputed studies
        if len(imputed_effects) > 0:
            fig.add_trace(
                go.Scatter(
                    x=imputed_effects,
                    y=imputed_se,
                    mode='markers',
                    marker=dict(size=10, color='red', symbol='x'),
                    name='Imputed',
                    hovertemplate='Effect: %{x:.3f}<br>SE: %{y:.3f}<extra></extra>'
                ),
                row=2, col=1
            )

    # 4. P-value distribution
    z_scores = effects / se
    p_values = 2 * (1 - np.abs(z_scores))  # Two-tailed p-values (approximate)

    fig.add_trace(
        go.Histogram(
            x=p_values,
            nbinsx=20,
            marker_color='steelblue',
            name='P-values',
            showlegend=False,
            hovertemplate='P-value range: %{x}<br>Count: %{y}<extra></extra>'
        ),
        row=2, col=2
    )

    # Update layout
    fig.update_xaxes(title_text="Effect Size", row=1, col=1)
    fig.update_yaxes(title_text="Standard Error", row=1, col=1, autorange="reversed")

    fig.update_xaxes(title_text="Precision (1/SE)", row=1, col=2)
    fig.update_yaxes(title_text="Standardized Effect", row=1, col=2)

    fig.update_xaxes(title_text="Effect Size", row=2, col=1)
    fig.update_yaxes(title_text="Standard Error", row=2, col=1, autorange="reversed")

    fig.update_xaxes(title_text="P-value", row=2, col=2)
    fig.update_yaxes(title_text="Frequency", row=2, col=2)

    fig.update_layout(
        height=1000,
        width=1400,
        title_text="<b>Publication Bias Assessment Dashboard</b>",
        title_font_size=20,
        hovermode='closest'
    )

    return fig


__all__ = [
    'create_meta_analysis_dashboard',
    'interactive_sensitivity_dashboard',
    'bias_assessment_dashboard',
]
