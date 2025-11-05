"""
Individual Participant Data (IPD) Meta-Analysis

Gold standard for meta-analysis using raw participant-level data.
Implements one-stage and two-stage approaches for IPD-MA.

Key Advantages over Aggregate Data MA:
- Prevents aggregation bias
- Allows investigation of individual-level moderators
- Better handling of continuous covariates
- Can assess interactions not reported in original studies
- More powerful for subgroup analyses
- Better handling of missing data

References:
- Riley et al. (2010). An alternative model for bivariate random-effects meta-analysis
  when the within-study correlations are unknown. Biostatistics, 11(1), 172-186.
- Debray et al. (2015). Individual participant data meta-analysis for a binary outcome.
  Statistics in Medicine, 34(9), 1555-1575.
- Burke et al. (2017). Meta-analysis using individual participant data: one-stage and
  two-stage approaches, and why they may differ. Statistics in Medicine, 36(5), 855-875.
- Cochrane Handbook Chapter 26 (2024). Individual participant data.

Latest advances (2024):
- Improved one-stage models with better convergence
- Guidance on when to use one-stage vs two-stage
- Handling of missing data in IPD-MA
- Software implementations (ipdmetan, IPDfromKM)
"""

from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
import pandas as pd
from scipy import stats
from dataclasses import dataclass
from enum import Enum
import warnings

from metapython.core.config import logger


class EffectType(Enum):
    """Type of effect measure for IPD-MA."""
    MEAN_DIFFERENCE = "mean_difference"
    LOG_ODDS_RATIO = "log_odds_ratio"
    LOG_HAZARD_RATIO = "log_hazard_ratio"
    RISK_DIFFERENCE = "risk_difference"


@dataclass
class IPDResult:
    """Results from IPD meta-analysis."""
    pooled_effect: float
    pooled_se: float
    ci_lower: float
    ci_upper: float
    tau2: Optional[float] = None  # Between-study heterogeneity
    i2: Optional[float] = None
    n_studies: int = 0
    n_participants: int = 0
    study_effects: Optional[Dict[str, float]] = None
    covariate_effects: Optional[Dict[str, float]] = None
    method: str = "IPD-MA"
    stage: str = "one-stage"  # "one-stage" or "two-stage"
    warnings: List[str] = None


class OneStageIPD:
    """
    One-stage IPD meta-analysis.

    Analyzes all participant data simultaneously in a mixed-effects model.
    Study is included as a random effect to account for clustering.

    Advantages:
    - More efficient use of information
    - Better for sparse data within studies
    - Allows borrowing of strength across studies
    - Natural framework for individual-level interactions

    Model:
        Y_ij = β0 + β1*Treatment_ij + β2*Covariate_ij +
               β3*Treatment_ij*Covariate_ij + u_j + ε_ij

    where:
        Y_ij = outcome for participant i in study j
        u_j ~ N(0, τ²) = random study effect
        ε_ij ~ N(0, σ²_j) = residual

    References:
    - Burke et al. (2017). Statistics in Medicine, 36(5), 855-875.
    - Debray et al. (2015). Statistics in Medicine, 34(9), 1555-1575.

    Example:
        >>> ipd_data = pd.DataFrame({
        ...     'study': [1, 1, 1, 2, 2, 2],
        ...     'treatment': [1, 1, 0, 1, 0, 0],
        ...     'outcome': [5.2, 4.8, 3.1, 6.0, 3.5, 3.8],
        ...     'age': [45, 50, 48, 52, 49, 47]
        ... })
        >>> model = OneStageIPD()
        >>> result = model.fit(ipd_data, outcome='outcome',
        ...                    treatment='treatment', study_id='study')
    """

    def __init__(
        self,
        effect_type: EffectType = EffectType.MEAN_DIFFERENCE,
        method: str = "REML"  # REML or ML
    ):
        """
        Initialize one-stage IPD meta-analysis.

        Args:
            effect_type: Type of outcome (continuous, binary, time-to-event)
            method: Estimation method (REML or ML)
        """
        self.effect_type = effect_type
        self.method = method

    def fit(
        self,
        data: pd.DataFrame,
        outcome: str,
        treatment: str,
        study_id: str,
        covariates: Optional[List[str]] = None,
        interactions: Optional[List[str]] = None,
        max_iter: int = 100,
        tol: float = 1e-6
    ) -> IPDResult:
        """
        Fit one-stage IPD meta-analysis.

        Args:
            data: DataFrame with IPD
            outcome: Outcome variable name
            treatment: Treatment indicator (0/1)
            study_id: Study identifier
            covariates: List of covariate names
            interactions: Covariates to interact with treatment
            max_iter: Maximum iterations
            tol: Convergence tolerance

        Returns:
            IPDResult with pooled estimates
        """
        # Validate inputs
        required_cols = [outcome, treatment, study_id]
        if not all(col in data.columns for col in required_cols):
            raise ValueError(f"Missing required columns: {required_cols}")

        n_participants = len(data)
        n_studies = data[study_id].nunique()
        studies = data[study_id].unique()

        logger.info(f"One-stage IPD-MA: {n_studies} studies, {n_participants} participants")

        # Prepare design matrix
        X_list = []
        X_list.append(np.ones(n_participants))  # Intercept
        X_list.append(data[treatment].values)  # Treatment

        covariate_names = []
        if covariates:
            for cov in covariates:
                X_list.append(data[cov].values)
                covariate_names.append(cov)

        if interactions:
            for interact_var in interactions:
                X_list.append(data[treatment].values * data[interact_var].values)
                covariate_names.append(f"{treatment}*{interact_var}")

        X = np.column_stack(X_list)
        y = data[outcome].values

        # Study indicators for random effects
        study_dummies = pd.get_dummies(data[study_id], prefix='study', drop_first=False)
        Z = study_dummies.values

        # Initialize parameters
        tau2 = 0.1  # Between-study variance
        sigma2 = np.var(y)  # Residual variance

        # Iteratively reweighted least squares (IGLS algorithm)
        for iteration in range(max_iter):
            tau2_old = tau2

            # Construct covariance matrix
            # V = Z * τ² * Z^T + σ² * I
            V = tau2 * (Z @ Z.T) + sigma2 * np.eye(n_participants)

            # Generalized least squares
            try:
                V_inv = np.linalg.inv(V)
            except np.linalg.LinAlgError:
                warnings.warn("Covariance matrix singular, using pseudo-inverse")
                V_inv = np.linalg.pinv(V)

            # Fixed effects estimate
            XtVX = X.T @ V_inv @ X
            XtVy = X.T @ V_inv @ y
            beta = np.linalg.solve(XtVX, XtVy)

            # Update variance components
            residuals = y - X @ beta

            # Random effects estimate
            u = tau2 * Z.T @ V_inv @ residuals

            # Update tau² using REML
            P = V_inv - V_inv @ X @ np.linalg.solve(XtVX, X.T @ V_inv)
            tau2_new = (residuals @ P @ residuals) / np.trace(P @ Z @ Z.T)
            tau2 = max(0, tau2_new)

            # Update σ²
            sigma2 = (residuals @ V_inv @ residuals - u @ u) / (n_participants - n_studies)

            # Check convergence
            if abs(tau2 - tau2_old) < tol:
                break

        # Compute standard errors
        cov_beta = np.linalg.inv(X.T @ V_inv @ X)
        se_beta = np.sqrt(np.diag(cov_beta))

        # Treatment effect (second coefficient)
        treatment_effect = beta[1]
        treatment_se = se_beta[1]
        ci = (
            treatment_effect - 1.96 * treatment_se,
            treatment_effect + 1.96 * treatment_se
        )

        # I² statistic
        Q = residuals @ P @ residuals
        df = n_studies - 1
        if Q > df:
            i2 = 100 * (Q - df) / Q
        else:
            i2 = 0

        # Study-specific effects (for two-stage comparison)
        study_effects = {}
        for study in studies:
            study_mask = data[study_id] == study
            study_data = data[study_mask]
            study_residual = residuals[study_mask]
            study_effects[str(study)] = np.mean(study_residual)

        # Covariate effects
        covariate_effects = {}
        if covariates or interactions:
            for i, name in enumerate(covariate_names, start=2):
                covariate_effects[name] = {
                    'effect': beta[i],
                    'se': se_beta[i],
                    'ci': (beta[i] - 1.96 * se_beta[i], beta[i] + 1.96 * se_beta[i])
                }

        return IPDResult(
            pooled_effect=treatment_effect,
            pooled_se=treatment_se,
            ci_lower=ci[0],
            ci_upper=ci[1],
            tau2=tau2,
            i2=i2,
            n_studies=n_studies,
            n_participants=n_participants,
            study_effects=study_effects,
            covariate_effects=covariate_effects,
            method=f"One-stage ({self.method})",
            stage="one-stage"
        )


class TwoStageIPD:
    """
    Two-stage IPD meta-analysis.

    Stage 1: Analyze each study separately to obtain effect estimates
    Stage 2: Pool study-specific estimates using standard meta-analysis

    Advantages:
    - Respects original study designs
    - Easier to implement
    - More familiar to researchers
    - Can use different models per study

    Disadvantages:
    - Less efficient than one-stage
    - Cannot estimate interactions if not in original studies
    - Requires sufficient data per study

    Reference:
    - Burke et al. (2017). Statistics in Medicine, 36(5), 855-875.

    Example:
        >>> model = TwoStageIPD()
        >>> result = model.fit(ipd_data, outcome='outcome',
        ...                    treatment='treatment', study_id='study')
    """

    def __init__(
        self,
        method: str = "DL"  # DL, REML, PM, ML
    ):
        """
        Initialize two-stage IPD meta-analysis.

        Args:
            method: Pooling method for stage 2
        """
        self.method = method

    def fit(
        self,
        data: pd.DataFrame,
        outcome: str,
        treatment: str,
        study_id: str,
        covariates: Optional[List[str]] = None,
        min_n_per_study: int = 5
    ) -> IPDResult:
        """
        Fit two-stage IPD meta-analysis.

        Args:
            data: DataFrame with IPD
            outcome: Outcome variable name
            treatment: Treatment indicator
            study_id: Study identifier
            covariates: Covariates to adjust for
            min_n_per_study: Minimum participants per study

        Returns:
            IPDResult with pooled estimates
        """
        studies = data[study_id].unique()
        n_studies = len(studies)
        n_participants = len(data)

        logger.info(f"Two-stage IPD-MA: {n_studies} studies, {n_participants} participants")

        # Stage 1: Analyze each study
        study_results = []
        study_effects_dict = {}

        for study in studies:
            study_data = data[data[study_id] == study]

            if len(study_data) < min_n_per_study:
                logger.warning(f"Study {study} has < {min_n_per_study} participants, skipping")
                continue

            # Fit model within study
            try:
                X_study = [np.ones(len(study_data)), study_data[treatment].values]
                if covariates:
                    for cov in covariates:
                        X_study.append(study_data[cov].values)

                X_study = np.column_stack(X_study)
                y_study = study_data[outcome].values

                # Ordinary least squares
                beta_study = np.linalg.lstsq(X_study, y_study, rcond=None)[0]
                residuals = y_study - X_study @ beta_study
                mse = np.sum(residuals**2) / (len(study_data) - X_study.shape[1])
                cov_beta = mse * np.linalg.inv(X_study.T @ X_study)
                se_study = np.sqrt(np.diag(cov_beta))

                # Treatment effect is second coefficient
                effect = beta_study[1]
                se = se_study[1]
                variance = se**2

                study_results.append({
                    'study': study,
                    'effect': effect,
                    'se': se,
                    'variance': variance,
                    'n': len(study_data)
                })

                study_effects_dict[str(study)] = effect

            except Exception as e:
                logger.error(f"Error analyzing study {study}: {e}")
                continue

        if len(study_results) < 2:
            raise ValueError("Need at least 2 studies for meta-analysis")

        # Stage 2: Pool estimates
        effects = np.array([r['effect'] for r in study_results])
        variances = np.array([r['variance'] for r in study_results])

        pooled_result = self._pool_estimates(effects, variances)

        return IPDResult(
            pooled_effect=pooled_result['effect'],
            pooled_se=pooled_result['se'],
            ci_lower=pooled_result['ci'][0],
            ci_upper=pooled_result['ci'][1],
            tau2=pooled_result.get('tau2'),
            i2=pooled_result.get('i2'),
            n_studies=len(study_results),
            n_participants=n_participants,
            study_effects=study_effects_dict,
            method=f"Two-stage ({self.method})",
            stage="two-stage"
        )

    def _pool_estimates(
        self,
        effects: np.ndarray,
        variances: np.ndarray
    ) -> Dict[str, Any]:
        """Pool stage 1 estimates using random-effects meta-analysis."""
        weights_fe = 1 / variances
        effect_fe = np.sum(weights_fe * effects) / np.sum(weights_fe)

        # Heterogeneity
        Q = np.sum(weights_fe * (effects - effect_fe)**2)
        df = len(effects) - 1

        if self.method == "DL":
            # DerSimonian-Laird
            C = np.sum(weights_fe) - np.sum(weights_fe**2) / np.sum(weights_fe)
            tau2 = max(0, (Q - df) / C)

        elif self.method == "REML":
            # REML estimation of tau²
            def reml_objective(tau2):
                w = 1 / (variances + tau2)
                return -0.5 * (
                    np.sum(np.log(variances + tau2)) +
                    np.log(np.sum(w)) +
                    np.sum(w * (effects - np.sum(w * effects) / np.sum(w))**2)
                )

            from scipy.optimize import minimize_scalar
            result = minimize_scalar(lambda t: -reml_objective(t), bounds=(0, 10), method='bounded')
            tau2 = result.x

        else:
            tau2 = 0

        # Random-effects pooling
        weights_re = 1 / (variances + tau2)
        effect_re = np.sum(weights_re * effects) / np.sum(weights_re)
        se_re = np.sqrt(1 / np.sum(weights_re))
        ci_re = (effect_re - 1.96 * se_re, effect_re + 1.96 * se_re)

        # I²
        if Q > df:
            i2 = 100 * (Q - df) / Q
        else:
            i2 = 0

        return {
            'effect': effect_re,
            'se': se_re,
            'ci': ci_re,
            'tau2': tau2,
            'i2': i2,
            'Q': Q
        }


def compare_one_vs_two_stage(
    data: pd.DataFrame,
    outcome: str,
    treatment: str,
    study_id: str,
    **kwargs
) -> Dict[str, IPDResult]:
    """
    Compare one-stage and two-stage IPD meta-analysis.

    Helps understand sensitivity of results to modeling approach.

    Args:
        data: IPD dataframe
        outcome: Outcome variable
        treatment: Treatment indicator
        study_id: Study identifier
        **kwargs: Additional arguments for both models

    Returns:
        Dictionary with results from both approaches

    Example:
        >>> comparison = compare_one_vs_two_stage(
        ...     ipd_data, 'outcome', 'treatment', 'study'
        ... )
        >>> print(f"One-stage: {comparison['one_stage'].pooled_effect:.3f}")
        >>> print(f"Two-stage: {comparison['two_stage'].pooled_effect:.3f}")
    """
    # One-stage
    one_stage_model = OneStageIPD()
    one_stage_result = one_stage_model.fit(
        data, outcome, treatment, study_id, **kwargs
    )

    # Two-stage
    two_stage_model = TwoStageIPD()
    two_stage_result = two_stage_model.fit(
        data, outcome, treatment, study_id, **kwargs
    )

    # Compute difference
    diff = abs(one_stage_result.pooled_effect - two_stage_result.pooled_effect)
    relative_diff = 100 * diff / abs(two_stage_result.pooled_effect) if two_stage_result.pooled_effect != 0 else 0

    logger.info(f"One-stage vs Two-stage difference: {diff:.4f} ({relative_diff:.1f}%)")

    return {
        'one_stage': one_stage_result,
        'two_stage': two_stage_result,
        'absolute_difference': diff,
        'relative_difference_percent': relative_diff
    }


__all__ = [
    'EffectType',
    'IPDResult',
    'OneStageIPD',
    'TwoStageIPD',
    'compare_one_vs_two_stage'
]
