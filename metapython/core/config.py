"""
Core configuration, constants, and optional dependency detection.

This module contains all configuration constants and detects optional
dependencies with graceful degradation.
"""

import os
import logging
from typing import List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===================================================================
# PYTENSOR CONFIGURATION FOR MINIMAL ENVIRONMENTS
# ===================================================================

# Set PyTensor configuration to minimize compilation overhead
# This must be done before any PyMC/PyTensor imports
if 'PYTENSOR_FLAGS' not in os.environ:
    os.environ['PYTENSOR_FLAGS'] = (
        "device=cpu,floatX=float32,optimizer=fast_compile,openmp=False,blas__ldflags="
    )

# ===================================================================
# STATISTICAL CONSTANTS
# ===================================================================

# Statistical thresholds
DEFAULT_ALPHA: float = 0.05
Z_CRITICAL_95: float = 1.96  # Normal distribution critical value for 95% CI
Z_CRITICAL_99: float = 2.58  # Normal distribution critical value for 99% CI
T_CRITICAL_DEFAULT_DF: int = 30  # Default degrees of freedom for t-distribution

# Outlier detection
OUTLIER_Z_THRESHOLD: float = 2.58  # 99% confidence threshold for outlier detection
OUTLIER_P_THRESHOLD: float = 0.01  # P-value threshold for outlier detection

# Sample size thresholds
MIN_STUDIES_DEFAULT: int = 2
MIN_STUDIES_FOR_GLMM: int = 3
MIN_STUDIES_FOR_NETWORK: int = 5
MIN_SAMPLE_SIZE_PER_ARM: int = 20
MIN_EVENTS_FOR_PETO: int = 1

# Numerical stability
NUMERICAL_EPSILON: float = 1e-10  # Small value to prevent division by zero
CONVERGENCE_TOLERANCE: float = 1e-6
MAX_ITERATIONS_DEFAULT: int = 1000

# Default values for missing data
DEFAULT_EFFECT_SIZE: float = 0.0
DEFAULT_SE: float = 0.2
DEFAULT_SE_SMALL: float = 0.1
DEFAULT_SE_MIN: float = 0.01

# Clustering defaults
DEFAULT_CLUSTER_CANDIDATES: List[int] = [2, 3, 4]

# ===================================================================
# OPTIONAL DEPENDENCIES WITH GRACEFUL FALLBACK
# ===================================================================

# PyMC/PyTensor with enhanced error handling for minimal environments
try:
    import pymc as pm  # noqa: F401
    import arviz as az  # noqa: F401
    HAS_PYMC: bool = True
except ImportError:
    HAS_PYMC = False
    logger.info("PyMC/PyTensor not available - Bayesian methods disabled")
except Exception as e:
    HAS_PYMC = False
    logger.info("PyMC/PyTensor initialization failed - Bayesian methods disabled")

# Statsmodels
try:
    import statsmodels.api as sm  # noqa: F401
    HAS_STATSMODELS: bool = True
except ImportError:
    HAS_STATSMODELS = False
    logger.info("Statsmodels not available - some advanced methods disabled")

# BioPython (PubMed integration)
try:
    from Bio import Entrez  # noqa: F401
    HAS_BIOPYTHON: bool = True
except ImportError:
    HAS_BIOPYTHON = False
    logger.info("BioPython not available - PubMed integration disabled")

# CVXPY (transport weighting)
try:
    import cvxpy as cp  # noqa: F401
    HAS_CVXPY: bool = True
except ImportError:
    HAS_CVXPY = False
    logger.info("CVXPY not available - transport weighting disabled")

# Scikit-learn
try:
    from sklearn.cluster import KMeans  # noqa: F401
    from sklearn.metrics import silhouette_score  # noqa: F401
    HAS_SKLEARN: bool = True
except ImportError:
    HAS_SKLEARN = False
    logger.info("Scikit-learn not available - ML methods disabled")

# XGBoost/SHAP
try:
    from xgboost import XGBRegressor  # noqa: F401
    import shap  # noqa: F401
    HAS_XGBOOST: bool = True
except ImportError:
    HAS_XGBOOST = False
    logger.info("XGBoost/SHAP not available - ML heterogeneity disabled")

# spaCy
try:
    import spacy  # noqa: F401
    HAS_SPACY: bool = True
except ImportError:
    HAS_SPACY = False
    logger.info("spaCy not available - NLP extraction disabled")

# Numba
try:
    from numba import njit, prange  # noqa: F401
    HAS_NUMBA: bool = True
except ImportError:
    HAS_NUMBA = False
    logger.info("Numba not available - performance optimization disabled")

# Plotly
try:
    import plotly.graph_objects as go  # noqa: F401
    import plotly.express as px  # noqa: F401
    HAS_PLOTLY: bool = True
except ImportError:
    HAS_PLOTLY = False
    logger.info("Plotly not available - interactive visualization disabled")

# NetworkX
try:
    import networkx as nx  # noqa: F401
    HAS_NETWORKX: bool = True
except ImportError:
    HAS_NETWORKX = False
    logger.info("NetworkX not available - network analysis disabled")

# Matplotlib patches (for advanced visualization)
try:
    from matplotlib.patches import Polygon, FancyBboxPatch  # noqa: F401
    HAS_MATPLOTLIB_PATCHES: bool = True
except ImportError:
    HAS_MATPLOTLIB_PATCHES = False

# ===================================================================
# SPACY MODEL HELPER WITH WARNING THROTTLE
# ===================================================================

_SPACY_MODEL_WARNING_SHOWN = False


def get_spacy_model(model_name: str = "en_core_web_sm") -> Optional[Any]:
    """
    Load spaCy model with throttled warnings for minimal environments.

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
            logger.info(
                f"spaCy model '{model_name}' not found - "
                f"install with: python -m spacy download {model_name}"
            )
            _SPACY_MODEL_WARNING_SHOWN = True
        return None
    except Exception:
        if not _SPACY_MODEL_WARNING_SHOWN:
            logger.info(
                f"Failed to load spaCy model '{model_name}' - "
                "NLP features will use fallback methods"
            )
            _SPACY_MODEL_WARNING_SHOWN = True
        return None


__all__ = [
    # Constants
    'DEFAULT_ALPHA',
    'Z_CRITICAL_95',
    'Z_CRITICAL_99',
    'T_CRITICAL_DEFAULT_DF',
    'OUTLIER_Z_THRESHOLD',
    'OUTLIER_P_THRESHOLD',
    'MIN_STUDIES_DEFAULT',
    'MIN_STUDIES_FOR_GLMM',
    'MIN_STUDIES_FOR_NETWORK',
    'MIN_SAMPLE_SIZE_PER_ARM',
    'MIN_EVENTS_FOR_PETO',
    'NUMERICAL_EPSILON',
    'CONVERGENCE_TOLERANCE',
    'MAX_ITERATIONS_DEFAULT',
    'DEFAULT_EFFECT_SIZE',
    'DEFAULT_SE',
    'DEFAULT_SE_SMALL',
    'DEFAULT_SE_MIN',
    'DEFAULT_CLUSTER_CANDIDATES',

    # Dependency flags
    'HAS_PYMC',
    'HAS_STATSMODELS',
    'HAS_BIOPYTHON',
    'HAS_CVXPY',
    'HAS_SKLEARN',
    'HAS_XGBOOST',
    'HAS_SPACY',
    'HAS_NUMBA',
    'HAS_PLOTLY',
    'HAS_NETWORKX',
    'HAS_MATPLOTLIB_PATCHES',

    # Utilities
    'get_spacy_model',
    'logger',
]
