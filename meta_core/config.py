"""
Core configuration, constants, dataclasses, and utility functions

Part of the MetaPython meta-analysis library.
"""

import datetime
import logging
import re
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any, Union

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import norm, chi2, t
from scipy.optimize import minimize

logger = logging.getLogger(__name__)

# ===================================================================
# CONSTANTS
# ===================================================================

# Statistical thresholds
DEFAULT_ALPHA = 0.05
Z_CRITICAL_95 = 1.96  # Normal distribution critical value for 95% CI
Z_CRITICAL_99 = 2.58  # Normal distribution critical value for 99% CI
T_CRITICAL_DEFAULT_DF = 30  # Default degrees of freedom for t-distribution

# Outlier detection
OUTLIER_Z_THRESHOLD = 2.58  # 99% confidence threshold for outlier detection
OUTLIER_P_THRESHOLD = 0.01  # P-value threshold for outlier detection

# Sample size thresholds
MIN_STUDIES_DEFAULT = 2
MIN_STUDIES_FOR_GLMM = 3
MIN_STUDIES_FOR_NETWORK = 5
MIN_SAMPLE_SIZE_PER_ARM = 20
MIN_EVENTS_FOR_PETO = 1

# Numerical stability
NUMERICAL_EPSILON = 1e-10  # Small value to prevent division by zero
CONVERGENCE_TOLERANCE = 1e-6
MAX_ITERATIONS_DEFAULT = 1000

# Default values for missing data
DEFAULT_EFFECT_SIZE = 0.0
DEFAULT_SE = 0.2
DEFAULT_SE_SMALL = 0.1
DEFAULT_SE_MIN = 0.01

# Clustering defaults
DEFAULT_CLUSTER_CANDIDATES = [2, 3, 4]

# ===================================================================
# OPTIONAL DEPENDENCIES WITH GRACEFUL FALLBACK
# Minimal environments may lack advanced dependencies - graceful degradation
# ===================================================================

# PyMC/PyTensor with enhanced error handling for minimal environments
try:
    import pymc as pm
    import arviz as az
    HAS_PYMC = True
except ImportError:
    # Single info log for missing PyMC - no stack trace spam
    HAS_PYMC = False
    logger.info("PyMC/PyTensor not available - Bayesian methods disabled")
except Exception as e:
    # Catch any PyTensor compilation or runtime errors gracefully
    HAS_PYMC = False
    logger.info("PyMC/PyTensor initialization failed - Bayesian methods disabled")

try:
    import statsmodels.api as sm
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False
    logger.info("Statsmodels not available - some advanced methods disabled")

try:
    from Bio import Entrez
    HAS_BIOPYTHON = True
except ImportError:
    HAS_BIOPYTHON = False
    logger.info("BioPython not available - PubMed integration disabled")

try:
    import cvxpy as cp
    HAS_CVXPY = True
except ImportError:
    HAS_CVXPY = False
    logger.info("CVXPY not available - transport weighting disabled")

try:
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    logger.info("Scikit-learn not available - ML methods disabled")

try:
    from xgboost import XGBRegressor
    import shap
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    logger.info("XGBoost/SHAP not available - ML heterogeneity disabled")

try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False
    logger.info("spaCy not available - NLP extraction disabled")

# ===================================================================
# SPACY MODEL HELPER WITH WARNING THROTTLE
# Ensures missing spaCy model warning appears only once per run
# ===================================================================

_SPACY_MODEL_WARNING_SHOWN = False

def get_spacy_model(model_name: str = "en_core_web_sm") -> Optional[Any]:
    """
    Load spaCy model with throttled warnings for minimal environments.

    In containerized or minimal environments, spaCy models may not be installed.
    This helper ensures the warning appears only once per run rather than
    spamming logs on every NLP operation.

    Args:
        model_name: Name of the spaCy model to load

    Returns:
        spacy.Language object if successful, None otherwise
    """
    global _SPACY_MODEL_WARNING_SHOWN
    
    if not HAS_SPACY:
        return None
    
    try:
        import spacy
        return spacy.load(model_name)
    except OSError:
        if not _SPACY_MODEL_WARNING_SHOWN:
            logger.info(f"spaCy model '{model_name}' not found - install with: python -m spacy download {model_name}")
            _SPACY_MODEL_WARNING_SHOWN = True
        return None
    except Exception:
        if not _SPACY_MODEL_WARNING_SHOWN:
            logger.info(f"Failed to load spaCy model '{model_name}' - NLP features will use fallback methods")
            _SPACY_MODEL_WARNING_SHOWN = True
        return None

try:
    from numba import njit, prange
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False
    logger.info("Numba not available - performance optimization disabled")

try:
    import dask.dataframe as dd
    HAS_DASK = True
except ImportError:
    HAS_DASK = False
    logger.info("Dask not available - big data processing disabled")

try:
    from jinja2 import Template
    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False
    logger.info("Jinja2 not available - HTML report generation disabled")

try:
    from joblib import Parallel, delayed
    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False
    logger.info("Joblib not available - parallel processing disabled")

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    logger.info("Streamlit not available - web dashboard disabled")

try:
    from flask import Flask, request, jsonify
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False
    logger.info("Flask not available - API server disabled")

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False
    logger.info("Pytest not available - testing framework disabled")

try:
    from matplotlib.patches import FancyBboxPatch
    HAS_MATPLOTLIB_PATCHES = True
except ImportError:
    HAS_MATPLOTLIB_PATCHES = False

# ===================================================================
# RESULT DATACLASSES FOR STRUCTURED OUTPUT
# ===================================================================

@dataclass
class FixedEffectsResults:
    """Results from fixed-effects meta-analysis"""
    effect: float = 0.0
    se: float = 0.0
    ci_low: float = 0.0
    ci_high: float = 0.0
    z_statistic: float = 0.0
    p_value: float = 1.0
    
    def is_significant(self, alpha: float = 0.05) -> bool:
        return self.p_value < alpha

@dataclass
class RandomEffectsResults:
    """Results from random-effects meta-analysis"""
    effect: float = 0.0
    se: float = 0.0
    ci_low: float = 0.0
    ci_high: float = 0.0
    z_statistic: float = 0.0
    p_value: float = 1.0
    tau2: float = 0.0
    
    def is_significant(self, alpha: float = 0.05) -> bool:
        return self.p_value < alpha

@dataclass
class HeterogeneityResults:
    """Results from heterogeneity assessment"""
    Q: float = 0.0
    df: int = 0
    p_value: float = 1.0
    I2: float = 0.0
    H2: float = 1.0
    tau2: float = 0.0
    
    def is_significant(self, alpha: float = 0.05) -> bool:
        return self.p_value < alpha

@dataclass
class PredictionIntervalResults:
    """Prediction interval for future studies"""
    low: float = 0.0
    high: float = 0.0
    se: float = 0.0

@dataclass
class BiasTestResults:
    """Publication bias test results"""
    egger_intercept: float = 0.0
    egger_p_value: float = 1.0
    egger_significant: bool = False
    begg_tau: float = 0.0
    begg_p_value: float = 1.0
    begg_significant: bool = False

@dataclass
class ConflictResults:
    """Conflict detection results"""
    k: int = 1
    silhouette: float = 0.0
    delta: float = 0.0
    clusters: pd.DataFrame = field(default_factory=pd.DataFrame)
    conflicting: bool = False

@dataclass
class MetaAnalysisResults:
    """Complete meta-analysis results"""
    fixed_effects: FixedEffectsResults = field(default_factory=FixedEffectsResults)
    random_effects: RandomEffectsResults = field(default_factory=RandomEffectsResults)
    heterogeneity: HeterogeneityResults = field(default_factory=HeterogeneityResults)
    prediction_interval: Optional[PredictionIntervalResults] = None
    bias_assessment: Optional[Any] = None
    conflict_detection: Optional[ConflictResults] = None
    subgroups: Optional[Dict[str, Any]] = None
    transport_analysis: Optional[Any] = None

# ===================================================================
# CORE CONFIGURATION AND VALIDATION
# ===================================================================

@dataclass
class UnifiedMetaConfig:
    """Unified configuration for all meta-analysis methods"""
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
    conflict_k_candidates: List[int] = None
    missing_study_max: int = 5
    bayesian_chains: int = 2
    bayesian_draws: int = 1000

    # Living MA settings
    pubmed_email: str = "researcher@example.com"
    pubmed_max_records: int = 200
    auto_update_threshold: int = 5

    def __post_init__(self) -> None:
        if self.conflict_k_candidates is None:
            self.conflict_k_candidates = DEFAULT_CLUSTER_CANDIDATES

class UnifiedMetaError(Exception):
    """Base exception for unified meta-analysis"""
    pass

class InsufficientDataError(UnifiedMetaError):
    """Raised when insufficient data for analysis"""
    pass

class NumericalInstabilityError(UnifiedMetaError):
    """Raised when numerical issues occur"""
    pass

def validate_inputs(func):
    """Enhanced decorator for comprehensive input validation"""
    def wrapper(*args, **kwargs):
        # Get the function signature to identify parameters
        import inspect
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        
        # Validate common parameters
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
        
        # Check array lengths match
        if 'effects' in bound_args.arguments and 'variances' in bound_args.arguments:
            effects = bound_args.arguments['effects']
            variances = bound_args.arguments['variances']
            if len(effects) != len(variances):
                raise ValueError("Effects and variances must have the same length")
        
        # Minimum studies check
        if 'effects' in bound_args.arguments:
            effects = bound_args.arguments['effects']
            if len(effects) < 2:
                raise InsufficientDataError("At least 2 studies required for meta-analysis")
        
        return func(*bound_args.args, **bound_args.kwargs)
    return wrapper

def safe_solve(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Numerically stable matrix solving"""
    try:
        return np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        return np.linalg.lstsq(A, b, rcond=None)[0]

def safe_matrix_inverse(A: np.ndarray) -> np.ndarray:
    """Numerically stable matrix inversion"""
    try:
        return np.linalg.inv(A)
    except np.linalg.LinAlgError:
        return np.linalg.pinv(A)

def calculate_pooled_estimate(effects: np.ndarray,
                              weights_or_variances: np.ndarray,
                              use_variances: bool = False) -> Tuple[float, float]:
    """
    Calculate pooled effect and standard error from weights or variances.

    This utility function consolidates duplicated pooled estimate calculations
    throughout the codebase.

    Args:
        effects: Array of effect sizes
        weights_or_variances: Array of weights or variances
        use_variances: If True, weights_or_variances contains variances and will be converted to weights

    Returns:
        Tuple of (pooled_effect, pooled_se)
    """
    if use_variances:
        weights = 1 / weights_or_variances
    else:
        weights = weights_or_variances

    pooled_effect = np.sum(weights * effects) / np.sum(weights)
    pooled_se = np.sqrt(1 / np.sum(weights))
    return float(pooled_effect), float(pooled_se)

def calculate_confidence_interval(effect: float,
                                  se: float,
                                  alpha: float = 0.05,
                                  use_t: bool = False,
                                  df: Optional[int] = None) -> Tuple[float, float]:
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
    """
    if use_t and df is not None:
        crit = t.ppf(1 - alpha/2, df)
    else:
        crit = norm.ppf(1 - alpha/2)

    ci_low = effect - crit * se
    ci_high = effect + crit * se
    return float(ci_low), float(ci_high)

# ===================================================================
# ENHANCED TAU² ESTIMATORS
# ===================================================================

class TauSquaredEstimators: