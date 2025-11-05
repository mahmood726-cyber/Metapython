"""
Core data models and result classes for meta-analysis.

This module contains all dataclasses and custom exceptions used throughout
the MetaPython package.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import pandas as pd
import numpy as np

from metapython.core.config import (
    DEFAULT_ALPHA,
    MIN_STUDIES_DEFAULT,
    MAX_ITERATIONS_DEFAULT,
    CONVERGENCE_TOLERANCE,
    DEFAULT_CLUSTER_CANDIDATES,
)


# ===================================================================
# RESULT DATACLASSES FOR STRUCTURED OUTPUT
# ===================================================================

@dataclass
class FixedEffectsResults:
    """Results from fixed-effects meta-analysis."""

    effect: float = 0.0
    se: float = 0.0
    ci_low: float = 0.0
    ci_high: float = 0.0
    z_statistic: float = 0.0
    p_value: float = 1.0

    def is_significant(self, alpha: float = 0.05) -> bool:
        """Check if the effect is statistically significant."""
        return self.p_value < alpha


@dataclass
class RandomEffectsResults:
    """Results from random-effects meta-analysis."""

    effect: float = 0.0
    se: float = 0.0
    ci_low: float = 0.0
    ci_high: float = 0.0
    z_statistic: float = 0.0
    p_value: float = 1.0
    tau2: float = 0.0

    def is_significant(self, alpha: float = 0.05) -> bool:
        """Check if the effect is statistically significant."""
        return self.p_value < alpha


@dataclass
class HeterogeneityResults:
    """Results from heterogeneity assessment."""

    Q: float = 0.0
    df: int = 0
    p_value: float = 1.0
    I2: float = 0.0
    H2: float = 1.0
    tau2: float = 0.0

    def is_significant(self, alpha: float = 0.05) -> bool:
        """Check if heterogeneity is statistically significant."""
        return self.p_value < alpha


@dataclass
class PredictionIntervalResults:
    """Prediction interval for future studies."""

    low: float = 0.0
    high: float = 0.0
    se: float = 0.0


@dataclass
class BiasTestResults:
    """Publication bias test results."""

    egger_intercept: float = 0.0
    egger_p_value: float = 1.0
    egger_significant: bool = False
    begg_tau: float = 0.0
    begg_p_value: float = 1.0
    begg_significant: bool = False


@dataclass
class ConflictResults:
    """Conflict detection results."""

    k: int = 1
    silhouette: float = 0.0
    delta: float = 0.0
    clusters: pd.DataFrame = field(default_factory=pd.DataFrame)
    conflicting: bool = False


@dataclass
class MetaAnalysisResults:
    """Complete meta-analysis results container."""

    fixed_effects: FixedEffectsResults = field(default_factory=FixedEffectsResults)
    random_effects: RandomEffectsResults = field(default_factory=RandomEffectsResults)
    heterogeneity: HeterogeneityResults = field(default_factory=HeterogeneityResults)
    prediction_interval: Optional[PredictionIntervalResults] = None
    bias_assessment: Optional[Any] = None
    conflict_detection: Optional[ConflictResults] = None
    subgroups: Optional[Dict[str, Any]] = None
    transport_analysis: Optional[Any] = None


# ===================================================================
# CONFIGURATION DATACLASS
# ===================================================================

@dataclass
class UnifiedMetaConfig:
    """Unified configuration for all meta-analysis methods."""

    # Core settings
    alpha: float = DEFAULT_ALPHA
    tau2_method: str = 'REML'
    use_hksj: bool = False
    prediction_interval: bool = True
    bias_correction: bool = True
    min_studies: int = MIN_STUDIES_DEFAULT
    max_iterations: int = MAX_ITERATIONS_DEFAULT
    convergence_tolerance: float = CONVERGENCE_TOLERANCE

    # CBAMM settings
    transport_truncation: float = 0.02
    conflict_k_candidates: Optional[List[int]] = None
    missing_study_max: int = 5
    bayesian_chains: int = 2
    bayesian_draws: int = 1000

    # Living MA settings
    pubmed_email: str = "researcher@example.com"
    pubmed_max_records: int = 200
    auto_update_threshold: int = 5

    def __post_init__(self) -> None:
        """Initialize default values for optional fields."""
        if self.conflict_k_candidates is None:
            self.conflict_k_candidates = DEFAULT_CLUSTER_CANDIDATES


# ===================================================================
# CUSTOM EXCEPTIONS
# ===================================================================

class UnifiedMetaError(Exception):
    """Base exception for unified meta-analysis."""
    pass


class InsufficientDataError(UnifiedMetaError):
    """Raised when insufficient data for analysis."""
    pass


class NumericalInstabilityError(UnifiedMetaError):
    """Raised when numerical issues occur."""
    pass


class SecurityError(Exception):
    """Raised for security-related issues (e.g., path traversal)."""
    pass


__all__ = [
    # Result classes
    'FixedEffectsResults',
    'RandomEffectsResults',
    'HeterogeneityResults',
    'PredictionIntervalResults',
    'BiasTestResults',
    'ConflictResults',
    'MetaAnalysisResults',

    # Configuration
    'UnifiedMetaConfig',

    # Exceptions
    'UnifiedMetaError',
    'InsufficientDataError',
    'NumericalInstabilityError',
    'SecurityError',
]
