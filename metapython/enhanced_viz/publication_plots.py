"""
Publication-Quality Plots for Meta-Analysis

Implements advanced visualization methods from:
- Lewis & Clarke (2001). "Forest plots" BMJ, 322(7300), 1479-1480.
- Galbraith (1988). "A note on graphical presentation of estimated odds ratios"
  Statistics in Medicine, 7(8), 889-894.
- Peters et al. (2008). "Contour-enhanced meta-analysis funnel plots"
  Research Synthesis Methods, 1(1), 27-42.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import gridspec
from scipy import stats
import warnings

from metapython.core.config import HAS_PLOTLY, logger

if HAS_PLOTLY:
    import plotly.graph_objects as go
    import plotly.express as px


def advanced_forest_plot(
    effects: np.ndarray,
    se: np.ndarray,
    study_labels: np.ndarray,
    pooled_effect: float,
    pooled_se: float,
    groups: Optional[np.ndarray] = None,
    prediction_interval: Optional[Tuple[float, float]] = None,
    weights: Optional[np.ndarray] = None,
    title: str = "Forest Plot",
    effect_label: str = "Effect Size",
    figsize: Tuple[int, int] = (12, 10),
    journal_style: str = "default"
) -> plt.Figure:
    """
    Create advanced publication-quality forest plot with subgroups.

    Features:
    - Subgroup analysis with separate pooled estimates
    - Prediction interval diamond
    - Weighted box sizes
    - Professional formatting for publication
    - Multiple journal style presets

    Args:
        effects: Effect sizes
        se: Standard errors
        study_labels: Study names
        pooled_effect: Overall pooled effect
        pooled_se: SE of pooled effect
        groups: Optional group labels for subgroup analysis
        prediction_interval: Optional prediction interval (low, high)
        weights: Optional custom weights for box sizes
        title: Plot title
        effect_label: Label for x-axis
        figsize: Figure size
        journal_style: 'default', 'bmj', 'jama', 'lancet', 'nature'

    Returns:
        Matplotlib figure
    """
    n_studies = len(effects)

    # Calculate CIs
    ci_low = effects - 1.96 * se
    ci_high = effects + 1.96 * se

    # Calculate weights for box sizes
    if weights is None:
        weights = 1 / (se ** 2)
    weights_normalized = weights / np.max(weights) * 100

    # Set journal-specific style
    style_params = _get_journal_style(journal_style)

    fig = plt.figure(figsize=figsize)
    gs = gridspec.GridSpec(1, 2, width_ratios=[2, 3], wspace=0.05)

    # Left panel: Study labels and weights
    ax_labels = plt.subplot(gs[0])
    ax_labels.axis('off')

    # Right panel: Forest plot
    ax_forest = plt.subplot(gs[1])

    y_positions = np.arange(n_studies)

    # Handle subgroups
    if groups is not None:
        unique_groups = np.unique(groups)
        y_offset = 0
        current_y = 0

        for group in unique_groups:
            group_mask = groups == group
            group_effects = effects[group_mask]
            group_se = se[group_mask]
            group_labels = study_labels[group_mask]
            group_weights = weights_normalized[group_mask]
            group_ci_low = ci_low[group_mask]
            group_ci_high = ci_high[group_mask]

            n_group = np.sum(group_mask)

            # Plot group studies
            for i in range(n_group):
                y = current_y + i

                # CI line
                ax_forest.plot([group_ci_low[i], group_ci_high[i]], [y, y],
                             color=style_params['ci_color'], linewidth=1.5, zorder=1)

                # Effect size box
                box_size = np.sqrt(group_weights[i]) / 5
                rect = patches.Rectangle(
                    (group_effects[i] - box_size/2, y - box_size/2),
                    box_size, box_size,
                    facecolor=style_params['box_color'],
                    edgecolor='black',
                    linewidth=1,
                    zorder=2
                )
                ax_forest.add_patch(rect)

                # Study label
                ax_labels.text(0.98, y, f"  {group_labels[i]}",
                             ha='right', va='center',
                             fontsize=style_params['label_fontsize'])

                # Weight percentage
                ax_labels.text(1.0, y, f"{group_weights[i]:.1f}%",
                             ha='left', va='center',
                             fontsize=style_params['label_fontsize'])

            # Group pooled estimate
            group_weights_raw = 1 / (group_se ** 2)
            group_pooled = np.sum(group_weights_raw * group_effects) / np.sum(group_weights_raw)
            group_pooled_se = np.sqrt(1 / np.sum(group_weights_raw))
            group_pooled_ci_low = group_pooled - 1.96 * group_pooled_se
            group_pooled_ci_high = group_pooled + 1.96 * group_pooled_se

            y_group = current_y + n_group + 0.5

            # Group diamond
            _draw_diamond(ax_forest, group_pooled, group_pooled_ci_low,
                         group_pooled_ci_high, y_group,
                         color=style_params['subgroup_color'])

            # Group label
            ax_labels.text(0.5, y_group, f"Subtotal: {group}",
                         ha='left', va='center', weight='bold',
                         fontsize=style_params['label_fontsize'] + 1)

            current_y = y_group + 2

        y_overall = current_y + 1
    else:
        # Plot all studies
        for i in range(n_studies):
            # CI line
            ax_forest.plot([ci_low[i], ci_high[i]], [i, i],
                         color=style_params['ci_color'], linewidth=1.5, zorder=1)

            # Effect size box
            box_size = np.sqrt(weights_normalized[i]) / 5
            rect = patches.Rectangle(
                (effects[i] - box_size/2, i - box_size/2),
                box_size, box_size,
                facecolor=style_params['box_color'],
                edgecolor='black',
                linewidth=1,
                zorder=2
            )
            ax_forest.add_patch(rect)

            # Study label
            ax_labels.text(0.98, i, f"  {study_labels[i]}",
                         ha='right', va='center',
                         fontsize=style_params['label_fontsize'])

            # Weight percentage
            ax_labels.text(1.0, i, f"{weights_normalized[i]:.1f}%",
                         ha='left', va='center',
                         fontsize=style_params['label_fontsize'])

        y_overall = n_studies + 2

    # Overall pooled estimate diamond
    pooled_ci_low = pooled_effect - 1.96 * pooled_se
    pooled_ci_high = pooled_effect + 1.96 * pooled_se
    _draw_diamond(ax_forest, pooled_effect, pooled_ci_low, pooled_ci_high,
                 y_overall, color=style_params['overall_color'])

    # Overall label
    ax_labels.text(0.5, y_overall, "Overall",
                 ha='left', va='center', weight='bold',
                 fontsize=style_params['label_fontsize'] + 2)

    # Prediction interval
    if prediction_interval is not None:
        y_pred = y_overall + 1.5
        _draw_diamond(ax_forest, pooled_effect, prediction_interval[0],
                     prediction_interval[1], y_pred,
                     color=style_params['prediction_color'], alpha=0.3)
        ax_labels.text(0.5, y_pred, "Prediction Interval",
                     ha='left', va='center', style='italic',
                     fontsize=style_params['label_fontsize'])

    # Vertical line at null effect
    ax_forest.axvline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)

    # Formatting
    ax_forest.set_xlabel(effect_label, fontsize=style_params['axis_fontsize'])
    ax_forest.set_title(title, fontsize=style_params['title_fontsize'], weight='bold')
    ax_forest.set_ylim(-1, y_overall + 3)
    ax_forest.tick_params(axis='both', labelsize=style_params['tick_fontsize'])
    ax_forest.spines['top'].set_visible(False)
    ax_forest.spines['right'].set_visible(False)
    ax_forest.spines['left'].set_visible(False)
    ax_forest.set_yticks([])

    ax_labels.set_ylim(-1, y_overall + 3)
    ax_labels.set_xlim(0, 1.2)

    plt.tight_layout()

    return fig


def _draw_diamond(ax, center, ci_low, ci_high, y, color='red', alpha=0.7):
    """Draw diamond for pooled estimate."""
    diamond_x = [ci_low, center, ci_high, center, ci_low]
    diamond_y = [y, y + 0.3, y, y - 0.3, y]
    ax.fill(diamond_x, diamond_y, color=color, alpha=alpha, edgecolor='black', linewidth=1.5)


def _get_journal_style(style: str) -> Dict[str, Any]:
    """Get journal-specific style parameters."""
    styles = {
        'default': {
            'box_color': 'steelblue',
            'ci_color': 'gray',
            'overall_color': 'darkred',
            'subgroup_color': 'indianred',
            'prediction_color': 'coral',
            'label_fontsize': 9,
            'axis_fontsize': 11,
            'title_fontsize': 13,
            'tick_fontsize': 9,
        },
        'bmj': {
            'box_color': '#004c93',
            'ci_color': '#666666',
            'overall_color': '#c00000',
            'subgroup_color': '#e06666',
            'prediction_color': '#f4cccc',
            'label_fontsize': 8,
            'axis_fontsize': 10,
            'title_fontsize': 12,
            'tick_fontsize': 8,
        },
        'jama': {
            'box_color': '#0072b2',
            'ci_color': '#666666',
            'overall_color': '#d55e00',
            'subgroup_color': '#f0a020',
            'prediction_color': '#ffd580',
            'label_fontsize': 9,
            'axis_fontsize': 11,
            'title_fontsize': 13,
            'tick_fontsize': 9,
        },
        'lancet': {
            'box_color': '#2e3192',
            'ci_color': '#000000',
            'overall_color': '#dc0019',
            'subgroup_color': '#ff6b6b',
            'prediction_color': '#ffb3b3',
            'label_fontsize': 9,
            'axis_fontsize': 11,
            'title_fontsize': 13,
            'tick_fontsize': 9,
        },
        'nature': {
            'box_color': '#0077bb',
            'ci_color': '#333333',
            'overall_color': '#ee7733',
            'subgroup_color': '#ffaa66',
            'prediction_color': '#ffccaa',
            'label_fontsize': 8,
            'axis_fontsize': 10,
            'title_fontsize': 12,
            'tick_fontsize': 8,
        },
    }

    return styles.get(style, styles['default'])


def cumulative_forest_plot(
    effects: np.ndarray,
    se: np.ndarray,
    years: np.ndarray,
    study_labels: np.ndarray,
    title: str = "Cumulative Meta-Analysis",
    figsize: Tuple[int, int] = (12, 10)
) -> plt.Figure:
    """
    Create cumulative forest plot showing evolution of evidence over time.

    Args:
        effects: Effect sizes
        se: Standard errors
        years: Publication years
        study_labels: Study names
        title: Plot title
        figsize: Figure size

    Returns:
        Matplotlib figure
    """
    # Sort by year
    sort_idx = np.argsort(years)
    effects_sorted = effects[sort_idx]
    se_sorted = se[sort_idx]
    years_sorted = years[sort_idx]
    labels_sorted = study_labels[sort_idx]

    n_studies = len(effects)

    # Calculate cumulative estimates
    cumulative_effects = []
    cumulative_ci_low = []
    cumulative_ci_high = []

    for i in range(1, n_studies + 1):
        cum_effects = effects_sorted[:i]
        cum_se = se_sorted[:i]
        cum_weights = 1 / (cum_se ** 2)

        pooled = np.sum(cum_weights * cum_effects) / np.sum(cum_weights)
        pooled_se = np.sqrt(1 / np.sum(cum_weights))

        cumulative_effects.append(pooled)
        cumulative_ci_low.append(pooled - 1.96 * pooled_se)
        cumulative_ci_high.append(pooled + 1.96 * pooled_se)

    cumulative_effects = np.array(cumulative_effects)
    cumulative_ci_low = np.array(cumulative_ci_low)
    cumulative_ci_high = np.array(cumulative_ci_high)

    # Create plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize, gridspec_kw={'width_ratios': [1, 2]})

    # Left panel: Cumulative estimate over time
    ax1.plot(years_sorted, cumulative_effects, 'o-', color='steelblue', linewidth=2, markersize=6)
    ax1.fill_between(years_sorted, cumulative_ci_low, cumulative_ci_high,
                     alpha=0.3, color='steelblue')
    ax1.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax1.set_xlabel('Year', fontsize=11)
    ax1.set_ylabel('Cumulative Effect Size', fontsize=11)
    ax1.set_title('Cumulative Estimate', fontsize=12, weight='bold')
    ax1.grid(True, alpha=0.3)

    # Right panel: Forest plot of cumulative estimates
    y_pos = np.arange(n_studies)

    for i in range(n_studies):
        # CI line
        ax2.plot([cumulative_ci_low[i], cumulative_ci_high[i]], [i, i],
                color='gray', linewidth=1.5)

        # Effect size marker
        ax2.plot(cumulative_effects[i], i, 'D', color='steelblue',
                markersize=8, markeredgecolor='black', markeredgewidth=1)

        # Label
        ax2.text(-0.1, i, f"{labels_sorted[i]} ({int(years_sorted[i])})",
                ha='right', va='center', fontsize=9, transform=ax2.get_yaxis_transform())

    ax2.axvline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax2.set_xlabel('Cumulative Effect Size', fontsize=11)
    ax2.set_title('Cumulative Forest Plot', fontsize=12, weight='bold')
    ax2.set_yticks([])
    ax2.spines['left'].set_visible(False)

    plt.suptitle(title, fontsize=14, weight='bold', y=0.98)
    plt.tight_layout()

    return fig


def radial_plot(
    effects: np.ndarray,
    se: np.ndarray,
    study_labels: Optional[np.ndarray] = None,
    title: str = "Radial (Galbraith) Plot",
    figsize: Tuple[int, int] = (10, 10)
) -> plt.Figure:
    """
    Create radial (Galbraith) plot for heterogeneity assessment.

    Implements: Galbraith (1988). Statistics in Medicine, 7(8), 889-894.

    Args:
        effects: Effect sizes
        se: Standard errors
        study_labels: Optional study names
        title: Plot title
        figsize: Figure size

    Returns:
        Matplotlib figure
    """
    n_studies = len(effects)

    if study_labels is None:
        study_labels = np.array([f"Study {i+1}" for i in range(n_studies)])

    # Calculate inverse SE (precision)
    precision = 1 / se

    # Standardized effect (z-score)
    z_scores = effects / se

    # Calculate regression line (pooled estimate)
    weights = precision ** 2
    pooled = np.sum(weights * effects) / np.sum(weights)
    slope = pooled

    # Create plot
    fig, ax = plt.subplots(figsize=figsize)

    # Plot studies
    ax.scatter(precision, z_scores, s=100, alpha=0.6, c='steelblue',
              edgecolors='black', linewidth=1, zorder=3)

    # Add study labels
    for i in range(n_studies):
        ax.annotate(study_labels[i], (precision[i], z_scores[i]),
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=8, alpha=0.7)

    # Regression line (pooled estimate)
    x_range = np.array([0, np.max(precision) * 1.1])
    ax.plot(x_range, slope * x_range, 'r-', linewidth=2, label=f'Pooled estimate = {slope:.3f}')

    # 95% confidence bounds
    ax.plot(x_range, slope * x_range + 1.96, 'r--', linewidth=1.5, alpha=0.5)
    ax.plot(x_range, slope * x_range - 1.96, 'r--', linewidth=1.5, alpha=0.5)

    # Formatting
    ax.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.3)
    ax.set_xlabel('Inverse Standard Error (Precision)', fontsize=12)
    ax.set_ylabel('Standardized Effect (Z-score)', fontsize=12)
    ax.set_title(title, fontsize=14, weight='bold')
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    return fig


def labbé_plot(
    events_treatment: np.ndarray,
    total_treatment: np.ndarray,
    events_control: np.ndarray,
    total_control: np.ndarray,
    study_labels: Optional[np.ndarray] = None,
    title: str = "L'Abbé Plot",
    figsize: Tuple[int, int] = (10, 10)
) -> plt.Figure:
    """
    Create L'Abbé plot for binary outcomes.

    Shows event rates in treatment vs control groups.

    Args:
        events_treatment: Number of events in treatment
        total_treatment: Total in treatment
        events_control: Number of events in control
        total_control: Total in control
        study_labels: Optional study names
        title: Plot title
        figsize: Figure size

    Returns:
        Matplotlib figure
    """
    n_studies = len(events_treatment)

    if study_labels is None:
        study_labels = np.array([f"Study {i+1}" for i in range(n_studies)])

    # Calculate proportions
    prop_treatment = events_treatment / total_treatment
    prop_control = events_control / total_control

    # Bubble sizes proportional to total N
    total_n = total_treatment + total_control
    sizes = (total_n / np.max(total_n)) * 1000

    # Create plot
    fig, ax = plt.subplots(figsize=figsize)

    # Scatter plot with bubble sizes
    scatter = ax.scatter(prop_control, prop_treatment, s=sizes, alpha=0.5,
                        c=np.arange(n_studies), cmap='viridis',
                        edgecolors='black', linewidth=1)

    # Add study labels
    for i in range(n_studies):
        ax.annotate(study_labels[i], (prop_control[i], prop_treatment[i]),
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=8, alpha=0.7)

    # Line of equality
    ax.plot([0, 1], [0, 1], 'k--', linewidth=2, alpha=0.5, label='No effect')

    # Formatting
    ax.set_xlabel('Event Rate in Control Group', fontsize=12)
    ax.set_ylabel('Event Rate in Treatment Group', fontsize=12)
    ax.set_title(title, fontsize=14, weight='bold')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Study Index', fontsize=10)

    plt.tight_layout()

    return fig


def contour_enhanced_funnel(
    effects: np.ndarray,
    se: np.ndarray,
    pooled_effect: float,
    title: str = "Contour-Enhanced Funnel Plot",
    figsize: Tuple[int, int] = (10, 10)
) -> plt.Figure:
    """
    Create contour-enhanced funnel plot.

    Implements: Peters et al. (2008). Research Synthesis Methods, 1(1), 27-42.

    Shows significance contours to aid interpretation of publication bias.

    Args:
        effects: Effect sizes
        se: Standard errors
        pooled_effect: Pooled effect estimate
        title: Plot title
        figsize: Figure size

    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Create contour regions
    se_range = np.linspace(0, np.max(se) * 1.2, 100)

    # p < 0.01 region (darker)
    ci_99_lower = pooled_effect - 2.576 * se_range
    ci_99_upper = pooled_effect + 2.576 * se_range
    ax.fill_betweenx(se_range, ci_99_lower, ci_99_upper,
                     alpha=0.1, color='gray', label='p > 0.01')

    # p < 0.05 region (lighter)
    ci_95_lower = pooled_effect - 1.96 * se_range
    ci_95_upper = pooled_effect + 1.96 * se_range
    ax.fill_betweenx(se_range, ci_95_lower, ci_95_upper,
                     alpha=0.15, color='lightgray', label='p > 0.05')

    # p < 0.10 region (lightest)
    ci_90_lower = pooled_effect - 1.645 * se_range
    ci_90_upper = pooled_effect + 1.645 * se_range
    ax.fill_betweenx(se_range, ci_90_lower, ci_90_upper,
                     alpha=0.2, color='whitesmoke', label='p > 0.10')

    # Plot studies
    ax.scatter(effects, se, s=100, alpha=0.6, c='steelblue',
              edgecolors='black', linewidth=1, zorder=3)

    # Pooled estimate line
    ax.axvline(pooled_effect, color='red', linestyle='--', linewidth=2,
              label=f'Pooled effect = {pooled_effect:.3f}')

    # Formatting
    ax.set_xlabel('Effect Size', fontsize=12)
    ax.set_ylabel('Standard Error', fontsize=12)
    ax.set_title(title, fontsize=14, weight='bold')
    ax.invert_yaxis()  # Invert y-axis (precision at top)
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    return fig


def galbraith_plot(
    effects: np.ndarray,
    variances: np.ndarray,
    study_labels: Optional[np.ndarray] = None,
    title: str = "Galbraith Plot",
    figsize: Tuple[int, int] = (10, 8)
) -> plt.Figure:
    """
    Create Galbraith plot for assessing heterogeneity.

    Alternative presentation to radial plot.

    Args:
        effects: Effect sizes
        variances: Within-study variances
        study_labels: Optional study names
        title: Plot title
        figsize: Figure size

    Returns:
        Matplotlib figure
    """
    n_studies = len(effects)

    if study_labels is None:
        study_labels = np.array([f"Study {i+1}" for i in range(n_studies)])

    # Calculate precision (inverse SE)
    se = np.sqrt(variances)
    precision = 1 / se

    # Calculate z-scores
    z = effects * precision

    # Calculate pooled estimate
    weights = 1 / variances
    pooled = np.sum(weights * effects) / np.sum(weights)

    # Create plot
    fig, ax = plt.subplots(figsize=figsize)

    # Plot points
    ax.scatter(precision, z, s=100, alpha=0.6, c='steelblue',
              edgecolors='black', linewidth=1)

    # Add labels
    for i in range(n_studies):
        ax.annotate(study_labels[i], (precision[i], z[i]),
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=8, alpha=0.7)

    # Reference lines
    x_max = np.max(precision) * 1.1
    x_range = np.array([0, x_max])

    # Pooled estimate
    ax.plot(x_range, pooled * x_range, 'r-', linewidth=2,
           label=f'Pooled = {pooled:.3f}')

    # 95% CI bounds
    ax.plot(x_range, pooled * x_range + 1.96, 'r--', linewidth=1, alpha=0.5)
    ax.plot(x_range, pooled * x_range - 1.96, 'r--', linewidth=1, alpha=0.5)

    # Formatting
    ax.axhline(0, color='black', linestyle=':', linewidth=1, alpha=0.3)
    ax.set_xlabel('Precision (1/SE)', fontsize=12)
    ax.set_ylabel('Z = Effect / SE', fontsize=12)
    ax.set_title(title, fontsize=14, weight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    return fig


__all__ = [
    'advanced_forest_plot',
    'cumulative_forest_plot',
    'radial_plot',
    'labbé_plot',
    'contour_enhanced_funnel',
    'galbraith_plot',
]
