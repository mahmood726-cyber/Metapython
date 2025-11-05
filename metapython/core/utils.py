"""
Core utility functions for meta-analysis calculations.

This module contains shared mathematical and statistical utility functions
used throughout the MetaPython package.
"""

import inspect
import pathlib
from typing import Tuple, Optional, List, Callable, Any
import numpy as np
from scipy.stats import norm, t

from metapython.core.models import InsufficientDataError, SecurityError


# ===================================================================
# VALIDATION UTILITIES
# ===================================================================

def validate_inputs(func: Callable) -> Callable:
    """
    Enhanced decorator for comprehensive input validation.

    Validates common parameters like effects and variances for:
    - Type correctness (array-like)
    - No NaN or infinite values
    - Positive variances
    - Matching array lengths
    - Minimum number of studies

    Args:
        func: Function to wrap with validation

    Returns:
        Wrapped function with input validation
    """

    def wrapper(*args, **kwargs):
        # Get the function signature to identify parameters
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Validate effects parameter
        if 'effects' in bound_args.arguments:
            effects = bound_args.arguments['effects']
            if not isinstance(effects, np.ndarray):
                if isinstance(effects, (list, tuple)):
                    effects = np.array(effects)
                    bound_args.arguments['effects'] = effects
                else:
                    raise TypeError("Effects must be array-like")

            if np.any(np.isnan(effects)) or np.any(np.isinf(effects)):
                raise ValueError("Effects cannot contain NaN or infinite values")

        # Validate variances parameter
        if 'variances' in bound_args.arguments:
            variances = bound_args.arguments['variances']
            if not isinstance(variances, np.ndarray):
                if isinstance(variances, (list, tuple)):
                    variances = np.array(variances)
                    bound_args.arguments['variances'] = variances
                else:
                    raise TypeError("Variances must be array-like")

            if np.any(variances <= 0):
                raise ValueError("Variances must be positive")

            if np.any(np.isnan(variances)) or np.any(np.isinf(variances)):
                raise ValueError("Variances cannot contain NaN or infinite values")

        # Validate standard errors parameter
        if 'se' in bound_args.arguments:
            se = bound_args.arguments['se']
            if not isinstance(se, np.ndarray):
                if isinstance(se, (list, tuple)):
                    se = np.array(se)
                    bound_args.arguments['se'] = se
                else:
                    raise TypeError("Standard errors must be array-like")

            if np.any(se <= 0):
                raise ValueError("Standard errors must be positive")

            if np.any(np.isnan(se)) or np.any(np.isinf(se)):
                raise ValueError("Standard errors cannot contain NaN or infinite values")

        # Check array lengths match
        if 'effects' in bound_args.arguments and 'variances' in bound_args.arguments:
            effects = bound_args.arguments['effects']
            variances = bound_args.arguments['variances']
            if len(effects) != len(variances):
                raise ValueError("Effects and variances must have the same length")

        if 'effects' in bound_args.arguments and 'se' in bound_args.arguments:
            effects = bound_args.arguments['effects']
            se = bound_args.arguments['se']
            if len(effects) != len(se):
                raise ValueError("Effects and standard errors must have the same length")

        # Minimum studies check
        if 'effects' in bound_args.arguments:
            effects = bound_args.arguments['effects']
            if len(effects) < 2:
                raise InsufficientDataError("At least 2 studies required for meta-analysis")

        return func(*bound_args.args, **bound_args.kwargs)

    return wrapper


def validate_file_path(
    file_path: str,
    base_dir: Optional[str] = None,
    max_size_mb: float = 100.0,
    allowed_extensions: Optional[List[str]] = None
) -> str:
    """
    Validate and sanitize file path with security checks.

    Prevents path traversal attacks and validates file characteristics.

    Args:
        file_path: Path to validate
        base_dir: Base directory to restrict access to
        max_size_mb: Maximum allowed file size in megabytes
        allowed_extensions: List of allowed file extensions (e.g., ['.csv', '.xlsx'])

    Returns:
        Resolved absolute path as string

    Raises:
        SecurityError: If path validation fails
        FileNotFoundError: If file doesn't exist
        ValueError: If file exceeds size limit or has invalid extension
    """
    file_path_obj = pathlib.Path(file_path).resolve()

    # Check base directory restriction (prevent path traversal)
    if base_dir is not None:
        base_dir_obj = pathlib.Path(base_dir).resolve()
        try:
            file_path_obj.relative_to(base_dir_obj)
        except ValueError:
            raise SecurityError(
                f"Access denied: {file_path} is outside allowed directory {base_dir}"
            )

    # Check file exists
    if not file_path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Check it's a file, not a directory
    if not file_path_obj.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    # Check file size
    size_mb = file_path_obj.stat().st_size / (1024 * 1024)
    if size_mb > max_size_mb:
        raise ValueError(
            f"File too large: {size_mb:.1f} MB (max: {max_size_mb} MB)"
        )

    # Check file extension
    if allowed_extensions is not None:
        if file_path_obj.suffix.lower() not in [
            ext.lower() for ext in allowed_extensions
        ]:
            raise ValueError(
                f"Invalid file extension: {file_path_obj.suffix}. "
                f"Allowed: {allowed_extensions}"
            )

    return str(file_path_obj)


# ===================================================================
# MATHEMATICAL UTILITIES
# ===================================================================

def safe_solve(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Numerically stable matrix solving.

    Uses np.linalg.solve with fallback to least squares if singular.

    Args:
        A: Coefficient matrix
        b: Right-hand side vector

    Returns:
        Solution vector x where Ax = b
    """
    try:
        return np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        return np.linalg.lstsq(A, b, rcond=None)[0]


def safe_matrix_inverse(A: np.ndarray) -> np.ndarray:
    """
    Numerically stable matrix inversion.

    Uses np.linalg.inv with fallback to pseudoinverse if singular.

    Args:
        A: Matrix to invert

    Returns:
        Inverse or pseudoinverse of A
    """
    try:
        return np.linalg.inv(A)
    except np.linalg.LinAlgError:
        return np.linalg.pinv(A)


def calculate_pooled_estimate(
    effects: np.ndarray,
    weights_or_variances: np.ndarray,
    use_variances: bool = False
) -> Tuple[float, float]:
    """
    Calculate pooled effect and standard error from weights or variances.

    This utility function consolidates duplicated pooled estimate calculations
    throughout the codebase.

    Args:
        effects: Array of effect sizes
        weights_or_variances: Array of weights or variances
        use_variances: If True, convert variances to weights (1/variance)

    Returns:
        Tuple of (pooled_effect, pooled_se)

    Example:
        >>> effects = np.array([0.2, 0.5, 0.3])
        >>> variances = np.array([0.01, 0.02, 0.015])
        >>> pooled, se = calculate_pooled_estimate(effects, variances, use_variances=True)
    """
    if use_variances:
        weights = 1 / weights_or_variances
    else:
        weights = weights_or_variances

    pooled_effect = np.sum(weights * effects) / np.sum(weights)
    pooled_se = np.sqrt(1 / np.sum(weights))
    return float(pooled_effect), float(pooled_se)


def calculate_confidence_interval(
    effect: float,
    se: float,
    alpha: float = 0.05,
    use_t: bool = False,
    df: Optional[int] = None
) -> Tuple[float, float]:
    """
    Calculate confidence interval for an effect estimate.

    This utility function consolidates duplicated CI calculations
    throughout the codebase.

    Args:
        effect: Point estimate
        se: Standard error
        alpha: Significance level (default 0.05 for 95% CI)
        use_t: If True, use t-distribution instead of normal
        df: Degrees of freedom (required if use_t=True)

    Returns:
        Tuple of (ci_low, ci_high)

    Example:
        >>> ci_low, ci_high = calculate_confidence_interval(0.5, 0.1)
        >>> print(f"95% CI: [{ci_low:.3f}, {ci_high:.3f}]")
    """
    if use_t and df is not None:
        crit = t.ppf(1 - alpha / 2, df)
    else:
        crit = norm.ppf(1 - alpha / 2)

    ci_low = effect - crit * se
    ci_high = effect + crit * se
    return ci_low, ci_high


def check_convergence(
    current: float,
    previous: float,
    tolerance: float = 1e-6,
    relative: bool = True
) -> bool:
    """
    Check if iterative algorithm has converged.

    Args:
        current: Current value
        previous: Previous value
        tolerance: Convergence tolerance
        relative: If True, use relative difference; otherwise absolute

    Returns:
        True if converged
    """
    if relative:
        if abs(previous) < 1e-10:
            return abs(current - previous) < tolerance
        return abs((current - previous) / previous) < tolerance
    else:
        return abs(current - previous) < tolerance


__all__ = [
    'validate_inputs',
    'validate_file_path',
    'safe_solve',
    'safe_matrix_inverse',
    'calculate_pooled_estimate',
    'calculate_confidence_interval',
    'check_convergence',
]
