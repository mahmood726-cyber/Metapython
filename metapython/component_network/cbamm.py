"""
Component-Based Aggregate Meta-Analysis Method (CBAMM)

Advanced network meta-analysis decomposing complex interventions into components.
Inspired by mahmood726-cyber/HFN786 repository.

Key Innovation:
- Complex interventions have multiple components
- Different trials combine components differently
- CBAMM separates effects of individual components
- Enables optimal combination selection

Example:
- Exercise intervention: (Aerobic + Strength + Flexibility)
- Trial A: Aerobic + Strength
- Trial B: Aerobic + Flexibility
- Trial C: All three components
- CBAMM estimates individual component effects

Applications:
- Behavioral interventions
- Multi-component pharmacological treatments
- Complex public health interventions
- Combination therapies

References:
- Welton NJ, et al. (2013). Evidence Synthesis for Decision Making: A Component Network
  Meta-analysis. Medical Decision Making, 33(5), 597-610.
- Freeman SC, et al. (2018). Component network meta-analysis identifies the most effective
  components of psychological preparation for adults undergoing surgery under general
  anaesthesia. Journal of Clinical Epidemiology, 98, 111-122.
- Mills EJ, et al. (2012). Demystifying trial networks and network meta-analysis.
  BMJ, 344, e2914.

Latest advances (2024):
- Integration with IPD for component-level interactions
- Bayesian hierarchical modeling of component effects
- Additive vs synergistic component models
"""

from typing import Dict, List, Optional, Tuple, Any, Set
import numpy as np
from scipy import stats, optimize
from dataclasses import dataclass
import warnings
from itertools import combinations

from metapython.core.config import logger


@dataclass
class ComponentMAResult:
    """Results from component-based meta-analysis."""
    component_effects: Dict[str, float]
    component_se: Dict[str, float]
    component_ci: Dict[str, Tuple[float, float]]
    interaction_effects: Optional[Dict[Tuple[str, str], float]] = None
    predicted_effects: Optional[Dict[frozenset, float]] = None
    model_fit: Optional[Dict[str, float]] = None
    best_combination: Optional[List[str]] = None


class ComponentNetworkMA:
    """
    Component-Based Network Meta-Analysis (CBAMM).

    Decomposes complex interventions into components and estimates
    separate effect for each component.

    Additive Model:
        Effect(A+B) = Effect(A) + Effect(B)

    Interaction Model:
        Effect(A+B) = Effect(A) + Effect(B) + Interaction(A,B)

    Example:
        >>> # Define component structure
        >>> # Trial 1: Aerobic + Strength training
        >>> # Trial 2: Aerobic + Flexibility
        >>> # Trial 3: Strength + Flexibility
        >>> # Trial 4: All three
        >>>
        >>> components_per_study = [
        ...     {'Aerobic', 'Strength'},
        ...     {'Aerobic', 'Flexibility'},
        ...     {'Strength', 'Flexibility'},
        ...     {'Aerobic', 'Strength', 'Flexibility'}
        ... ]
        >>>
        >>> effects = np.array([0.5, 0.4, 0.3, 0.7])
        >>> variances = np.array([0.01, 0.01, 0.01, 0.01])
        >>>
        >>> cbamm = ComponentNetworkMA()
        >>> result = cbamm.fit(effects, variances, components_per_study)
        >>>
        >>> print("Component effects:")
        >>> for comp, effect in result.component_effects.items():
        ...     print(f"  {comp}: {effect:.3f}")
    """

    def __init__(
        self,
        model: str = "additive",  # "additive" or "interaction"
        baseline: Optional[str] = "control"
    ):
        """
        Initialize component network meta-analysis.

        Args:
            model: "additive" (components add) or "interaction" (synergy/antagonism)
            baseline: Reference group (usually control/placebo)
        """
        self.model = model
        self.baseline = baseline

    def fit(
        self,
        effects: np.ndarray,
        variances: np.ndarray,
        component_sets: List[Set[str]],
        study_labels: Optional[List[str]] = None
    ) -> ComponentMAResult:
        """
        Fit component network meta-analysis.

        Args:
            effects: Study effect estimates
            variances: Within-study variances
            component_sets: List of sets, each containing component names for that study
            study_labels: Optional study names

        Returns:
            ComponentMAResult with component-specific effects
        """
        effects = np.asarray(effects)
        variances = np.asarray(variances)
        n_studies = len(effects)

        if len(component_sets) != n_studies:
            raise ValueError("Need component set for each study")

        logger.info(f"Component-based MA: {n_studies} studies")

        # Identify all unique components
        all_components = sorted(set.union(*component_sets))
        n_components = len(all_components)

        logger.info(f"Identified {n_components} components: {', '.join(all_components)}")

        # Create design matrix
        # Each row = study, each column = component
        # X[i,j] = 1 if study i includes component j, 0 otherwise
        X = np.zeros((n_studies, n_components))

        for i, comp_set in enumerate(component_sets):
            for j, comp in enumerate(all_components):
                if comp in comp_set:
                    X[i, j] = 1

        # Weighted least squares
        # Weights = 1 / variance
        W = np.diag(1 / variances)

        if self.model == "additive":
            # Additive model: Effect = sum of component effects
            # Solve: (X'WX)β = X'Wy

            XtWX = X.T @ W @ X
            XtWy = X.T @ W @ effects

            # Add small ridge for stability
            beta = np.linalg.solve(XtWX + np.eye(n_components) * 0.001, XtWy)

            # Standard errors
            cov_beta = np.linalg.inv(XtWX)
            se_beta = np.sqrt(np.diag(cov_beta))

            # Package results
            component_effects = {comp: beta[i] for i, comp in enumerate(all_components)}
            component_se = {comp: se_beta[i] for i, comp in enumerate(all_components)}
            component_ci = {
                comp: (beta[i] - 1.96 * se_beta[i], beta[i] + 1.96 * se_beta[i])
                for i, comp in enumerate(all_components)
            }

            # Predicted effects for each combination
            predicted = {}
            for comp_set in component_sets:
                predicted[frozenset(comp_set)] = sum(
                    component_effects[c] for c in comp_set
                )

            # Model fit
            fitted_values = X @ beta
            residuals = effects - fitted_values
            sse = np.sum(W @ residuals @ residuals)
            model_fit = {
                'sse': sse,
                'rmse': np.sqrt(sse / n_studies),
                'r_squared': 1 - sse / np.sum(W @ (effects - np.mean(effects))**2)
            }

            return ComponentMAResult(
                component_effects=component_effects,
                component_se=component_se,
                component_ci=component_ci,
                predicted_effects=predicted,
                model_fit=model_fit,
                best_combination=self._find_best_combination(component_effects)
            )

        elif self.model == "interaction":
            # Interaction model: Include pairwise interactions
            # Effect = sum(components) + sum(interactions)

            # Add interaction terms to design matrix
            interactions = list(combinations(all_components, 2))
            n_interactions = len(interactions)

            X_full = np.zeros((n_studies, n_components + n_interactions))
            X_full[:, :n_components] = X

            # Interaction columns: product of component indicators
            for k, (comp1, comp2) in enumerate(interactions):
                idx1 = all_components.index(comp1)
                idx2 = all_components.index(comp2)
                X_full[:, n_components + k] = X[:, idx1] * X[:, idx2]

            # Fit with interactions
            XtWX = X_full.T @ W @ X_full
            XtWy = X_full.T @ W @ effects

            beta_full = np.linalg.solve(
                XtWX + np.eye(n_components + n_interactions) * 0.001,
                XtWy
            )

            cov_beta = np.linalg.inv(XtWX)
            se_beta = np.sqrt(np.diag(cov_beta))

            # Extract component and interaction effects
            component_effects = {
                comp: beta_full[i]
                for i, comp in enumerate(all_components)
            }
            component_se = {
                comp: se_beta[i]
                for i, comp in enumerate(all_components)
            }
            component_ci = {
                comp: (
                    beta_full[i] - 1.96 * se_beta[i],
                    beta_full[i] + 1.96 * se_beta[i]
                )
                for i, comp in enumerate(all_components)
            }

            interaction_effects = {
                (comp1, comp2): beta_full[n_components + k]
                for k, (comp1, comp2) in enumerate(interactions)
            }

            # Predicted effects
            predicted = {}
            for comp_set in component_sets:
                comp_list = list(comp_set)
                pred = sum(component_effects[c] for c in comp_list)

                # Add interactions
                for comp1, comp2 in combinations(comp_list, 2):
                    if (comp1, comp2) in interaction_effects:
                        pred += interaction_effects[(comp1, comp2)]
                    elif (comp2, comp1) in interaction_effects:
                        pred += interaction_effects[(comp2, comp1)]

                predicted[frozenset(comp_set)] = pred

            # Model fit
            fitted_values = X_full @ beta_full
            residuals = effects - fitted_values
            sse = np.sum(W @ residuals @ residuals)
            model_fit = {
                'sse': sse,
                'rmse': np.sqrt(sse / n_studies),
                'r_squared': 1 - sse / np.sum(W @ (effects - np.mean(effects))**2)
            }

            return ComponentMAResult(
                component_effects=component_effects,
                component_se=component_se,
                component_ci=component_ci,
                interaction_effects=interaction_effects,
                predicted_effects=predicted,
                model_fit=model_fit,
                best_combination=self._find_best_combination(component_effects)
            )

        else:
            raise ValueError(f"Unknown model: {self.model}")

    def _find_best_combination(
        self,
        component_effects: Dict[str, float]
    ) -> List[str]:
        """
        Find best combination of components (all positive effects).

        Args:
            component_effects: Dictionary of component effects

        Returns:
            List of components to include
        """
        # Simple heuristic: include all components with positive effects
        best_combo = [
            comp for comp, effect in component_effects.items()
            if effect > 0
        ]

        return sorted(best_combo)

    def predict_combination(
        self,
        component_effects: Dict[str, float],
        components: Set[str],
        interaction_effects: Optional[Dict[Tuple[str, str], float]] = None
    ) -> float:
        """
        Predict effect of a new combination not in the data.

        Args:
            component_effects: Component main effects
            components: Set of components to combine
            interaction_effects: Optional interaction effects

        Returns:
            Predicted effect

        Example:
            >>> # Predict effect of Aerobic + Strength + Flexibility + Diet
            >>> # Even if this exact combination wasn't in the trials
            >>> pred = cbamm.predict_combination(
            ...     result.component_effects,
            ...     {'Aerobic', 'Strength', 'Flexibility', 'Diet'},
            ...     result.interaction_effects
            ... )
        """
        # Main effects
        predicted = sum(component_effects.get(c, 0) for c in components)

        # Interaction effects (if available)
        if interaction_effects:
            comp_list = list(components)
            for comp1, comp2 in combinations(comp_list, 2):
                if (comp1, comp2) in interaction_effects:
                    predicted += interaction_effects[(comp1, comp2)]
                elif (comp2, comp1) in interaction_effects:
                    predicted += interaction_effects[(comp2, comp1)]

        return predicted


def component_ranking(
    result: ComponentMAResult,
    criterion: str = "effect_size"
) -> List[Tuple[str, float]]:
    """
    Rank components by importance.

    Args:
        result: ComponentMAResult from fit()
        criterion: "effect_size", "precision", or "benefit_risk"

    Returns:
        List of (component, score) tuples, sorted by importance

    Example:
        >>> ranking = component_ranking(result, criterion="effect_size")
        >>> print("Most important components:")
        >>> for comp, score in ranking[:3]:
        ...     print(f"  {comp}: {score:.3f}")
    """
    if criterion == "effect_size":
        # Rank by absolute effect size
        scores = {
            comp: abs(effect)
            for comp, effect in result.component_effects.items()
        }

    elif criterion == "precision":
        # Rank by precision (1/SE) - more precise = more reliable
        scores = {
            comp: 1 / result.component_se[comp]
            for comp in result.component_effects.keys()
        }

    elif criterion == "benefit_risk":
        # Rank by effect size / SE (like z-score)
        scores = {
            comp: result.component_effects[comp] / result.component_se[comp]
            for comp in result.component_effects.keys()
        }

    else:
        raise ValueError(f"Unknown criterion: {criterion}")

    # Sort descending
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return ranked


__all__ = [
    'ComponentMAResult',
    'ComponentNetworkMA',
    'component_ranking'
]
