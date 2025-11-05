"""
Static publication-quality plots for meta-analysis using matplotlib.

Provides forest plots, funnel plots, radial plots, and Baujat plots
with customizable styling suitable for journal publication.
"""

from typing import Optional, List, Tuple, Dict, Any
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm


def forest_plot(
    effects: np.ndarray,
    se: np.ndarray,
    study_labels: np.ndarray,
    pooled_effect: Optional[float] = None,
    pooled_se: Optional[float] = None,
    title: str = "Forest Plot",
    xlabel: str = "Effect Size",
    alpha: float = 0.05,
    figsize: Tuple[int, int] = (10, 8),
    save_path: Optional[str] = None,
) -> plt.Figure:
    """
    Create publication-quality forest plot.

    Args:
        effects: Effect sizes for each study
        se: Standard errors
        study_labels: Study names
        pooled_effect: Pooled effect estimate
        pooled_se: Pooled standard error
        title: Plot title
        xlabel: X-axis label
        alpha: Significance level for CIs
        figsize: Figure size (width, height)
        save_path: Path to save figure

    Returns:
        matplotlib Figure object
    """
    n_studies = len(effects)
    z_crit = norm.ppf(1 - alpha / 2)

    # Calculate confidence intervals
    ci_low = effects - z_crit * se
    ci_high = effects + z_crit * se

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Plot each study
    y_positions = np.arange(n_studies)
    weights = 1 / (se ** 2)
    weights_norm = 100 * weights / np.max(weights)  # Normalize for marker size

    for i in range(n_studies):
        # Plot CI line
        ax.plot(
            [ci_low[i], ci_high[i]],
            [y_positions[i], y_positions[i]],
            'k-',
            linewidth=1,
            alpha=0.7
        )

        # Plot point estimate
        ax.scatter(
            effects[i],
            y_positions[i],
            s=weights_norm[i],
            c='steelblue',
            marker='s',
            edgecolors='black',
            linewidth=0.5,
            zorder=3
        )

    # Add pooled estimate if provided
    if pooled_effect is not None and pooled_se is not None:
        pooled_ci_low = pooled_effect - z_crit * pooled_se
        pooled_ci_high = pooled_effect + z_crit * pooled_se

        y_pooled = -1.5
        ax.plot(
            [pooled_ci_low, pooled_ci_high],
            [y_pooled, y_pooled],
            'k-',
            linewidth=2
        )
        ax.scatter(
            pooled_effect,
            y_pooled,
            s=200,
            c='darkred',
            marker='D',
            edgecolors='black',
            linewidth=1,
            zorder=3,
            label='Pooled Estimate'
        )

        # Add horizontal line separating pooled estimate
        ax.axhline(y=-0.5, color='gray', linestyle='--', linewidth=1, alpha=0.5)

    # Add vertical line at null effect
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.7)

    # Formatting
    ax.set_yticks(y_positions)
    ax.set_yticklabels(study_labels)
    ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3, linestyle=':')

    # Adjust layout
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig


def funnel_plot(
    effects: np.ndarray,
    se: np.ndarray,
    pooled_effect: Optional[float] = None,
    title: str = "Funnel Plot",
    xlabel: str = "Effect Size",
    show_contours: bool = True,
    figsize: Tuple[int, int] = (10, 8),
    save_path: Optional[str] = None,
) -> plt.Figure:
    """
    Create publication-quality funnel plot for publication bias assessment.

    Args:
        effects: Effect sizes
        se: Standard errors
        pooled_effect: Pooled effect (default: use mean of effects)
        title: Plot title
        xlabel: X-axis label
        show_contours: Whether to show 95% and 99% confidence contours
        figsize: Figure size
        save_path: Path to save figure

    Returns:
        matplotlib Figure object
    """
    if pooled_effect is None:
        pooled_effect = np.mean(effects)

    fig, ax = plt.subplots(figsize=figsize)

    # Plot studies
    ax.scatter(
        effects,
        se,
        s=100,
        c='steelblue',
        alpha=0.6,
        edgecolors='black',
        linewidth=0.5
    )

    # Add contour lines for 95% and 99% CI
    if show_contours:
        se_range = np.linspace(0, np.max(se) * 1.1, 100)

        # 95% CI
        ci_95_low = pooled_effect - 1.96 * se_range
        ci_95_high = pooled_effect + 1.96 * se_range
        ax.plot(ci_95_low, se_range, 'k--', linewidth=1, alpha=0.5, label='95% CI')
        ax.plot(ci_95_high, se_range, 'k--', linewidth=1, alpha=0.5)

        # 99% CI
        ci_99_low = pooled_effect - 2.58 * se_range
        ci_99_high = pooled_effect + 2.58 * se_range
        ax.plot(ci_99_low, se_range, 'k:', linewidth=1, alpha=0.5, label='99% CI')
        ax.plot(ci_99_high, se_range, 'k:', linewidth=1, alpha=0.5)

    # Add pooled effect line
    ax.axvline(
        x=pooled_effect,
        color='darkred',
        linestyle='-',
        linewidth=2,
        label='Pooled Effect'
    )

    # Invert y-axis (precision increases upward)
    ax.invert_yaxis()

    # Formatting
    ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
    ax.set_ylabel('Standard Error', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right')
    ax.grid(alpha=0.3, linestyle=':')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig


def radial_plot(
    effects: np.ndarray,
    se: np.ndarray,
    study_labels: Optional[np.ndarray] = None,
    title: str = "Radial (Galbraith) Plot",
    figsize: Tuple[int, int] = (10, 8),
    save_path: Optional[str] = None,
) -> plt.Figure:
    """
    Create radial (Galbraith) plot for heterogeneity assessment.

    Args:
        effects: Effect sizes
        se: Standard errors
        study_labels: Optional study labels
        title: Plot title
        figsize: Figure size
        save_path: Path to save figure

    Returns:
        matplotlib Figure object
    """
    # Calculate transformed coordinates
    precision = 1 / se
    z_scores = effects / se

    fig, ax = plt.subplots(figsize=figsize)

    # Plot studies
    scatter = ax.scatter(
        precision,
        z_scores,
        s=100,
        c='steelblue',
        alpha=0.6,
        edgecolors='black',
        linewidth=0.5
    )

    # Add reference lines
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    ax.axhline(y=1.96, color='red', linestyle=':', linewidth=1, alpha=0.5)
    ax.axhline(y=-1.96, color='red', linestyle=':', linewidth=1, alpha=0.5)

    # Add labels if provided
    if study_labels is not None:
        for i, label in enumerate(study_labels):
            ax.annotate(
                label,
                (precision[i], z_scores[i]),
                xytext=(5, 5),
                textcoords='offset points',
                fontsize=8,
                alpha=0.7
            )

    # Formatting
    ax.set_xlabel('Precision (1/SE)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Standardized Effect (Effect/SE)', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.grid(alpha=0.3, linestyle=':')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig


def baujat_plot(
    effects: np.ndarray,
    se: np.ndarray,
    study_labels: Optional[np.ndarray] = None,
    title: str = "Baujat Plot",
    figsize: Tuple[int, int] = (10, 8),
    save_path: Optional[str] = None,
) -> plt.Figure:
    """
    Create Baujat plot for identifying influential studies.

    Args:
        effects: Effect sizes
        se: Standard errors
        study_labels: Optional study labels
        title: Plot title
        figsize: Figure size
        save_path: Path to save figure

    Returns:
        matplotlib Figure object
    """
    n_studies = len(effects)

    # Calculate pooled effect
    weights = 1 / (se ** 2)
    pooled_effect = np.sum(weights * effects) / np.sum(weights)

    # Calculate contribution to Q and influence
    contrib_to_q = weights * (effects - pooled_effect) ** 2

    # Calculate influence (change in pooled effect when study removed)
    influence = np.zeros(n_studies)
    for i in range(n_studies):
        # Leave-one-out pooled effect
        loo_weights = np.delete(weights, i)
        loo_effects = np.delete(effects, i)
        loo_pooled = np.sum(loo_weights * loo_effects) / np.sum(loo_weights)
        influence[i] = abs(pooled_effect - loo_pooled)

    fig, ax = plt.subplots(figsize=figsize)

    # Plot studies
    scatter = ax.scatter(
        contrib_to_q,
        influence,
        s=150,
        c='steelblue',
        alpha=0.6,
        edgecolors='black',
        linewidth=0.5
    )

    # Add labels if provided
    if study_labels is not None:
        for i, label in enumerate(study_labels):
            ax.annotate(
                label,
                (contrib_to_q[i], influence[i]),
                xytext=(5, 5),
                textcoords='offset points',
                fontsize=8,
                alpha=0.7
            )

    # Formatting
    ax.set_xlabel('Contribution to Overall Heterogeneity (Q)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Influence on Pooled Effect', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.grid(alpha=0.3, linestyle=':')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig


__all__ = [
    'forest_plot',
    'funnel_plot',
    'radial_plot',
    'baujat_plot',
]
