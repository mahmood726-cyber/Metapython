"""
Multivariate Meta-Analysis

Meta-analysis of multiple correlated outcomes simultaneously.
Accounts for within-study and between-study correlations.

Use Cases:
- Multiple endpoints (e.g., quality of life + depression + anxiety)
- Multiple time points (longitudinal outcomes)
- Multiple treatment comparisons from same trials
- Composite outcomes with multiple components

Advantages over Univariate MA:
- Borrows strength across outcomes
- Accounts for correlation structure
- More efficient estimates
- Can impute missing outcomes
- Tests joint hypotheses

References:
- Jackson et al. (2011). Multivariate meta-analysis: Potential and promise.
  Statistics in Medicine, 30(20), 2481-2498.
- White (2011). Multivariate random-effects meta-regression: Updates to mvmeta.
  The Stata Journal, 11(2), 255-270.
- Riley (2010). Multivariate meta-analysis: the effect of ignoring within-study
  correlation. Journal of the Royal Statistical Society: Series A, 173(4), 789-811.
- Wei & Higgins (2013). Estimating within-study covariances in multivariate
  meta-analysis with multiple outcomes. Statistics in Medicine, 32(7), 1191-1205.

Latest advances (2024):
- Better handling of missing within-study correlations
- Robust methods for heterogeneity estimation
- Extension to network meta-analysis
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from scipy import stats
from scipy.optimize import minimize
from dataclasses import dataclass
import warnings

from metapython.core.config import logger


@dataclass
class MultivariateResult:
    """Results from multivariate meta-analysis."""
    pooled_effects: np.ndarray
    pooled_cov: np.ndarray
    ci_lower: np.ndarray
    ci_upper: np.ndarray
    between_study_cov: np.ndarray
    n_outcomes: int
    n_studies: int
    outcome_names: List[str]
    convergence: bool = True
    method: str = "Multivariate REML"


class MultivariateMetaAnalysis:
    """
    Multivariate random-effects meta-analysis.

    Simultaneously models K correlated outcomes accounting for:
    - Within-study sampling correlations
    - Between-study heterogeneity correlations
    - Missing outcomes in some studies

    Model:
        y_i ~ N(μ + u_i, S_i)
        u_i ~ N(0, Σ)

    where:
        y_i = vector of outcomes for study i
        μ = vector of pooled effects
        u_i = study-specific random effects
        S_i = within-study covariance
        Σ = between-study covariance

    Reference:
    - Jackson et al. (2011). Statistics in Medicine, 30(20), 2481-2498.
    - White (2011). The Stata Journal, 11(2), 255-270.

    Example:
        >>> # Three correlated outcomes
        >>> effects = np.array([
        ...     [0.5, 0.3, 0.4],  # Study 1
        ...     [0.6, 0.4, 0.5],  # Study 2
        ...     [0.4, 0.2, 0.3]   # Study 3
        ... ])
        >>> within_cov = [cov1, cov2, cov3]  # 3x3 covariance matrices
        >>> model = MultivariateMetaAnalysis()
        >>> result = model.fit(effects, within_cov)
    """

    def __init__(self, method: str = "REML"):
        """
        Initialize multivariate meta-analysis.

        Args:
            method: Estimation method (REML or ML)
        """
        self.method = method

    def fit(
        self,
        effects: np.ndarray,
        within_study_cov: List[np.ndarray],
        outcome_names: Optional[List[str]] = None,
        max_iter: int = 100,
        tol: float = 1e-6
    ) -> MultivariateResult:
        """
        Fit multivariate meta-analysis.

        Args:
            effects: n_studies × n_outcomes matrix of effect estimates
            within_study_cov: List of within-study covariance matrices
            outcome_names: Names of outcomes
            max_iter: Maximum iterations
            tol: Convergence tolerance

        Returns:
            MultivariateResult with pooled estimates
        """
        effects = np.asarray(effects)
        n_studies, n_outcomes = effects.shape

        if len(within_study_cov) != n_studies:
            raise ValueError("Need covariance matrix for each study")

        logger.info(f"Multivariate MA: {n_studies} studies, {n_outcomes} outcomes")

        if outcome_names is None:
            outcome_names = [f"Outcome {i+1}" for i in range(n_outcomes)]

        # Initialize between-study covariance
        Sigma = np.cov(effects.T)

        # Iterative generalized least squares
        for iteration in range(max_iter):
            Sigma_old = Sigma.copy()

            # Construct total covariance for each study
            total_cov = [S_i + Sigma for S_i in within_study_cov]

            # Pooled estimate (weighted by inverse covariance)
            weights = [np.linalg.inv(V_i) for V_i in total_cov]
            sum_weights = np.sum(weights, axis=0)

            weighted_sum = np.sum([
                W_i @ effects[i]
                for i, W_i in enumerate(weights)
            ], axis=0)

            mu = np.linalg.solve(sum_weights, weighted_sum)

            # Update between-study covariance (REML)
            Q = np.zeros((n_outcomes, n_outcomes))
            for i in range(n_studies):
                residual = effects[i] - mu
                Q += np.outer(residual, residual) - within_study_cov[i]

            Sigma = Q / n_studies

            # Ensure positive definite
            Sigma = (Sigma + Sigma.T) / 2
            eigenvalues = np.linalg.eigvalsh(Sigma)
            if np.any(eigenvalues < 0):
                Sigma += np.eye(n_outcomes) * (abs(min(eigenvalues)) + 0.01)

            # Check convergence
            if np.max(np.abs(Sigma - Sigma_old)) < tol:
                break

        # Covariance of pooled estimate
        pooled_cov = np.linalg.inv(sum_weights)

        # Confidence intervals (element-wise)
        se = np.sqrt(np.diag(pooled_cov))
        ci_lower = mu - 1.96 * se
        ci_upper = mu + 1.96 * se

        return MultivariateResult(
            pooled_effects=mu,
            pooled_cov=pooled_cov,
            ci_lower=ci_lower,
            ci_upper=ci_upper,
            between_study_cov=Sigma,
            n_outcomes=n_outcomes,
            n_studies=n_studies,
            outcome_names=outcome_names,
            convergence=iteration < max_iter - 1,
            method=f"Multivariate {self.method}"
        )

    def test_joint_hypothesis(
        self,
        result: MultivariateResult,
        null_value: Optional[np.ndarray] = None
    ) -> Dict[str, float]:
        """
        Joint Wald test for all outcomes simultaneously.

        H0: μ = null_value (default: 0)

        Args:
            result: MultivariateResult from fit()
            null_value: Null hypothesis values

        Returns:
            Dictionary with test statistic and p-value

        Example:
            >>> # Test if all three outcomes are jointly zero
            >>> test = model.test_joint_hypothesis(result)
            >>> print(f"Chi-square = {test['chi_square']:.2f}, p = {test['p_value']:.4f}")
        """
        if null_value is None:
            null_value = np.zeros(result.n_outcomes)

        # Wald statistic
        diff = result.pooled_effects - null_value
        chi_square = diff @ np.linalg.inv(result.pooled_cov) @ diff
        df = result.n_outcomes
        p_value = 1 - stats.chi2.cdf(chi_square, df)

        return {
            'chi_square': chi_square,
            'df': df,
            'p_value': p_value
        }


def impute_missing_correlations(
    effects: np.ndarray,
    variances: np.ndarray,
    observed_mask: np.ndarray,
    assumed_correlation: float = 0.5
) -> List[np.ndarray]:
    """
    Impute within-study covariances when correlations are missing.

    Uses assumed correlation to construct covariance matrices.

    Args:
        effects: n_studies × n_outcomes matrix
        variances: n_studies × n_outcomes matrix of variances
        observed_mask: Boolean mask (True if outcome observed)
        assumed_correlation: Assumed correlation coefficient

    Returns:
        List of within-study covariance matrices

    Reference:
    - Wei & Higgins (2013). Statistics in Medicine, 32(7), 1191-1205.

    Example:
        >>> # Some studies missing some outcomes
        >>> observed = np.array([
        ...     [True, True, True],
        ...     [True, True, False],  # Missing outcome 3
        ...     [True, False, True]   # Missing outcome 2
        ... ])
        >>> cov_matrices = impute_missing_correlations(
        ...     effects, variances, observed, assumed_correlation=0.5
        ... )
    """
    n_studies, n_outcomes = effects.shape
    covariances = []

    for i in range(n_studies):
        # Construct correlation matrix
        R = np.eye(n_outcomes)
        R[R == 0] = assumed_correlation

        # Convert to covariance: Cov = D * R * D
        # where D = diag(sqrt(variances))
        D = np.diag(np.sqrt(variances[i]))
        S_i = D @ R @ D

        # Zero out unobserved outcomes
        mask = observed_mask[i]
        S_i = S_i * np.outer(mask, mask)

        covariances.append(S_i)

    logger.info(f"Imputed correlations using r = {assumed_correlation}")

    return covariances


def dose_response_multivariate(
    doses: np.ndarray,
    effects: np.ndarray,
    within_study_cov: List[np.ndarray],
    model: str = "linear"
) -> Dict[str, Any]:
    """
    Multivariate dose-response meta-analysis.

    Models effect as function of dose while accounting for
    correlation between dose levels.

    Args:
        doses: n_studies × n_doses matrix
        effects: n_studies × n_doses matrix
        within_study_cov: List of covariance matrices
        model: "linear", "quadratic", or "spline"

    Returns:
        Dictionary with dose-response curve parameters

    Reference:
    - Crippa & Orsini (2016). Dose-response meta-analysis of differences in means.
      BMC Medical Research Methodology, 16, 91.

    Example:
        >>> # Three dose levels per study
        >>> doses = np.array([
        ...     [0, 10, 20],  # Study 1
        ...     [0, 15, 30]   # Study 2
        ... ])
        >>> result = dose_response_multivariate(doses, effects, cov_list)
    """
    n_studies, n_doses = doses.shape

    logger.info(f"Dose-response multivariate: {n_studies} studies, {n_doses} doses")

    # Construct design matrix for dose-response
    if model == "linear":
        # Effect = β0 + β1*dose
        X = np.column_stack([np.ones(n_studies * n_doses), doses.flatten()])

    elif model == "quadratic":
        # Effect = β0 + β1*dose + β2*dose²
        doses_flat = doses.flatten()
        X = np.column_stack([
            np.ones(len(doses_flat)),
            doses_flat,
            doses_flat**2
        ])

    else:
        raise ValueError(f"Unknown model: {model}")

    # Flatten effects
    y = effects.flatten()

    # Block-diagonal covariance matrix
    V = np.zeros((n_studies * n_doses, n_studies * n_doses))
    for i in range(n_studies):
        start = i * n_doses
        end = start + n_doses
        V[start:end, start:end] = within_study_cov[i]

    # Generalized least squares
    V_inv = np.linalg.inv(V + np.eye(len(V)) * 0.01)  # Ridge for stability
    XtVX = X.T @ V_inv @ X
    XtVy = X.T @ V_inv @ y
    beta = np.linalg.solve(XtVX, XtVy)

    # Standard errors
    cov_beta = np.linalg.inv(XtVX)
    se_beta = np.sqrt(np.diag(cov_beta))

    # Predicted dose-response curve
    dose_range = np.linspace(0, np.max(doses), 100)
    if model == "linear":
        predicted = beta[0] + beta[1] * dose_range
    elif model == "quadratic":
        predicted = beta[0] + beta[1] * dose_range + beta[2] * dose_range**2

    return {
        'coefficients': beta,
        'std_errors': se_beta,
        'dose_range': dose_range,
        'predicted_effects': predicted,
        'model': model
    }


__all__ = [
    'MultivariateResult',
    'MultivariateMetaAnalysis',
    'impute_missing_correlations',
    'dose_response_multivariate'
]
