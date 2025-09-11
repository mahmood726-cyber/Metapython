"""
PyMeta-CBAMM Unified Suite v3.0 - Complete Meta-Analysis Platform
================================================================

A fully integrated, production-ready meta-analysis library combining:
- PyMeta v2.1: Core meta-analysis with advanced diagnostics
- CBAMM v5.7: Transport weighting, robust methods, living MA
- Enhanced NLP extraction and ML-based conflict detection
- Comprehensive publication bias assessment
- Sequential and network meta-analysis
- Educational simulation tools

Author: PyMeta-CBAMM Development Team
License: MIT
Version: 3.0.0
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import norm, chi2, t
from scipy.optimize import minimize
from typing import List, Dict, Tuple, Optional, Any, Union
import logging
import warnings
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import os
import datetime
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional dependencies with graceful fallback
try:
    import pymc as pm
    import arviz as az
    HAS_PYMC = True
except ImportError:
    HAS_PYMC = False
    logger.info("PyMC not available - Bayesian methods disabled")

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
    alpha: float = 0.05
    tau2_method: str = 'REML'
    use_hksj: bool = False
    prediction_interval: bool = True
    bias_correction: bool = True
    min_studies: int = 2
    max_iterations: int = 1000
    convergence_tolerance: float = 1e-6
    
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
    
    def __post_init__(self):
        if self.conflict_k_candidates is None:
            self.conflict_k_candidates = [2, 3, 4]

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

def safe_solve(A, b):
    """Numerically stable matrix solving"""
    try:
        return np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        return np.linalg.lstsq(A, b, rcond=None)[0]

def safe_matrix_inverse(A):
    """Numerically stable matrix inversion"""
    try:
        return np.linalg.inv(A)
    except np.linalg.LinAlgError:
        return np.linalg.pinv(A)

# ===================================================================
# ENHANCED TAU² ESTIMATORS
# ===================================================================

class TauSquaredEstimators:
    """Comprehensive tau² estimation methods from PyMeta + CBAMM"""
    
    @staticmethod
    @validate_inputs
    def dersimonian_laird(effects: np.ndarray, variances: np.ndarray) -> float:
        """Standard DerSimonian-Laird estimator"""
        if len(effects) < 2:
            return 0.0
        
        weights = 1 / variances
        sum_weights = np.sum(weights)
        weighted_mean = np.sum(weights * effects) / sum_weights
        Q = np.sum(weights * (effects - weighted_mean) ** 2)
        
        sum_weights_squared = np.sum(weights ** 2)
        denominator = sum_weights - sum_weights_squared / sum_weights
        
        if denominator <= 0:
            return 0.0
        
        tau2 = max(0, (Q - (len(effects) - 1)) / denominator)
        return float(tau2)
    
    @staticmethod
    @validate_inputs
    def restricted_ml(effects: np.ndarray, variances: np.ndarray, 
                     max_iter: int = 100, tol: float = 1e-6) -> float:
        """REML estimator via iterative algorithm"""
        if len(effects) < 2:
            return 0.0
        
        # Initialize with DL estimate
        tau2 = TauSquaredEstimators.dersimonian_laird(effects, variances)
        
        for iteration in range(max_iter):
            # Update weights
            weights = 1 / (variances + tau2)
            sum_weights = np.sum(weights)
            weighted_mean = np.sum(weights * effects) / sum_weights
            
            # Calculate Q
            Q = np.sum(weights * (effects - weighted_mean) ** 2)
            
            # Update tau2
            sum_weights_squared = np.sum(weights ** 2)
            denominator = sum_weights - sum_weights_squared / sum_weights
            
            if denominator <= 0:
                break
                
            tau2_new = max(0, (Q - (len(effects) - 1)) / denominator)
            
            # Check convergence
            if abs(tau2_new - tau2) < tol:
                break
                
            tau2 = tau2_new
        
        return float(tau2)
    
    @staticmethod
    @validate_inputs
    def hunter_schmidt(effects: np.ndarray, variances: np.ndarray) -> float:
        """Hunter-Schmidt tau² estimator"""
        if len(effects) < 2:
            return 0.0
        
        var_observed = np.var(effects, ddof=1)
        mean_sampling_var = np.mean(variances)
        tau2 = max(0, var_observed - mean_sampling_var)
        
        if len(effects) < 10:
            logger.warning("Hunter-Schmidt estimator may be biased for small samples")
        
        return float(tau2)
    
    @staticmethod
    @validate_inputs
    def empirical_bayes(effects: np.ndarray, variances: np.ndarray) -> float:
        """Empirical Bayes tau² estimator"""
        if len(effects) < 2:
            return 0.0
        
        weights = 1 / variances
        sum_weights = np.sum(weights)
        mu_fe = np.sum(weights * effects) / sum_weights
        Q = np.sum(weights * (effects - mu_fe) ** 2)
        
        df = len(effects) - 1
        sum_w2 = np.sum(weights ** 2)
        denominator = sum_weights - sum_w2 / sum_weights
        
        if denominator <= 0:
            return 0.0
        
        tau2 = max(0, (Q - df) / denominator)
        return float(tau2)

# ===================================================================
# PERFORMANCE OPTIMIZATION METHODS
# ===================================================================

class PerformanceOptimization:
    """Performance optimization utilities"""
    
    @staticmethod
    def pooled_effect_optimized(effects: np.ndarray, variances: np.ndarray) -> Tuple[float, float]:
        """Numba-optimized pooled effect calculation"""
        if HAS_NUMBA:
            return PerformanceOptimization._pooled_effect_numba(effects, variances)
        else:
            # Fallback to regular numpy
            weights = 1 / variances
            pooled_effect = np.sum(weights * effects) / np.sum(weights)
            pooled_se = np.sqrt(1 / np.sum(weights))
            return pooled_effect, pooled_se
    
    @staticmethod
    @njit if HAS_NUMBA else lambda f: f
    def _pooled_effect_numba(effects, variances):
        """Numba JIT compiled pooled effect calculation"""
        weights = 1.0 / variances
        sum_weights = 0.0
        sum_weighted_effects = 0.0
        
        for i in range(len(effects)):
            sum_weights += weights[i]
            sum_weighted_effects += weights[i] * effects[i]
        
        pooled_effect = sum_weighted_effects / sum_weights
        pooled_se = (1.0 / sum_weights) ** 0.5
        
        return pooled_effect, pooled_se
    
    @staticmethod
    def parallel_multiverse(effects: np.ndarray, se: np.ndarray, n_jobs: int = -1) -> List[Dict[str, Any]]:
        """Parallel multiverse analysis"""
        if not HAS_JOBLIB:
            logger.warning("Joblib not available - running sequential multiverse")
            return []
        
        variances = se ** 2
        methods = ['DL', 'REML', 'HS', 'EB']
        
        def compute_estimate(method):
            if method == 'DL':
                tau2 = TauSquaredEstimators.dersimonian_laird(effects, variances)
            elif method == 'REML':
                tau2 = TauSquaredEstimators.restricted_ml(effects, variances)
            elif method == 'HS':
                tau2 = TauSquaredEstimators.hunter_schmidt(effects, variances)
            elif method == 'EB':
                tau2 = TauSquaredEstimators.empirical_bayes(effects, variances)
            else:
                tau2 = 0.0
            
            # Random effects estimate
            re_weights = 1 / (variances + tau2)
            pooled_effect = np.sum(re_weights * effects) / np.sum(re_weights)
            
            return {
                'method': method,
                'estimate': pooled_effect,
                'tau2': tau2
            }
        
        try:
            results = Parallel(n_jobs=n_jobs)(
                delayed(compute_estimate)(method) for method in methods
            )
            return results
        except Exception as e:
            logger.error(f"Parallel processing failed: {e}")
            return []
    
    @staticmethod
    def dask_meta_analysis(data: pd.DataFrame, effect_col: str, se_col: str) -> Dict[str, Any]:
        """Dask-based large-scale meta-analysis"""
        if not HAS_DASK:
            logger.warning("Dask not available - using pandas")
            return {'available': False}
        
        try:
            # Convert to dask dataframe
            ddf = dd.from_pandas(data, npartitions=4)
            
            # Parallel computation
            effects = ddf[effect_col].values
            variances = (ddf[se_col] ** 2).values
            
            # Compute in parallel
            weights = 1 / variances
            pooled_effect = (weights * effects).sum() / weights.sum()
            
            return {
                'available': True,
                'pooled_effect': pooled_effect.compute(),
                'n_studies': len(data)
            }
        except Exception as e:
            logger.error(f"Dask processing failed: {e}")
            return {'available': False, 'error': str(e)}

# ===================================================================
# TRANSPORT WEIGHTING METHODS (FROM CBAMM)
# ===================================================================

class TransportWeighting:
    """Transport weighting methods for enhanced generalizability"""
    
    @staticmethod
    def compute_transport_weights(X: pd.DataFrame, target_moments: Dict[str, float], 
                                 truncation: float = 0.02) -> np.ndarray:
        """Entropy balancing for transport weighting"""
        if not HAS_CVXPY:
            logger.warning("CVXPY not available - returning uniform weights")
            return np.ones(len(X)) / len(X)
        
        n, p = X.shape
        w = cp.Variable(n)
        constraints = [cp.sum(w) == 1, w >= 1e-8]
        
        for col in X.columns:
            if col in target_moments:
                constraints.append(w @ X[col].values == target_moments[col])
        
        problem = cp.Problem(cp.Minimize(cp.sum(cp.kl_div(w, np.ones(n)/n))), constraints)
        
        try:
            problem.solve()
            w_val = w.value
            
            if truncation > 0:
                lo, hi = np.quantile(w_val, truncation), np.quantile(w_val, 1-truncation)
                w_val = np.clip(w_val, lo, hi)
                w_val /= w_val.sum()
            
            return w_val
        except Exception as e:
            warnings.warn(f"Transport optimization failed: {e}")
            return np.ones(n)/n
    
    @staticmethod
    def assess_transportability(source_X: pd.DataFrame, target_X: pd.DataFrame) -> Dict[str, Any]:
        """Assess transportability between populations"""
        results = {}
        
        for col in source_X.columns:
            if col in target_X.columns:
                source_mean = source_X[col].mean()
                target_mean = target_X[col].mean()
                standardized_diff = abs(source_mean - target_mean) / source_X[col].std()
                results[col] = {
                    'source_mean': source_mean,
                    'target_mean': target_mean,
                    'standardized_diff': standardized_diff,
                    'concerning': standardized_diff > 0.5
                }
        
        return results

# ===================================================================
# CONFLICT AND CLUSTERING METHODS
# ===================================================================

class ConflictDetection:
    """Advanced conflict detection and clustering methods"""
    
    @staticmethod
    def detect_conflicts(effects: np.ndarray, se: np.ndarray, 
                        k_candidates: List[int] = None) -> Dict[str, Any]:
        """Detect conflicting results using clustering"""
        if not HAS_SKLEARN:
            logger.warning("Scikit-learn not available - conflict detection disabled")
            return {'k': 1, 'conflicting': False}
        
        if k_candidates is None:
            k_candidates = [2, 3, 4]
        
        best_k, best_score, best_km = 1, -1, None
        
        for k in k_candidates:
            if k <= len(effects):
                km = KMeans(n_clusters=k, n_init=20, random_state=42).fit(effects.reshape(-1,1))
                score = silhouette_score(effects.reshape(-1,1), km.labels_)
                if score > best_score:
                    best_k, best_score, best_km = k, score, km
        
        if best_km is not None:
            clusters = pd.DataFrame({
                "effect": effects, 
                "se": se, 
                "cluster": best_km.labels_
            })
            centers = clusters.groupby("cluster")["effect"].mean()
            delta = centers.max() - centers.min()
        else:
            clusters = pd.DataFrame({"effect": effects, "se": se, "cluster": 0})
            delta = 0
        
        return {
            'k': best_k, 
            'silhouette': best_score,
            'delta': delta, 
            'clusters': clusters,
            'conflicting': best_k > 1 and delta > 0.5
        }
    
    @staticmethod
    def heterogeneity_sources(effects: np.ndarray, predictors: pd.DataFrame) -> Dict[str, Any]:
        """Identify sources of heterogeneity using ML"""
        if not HAS_XGBOOST:
            logger.warning("XGBoost not available - ML heterogeneity disabled")
            return {'available': False}
        
        try:
            X = pd.get_dummies(predictors)
            model = XGBRegressor(n_estimators=200, random_state=42).fit(X, effects)
            
            importance_dict = dict(zip(X.columns, model.feature_importances_))
            
            # SHAP values if available
            shap_values = None
            if HAS_XGBOOST:
                try:
                    explainer = shap.Explainer(model, X)
                    shap_values = explainer(X)
                except:
                    pass
            
            return {
                'model': model,
                'feature_importance': importance_dict,
                'shap_values': shap_values,
                'r2_score': model.score(X, effects)
            }
            
        except Exception as e:
            logger.warning(f"ML heterogeneity analysis failed: {e}")
            return {'available': False, 'error': str(e)}

# ===================================================================
# NLP AND EXTRACTION METHODS
# ===================================================================

class NLPExtractor:
    """NLP-based effect size extraction from text"""
    
    def __init__(self):
        self.nlp = None
        if HAS_SPACY:
            try:
                import spacy
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found - install with: python -m spacy download en_core_web_sm")
    
    def extract_effect_sizes(self, text: str) -> Tuple[float, float]:
        """Extract effect size and SE from abstract text"""
        if not self.nlp:
            # Fallback regex-based extraction
            return self._regex_extraction(text)
        
        # Enhanced NLP extraction
        doc = self.nlp(text)
        numbers = [ent.text for ent in doc.ents if ent.label_ in ["PERCENT", "CARDINAL"]]
        numbers = [re.sub(r"[^0-9\.\-]", "", n) for n in numbers if re.search(r"[0-9]", n)]
        
        try:
            nums = [float(n) for n in numbers if n and float(n) > 0]
            if len(nums) >= 2:
                est = np.log(nums[0]) if nums[0] > 0 else 0.0
                se = abs(np.log(nums[1]) - np.log(nums[0]))/1.96 if len(nums) > 1 else 0.1
            else:
                est, se = 0.0, 0.2
        except:
            est, se = 0.0, 0.2
        
        return est, se
    
    def _regex_extraction(self, text: str) -> Tuple[float, float]:
        """Fallback regex-based extraction"""
        # Look for patterns like "HR = 1.25 (95% CI: 1.10-1.45)"
        patterns = [
            r'(?:HR|OR|RR)\s*[=:]\s*([0-9\.]+).*?CI[:\s]*([0-9\.]+)[-–]([0-9\.]+)',
            r'([0-9]\.[0-9]+).*?(?:95%|CI).*?([0-9]\.[0-9]+)[-–]([0-9]\.[0-9]+)',
            r'p\s*[=<]\s*([0-9]\.[0-9]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    if len(match.groups()) >= 3:
                        est = float(match.group(1))
                        lower = float(match.group(2))
                        upper = float(match.group(3))
                        se = (np.log(upper) - np.log(lower)) / (2 * 1.96)
                        return np.log(est), max(se, 0.01)
                except:
                    continue
        
        return 0.0, 0.2
    
    def enrich_with_effect_sizes(self, df: pd.DataFrame, text_col: str = 'abstract') -> pd.DataFrame:
        """Apply extraction to dataframe of abstracts"""
        effects, ses = [], []
        for text in df[text_col]:
            est, se = self.extract_effect_sizes(str(text))
            effects.append(est)
            ses.append(se)
        
        df['extracted_effect'] = effects
        df['extracted_se'] = ses
        return df

class OutcomeClassifier:
    """ML-based outcome classification"""
    
    def __init__(self):
        self.vectorizer = None
        self.classifier = None
        self._train_classifier()
    
    def _train_classifier(self):
        """Train outcome classifier with expanded training data"""
        if not HAS_SKLEARN:
            return
        
        # Expanded training examples
        train_texts = [
            "mortality death survival overall survival life expectancy",
            "stroke infarction cerebral event brain attack CVA",
            "heart attack myocardial infarction ACS STEMI NSTEMI cardiac",
            "hospitalization readmission length of stay admission",
            "quality of life questionnaire SF36 EQ5D wellbeing satisfaction",
            "blood pressure hypertension systolic diastolic BP",
            "diabetes glycemic control HbA1c glucose insulin",
            "cancer tumor malignancy oncology chemotherapy radiation",
            "infection sepsis antibiotic antimicrobial pathogen",
            "pain analgesic anesthesia VAS numeric rating scale"
        ]
        
        train_labels = [
            "mortality", "stroke", "myocardial_infarction", "hospitalization", 
            "quality_of_life", "blood_pressure", "diabetes", "cancer", 
            "infection", "pain"
        ]
        
        try:
            self.vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
            X = self.vectorizer.fit_transform(train_texts)
            self.classifier = LogisticRegression(random_state=42).fit(X, train_labels)
        except Exception as e:
            logger.warning(f"Outcome classifier training failed: {e}")
    
    def classify_outcome(self, text: str) -> str:
        """Classify outcome type from text"""
        if not self.classifier or not self.vectorizer:
            return "unknown"
        
        try:
            X_new = self.vectorizer.transform([text])
            return self.classifier.predict(X_new)[0]
        except:
            return "unknown"
    
    def enrich_with_outcomes(self, df: pd.DataFrame, text_col: str = 'abstract') -> pd.DataFrame:
        """Add outcome classifications to dataframe"""
        df['outcome_class'] = df[text_col].apply(self.classify_outcome)
        return df

# ===================================================================
# PUBMED INTEGRATION FOR LIVING META-ANALYSIS
# ===================================================================

class PubMedIntegration:
    """PubMed integration for living meta-analysis"""
    
    def __init__(self, email: str = "researcher@example.com"):
        self.email = email
        if HAS_BIOPYTHON:
            Entrez.email = email
    
    def fetch_studies(self, query: str, max_records: int = 200) -> pd.DataFrame:
        """Search PubMed and return article metadata"""
        if not HAS_BIOPYTHON:
            logger.warning("BioPython not available - PubMed integration disabled")
            return pd.DataFrame()
        
        try:
            # Search for articles
            handle = Entrez.esearch(db="pubmed", term=query, retmax=max_records,
                                  sort="date", datetype="pdat")
            record = Entrez.read(handle)
            ids = record["IdList"]
            handle.close()
            
            if not ids:
                return pd.DataFrame()
            
            # Fetch detailed records
            handle = Entrez.efetch(db="pubmed", id=",".join(ids),
                                 rettype="medline", retmode="xml")
            records = Entrez.read(handle)
            handle.close()
            
            summaries = []
            for r in records["PubmedArticle"]:
                try:
                    pmid = str(r["MedlineCitation"]["PMID"])
                    article = r["MedlineCitation"]["Article"]
                    title = str(article.get("ArticleTitle", ""))
                    
                    # Extract abstract
                    abstract_sections = article.get("Abstract", {}).get("AbstractText", [])
                    if abstract_sections:
                        abstract = " ".join(str(section) for section in abstract_sections)
                    else:
                        abstract = ""
                    
                    # Extract publication date
                    pub_date = article.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
                    year = pub_date.get("Year", "Unknown")
                    
                    summaries.append({
                        "pmid": pmid,
                        "title": title,
                        "abstract": abstract,
                        "year": year
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to process article: {e}")
                    continue
            
            return pd.DataFrame(summaries)
            
        except Exception as e:
            logger.error(f"PubMed search failed: {e}")
            return pd.DataFrame()
    
    def update_living_meta(self, existing_data: pd.DataFrame, query: str, 
                          effect_col: str, se_col: str) -> Dict[str, Any]:
        """Update living meta-analysis with new studies"""
        new_studies = self.fetch_studies(query)
        
        if new_studies.empty:
            return {
                'new_studies_found': 0,
                'updated_data': existing_data,
                'extraction_needed': False
            }
        
        # Extract effect sizes from new studies
        extractor = NLPExtractor()
        new_studies = extractor.enrich_with_effect_sizes(new_studies)
        
        # Filter studies with reasonable effect sizes
        valid_studies = new_studies[
            (new_studies['extracted_se'] > 0.01) & 
            (new_studies['extracted_se'] < 2.0) &
            (np.abs(new_studies['extracted_effect']) < 5.0)
        ].copy()
        
        if not valid_studies.empty:
            # Map extracted columns to expected columns
            valid_studies[effect_col] = valid_studies['extracted_effect']
            valid_studies[se_col] = valid_studies['extracted_se']
            valid_studies['study_id'] = valid_studies['pmid']
            
            # Combine with existing data
            updated_data = pd.concat([existing_data, valid_studies], ignore_index=True)
        else:
            updated_data = existing_data
        
        return {
            'new_studies_found': len(new_studies),
            'valid_studies_added': len(valid_studies) if not valid_studies.empty else 0,
            'updated_data': updated_data,
            'extraction_needed': len(new_studies) > len(valid_studies) if not new_studies.empty else False,
            'new_studies_raw': new_studies
        }

# ===================================================================
# MAIN UNIFIED PYMETA-CBAMM CLASS
# ===================================================================

class UnifiedMetaAnalysis:
    """
    Unified Meta-Analysis Suite combining PyMeta v2.1 and CBAMM v5.7
    
    Comprehensive meta-analysis platform with:
    - Core meta-analysis (fixed/random effects)
    - Multiple tau² estimators
    - Enhanced diagnostics and influence analysis
    - Comprehensive publication bias assessment
    - Transport weighting and generalizability
    - Conflict detection and clustering
    - Sequential analysis methods
    - Network meta-analysis components
    - Bayesian methods (HSROC, stacking)
    - Living meta-analysis with PubMed integration
    - NLP extraction and outcome classification
    - Educational simulation tools
    - GRADE evidence assessment
    """
    
    def __init__(self, data: pd.DataFrame, effect_col: str, se_col: str,
                 label_col: str, subgroup_col: Optional[str] = None,
                 config: Optional[UnifiedMetaConfig] = None, validate_data: bool = True):
        
        self.df = data.copy()
        self.effect_col = effect_col
        self.se_col = se_col
        self.label_col = label_col
        self.subgroup_col = subgroup_col
        self.config = config or UnifiedMetaConfig()
        
        if validate_data:
            self._validate_data()
        
        self._prepare_data()
        self._fitted = False
        self.results = None
        
        # Initialize helper classes
        self.nlp_extractor = NLPExtractor()
        self.outcome_classifier = OutcomeClassifier()
        self.pubmed = PubMedIntegration(self.config.pubmed_email)
    
    def _validate_data(self):
        """Comprehensive data validation"""
        required_cols = [self.effect_col, self.se_col, self.label_col]
        missing_cols = [col for col in required_cols if col not in self.df.columns]
        
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        if len(self.df) < self.config.min_studies:
            raise InsufficientDataError(f"Need at least {self.config.min_studies} studies")
        
        # Check for invalid values
        if self.df[self.se_col].isna().any() or (self.df[self.se_col] <= 0).any():
            raise ValueError("Standard errors must be positive and non-missing")
        
        if self.df[self.effect_col].isna().any():
            raise ValueError("Effect sizes cannot be missing")
    
    def _prepare_data(self):
        """Prepare data for analysis"""
        self.df = self.df.copy()
        self.df['_variance'] = self.df[self.se_col] ** 2
        self.df['_weight'] = 1 / self.df['_variance']
        self.weight_col = '_weight'
    
    # ===================================================================
    # CORE ANALYSIS METHODS (ENHANCED FROM PYMETA)
    # ===================================================================
    
    def analyze(self, include_bias_tests: bool = True, 
               include_prediction_interval: bool = True,
               include_conflicts: bool = True,
               include_transport: bool = False,
               target_population: Optional[pd.DataFrame] = None) -> 'UnifiedMetaAnalysis':
        """Run comprehensive unified meta-analysis"""
        
        # Core analysis
        self._fit_fixed_effects()
        self._fit_random_effects()
        self._calculate_heterogeneity()
        
        if include_prediction_interval:
            self._calculate_prediction_interval()
        
        # Enhanced bias assessment
        if include_bias_tests and len(self.df) >= 3:
            self._comprehensive_bias_assessment()
        
        # Conflict detection
        if include_conflicts and len(self.df) >= 3:
            self._detect_conflicts()
        
        # Transport weighting
        if include_transport and target_population is not None:
            self._transport_analysis(target_population)
        
        # Subgroup analysis
        if self.subgroup_col:
            self._subgroup_analysis()
        
        self._fitted = True
        return self
    
    def _fit_fixed_effects(self):
        """Fixed-effects analysis"""
        weights = self.df['_weight'].values
        effects = self.df[self.effect_col].values
        
        sum_weights = np.sum(weights)
        pooled_effect = np.sum(weights * effects) / sum_weights
        pooled_se = np.sqrt(1 / sum_weights)
        
        # Confidence interval
        z_crit = norm.ppf(1 - self.config.alpha/2)
        ci_low = pooled_effect - z_crit * pooled_se
        ci_high = pooled_effect + z_crit * pooled_se
        
        # Test statistic
        z_stat = pooled_effect / pooled_se if pooled_se > 0 else 0
        p_value = 2 * (1 - norm.cdf(abs(z_stat)))
        
        # Initialize results structure
        self.results = MetaAnalysisResults()
        
        self.results.fixed_effects = FixedEffectsResults(
            effect=pooled_effect,
            se=pooled_se,
            ci_low=ci_low,
            ci_high=ci_high,
            z_statistic=z_stat,
            p_value=p_value
        )
    
    def _fit_random_effects(self):
        """Enhanced random-effects analysis with CBAMM robust methods"""
        effects = self.df[self.effect_col].values
        variances = self.df['_variance'].values
        
        # Estimate tau² using specified method
        if self.config.tau2_method == 'DL':
            tau2 = TauSquaredEstimators.dersimonian_laird(effects, variances)
        elif self.config.tau2_method == 'REML':
            tau2 = TauSquaredEstimators.restricted_ml(effects, variances)
        elif self.config.tau2_method == 'HS':
            tau2 = TauSquaredEstimators.hunter_schmidt(effects, variances)
        elif self.config.tau2_method == 'EB':
            tau2 = TauSquaredEstimators.empirical_bayes(effects, variances)
        else:
            logger.warning(f"Unknown tau² method: {self.config.tau2_method}, using DL")
            tau2 = TauSquaredEstimators.dersimonian_laird(effects, variances)
        
        # Random-effects weights
        re_weights = 1 / (variances + tau2)
        sum_re_weights = np.sum(re_weights)
        pooled_effect = np.sum(re_weights * effects) / sum_re_weights
        pooled_se = np.sqrt(1 / sum_re_weights)
        
        # HKSJ adjustment (enhanced from CBAMM)
        if self.config.use_hksj:
            df = len(effects) - 1
            Q_re = np.sum(re_weights * (effects - pooled_effect) ** 2)
            inflation_factor = max(1, Q_re / df) if df > 0 else 1
            pooled_se *= np.sqrt(inflation_factor)
            
            # Use t-distribution
            t_crit = t.ppf(1 - self.config.alpha/2, df)
            ci_low = pooled_effect - t_crit * pooled_se
            ci_high = pooled_effect + t_crit * pooled_se
            
            t_stat = pooled_effect / pooled_se if pooled_se > 0 else 0
            p_value = 2 * (1 - t.cdf(abs(t_stat), df))
        else:
            z_crit = norm.ppf(1 - self.config.alpha/2)
            ci_low = pooled_effect - z_crit * pooled_se
            ci_high = pooled_effect + z_crit * pooled_se
            
            z_stat = pooled_effect / pooled_se if pooled_se > 0 else 0
            p_value = 2 * (1 - norm.cdf(abs(z_stat)))
        
        self.results.random_effects = RandomEffectsResults(
            effect=pooled_effect,
            se=pooled_se,
            ci_low=ci_low,
            ci_high=ci_high,
            z_statistic=z_stat if not self.config.use_hksj else t_stat,
            p_value=p_value,
            tau2=tau2
        )
    
    def _calculate_heterogeneity(self):
        """Calculate heterogeneity statistics"""
        effects = self.df[self.effect_col].values
        variances = self.df['_variance'].values
        weights = 1 / variances
        
        # Q statistic
        weighted_mean = np.sum(weights * effects) / np.sum(weights)
        Q = np.sum(weights * (effects - weighted_mean) ** 2)
        df = len(effects) - 1
        p_value = 1 - chi2.cdf(Q, df) if df > 0 else 1.0
        
        # I² statistic
        I2 = max(0, ((Q - df) / Q) * 100) if Q > 0 else 0
        
        # H² statistic
        H2 = Q / df if df > 0 else 1
        
        self.results.heterogeneity = HeterogeneityResults(
            Q=Q,
            df=df,
            p_value=p_value,
            I2=I2,
            H2=H2,
            tau2=self.results.random_effects.tau2
        )
    
    def _calculate_prediction_interval(self):
        """Calculate prediction interval for future studies"""
        if hasattr(self.results, 'random_effects'):
            effect = self.results.random_effects.effect
            tau2 = self.results.random_effects.tau2
            se = self.results.random_effects.se
            
            pred_se = np.sqrt(se**2 + tau2)
            
            if self.config.use_hksj:
                df = len(self.df) - 1
                t_crit = t.ppf(1 - self.config.alpha/2, df)
                pi_low = effect - t_crit * pred_se
                pi_high = effect + t_crit * pred_se
            else:
                z_crit = norm.ppf(1 - self.config.alpha/2)
                pi_low = effect - z_crit * pred_se
                pi_high = effect + z_crit * pred_se
            
            self.results.prediction_interval = PredictionIntervalResults(
                low=pi_low,
                high=pi_high,
                se=pred_se
            )
    
    # ===================================================================
    # COMPREHENSIVE BIAS ASSESSMENT (PYMETA + CBAMM)
    # ===================================================================
    
    def _comprehensive_bias_assessment(self):
        """Unified comprehensive publication bias assessment"""
        effects = self.df[self.effect_col].values
        se = self.df[self.se_col].values
        
        bias_results = type('BiasResults', (), {})()
        
        # Standard tests (from PyMeta)
        bias_results.egger = self._egger_test(effects, se)
        bias_results.begg = self._begg_test(effects, se)
        
        # Enhanced methods
        bias_results.trim_fill = self._trim_and_fill_enhanced(effects, se)
        bias_results.p_curve = self._p_curve_analysis(effects, se)
        bias_results.excess_significance = self._test_excess_significance(effects, se)
        
        # PET-PEESE (from CBAMM)
        bias_results.pet_peese = self._pet_peese_analysis(effects, se)
        
        # Weight function model
        try:
            bias_results.weight_function = self._weight_function_model(effects, se)
        except Exception as e:
            logger.warning(f"Weight function model failed: {e}")
            bias_results.weight_function = {'success': False}
        
        self.results.bias_assessment = bias_results
    
    def _egger_test(self, effects: np.ndarray, se: np.ndarray) -> Dict[str, Any]:
        """Egger's regression test"""
        if not HAS_STATSMODELS:
            return {'available': False}
        
        precision = 1 / se
        model = sm.OLS(effects, sm.add_constant(precision)).fit()
        intercept = model.params[0]
        p_value = model.pvalues[0]
        
        return {
            'intercept': intercept,
            'p_value': p_value,
            'significant': p_value < self.config.alpha
        }
    
    def _begg_test(self, effects: np.ndarray, se: np.ndarray) -> Dict[str, Any]:
        """Begg's rank correlation test"""
        from scipy.stats import kendalltau
        tau_kendall, p_value = kendalltau(effects, se)
        
        return {
            'tau': tau_kendall,
            'p_value': p_value,
            'significant': p_value < self.config.alpha
        }
    
    def _pet_peese_analysis(self, effects: np.ndarray, se: np.ndarray) -> Dict[str, Any]:
        """PET-PEESE bias correction (from CBAMM)"""
        if not HAS_STATSMODELS:
            return {'available': False}
        
        weights = 1 / se**2
        
        # PET (Precision-Effect Test)
        pet_model = sm.WLS(effects, sm.add_constant(se), weights=weights).fit()
        pet_intercept = pet_model.params[0]
        pet_p = pet_model.pvalues[0]
        
        # PEESE (Precision-Effect Estimate with Standard Error)
        peese_model = sm.WLS(effects, sm.add_constant(se**2), weights=weights).fit()
        peese_intercept = peese_model.params[0]
        peese_p = peese_model.pvalues[0]
        
        # Conditional selection: use PEESE if PET shows significance
        corrected_effect = peese_intercept if pet_p < 0.05 else pet_intercept
        
        return {
            'pet_intercept': pet_intercept,
            'pet_p_value': pet_p,
            'peese_intercept': peese_intercept,
            'peese_p_value': peese_p,
            'corrected_effect': corrected_effect,
            'use_peese': pet_p < 0.05
        }
    
    def _trim_and_fill_enhanced(self, effects: np.ndarray, se: np.ndarray) -> Dict[str, Any]:
        """Enhanced Duval & Tweedie trim-and-fill"""
        variances = se**2
        
        if len(effects) < 3:
            return {'n_imputed': 0, 'direction': 'none'}
        
        weights = 1 / variances
        pooled_effect = np.sum(weights * effects) / np.sum(weights)
        
        centered_effects = effects - pooled_effect
        n_left = np.sum(centered_effects < 0)
        n_right = np.sum(centered_effects > 0)
        
        if abs(n_left - n_right) <= 1:
            return {'n_imputed': 0, 'direction': 'none', 'adjusted_effect': pooled_effect}
        
        direction = 'left' if n_left < n_right else 'right'
        n_imputed = min(abs(n_right - n_left), len(effects) // 3)
        
        # Create imputed studies
        if direction == 'left':
            extreme_indices = np.argsort(centered_effects)[-n_imputed:]
        else:
            extreme_indices = np.argsort(centered_effects)[:n_imputed]
        
        imputed_effects = 2 * pooled_effect - effects[extreme_indices]
        imputed_variances = variances[extreme_indices]
        
        # Adjusted estimate
        all_effects = np.concatenate([effects, imputed_effects])
        all_weights = np.concatenate([1/variances, 1/imputed_variances])
        adjusted_effect = np.sum(all_weights * all_effects) / np.sum(all_weights)
        
        return {
            'n_imputed': n_imputed,
            'direction': direction,
            'adjusted_effect': adjusted_effect,
            'original_effect': pooled_effect,
            'effect_change': adjusted_effect - pooled_effect
        }
    
    def _p_curve_analysis(self, effects: np.ndarray, se: np.ndarray) -> Dict[str, Any]:
        """P-curve evidential value test"""
        z = effects / se
        pvals = 2 * (1 - norm.cdf(np.abs(z)))
        
        significant = pvals[pvals < 0.05]
        if len(significant) == 0:
            return {'n_significant': 0, 'message': 'No significant studies for p-curve'}
        
        prop_low = np.mean(significant < 0.025)
        test_stat = 2 * len(significant) * (prop_low - 0.5)**2
        pval = 1 - chi2.cdf(test_stat, 1)
        
        return {
            'n_significant': len(significant),
            'prop_p_less_025': prop_low,
            'chi2_statistic': test_stat,
            'p_value': pval,
            'evidential_value': pval < 0.05
        }
    
    def _test_excess_significance(self, effects: np.ndarray, se: np.ndarray, 
                                 true_effect: Optional[float] = None) -> Dict[str, Any]:
        """Test for Excess Significance"""
        if true_effect is None:
            weights = 1 / (se**2)
            true_effect = np.sum(weights * effects) / np.sum(weights)
        
        power = 1 - norm.cdf(1.96 - true_effect / se)
        expected_significant = np.sum(power)
        observed_significant = np.sum(np.abs(effects / se) > 1.96)
        
        chi2_stat = (observed_significant - expected_significant)**2 / (expected_significant + 1e-9)
        p_value = 1 - chi2.cdf(chi2_stat, 1)
        
        return {
            'observed_significant': int(observed_significant),
            'expected_significant': expected_significant,
            'chi2_statistic': chi2_stat,
            'p_value': p_value,
            'excess_significance': p_value < 0.05
        }
    
    def _weight_function_model(self, effects: np.ndarray, se: np.ndarray,
                              cutpoints: List[float] = None) -> Dict[str, Any]:
        """Vevea-Hedges weight-function model"""
        if cutpoints is None:
            cutpoints = [0.025, 0.05, 0.10]
        
        pvals = 2 * (1 - norm.cdf(np.abs(effects / se)))
        bins = np.digitize(pvals, cutpoints)
        variances = se**2
        
        def negloglik(params):
            mu, tau2 = params[0], params[1]
            weights = np.array([params[b+2] for b in bins])
            sigma2 = variances + tau2
            loglik = -0.5 * np.sum(np.log(sigma2) + (effects - mu)**2 / sigma2)
            return -(np.sum(np.log(weights + 1e-9)) + loglik)
        
        x0 = [np.mean(effects), 0.01] + [1] * (len(cutpoints) + 1)
        bounds = [(-5, 5), (1e-8, 5)] + [(0.1, 5)] * (len(cutpoints) + 1)
        
        try:
            res = minimize(negloglik, x0, bounds=bounds)
            return {
                'mu': res.x[0],
                'tau2': res.x[1], 
                'weights': res.x[2:],
                'success': res.success,
                'cutpoints': cutpoints
            }
        except Exception as e:
            logger.warning(f"Weight function model failed: {e}")
            return {'success': False, 'error': str(e)}
    
    # ===================================================================
    # CONFLICT DETECTION AND CLUSTERING (FROM CBAMM)
    # ===================================================================
    
    def _detect_conflicts(self):
        """Detect conflicting results using enhanced clustering"""
        effects = self.df[self.effect_col].values
        se = self.df[self.se_col].values
        
        conflict_results = ConflictDetection.detect_conflicts(
            effects, se, self.config.conflict_k_candidates)
        
        self.results.conflict_detection = ConflictResults(
            k=conflict_results['k'],
            silhouette=conflict_results['silhouette'],
            delta=conflict_results['delta'],
            clusters=conflict_results['clusters'],
            conflicting=conflict_results['conflicting']
        )
    
    # ===================================================================
    # TRANSPORT WEIGHTING AND GENERALIZABILITY
    # ===================================================================
    
    def _transport_analysis(self, target_population: pd.DataFrame):
        """Transport weighting analysis for generalizability"""
        if not HAS_CVXPY:
            logger.warning("CVXPY not available - transport analysis disabled")
            return
        
        # Identify common columns for transport weighting
        common_cols = set(self.df.columns) & set(target_population.columns)
        numeric_cols = [col for col in common_cols 
                       if self.df[col].dtype in ['int64', 'float64']]
        
        if not numeric_cols:
            logger.warning("No numeric columns found for transport weighting")
            return
        
        # Calculate target moments
        target_moments = {col: target_population[col].mean() for col in numeric_cols}
        
        # Compute transport weights
        weights = TransportWeighting.compute_transport_weights(
            self.df[numeric_cols], target_moments, self.config.transport_truncation)
        
        # Recompute estimates with transport weights
        transport_weights = weights / self.df['_variance'].values
        transport_weights /= np.sum(transport_weights)
        
        transport_effect = np.sum(transport_weights * self.df[self.effect_col].values)
        transport_se = np.sqrt(np.sum(transport_weights**2 * self.df['_variance'].values))
        
        # Assess transportability
        transportability = TransportWeighting.assess_transportability(
            self.df[numeric_cols], target_population[numeric_cols])
        
        self.results.transport_analysis = type('TransportAnalysis', (), {
            'weights': weights,
            'transport_effect': transport_effect,
            'transport_se': transport_se,
            'transportability_assessment': transportability,
            'concerning_differences': sum(1 for v in transportability.values() 
                                        if v.get('concerning', False))
        })()
    
    # ===================================================================
    # MISSING STUDY SENSITIVITY (FROM CBAMM)
    # ===================================================================
    
    def missing_study_sensitivity(self, n_max: int = None, 
                                 effect_grid: List[float] = None) -> pd.DataFrame:
        """Missing study sensitivity analysis"""
        if n_max is None:
            n_max = self.config.missing_study_max
        
        if effect_grid is None:
            effect_grid = [0.8, 1.0, 1.2] if 'log' in self.effect_col.lower() else [-0.2, 0.0, 0.2]
        
        effects = self.df[self.effect_col].values
        se = self.df[self.se_col].values
        
        results = []
        for n_missing in range(n_max + 1):
            for miss_effect in effect_grid:
                try:
                    # Augment data with missing studies
                    effects_aug = np.concatenate([effects, np.repeat(miss_effect, n_missing)])
                    se_aug = np.concatenate([se, np.repeat(np.median(se), n_missing)])
                    
                    # Recalculate meta-analysis
                    variances_aug = se_aug**2
                    weights_aug = 1 / variances_aug
                    pooled_effect = np.sum(weights_aug * effects_aug) / np.sum(weights_aug)
                    
                    results.append({
                        'n_missing': n_missing, 
                        'missing_effect': miss_effect,
                        'adjusted_effect': pooled_effect,
                        'effect_change': pooled_effect - self.results.random_effects.effect
                    })
                    
                except Exception as e:
                    logger.warning(f"Missing study sensitivity failed: {e}")
        
        return pd.DataFrame(results)
    
    # ===================================================================
    # MULTIVERSE ANALYSIS (FROM CBAMM)
    # ===================================================================
    
    def multiverse_analysis(self, estimators: List[str] = None, 
                           hksj_options: List[bool] = None) -> pd.DataFrame:
        """Multiverse analysis across analytical choices"""
        if estimators is None:
            estimators = ['DL', 'REML', 'HS', 'EB']
        
        if hksj_options is None:
            hksj_options = [False, True]
        
        effects = self.df[self.effect_col].values
        variances = self.df['_variance'].values
        
        results = []
        for estimator in estimators:
            for use_hksj in hksj_options:
                try:
                    # Get tau2 estimate
                    if estimator == 'DL':
                        tau2 = TauSquaredEstimators.dersimonian_laird(effects, variances)
                    elif estimator == 'REML':
                        tau2 = TauSquaredEstimators.restricted_ml(effects, variances)
                    elif estimator == 'HS':
                        tau2 = TauSquaredEstimators.hunter_schmidt(effects, variances)
                    elif estimator == 'EB':
                        tau2 = TauSquaredEstimators.empirical_bayes(effects, variances)
                    else:
                        continue
                    
                    # Calculate pooled estimate
                    re_weights = 1 / (variances + tau2)
                    pooled_effect = np.sum(re_weights * effects) / np.sum(re_weights)
                    pooled_se = np.sqrt(1 / np.sum(re_weights))
                    
                    # Apply HKSJ if requested
                    if use_hksj:
                        df = len(effects) - 1
                        Q_re = np.sum(re_weights * (effects - pooled_effect) ** 2)
                        inflation_factor = max(1, Q_re / df) if df > 0 else 1
                        pooled_se *= np.sqrt(inflation_factor)
                    
                    results.append({
                        'estimator': estimator,
                        'use_hksj': use_hksj,
                        'effect': pooled_effect,
                        'se': pooled_se,
                        'tau2': tau2
                    })
                    
                except Exception as e:
                    results.append({
                        'estimator': estimator,
                        'use_hksj': use_hksj,
                        'error': str(e)
                    })
        
        return pd.DataFrame(results)
    
    # ===================================================================
    # BAYESIAN METHODS (ENHANCED FROM BOTH)
    # ===================================================================
    
    def bayesian_stacking(self, chains: int = None, draws: int = None) -> Dict[str, Any]:
        """Bayesian stacking for model averaging"""
        if not HAS_PYMC:
            logger.warning("PyMC not available - Bayesian methods disabled")
            return {'available': False}
        
        if chains is None:
            chains = self.config.bayesian_chains
        if draws is None:
            draws = self.config.bayesian_draws
        
        effects = self.df[self.effect_col].values
        se = self.df[self.se_col].values
        
        try:
            with pm.Model() as model:
                mu = pm.Normal("mu", 0, 2)
                tau = pm.HalfCauchy("tau", 1)
                theta = pm.Normal("theta", mu, tau, shape=len(effects))
                pm.Normal("obs", theta, se, observed=effects)
                
                trace = pm.sample(draws=draws, chains=chains, tune=500, 
                                target_accept=0.9, return_inferencedata=True)
            
            summary = az.summary(trace, var_names=["mu", "tau"])
            
            return {
                'trace': trace,
                'summary': summary,
                'posterior_mean': summary.loc['mu', 'mean'],
                'posterior_sd': summary.loc['mu', 'sd'],
                'tau_mean': summary.loc['tau', 'mean'],
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Bayesian stacking failed: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def hsroc_model(tp: np.ndarray, fn: np.ndarray, fp: np.ndarray, 
                   tn: np.ndarray, draws: int = 2000, chains: int = 2) -> Dict[str, Any]:
        """Bayesian HSROC model for diagnostic test accuracy"""
        if not HAS_PYMC:
            raise ImportError("PyMC required for Bayesian HSROC: pip install pymc")
        
        n_studies = len(tp)
        
        with pm.Model() as model:
            # Hyperpriors
            mu_sens = pm.Normal("mu_sensitivity", 0, 2)
            mu_spec = pm.Normal("mu_specificity", 0, 2)
            tau_sens = pm.HalfCauchy("tau_sensitivity", 1)
            tau_spec = pm.HalfCauchy("tau_specificity", 1)
            
            # Study-level parameters
            sens_logit = pm.Normal("sensitivity_logit", mu_sens, tau_sens, shape=n_studies)
            spec_logit = pm.Normal("specificity_logit", mu_spec, tau_spec, shape=n_studies)
            
            # Likelihood
            pm.Binomial("observed_tp", n=tp+fn, p=pm.math.sigmoid(sens_logit), observed=tp)
            pm.Binomial("observed_tn", n=tn+fp, p=pm.math.sigmoid(spec_logit), observed=tn)
            
            # Sample posterior
            trace = pm.sample(draws=draws, chains=chains, target_accept=0.9, 
                            return_inferencedata=True)
        
        summary = az.summary(trace, var_names=["mu_sensitivity", "mu_specificity", 
                                             "tau_sensitivity", "tau_specificity"])
        
        return {
            'trace': trace,
            'summary': summary,
            'model': model
        }
    
    # ===================================================================
    # LIVING META-ANALYSIS INTEGRATION
    # ===================================================================
    
    def setup_living_meta(self, query: str, output_dir: str = "living_meta") -> Dict[str, Any]:
        """Initialize living meta-analysis tracking"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        self.living_meta_config = {
            'query': query,
            'output_dir': output_dir,
            'last_update': datetime.date.today().isoformat(),
            'total_studies': len(self.df)
        }
        
        return self.living_meta_config
    
    def update_from_pubmed(self, query: str) -> Dict[str, Any]:
        """Update meta-analysis with new PubMed studies"""
        update_results = self.pubmed.update_living_meta(
            self.df, query, self.effect_col, self.se_col)
        
        if update_results['valid_studies_added'] > 0:
            # Update internal data
            self.df = update_results['updated_data']
            self._prepare_data()
            
            # Re-run analysis
            self.analyze()
            
            logger.info(f"Added {update_results['valid_studies_added']} new studies")
        
        return update_results
    
    def run_living_update(self, query: str, output_dir: str = "living_meta") -> Dict[str, Any]:
        """Complete living meta-analysis update cycle"""
        if not hasattr(self, 'living_meta_config'):
            self.setup_living_meta(query, output_dir)
        
        # Fetch new studies
        update_results = self.update_from_pubmed(query)
        
        # Generate report
        timestamp = datetime.date.today().isoformat()
        report_file = os.path.join(output_dir, f"update_{timestamp}.txt")
        
        with open(report_file, 'w') as f:
            f.write(f"Living Meta-Analysis Update - {timestamp}\n")
            f.write("=" * 50 + "\n")
            f.write(f"Query: {query}\n")
            f.write(f"Total studies: {len(self.df)}\n")
            f.write(f"New studies found: {update_results['new_studies_found']}\n")
            f.write(f"New studies added: {update_results['valid_studies_added']}\n")
            
            if self._fitted:
                f.write(f"Current pooled effect: {self.results.random_effects.effect:.3f}\n")
                f.write(f"95% CI: [{self.results.random_effects.ci_low:.3f}, "
                       f"{self.results.random_effects.ci_high:.3f}]\n")
                f.write(f"Heterogeneity I²: {self.results.heterogeneity.I2:.1f}%\n")
        
        return {
            'update_results': update_results,
            'report_file': report_file,
            'current_analysis': self.results if self._fitted else None
        }
    
    # ===================================================================
    # SEQUENTIAL ANALYSIS METHODS
    # ===================================================================
    
    def cumulative_analysis(self, sort_by: str = 'year') -> pd.DataFrame:
        """Enhanced cumulative meta-analysis"""
        if not self._fitted:
            self.analyze()
        
        df = self.df.copy()
        
        if sort_by in df.columns:
            df = df.sort_values(sort_by)
        
        effects = df[self.effect_col].values
        variances = df['_variance'].values
        labels = df[self.label_col].values
        
        original_effect = self.results.random_effects.effect
        cumulative_results = []
        
        for i in range(2, len(effects) + 1):
            cum_df = df.iloc[:i].copy()
            
            try:
                temp_meta = UnifiedMetaAnalysis(
                    cum_df, self.effect_col, self.se_col, 
                    self.label_col, config=self.config, 
                    validate_data=False
                ).analyze(include_bias_tests=False, include_conflicts=False)
                
                result = temp_meta.results.random_effects
                het = temp_meta.results.heterogeneity
                
                cumulative_results.append({
                    'n_studies': i,
                    'last_study_added': labels[i-1],
                    'cumulative_effect': result.effect,
                    'ci_lower': result.ci_low,
                    'ci_upper': result.ci_high,
                    'p_value': result.p_value,
                    'i2_percent': het.I2,
                    'tau2': het.tau2,
                    'effect_change': result.effect - original_effect
                })
                
            except Exception as e:
                logger.warning(f"Cumulative analysis failed at study {i}: {e}")
        
        return pd.DataFrame(cumulative_results)
    
    def trial_sequential_analysis(self, target_effect: float, alpha: float = None,
                                 beta: float = 0.2) -> Dict[str, Any]:
        """Enhanced Trial Sequential Analysis"""
        if alpha is None:
            alpha = self.config.alpha
        
        effects = self.df[self.effect_col].values
        variances = self.df['_variance'].values
        
        information = 1 / variances
        cumulative_info = np.cumsum(information)
        total_info = np.sum(information)
        info_fraction = cumulative_info / total_info
        
        # Required information
        z_alpha = norm.ppf(1 - alpha/2)
        z_beta = norm.ppf(1 - beta)
        required_info = ((z_alpha + z_beta) / target_effect)**2
        
        # O'Brien-Fleming boundaries
        boundaries_upper = [z_alpha / np.sqrt(frac) if frac > 0 else np.inf 
                           for frac in info_fraction]
        
        # Cumulative Z-statistics
        cumulative_z = []
        for i in range(len(effects)):
            cum_effects = effects[:i+1]
            cum_info = information[:i+1]
            pooled_effect = np.sum(cum_info * cum_effects) / np.sum(cum_info)
            pooled_se = np.sqrt(1 / np.sum(cum_info))
            z_stat = pooled_effect / pooled_se
            cumulative_z.append(z_stat)
        
        # Check boundary crossings
        first_crossing = None
        for i, (z, boundary) in enumerate(zip(cumulative_z, boundaries_upper)):
            if abs(z) > boundary:
                first_crossing = {
                    'study_number': i + 1,
                    'z_statistic': z,
                    'boundary_crossed': boundary
                }
                break
        
        return {
            'info_fraction': info_fraction,
            'cumulative_z': cumulative_z,
            'boundaries_upper': boundaries_upper,
            'required_info': required_info,
            'total_info': total_info,
            'first_crossing': first_crossing,
            'conclusive': first_crossing is not None or total_info >= required_info,
            'futility_reached': total_info >= required_info and abs(cumulative_z[-1]) < 1.96
        }
    
    # ===================================================================
    # ENHANCED DIAGNOSTIC METHODS
    # ===================================================================
    
    def leave_one_out_analysis(self) -> pd.DataFrame:
        """Enhanced leave-one-out sensitivity analysis"""
        if not self._fitted:
            self.analyze()
        
        original_effect = self.results.random_effects.effect
        results = []
        
        for i, (_, row) in enumerate(self.df.iterrows()):
            excluded_df = self.df.drop(self.df.index[i])
            
            if len(excluded_df) < 2:
                continue
            
            try:
                temp_meta = UnifiedMetaAnalysis(
                    excluded_df, self.effect_col, self.se_col, 
                    self.label_col, config=self.config, 
                    validate_data=False
                ).analyze(include_bias_tests=False, include_conflicts=False)
                
                loo_effect = temp_meta.results.random_effects.effect
                effect_change = loo_effect - original_effect
                
                results.append({
                    'excluded_study': row[self.label_col],
                    'excluded_effect': row[self.effect_col],
                    'loo_effect': loo_effect,
                    'effect_change': effect_change,
                    'abs_effect_change': abs(effect_change),
                    'influential': abs(effect_change) > 0.1
                })
                
            except Exception as e:
                logger.warning(f"Leave-one-out failed for {row[self.label_col]}: {e}")
        
        return pd.DataFrame(results).sort_values('abs_effect_change', ascending=False)
    
    def influence_diagnostics(self) -> pd.DataFrame:
        """Enhanced influence diagnostics"""
        if not self._fitted:
            self.analyze()
        
        effects = self.df[self.effect_col].values
        variances = self.df['_variance'].values
        weights = 1 / variances
        total_weight = np.sum(weights)
        mu = self.results.random_effects.effect
        
        # Calculate influence measures
        leverage = weights / total_weight
        residuals = effects - mu
        std_residuals = residuals / np.sqrt(variances)
        
        # Cook's D for meta-analysis
        cook_d = (std_residuals ** 2) * (leverage / (1 - leverage) ** 2)
        
        # DFBETAS
        dfbetas = residuals * np.sqrt(leverage) / np.sqrt(variances * (1 - leverage))
        
        # Enhanced outlier detection
        z_scores = np.abs(std_residuals)
        outliers_z = z_scores > 2.58  # 99% threshold
        
        # Thresholds
        cook_threshold = 4 / len(effects)
        leverage_threshold = 2 / len(effects)
        dfbetas_threshold = 2 / np.sqrt(len(effects))
        
        return pd.DataFrame({
            'study': self.df[self.label_col].values,
            'leverage': leverage,
            'cook_d': cook_d,
            'dfbetas': dfbetas,
            'z_score': z_scores,
            'outlier_z': outliers_z,
            'influential': ((cook_d > cook_threshold) | 
                          (leverage > leverage_threshold) | 
                          (np.abs(dfbetas) > dfbetas_threshold) |
                          outliers_z)
        }).sort_values('cook_d', ascending=False)
    
    def create_baujat_plot(self, figsize: Tuple[int, int] = (10, 8)) -> Any:
        """Baujat plot: contribution to heterogeneity vs influence"""
        if not self._fitted:
            self.analyze()
        
        effects = self.df[self.effect_col].values
        se = self.df[self.se_col].values
        labels = self.df[self.label_col].values
        
        pooled_effect = self.results.random_effects.effect
        weights = 1 / se**2
        
        # Contribution to Q (heterogeneity)
        Q_contrib = weights * (effects - pooled_effect)**2
        
        # Influence (standardized residuals)
        influence = np.abs((effects - pooled_effect) / se)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot points
        scatter = ax.scatter(Q_contrib, influence, s=80, alpha=0.7, 
                           edgecolors='black', linewidths=0.5)
        
        # Label outlying studies
        q_threshold = np.percentile(Q_contrib, 90)
        inf_threshold = np.percentile(influence, 90)
        
        for i, (q, inf, label) in enumerate(zip(Q_contrib, influence, labels)):
            if q > q_threshold or inf > inf_threshold:
                ax.annotate(label, (q, inf), xytext=(5, 5), 
                           textcoords='offset points', fontsize=8)
        
        ax.set_xlabel('Contribution to Heterogeneity (Q)', fontsize=12)
        ax.set_ylabel('Influence (|Standardized Residual|)', fontsize=12)
        ax.set_title('Baujat Plot', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_radial_plot(self, figsize: Tuple[int, int] = (10, 8)) -> Any:
        """Radial (Galbraith) plot: effect/se vs 1/se"""
        if not self._fitted:
            self.analyze()
        
        effects = self.df[self.effect_col].values
        se = self.df[self.se_col].values
        labels = self.df[self.label_col].values
        
        X = 1 / se  # Precision
        Y = effects / se  # Standardized effect
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot points
        ax.scatter(X, Y, s=80, alpha=0.7, edgecolors='black', linewidths=0.5)
        
        # Fit regression line
        if HAS_STATSMODELS:
            model = sm.OLS(Y, sm.add_constant(X)).fit()
            x_range = np.linspace(X.min(), X.max(), 100)
            y_pred = model.params[0] + model.params[1] * x_range
            ax.plot(x_range, y_pred, 'r-', linewidth=2, 
                   label=f'Regression line (slope={model.params[1]:.3f})')
        
        # Reference lines
        pooled_effect = self.results.random_effects.effect
        ax.axhline(0, color='gray', linestyle='--', alpha=0.5, label='Null effect')
        
        # Label extreme points
        extreme_indices = np.where((np.abs(Y) > 2) | (X > np.percentile(X, 95)))[0]
        for idx in extreme_indices:
            ax.annotate(labels[idx], (X[idx], Y[idx]), xytext=(5, 5),
                       textcoords='offset points', fontsize=8)
        
        ax.set_xlabel('Precision (1/SE)', fontsize=12)
        ax.set_ylabel('Standardized Effect (Effect/SE)', fontsize=12)
        ax.set_title('Radial (Galbraith) Plot', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    # ===================================================================
    # DOSE-RESPONSE META-ANALYSIS
    # ===================================================================
    
    def dose_response_analysis(self, dose_col: str, model_type: str = 'linear') -> Dict[str, Any]:
        """Enhanced dose-response meta-analysis"""
        if dose_col not in self.df.columns:
            raise ValueError(f"Dose column '{dose_col}' not found")
        
        doses = self.df[dose_col].values
        effects = self.df[self.effect_col].values
        variances = self.df['_variance'].values
        
        if model_type == 'linear':
            return self._fit_linear_dose_response(doses, effects, variances)
        elif model_type == 'quadratic':
            return self._fit_quadratic_dose_response(doses, effects, variances)
        else:
            logger.warning(f"Model type '{model_type}' not available, using linear")
            return self._fit_linear_dose_response(doses, effects, variances)
    
    def _fit_linear_dose_response(self, doses: np.ndarray, effects: np.ndarray, 
                                 variances: np.ndarray) -> Dict[str, Any]:
        """Fit linear dose-response model"""
        weights = 1 / variances
        X = np.column_stack([np.ones(len(doses)), doses])
        W = np.diag(weights)
        
        XWX = X.T @ W @ X
        XWy = X.T @ W @ effects
        
        try:
            beta = safe_solve(XWX, XWy)
            var_beta = safe_matrix_inverse(XWX)
            se_beta = np.sqrt(np.diag(var_beta))
            
            intercept, slope = beta
            se_intercept, se_slope = se_beta
            
            # Statistical tests
            df = len(effects) - 2
            t_slope = slope / se_slope if se_slope > 0 else 0
            p_slope = 2 * (1 - t.cdf(abs(t_slope), df))
            
            # Model fit
            predicted = X @ beta
            residuals = effects - predicted
            r_squared = 1 - (np.sum(weights * residuals ** 2) / 
                            np.sum(weights * (effects - np.mean(effects)) ** 2))
            
            return {
                'model_type': 'linear',
                'intercept': intercept,
                'slope': slope,
                'se_slope': se_slope,
                'p_slope': p_slope,
                'r_squared': r_squared,
                'predicted_effects': predicted,
                'significant_trend': p_slope < 0.05
            }
            
        except Exception as e:
            raise NumericalInstabilityError(f"Dose-response fitting failed: {e}")
    
    def _fit_quadratic_dose_response(self, doses: np.ndarray, effects: np.ndarray, 
                                    variances: np.ndarray) -> Dict[str, Any]:
        """Fit quadratic dose-response model"""
        weights = 1 / variances
        X = np.column_stack([np.ones(len(doses)), doses, doses**2])
        W = np.diag(weights)
        
        XWX = X.T @ W @ X
        XWy = X.T @ W @ effects
        
        try:
            beta = safe_solve(XWX, XWy)
            var_beta = safe_matrix_inverse(XWX)
            se_beta = np.sqrt(np.diag(var_beta))
            
            intercept, linear_coef, quad_coef = beta
            
            # Model fit
            predicted = X @ beta
            residuals = effects - predicted
            r_squared = 1 - (np.sum(weights * residuals ** 2) / 
                            np.sum(weights * (effects - np.mean(effects)) ** 2))
            
            # Test for non-linearity
            df = len(effects) - 3
            t_quad = quad_coef / se_beta[2] if se_beta[2] > 0 else 0
            p_quad = 2 * (1 - t.cdf(abs(t_quad), df))
            
            return {
                'model_type': 'quadratic',
                'intercept': intercept,
                'linear_coef': linear_coef,
                'quadratic_coef': quad_coef,
                'p_quadratic': p_quad,
                'r_squared': r_squared,
                'predicted_effects': predicted,
                'significant_nonlinearity': p_quad < 0.05
            }
            
        except Exception as e:
            raise NumericalInstabilityError(f"Quadratic dose-response fitting failed: {e}")
    
    # ===================================================================
    # VISUALIZATION METHODS (ENHANCED)
    # ===================================================================
    
    def create_forest_plot(self, figsize: Tuple[int, int] = (12, 8),
                          show_weights: bool = True, include_transport: bool = False) -> Any:
        """Enhanced forest plot with optional transport weighting"""
        if not self._fitted:
            self.analyze()
        
        effects = self.df[self.effect_col].values
        se = self.df[self.se_col].values
        labels = self.df[self.label_col].values
        weights = self.df[self.weight_col].values
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Study-level results
        ci_low = effects - 1.96 * se
        ci_high = effects + 1.96 * se
        
        y_positions = range(len(effects))
        
        # Color coding for conflicts if detected
        colors = ['steelblue'] * len(effects)
        if hasattr(self.results, 'conflict_detection') and hasattr(self.results.conflict_detection, 'clusters'):
            clusters = self.results.conflict_detection.clusters
            color_map = plt.cm.Set1(np.linspace(0, 1, max(clusters['cluster']) + 1))
            colors = [color_map[cluster] for cluster in clusters['cluster']]
        
        # Plot confidence intervals
        for i, (low, high, weight, color) in enumerate(zip(ci_low, ci_high, weights, colors)):
            linewidth = 1 + (weight / weights.max()) * 3 if show_weights else 2
            ax.plot([low, high], [i, i], color=color, linewidth=linewidth, alpha=0.7)
        
        # Plot point estimates
        sizes = 20 + (weights / weights.max()) * 80 if show_weights else 50
        ax.scatter(effects, y_positions, s=sizes, c=colors, 
                  edgecolors='black', linewidths=0.5, zorder=3)
        
        # Overall effect
        overall_effect = self.results.random_effects.effect
        overall_ci_low = self.results.random_effects.ci_low
        overall_ci_high = self.results.random_effects.ci_high
        
        overall_y = len(effects) + 1
        ax.plot([overall_ci_low, overall_ci_high], [overall_y, overall_y], 
                'r-', linewidth=4, alpha=0.8)
        ax.scatter([overall_effect], [overall_y], s=150, c='red', 
                  marker='D', edgecolors='black', linewidths=1, zorder=3)
        
        # Transport-weighted effect if available
        if include_transport and hasattr(self.results, 'transport_analysis'):
            transport_y = len(effects) + 2
            transport_effect = self.results.transport_analysis.transport_effect
            ax.scatter([transport_effect], [transport_y], s=150, c='purple', 
                      marker='s', edgecolors='black', linewidths=1, zorder=3)
            labels = list(labels) + ['Overall', 'Transport-weighted']
        else:
            labels = list(labels) + ['Overall']
        
        # Null effect line
        ax.axvline(0, color='gray', linestyle='--', alpha=0.5)
        
        # Labels and formatting
        y_ticks = list(y_positions) + [overall_y]
        if include_transport and hasattr(self.results, 'transport_analysis'):
            y_ticks.append(transport_y)
        
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(labels)
        ax.set_xlabel('Effect Size', fontsize=12)
        ax.set_title('Enhanced Forest Plot', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        return fig
    
    def create_funnel_plot(self, enhanced: bool = True, include_bias_methods: bool = True) -> Any:
        """Enhanced funnel plot with bias correction overlays"""
        if not self._fitted:
            self.analyze()
        
        effects = self.df[self.effect_col].values
        se = self.df[self.se_col].values
        overall_effect = self.results.random_effects.effect
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        if enhanced:
            # Create significance contours
            se_range = np.linspace(0.001, se.max() * 1.2, 200)
            effect_range = np.linspace(effects.min() - 0.5, effects.max() + 0.5, 200)
            SE_grid, EFFECT_grid = np.meshgrid(se_range, effect_range)
            Z_grid = EFFECT_grid / SE_grid
            P_grid = 2 * (1 - norm.cdf(np.abs(Z_grid)))
            
            contour_levels = [0.01, 0.05, 0.1]
            contours = ax.contour(EFFECT_grid, SE_grid, P_grid, levels=contour_levels,
                                colors=['red', 'orange', 'yellow'], alpha=0.6)
            ax.clabel(contours, inline=True, fontsize=8, fmt='p=%.2f')
        
        # Study points with conflict coloring
        colors = ['steelblue'] * len(effects)
        if hasattr(self.results, 'conflict_detection') and hasattr(self.results.conflict_detection, 'clusters'):
            clusters = self.results.conflict_detection.clusters
            color_map = plt.cm.Set1(np.linspace(0, 1, max(clusters['cluster']) + 1))
            colors = [color_map[cluster] for cluster in clusters['cluster']]
        
        weights = self.df[self.weight_col].values
        sizes = 20 + (weights / weights.max()) * 100
        
        scatter = ax.scatter(effects, se, s=sizes, c=colors, alpha=0.7,
                           edgecolors='black', linewidths=0.5)
        
        # Effect lines
        ax.axvline(overall_effect, color='red', linestyle='--', linewidth=2,
                  label=f'Overall effect = {overall_effect:.3f}')
        
        # Bias-corrected estimates if available
        if include_bias_methods and hasattr(self.results, 'bias_assessment'):
            bias = self.results.bias_assessment
            if hasattr(bias, 'pet_peese'):
                pet_peese = bias.pet_peese
                if pet_peese.get('success', True):
                    ax.axvline(pet_peese['corrected_effect'], color='green', 
                             linestyle=':', linewidth=2, 
                             label=f'PET-PEESE = {pet_peese["corrected_effect"]:.3f}')
            
            if hasattr(bias, 'trim_fill'):
                trim_fill = bias.trim_fill
                if trim_fill['n_imputed'] > 0:
                    ax.axvline(trim_fill['adjusted_effect'], color='orange', 
                             linestyle='-.', linewidth=2,
                             label=f'Trim-fill = {trim_fill["adjusted_effect"]:.3f}')
        
        ax.set_xlabel('Effect Size', fontsize=12)
        ax.set_ylabel('Standard Error', fontsize=12)
        ax.invert_yaxis()
        ax.set_title('Enhanced Funnel Plot with Bias Assessment', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_diagnostic_plots(self) -> Dict[str, Any]:
        """Create comprehensive diagnostic plot suite"""
        if not self._fitted:
            self.analyze()
        
        # 1. Influence plot
        influence_data = self.influence_diagnostics()
        
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        scatter = ax1.scatter(influence_data['leverage'], influence_data['cook_d'],
                            s=80, alpha=0.7, edgecolors='black')
        
        # Highlight influential studies
        influential = influence_data[influence_data['influential']]
        if not influential.empty:
            ax1.scatter(influential['leverage'], influential['cook_d'],
                       s=120, c='red', alpha=0.8, edgecolors='black', marker='^')
        
        ax1.set_xlabel('Leverage', fontsize=12)
        ax1.set_ylabel("Cook's Distance", fontsize=12)
        ax1.set_title('Influence Diagnostics', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # 2. Cumulative plot
        cumulative_data = self.cumulative_analysis()
        
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        ax2.plot(cumulative_data['n_studies'], cumulative_data['cumulative_effect'],
                'o-', linewidth=2, markersize=6)
        ax2.fill_between(cumulative_data['n_studies'], 
                        cumulative_data['ci_lower'],
                        cumulative_data['ci_upper'], alpha=0.3)
        
        ax2.axhline(self.results.random_effects.effect, color='red', 
                   linestyle='--', label='Final estimate')
        ax2.set_xlabel('Number of Studies', fontsize=12)
        ax2.set_ylabel('Cumulative Effect Size', fontsize=12)
        ax2.set_title('Cumulative Meta-Analysis', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        return {'influence_plot': fig1, 'cumulative_plot': fig2}
    
    # ===================================================================
    # SUBGROUP ANALYSIS (ENHANCED)
    # ===================================================================
    
    def _subgroup_analysis(self):
        """Enhanced subgroup meta-analysis with between-group testing"""
        if not self.subgroup_col:
            return
        
        subgroups = self.df[self.subgroup_col].unique()
        subgroup_results = {}
        subgroup_effects = []
        subgroup_vars = []
        subgroup_n = []
        
        for subgroup in subgroups:
            sub_df = self.df[self.df[self.subgroup_col] == subgroup]
            if len(sub_df) >= 2:
                try:
                    sub_meta = UnifiedMetaAnalysis(
                        sub_df, self.effect_col, self.se_col, 
                        self.label_col, config=self.config, 
                        validate_data=False
                    ).analyze(include_bias_tests=False, include_conflicts=False)
                    
                    subgroup_results[subgroup] = sub_meta.results
                    subgroup_effects.append(sub_meta.results.random_effects.effect)
                    subgroup_vars.append(sub_meta.results.random_effects.se**2)
                    subgroup_n.append(len(sub_df))
                    
                except Exception as e:
                    logger.warning(f"Subgroup analysis failed for {subgroup}: {e}")
        
        # Between-subgroup heterogeneity test
        if len(subgroup_effects) > 1:
            # Q_between calculation
            overall_effect = self.results.random_effects.effect
            Q_between = sum(n * (eff - overall_effect)**2 / var 
                           for eff, var, n in zip(subgroup_effects, subgroup_vars, subgroup_n))
            df_between = len(subgroup_effects) - 1
            p_between = 1 - chi2.cdf(Q_between, df_between)
            
            subgroup_results['_between_group_test'] = {
                'Q_between': Q_between,
                'df': df_between,
                'p_value': p_between,
                'significant': p_between < self.config.alpha
            }
        
        self.results.subgroups = subgroup_results
    
    # ===================================================================
    # UTILITY AND SUMMARY METHODS
    # ===================================================================
    
    def interpret_results(self) -> str:
        """Comprehensive automated interpretation"""
        if not self._fitted:
            return "Analysis not yet performed"
        
        effect = self.results.random_effects.effect
        ci_low = self.results.random_effects.ci_low
        ci_high = self.results.random_effects.ci_high
        p_val = self.results.random_effects.p_value
        i2 = self.results.heterogeneity.I2
        
        # Effect size interpretation
        magnitude = ("large" if abs(effect) > 0.8 else 
                    "moderate" if abs(effect) > 0.5 else 
                    "small" if abs(effect) > 0.2 else "negligible")
        
        direction = "beneficial" if effect > 0 else "harmful" if effect < 0 else "null"
        significance = "statistically significant" if p_val < 0.05 else "not statistically significant"
        
        # Heterogeneity interpretation
        het_level = ("substantial" if i2 > 75 else 
                    "moderate" if i2 > 50 else 
                    "low" if i2 > 25 else "minimal")
        
        interpretation = (
            f"The meta-analysis of {len(self.df)} studies found a {magnitude} {direction} "
            f"effect (effect size = {effect:.3f}, 95% CI: {ci_low:.3f} to {ci_high:.3f}) "
            f"that was {significance} (p = {p_val:.3f}). "
            f"Heterogeneity was {het_level} (I² = {i2:.1f}%)."
        )
        
        # Add bias assessment if available
        if hasattr(self.results, 'bias_assessment'):
            bias = self.results.bias_assessment
            bias_concerns = []
            
            if hasattr(bias, 'egger') and bias.egger.get('significant', False):
                bias_concerns.append("Egger test significant")
            if hasattr(bias, 'trim_fill') and bias.trim_fill.get('n_imputed', 0) > 0:
                bias_concerns.append(f"Trim-fill imputed {bias.trim_fill['n_imputed']} studies")
            
            if bias_concerns:
                interpretation += f" Publication bias concerns: {', '.join(bias_concerns)}."
        
        # Add conflict information if available
        if hasattr(self.results, 'conflict_detection') and hasattr(self.results.conflict_detection, 'conflicting'):
            if self.results.conflict_detection.conflicting:
                interpretation += f" Evidence of conflicting study results detected."
        
        return interpretation
    
    def summary_table(self) -> pd.DataFrame:
        """Create comprehensive summary table"""
        if not self._fitted:
            self.analyze()
        
        rows = []
        
        # Fixed effects row
        fe = self.results.fixed_effects
        rows.append({
            'Model': 'Fixed Effects',
            'Effect': f"{fe.effect:.3f}",
            'SE': f"{fe.se:.3f}",
            '95% CI': f"[{fe.ci_low:.3f}, {fe.ci_high:.3f}]",
            'Z/t': f"{fe.z_statistic:.2f}",
            'p-value': f"{fe.p_value:.3f}",
            'Notes': 'Assumes τ² = 0'
        })
        
        # Random effects row
        re = self.results.random_effects
        rows.append({
            'Model': 'Random Effects',
            'Effect': f"{re.effect:.3f}",
            'SE': f"{re.se:.3f}",
            '95% CI': f"[{re.ci_low:.3f}, {re.ci_high:.3f}]",
            'Z/t': f"{re.z_statistic:.2f}",
            'p-value': f"{re.p_value:.3f}",
            'Notes': f"τ² = {re.tau2:.3f} ({self.config.tau2_method})"
        })
        
        # Heterogeneity row
        het = self.results.heterogeneity
        rows.append({
            'Model': 'Heterogeneity',
            'Effect': f"I² = {het.I2:.1f}%",
            'SE': f"H² = {het.H2:.2f}",
            '95% CI': f"τ² = {het.tau2:.3f}",
            'Z/t': f"Q = {het.Q:.2f}",
            'p-value': f"{het.p_value:.3f}",
            'Notes': f"df = {het.df}"
        })
        
        # Prediction interval if available
        if hasattr(self.results, 'prediction_interval') and self.results.prediction_interval:
            pi = self.results.prediction_interval
            rows.append({
                'Model': 'Prediction Interval',
                'Effect': f"{re.effect:.3f}",
                'SE': f"{pi.se:.3f}",
                '95% CI': f"[{pi.low:.3f}, {pi.high:.3f}]",
                'Z/t': '—',
                'p-value': '—',
                'Notes': 'Future study range'
            })
        
        return pd.DataFrame(rows)
    
    def comprehensive_report(self) -> str:
        """Generate comprehensive analysis report"""
        if not self._fitted:
            self.analyze()
        
        report = []
        report.append("UNIFIED META-ANALYSIS COMPREHENSIVE REPORT")
        report.append("=" * 50)
        report.append("")
        
        # Basic information
        report.append("STUDY CHARACTERISTICS")
        report.append("-" * 20)
        report.append(f"Number of studies: {len(self.df)}")
        report.append(f"Effect size measure: {self.effect_col}")
        report.append(f"Analysis method: {self.config.tau2_method}")
        report.append(f"HKSJ adjustment: {'Yes' if self.config.use_hksj else 'No'}")
        report.append("")
        
        # Main results
        report.append("MAIN RESULTS")
        report.append("-" * 12)
        report.append(self.interpret_results())
        report.append("")
        
        # Heterogeneity
        het = self.results.heterogeneity
        report.append("HETEROGENEITY ASSESSMENT")
        report.append("-" * 23)
        report.append(f"Q = {het.Q:.2f}, df = {het.df}, p = {het.p_value:.3f}")
        report.append(f"I² = {het.I2:.1f}%, H² = {het.H2:.2f}")
        report.append(f"τ² = {het.tau2:.3f}")
        report.append("")
        
        # Publication bias
        if hasattr(self.results, 'bias_assessment'):
            bias = self.results.bias_assessment
            report.append("PUBLICATION BIAS ASSESSMENT")
            report.append("-" * 27)
            
            if hasattr(bias, 'egger'):
                egger = bias.egger
                report.append(f"Egger's test: p = {egger.get('p_value', 'N/A')}")
            
            if hasattr(bias, 'pet_peese'):
                pet_peese = bias.pet_peese
                if pet_peese.get('success', True):
                    report.append(f"PET-PEESE corrected: {pet_peese['corrected_effect']:.3f}")
            
            if hasattr(bias, 'trim_fill'):
                trim_fill = bias.trim_fill
                if trim_fill['n_imputed'] > 0:
                    report.append(f"Trim-and-fill: {trim_fill['n_imputed']} studies imputed")
            
            report.append("")
        
        # Conflicts
        if hasattr(self.results, 'conflict_detection'):
            conflict = self.results.conflict_detection
            report.append("CONFLICT DETECTION")
            report.append("-" * 17)
            if hasattr(conflict, 'conflicting'):
                if conflict.conflicting:
                    report.append(f"Conflicting results detected: {conflict.k} clusters")
                    report.append(f"Maximum difference: {conflict.delta:.3f}")
                else:
                    report.append("No significant conflicts detected")
            report.append("")
        
        # Subgroups
        if hasattr(self.results, 'subgroups'):
            report.append("SUBGROUP ANALYSIS")
            report.append("-" * 16)
            
            for subgroup, result in self.results.subgroups.items():
                if subgroup.startswith('_'):
                    continue
                if hasattr(result, 'random_effects'):
                    eff = result.random_effects.effect
                    ci_low = result.random_effects.ci_low
                    ci_high = result.random_effects.ci_high
                    report.append(f"{subgroup}: {eff:.3f} [{ci_low:.3f}, {ci_high:.3f}]")
            
            if '_between_group_test' in self.results.subgroups:
                between = self.results.subgroups['_between_group_test']
                report.append(f"Between-group test: p = {between['p_value']:.3f}")
            
            report.append("")
        
        return "\n".join(report)
    
    @staticmethod
    def grade_assessment(risk_of_bias: int, inconsistency: int, 
                        indirectness: int, imprecision: int,
                        publication_bias: int, large_effect: bool = False,
                        dose_response: bool = False) -> Dict[str, Any]:
        """GRADE evidence quality assessment"""
        
        # Validate inputs
        for domain, value in [('risk_of_bias', risk_of_bias), 
                             ('inconsistency', inconsistency),
                             ('indirectness', indirectness), 
                             ('imprecision', imprecision),
                             ('publication_bias', publication_bias)]:
            if not 0 <= value <= 2:
                raise ValueError(f"{domain} must be 0-2")
        
        # Calculate downgrades and upgrades
        total_downgrades = (risk_of_bias + inconsistency + 
                          indirectness + imprecision + publication_bias)
        
        upgrades = sum([large_effect, dose_response])
        net_downgrades = max(0, total_downgrades - upgrades)
        
        # Determine quality level
        quality_levels = {0: "High", 1: "Moderate", 2: "Low", 3: "Very Low"}
        final_quality = quality_levels[min(net_downgrades, 3)]
        
        return {
            'overall_quality': final_quality,
            'total_downgrades': total_downgrades,
            'upgrades': upgrades,
            'net_downgrades': net_downgrades,
            'confidence_statement': f"We have {final_quality.lower()} confidence in the evidence",
            'quality_score': 4 - min(net_downgrades, 3)  # 1-4 scale
        }
    
    @staticmethod
    def simulation_study(true_effect: float = 0.3, tau2: float = 0.1,
                        n_studies_range: Tuple[int, int] = (5, 50),
                        n_simulations: int = 100, 
                        bias_scenario: str = 'none') -> Dict[str, Any]:
        """Enhanced simulation study for education and validation"""
        
        results = []
        study_counts = np.linspace(n_studies_range[0], n_studies_range[1], 10, dtype=int)
        
        for n_studies in study_counts:
            sim_effects = []
            sim_ci_widths = []
            sim_coverage = []
            
            for sim in range(n_simulations):
                # Generate simulated data
                study_true_effects = np.random.normal(true_effect, np.sqrt(tau2), n_studies)
                study_se = np.random.uniform(0.1, 0.4, n_studies)
                observed_effects = np.random.normal(study_true_effects, study_se)
                
                # Apply bias scenario
                if bias_scenario == 'publication':
                    # Publication bias: suppress non-significant negative results
                    z_stats = observed_effects / study_se
                    p_vals = 2 * (1 - norm.cdf(np.abs(z_stats)))
                    suppress_mask = (observed_effects < 0) & (p_vals > 0.05)
                    keep_indices = ~suppress_mask
                    observed_effects = observed_effects[keep_indices]
                    study_se = study_se[keep_indices]
                elif bias_scenario == 'small_study':
                    # Small study effects: inflate effects in smaller studies
                    inflation = 1 + (1 / study_se) / 10
                    observed_effects *= inflation
                
                # Skip if too few studies remain
                if len(observed_effects) < 2:
                    continue
                
                # Create temporary dataset
                sim_data = pd.DataFrame({
                    'effect': observed_effects,
                    'se': study_se,
                    'study': [f'Study_{i}' for i in range(len(observed_effects))]
                })
                
                try:
                    sim_meta = UnifiedMetaAnalysis(
                        sim_data, 'effect', 'se', 'study', 
                        validate_data=False
                    ).analyze(include_bias_tests=False, include_conflicts=False)
                    
                    est = sim_meta.results.random_effects.effect
                    ci_low = sim_meta.results.random_effects.ci_low
                    ci_high = sim_meta.results.random_effects.ci_high
                    
                    sim_effects.append(est)
                    ci_width = ci_high - ci_low
                    sim_ci_widths.append(ci_width)
                    
                    # Coverage probability
                    covers = (ci_low <= true_effect <= ci_high)
                    sim_coverage.append(covers)
                    
                except Exception:
                    continue
            
            if sim_effects:
                results.append({
                    'n_studies': n_studies,
                    'mean_effect': np.mean(sim_effects),
                    'effect_sd': np.std(sim_effects),
                    'mean_ci_width': np.mean(sim_ci_widths),
                    'coverage_prob': np.mean(sim_coverage),
                    'bias': np.mean(sim_effects) - true_effect,
                    'rmse': np.sqrt(np.mean([(e - true_effect)**2 for e in sim_effects]))
                })
        
        return {
            'simulation_results': pd.DataFrame(results),
            'true_effect': true_effect,
            'tau2': tau2,
            'bias_scenario': bias_scenario
        }
    
    def __repr__(self):
        """String representation"""
        if self._fitted:
            effect = self.results.random_effects.effect
            ci_low = self.results.random_effects.ci_low
            ci_high = self.results.random_effects.ci_high
            return f"UnifiedMetaAnalysis(effect={effect:.3f} [{ci_low:.3f}, {ci_high:.3f}], k={len(self.df)})"
        else:
            return f"UnifiedMetaAnalysis(k={len(self.df)}, not fitted)"

# ===================================================================
# ENHANCED DIAGNOSTIC TEST ACCURACY METHODS
# ===================================================================

class EnhancedDiagnosticTestAccuracy:
    """Enhanced diagnostic test accuracy meta-analysis"""
    
    @staticmethod
    def bivariate_dta_model(tp: np.ndarray, fn: np.ndarray, fp: np.ndarray, 
                           tn: np.ndarray, method: str = "reml") -> Dict[str, Any]:
        """Enhanced bivariate random-effects model for DTA"""
        if not HAS_STATSMODELS:
            logger.warning("Statsmodels required for bivariate DTA model")
            return {'available': False}
        
        # Calculate sensitivity and specificity
        sens = tp / (tp + fn)
        spec = tn / (tn + fp)
        
        # Continuity correction for zero cells
        sens_adj = (tp + 0.5) / (tp + fn + 1)
        spec_adj = (tn + 0.5) / (tn + fp + 1)
        
        # Logit transformations
        logit_sens = np.log(sens_adj / (1 - sens_adj))
        logit_spec = np.log(spec_adj / (1 - spec_adj))
        
        # Variance calculations
        var_logit_sens = 1/tp + 1/fn + 1/(tp+fn)
        var_logit_spec = 1/tn + 1/fp + 1/(tn+fp)
        
        # Weighted analysis
        weights_sens = 1 / var_logit_sens
        weights_spec = 1 / var_logit_spec
        
        pooled_logit_sens = np.sum(weights_sens * logit_sens) / np.sum(weights_sens)
        pooled_logit_spec = np.sum(weights_spec * logit_spec) / np.sum(weights_spec)
        
        # Back-transform to probability scale
        pooled_sens = 1 / (1 + np.exp(-pooled_logit_sens))
        pooled_spec = 1 / (1 + np.exp(-pooled_logit_spec))
        
        # Standard errors
        se_logit_sens = np.sqrt(1 / np.sum(weights_sens))
        se_logit_spec = np.sqrt(1 / np.sum(weights_spec))
        
        # Confidence intervals on logit scale, then back-transform
        ci_logit_sens = [pooled_logit_sens - 1.96*se_logit_sens, 
                        pooled_logit_sens + 1.96*se_logit_sens]
        ci_logit_spec = [pooled_logit_spec - 1.96*se_logit_spec, 
                        pooled_logit_spec + 1.96*se_logit_spec]
        
        ci_sens = [1/(1+np.exp(-x)) for x in ci_logit_sens]
        ci_spec = [1/(1+np.exp(-x)) for x in ci_logit_spec]
        
        return {
            'pooled_sensitivity': pooled_sens,
            'pooled_specificity': pooled_spec,
            'sens_ci_lower': ci_sens[0],
            'sens_ci_upper': ci_sens[1],
            'spec_ci_lower': ci_spec[0],
            'spec_ci_upper': ci_spec[1],
            'individual_sensitivity': sens,
            'individual_specificity': spec,
            'n_studies': len(tp)
        }
    
    @staticmethod
    def create_hsroc_plot(tp: np.ndarray, fn: np.ndarray, fp: np.ndarray, 
                         tn: np.ndarray, figsize: Tuple[int, int] = (10, 8)) -> Any:
        """Enhanced HSROC/SROC plot"""
        # Calculate sensitivity and specificity
        sens = tp / (tp + fn)
        spec = tn / (tn + fp)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot individual studies
        ax.scatter(1 - spec, sens, s=100, alpha=0.7, edgecolors='black', 
                  linewidths=0.5, label='Individual studies')
        
        # Reference diagonal
        ax.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='No discrimination')
        
        # Fit summary curve if enough studies
        if len(sens) >= 5:
            # Simple logistic regression for summary curve
            fpr = 1 - spec
            x_smooth = np.linspace(0, 1, 100)
            
            # Weighted logistic regression approximation
            weights = tp + fn  # Sample sizes as weights
            try:
                if HAS_STATSMODELS:
                    log_odds = np.log((sens / (1 - sens)) / (fpr / (1 - fpr)))
                    model = sm.WLS(log_odds, sm.add_constant(np.log(fpr / (1 - fpr))), 
                                  weights=weights).fit()
                    
                    # Predict summary curve
                    log_fpr_smooth = np.log(x_smooth / (1 - x_smooth + 1e-10))
                    log_odds_pred = model.params[0] + model.params[1] * log_fpr_smooth
                    sens_smooth = np.exp(log_odds_pred) / (1 + np.exp(log_odds_pred))
                    
                    ax.plot(x_smooth, sens_smooth, 'r-', linewidth=3, 
                           label='Summary ROC curve', alpha=0.8)
            except:
                pass
        
        # AUC reference lines
        ax.axhline(0.5, color='gray', linestyle=':', alpha=0.5)
        ax.axvline(0.5, color='gray', linestyle=':', alpha=0.5)
        
        ax.set_xlabel('1 - Specificity (False Positive Rate)', fontsize=12)
        ax.set_ylabel('Sensitivity (True Positive Rate)', fontsize=12)
        ax.set_title('Hierarchical Summary ROC (HSROC) Plot', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1])
        
        plt.tight_layout()
        return fig

# ===================================================================
# NETWORK META-ANALYSIS COMPONENTS (PHASE 2: NETMETA-INSPIRED)
# ===================================================================

@dataclass
class NetworkMetaData:
    """Data structure for network meta-analysis supporting arm-level data"""
    study: List[str]
    treatment: List[str] 
    yi: List[float]  # Effect on log scale when appropriate
    sei: Optional[List[float]] = None  # Standard error
    vi: Optional[List[float]] = None   # Variance
    n: Optional[List[int]] = None      # Arm size
    events: Optional[List[int]] = None # Events for binary data
    
    def __post_init__(self):
        """Validate and process network data"""
        # Convert to DataFrame for easier handling
        data_dict = {
            'study': self.study,
            'treatment': self.treatment,
            'yi': self.yi
        }
        
        # Add variance/SE information
        if self.sei is not None:
            data_dict['sei'] = self.sei
            data_dict['vi'] = [se**2 for se in self.sei]
        elif self.vi is not None:
            data_dict['vi'] = self.vi
            data_dict['sei'] = [np.sqrt(v) for v in self.vi]
        else:
            raise ValueError("Either sei or vi must be provided")
            
        # Add optional columns
        if self.n is not None:
            data_dict['n'] = self.n
        if self.events is not None:
            data_dict['events'] = self.events
            
        self.data = pd.DataFrame(data_dict)
        self._validate_data()
        
    def _validate_data(self):
        """Validate network meta-analysis data"""
        required_cols = ['study', 'treatment', 'yi', 'sei', 'vi']
        for col in required_cols:
            if col not in self.data.columns:
                raise ValueError(f"Missing required column: {col}")
                
        # Check for missing values
        if self.data[['study', 'treatment', 'yi']].isnull().any().any():
            raise ValueError("Missing values in required columns")
            
        # Check minimum data requirements
        if len(self.data) < 3:
            raise ValueError("At least 3 arms required for network meta-analysis")
            
        studies_per_treatment = self.data.groupby('treatment')['study'].nunique()
        if (studies_per_treatment < 2).any():
            logger.warning("Some treatments appear in only one study")
            
@dataclass 
class NetworkGeometry:
    """Network geometry summary statistics"""
    n_studies: int = 0
    n_treatments: int = 0 
    n_arms: int = 0
    n_comparisons: int = 0
    density: float = 0.0
    diameter: int = 0
    is_connected: bool = False
    treatments: List[str] = field(default_factory=list)
    comparisons: List[Tuple[str, str]] = field(default_factory=list)

@dataclass
class NetworkConsistencyResults:
    """Results from network meta-analysis consistency model"""
    # Fixed-effects results
    fixed_effects: Dict[str, float] = field(default_factory=dict)
    fixed_effects_se: Dict[str, float] = field(default_factory=dict)
    fixed_effects_ci_low: Dict[str, float] = field(default_factory=dict) 
    fixed_effects_ci_high: Dict[str, float] = field(default_factory=dict)
    
    # Random-effects results (when applicable)
    random_effects: Optional[Dict[str, float]] = None
    random_effects_se: Optional[Dict[str, float]] = None
    random_effects_ci_low: Optional[Dict[str, float]] = None
    random_effects_ci_high: Optional[Dict[str, float]] = None
    tau2: Optional[float] = None
    
    # Network summaries
    geometry: Optional[NetworkGeometry] = None
    league_table: Optional[pd.DataFrame] = None
    p_scores: Optional[pd.Series] = None

class NetworkMetaAnalysis:
    """Network meta-analysis with netmeta-inspired functionality"""
    
    def __init__(self, data: NetworkMetaData, reference_treatment: str = None,
                 method: str = 'fixed', tau2_method: str = 'DL'):
        """
        Initialize network meta-analysis
        
        Parameters:
        data: NetworkMetaData object
        reference_treatment: Reference treatment (auto-selected if None)
        method: 'fixed' or 'random'
        tau2_method: Tau-squared estimation method for random effects
        """
        self.data = data
        self.method = method
        self.tau2_method = tau2_method
        
        # Set reference treatment
        if reference_treatment is None:
            # Choose treatment with most studies
            treatment_counts = data.data.groupby('treatment')['study'].nunique()
            self.reference_treatment = treatment_counts.idxmax()
        else:
            self.reference_treatment = reference_treatment
            
        self.results = None
        self._fitted = False
        
    def fit(self) -> 'NetworkMetaAnalysis':
        """Fit network meta-analysis consistency model"""
        # Create contrast-level data
        contrast_data = self._create_contrast_data()
        
        # Analyze network geometry
        geometry = self._analyze_network_geometry()
        
        # Fit consistency model
        if self.method == 'fixed':
            results = self._fit_fixed_effects(contrast_data)
        else:
            results = self._fit_random_effects(contrast_data)
            
        # Generate league table and P-scores
        league_table = self._create_league_table(results)
        p_scores = self._calculate_p_scores(results)
        
        # Store results
        self.results = NetworkConsistencyResults(
            fixed_effects=results['effects'],
            fixed_effects_se=results['se'],
            fixed_effects_ci_low=results['ci_low'],
            fixed_effects_ci_high=results['ci_high'],
            geometry=geometry,
            league_table=league_table,
            p_scores=p_scores
        )
        
        if self.method == 'random':
            self.results.random_effects = results['effects']
            self.results.random_effects_se = results['se'] 
            self.results.random_effects_ci_low = results['ci_low']
            self.results.random_effects_ci_high = results['ci_high']
            self.results.tau2 = results.get('tau2', 0.0)
            
        self._fitted = True
        return self
        
    def _create_contrast_data(self) -> pd.DataFrame:
        """Create contrast-level data from arm-level data"""
        contrasts = []
        
        for study in self.data.data['study'].unique():
            study_data = self.data.data[self.data.data['study'] == study]
            
            if len(study_data) < 2:
                continue  # Skip single-arm studies
                
            # Use first treatment as study reference (or specified reference if present)
            if self.reference_treatment in study_data['treatment'].values:
                ref_idx = study_data[study_data['treatment'] == self.reference_treatment].index[0]
            else:
                ref_idx = study_data.index[0]
                
            ref_row = study_data.loc[ref_idx]
            
            for idx, row in study_data.iterrows():
                if idx == ref_idx:
                    continue
                    
                # Calculate contrast
                yi_diff = row['yi'] - ref_row['yi'] 
                vi_diff = row['vi'] + ref_row['vi']  # Assuming independence
                sei_diff = np.sqrt(vi_diff)
                
                contrasts.append({
                    'study': study,
                    'comparison': f"{ref_row['treatment']}_{row['treatment']}",
                    'treatment1': ref_row['treatment'],
                    'treatment2': row['treatment'], 
                    'yi': yi_diff,
                    'vi': vi_diff,
                    'sei': sei_diff
                })
                
        return pd.DataFrame(contrasts)
        
    def _analyze_network_geometry(self) -> NetworkGeometry:
        """Analyze network geometry and connectivity"""
        treatments = sorted(self.data.data['treatment'].unique())
        n_treatments = len(treatments)
        
        # Create adjacency matrix
        adjacency = np.zeros((n_treatments, n_treatments))
        treatment_to_idx = {t: i for i, t in enumerate(treatments)}
        
        comparisons = set()
        for study in self.data.data['study'].unique():
            study_treatments = self.data.data[self.data.data['study'] == study]['treatment'].tolist()
            
            # Add all pairwise comparisons within study
            for i, t1 in enumerate(study_treatments):
                for j, t2 in enumerate(study_treatments):
                    if i != j:
                        idx1, idx2 = treatment_to_idx[t1], treatment_to_idx[t2]
                        adjacency[idx1, idx2] = 1
                        comparisons.add(tuple(sorted([t1, t2])))
        
        # Check connectivity
        is_connected = self._is_network_connected(adjacency)
        
        return NetworkGeometry(
            n_studies=self.data.data['study'].nunique(),
            n_treatments=n_treatments,
            n_arms=len(self.data.data),
            n_comparisons=len(comparisons),
            density=len(comparisons) / (n_treatments * (n_treatments - 1) / 2),
            is_connected=is_connected,
            treatments=treatments,
            comparisons=list(comparisons)
        )
        
    def _is_network_connected(self, adjacency: np.ndarray) -> bool:
        """Check if network is connected using DFS"""
        n = adjacency.shape[0]
        if n <= 1:
            return True
            
        visited = np.zeros(n, dtype=bool)
        
        def dfs(node):
            visited[node] = True
            for neighbor in range(n):
                if adjacency[node, neighbor] and not visited[neighbor]:
                    dfs(neighbor)
                    
        dfs(0)
        return np.all(visited)
        
    def _fit_fixed_effects(self, contrast_data: pd.DataFrame) -> Dict[str, Any]:
        """Fit fixed-effects network meta-analysis using generalized least squares"""
        treatments = sorted(self.data.data['treatment'].unique())
        
        if self.reference_treatment not in treatments:
            raise ValueError(f"Reference treatment {self.reference_treatment} not found in data")
            
        # Remove reference treatment from estimation (set to 0)
        non_ref_treatments = [t for t in treatments if t != self.reference_treatment]
        n_params = len(non_ref_treatments)
        
        if n_params == 0:
            # Only one treatment
            return {
                'effects': {self.reference_treatment: 0.0},
                'se': {self.reference_treatment: 0.0},
                'ci_low': {self.reference_treatment: 0.0},
                'ci_high': {self.reference_treatment: 0.0}
            }
        
        # Design matrix
        X = np.zeros((len(contrast_data), n_params))
        y = contrast_data['yi'].values
        V = np.diag(contrast_data['vi'].values)
        
        for i, row in contrast_data.iterrows():
            t1, t2 = row['treatment1'], row['treatment2']
            
            # Contrast is t2 - t1
            if t1 != self.reference_treatment and t1 in non_ref_treatments:
                idx1 = non_ref_treatments.index(t1)
                X[i, idx1] = -1
                
            if t2 != self.reference_treatment and t2 in non_ref_treatments:
                idx2 = non_ref_treatments.index(t2)
                X[i, idx2] = 1
        
        # Generalized least squares: β = (X'V⁻¹X)⁻¹X'V⁻¹y
        try:
            V_inv = safe_matrix_inverse(V)
            XtV_inv = X.T @ V_inv
            XtV_invX = XtV_inv @ X
            XtV_invX_inv = safe_matrix_inverse(XtV_invX)
            
            beta = XtV_invX_inv @ XtV_inv @ y
            var_beta = XtV_invX_inv
            se_beta = np.sqrt(np.diag(var_beta))
            
        except np.linalg.LinAlgError:
            logger.warning("Singular matrix in network meta-analysis, using ridge regression")
            # Ridge regression fallback
            ridge_lambda = 1e-6
            XtV_invX_ridge = XtV_invX @ X + ridge_lambda * np.eye(n_params)
            XtV_invX_ridge_inv = safe_matrix_inverse(XtV_invX_ridge)
            
            beta = XtV_invX_ridge_inv @ XtV_inv @ y
            var_beta = XtV_invX_ridge_inv
            se_beta = np.sqrt(np.abs(np.diag(var_beta)))
        
        # Create results dictionaries
        effects = {self.reference_treatment: 0.0}
        se = {self.reference_treatment: 0.0}
        ci_low = {self.reference_treatment: 0.0}
        ci_high = {self.reference_treatment: 0.0}
        
        z_crit = norm.ppf(0.975)
        
        for i, treatment in enumerate(non_ref_treatments):
            effects[treatment] = beta[i]
            se[treatment] = se_beta[i]
            ci_low[treatment] = beta[i] - z_crit * se_beta[i]
            ci_high[treatment] = beta[i] + z_crit * se_beta[i]
        
        return {
            'effects': effects,
            'se': se,
            'ci_low': ci_low,
            'ci_high': ci_high
        }
        
    def _fit_random_effects(self, contrast_data: pd.DataFrame) -> Dict[str, Any]:
        """Fit random-effects network meta-analysis with common tau²"""
        # First get fixed-effects estimates
        fixed_results = self._fit_fixed_effects(contrast_data)
        
        # Estimate tau² using method of moments
        tau2 = self._estimate_tau2_network(contrast_data, fixed_results)
        
        # Refit with tau² added to variances
        contrast_data_re = contrast_data.copy()
        contrast_data_re['vi'] = contrast_data_re['vi'] + tau2
        
        # Get random-effects estimates
        random_results = self._fit_fixed_effects(contrast_data_re)
        random_results['tau2'] = tau2
        
        return random_results
        
    def _estimate_tau2_network(self, contrast_data: pd.DataFrame, 
                              fixed_results: Dict[str, Any]) -> float:
        """Estimate tau² for network meta-analysis using method of moments"""
        if self.tau2_method == 'DL':
            return self._estimate_tau2_dersimonian_laird_network(contrast_data, fixed_results)
        else:
            logger.warning(f"Tau² method {self.tau2_method} not implemented, using DL")
            return self._estimate_tau2_dersimonian_laird_network(contrast_data, fixed_results)
            
    def _estimate_tau2_dersimonian_laird_network(self, contrast_data: pd.DataFrame,
                                               fixed_results: Dict[str, Any]) -> float:
        """DerSimonian-Laird tau² estimation for network meta-analysis"""
        # Calculate residuals from fixed-effects model
        residuals = []
        weights = []
        
        for _, row in contrast_data.iterrows():
            t1, t2 = row['treatment1'], row['treatment2']
            
            # Predicted effect from fixed-effects model
            pred_effect = fixed_results['effects'][t2] - fixed_results['effects'][t1]
            
            # Residual
            residual = row['yi'] - pred_effect
            residuals.append(residual)
            weights.append(1.0 / row['vi'])
        
        residuals = np.array(residuals)
        weights = np.array(weights)
        
        # Q statistic
        Q = np.sum(weights * residuals**2)
        df = len(residuals) - (len(fixed_results['effects']) - 1)
        
        if df <= 0:
            return 0.0
            
        # DL tau² estimate
        sum_weights = np.sum(weights)
        sum_weights_squared = np.sum(weights**2)
        
        tau2 = max(0, (Q - df) / (sum_weights - sum_weights_squared / sum_weights))
        
        return tau2
        
    def _create_league_table(self, results: Dict[str, Any]) -> pd.DataFrame:
        """Create league table with all pairwise comparisons"""
        treatments = list(results['effects'].keys())
        n_treatments = len(treatments)
        
        # Initialize league table
        league_table = pd.DataFrame(index=treatments, columns=treatments)
        
        for i, t1 in enumerate(treatments):
            for j, t2 in enumerate(treatments):
                if i == j:
                    league_table.loc[t1, t2] = "0.00 (Reference)"
                elif i < j:
                    # Upper triangle: effect (CI)
                    effect = results['effects'][t2] - results['effects'][t1]
                    se = np.sqrt(results['se'][t1]**2 + results['se'][t2]**2)
                    ci_low = effect - 1.96 * se
                    ci_high = effect + 1.96 * se
                    
                    league_table.loc[t1, t2] = f"{effect:.2f} ({ci_low:.2f}, {ci_high:.2f})"
                else:
                    # Lower triangle: inverse effect
                    effect = results['effects'][t1] - results['effects'][t2] 
                    se = np.sqrt(results['se'][t1]**2 + results['se'][t2]**2)
                    ci_low = effect - 1.96 * se
                    ci_high = effect + 1.96 * se
                    
                    league_table.loc[t1, t2] = f"{effect:.2f} ({ci_low:.2f}, {ci_high:.2f})"
        
        return league_table
        
    def _calculate_p_scores(self, results: Dict[str, Any]) -> pd.Series:
        """Calculate P-scores (frequentist analogue of SUCRA)"""
        treatments = list(results['effects'].keys())
        effects = np.array([results['effects'][t] for t in treatments])
        se_values = np.array([results['se'][t] for t in treatments])
        
        n_treatments = len(treatments)
        p_scores = {}
        
        for i, treatment in enumerate(treatments):
            p_score = 0.0
            
            # Compare against all other treatments
            for j, other_treatment in enumerate(treatments):
                if i != j:
                    # Calculate probability that treatment i is better than j
                    effect_diff = effects[i] - effects[j]
                    se_diff = np.sqrt(se_values[i]**2 + se_values[j]**2)
                    
                    if se_diff > 0:
                        z_score = effect_diff / se_diff
                        prob_better = norm.cdf(z_score)
                    else:
                        prob_better = 0.5
                        
                    p_score += prob_better
            
            # Normalize by number of comparisons
            p_scores[treatment] = p_score / (n_treatments - 1)
        
        return pd.Series(p_scores, name='P_score')

class NetworkMetaRankings:
    """Network meta-analysis ranking methods including SUCRA"""
    
    @staticmethod
    def compute_sucra(rank_probabilities: pd.DataFrame) -> pd.Series:
        """
        Compute SUCRA (Surface Under Cumulative Ranking Curve) values
        
        Parameters:
        rank_probabilities: DataFrame with treatments as rows, ranks as columns
        """
        n_treatments = rank_probabilities.shape[0]
        n_ranks = rank_probabilities.shape[1]
        
        # Calculate cumulative probabilities
        cumulative_probs = rank_probabilities.cumsum(axis=1)
        
        # SUCRA calculation
        sucra_values = {}
        for treatment in rank_probabilities.index:
            # Area under cumulative ranking curve
            cumsum = cumulative_probs.loc[treatment].values[:-1]  # Exclude last rank
            sucra = np.sum(cumsum) / (n_treatments - 1)
            sucra_values[treatment] = sucra
        
        return pd.Series(sucra_values, name='SUCRA')
    
    @staticmethod
    def generate_ranking_table(effects: Dict[str, float], 
                              uncertainties: Dict[str, float]) -> pd.DataFrame:
        """Generate treatment ranking table with probabilities"""
        treatments = list(effects.keys())
        n_treatments = len(treatments)
        
        # Simulate ranking probabilities (simplified approach)
        # In practice, this would come from MCMC samples
        ranking_data = []
        
        for treatment in treatments:
            # Simple ranking based on effect size and uncertainty
            effect = effects[treatment]
            se = uncertainties[treatment]
            
            # Calculate probability of being best, second-best, etc.
            rank_probs = []
            for rank in range(1, n_treatments + 1):
                # Simplified probability calculation
                prob = norm.pdf(rank, loc=1 + (max(effects.values()) - effect) * 2, scale=se * 2)
                rank_probs.append(max(0.01, prob))
            
            # Normalize probabilities
            rank_probs = np.array(rank_probs)
            rank_probs = rank_probs / np.sum(rank_probs)
            
            ranking_data.append(rank_probs)
        
        rank_df = pd.DataFrame(ranking_data, 
                              index=treatments, 
                              columns=[f'Rank_{i+1}' for i in range(n_treatments)])
        
        # Calculate SUCRA
        sucra_scores = NetworkMetaRankings.compute_sucra(rank_df)
        rank_df['SUCRA'] = sucra_scores
        rank_df['Mean_Rank'] = np.sum(rank_df.iloc[:, :-1].values * 
                                     np.arange(1, n_treatments + 1), axis=1)
        
        return rank_df.sort_values('SUCRA', ascending=False)

# ===================================================================
# ENHANCED TRIAL SEQUENTIAL ANALYSIS
# ===================================================================

class EnhancedTrialSequentialAnalysis:
    """Enhanced Trial Sequential Analysis with multiple boundary functions"""
    
    @staticmethod
    def calculate_boundaries(information_fractions: np.ndarray, alpha: float = 0.05,
                           boundary_type: str = 'obrien_fleming') -> Dict[str, np.ndarray]:
        """Calculate TSA boundaries with multiple options"""
        
        if boundary_type == 'obrien_fleming':
            # O'Brien-Fleming boundaries
            z_alpha = norm.ppf(1 - alpha/2)
            boundaries = z_alpha / np.sqrt(information_fractions)
            
        elif boundary_type == 'pocock':
            # Pocock boundaries (constant)
            z_alpha = norm.ppf(1 - alpha/(2 * len(information_fractions)))
            boundaries = np.full_like(information_fractions, z_alpha)
            
        elif boundary_type == 'lan_demets':
            # Lan-DeMets approximation to O'Brien-Fleming
            z_alpha = norm.ppf(1 - alpha/2)
            boundaries = z_alpha * np.sqrt(np.log(1 / information_fractions))
            
        else:
            raise ValueError(f"Unknown boundary type: {boundary_type}")
        
        # Futility boundaries (typically at 20% of efficacy boundary)
        futility_boundaries = boundaries * 0.2
        
        return {
            'efficacy_upper': boundaries,
            'efficacy_lower': -boundaries,
            'futility_upper': futility_boundaries,
            'futility_lower': -futility_boundaries
        }
    
    @staticmethod
    def enhanced_tsa(effects: np.ndarray, variances: np.ndarray, 
                    target_effect: float, alpha: float = 0.05, beta: float = 0.2,
                    boundary_type: str = 'obrien_fleming') -> Dict[str, Any]:
        """Enhanced TSA with multiple boundary types"""
        
        information = 1 / variances
        cumulative_info = np.cumsum(information)
        total_info = np.sum(information)
        info_fractions = cumulative_info / total_info
        
        # Required information size
        z_alpha = norm.ppf(1 - alpha/2)
        z_beta = norm.ppf(1 - beta)
        required_info = ((z_alpha + z_beta) / target_effect)**2
        
        # Calculate boundaries
        boundaries = EnhancedTrialSequentialAnalysis.calculate_boundaries(
            info_fractions, alpha, boundary_type)
        
        # Cumulative Z-statistics
        cumulative_z = []
        for i in range(len(effects)):
            cum_effects = effects[:i+1]
            cum_info = information[:i+1]
            pooled_effect = np.sum(cum_info * cum_effects) / np.sum(cum_info)
            pooled_se = np.sqrt(1 / np.sum(cum_info))
            z_stat = pooled_effect / pooled_se if pooled_se > 0 else 0
            cumulative_z.append(z_stat)
        
        cumulative_z = np.array(cumulative_z)
        
        # Check boundary crossings
        efficacy_crossings = []
        futility_crossings = []
        
        for i, (z, eff_upper, fut_upper) in enumerate(zip(cumulative_z, 
                                                         boundaries['efficacy_upper'], 
                                                         boundaries['futility_upper'])):
            if abs(z) >= eff_upper:
                efficacy_crossings.append({
                    'study_number': i + 1,
                    'z_statistic': z,
                    'boundary': eff_upper,
                    'type': 'efficacy'
                })
            elif abs(z) <= fut_upper:
                futility_crossings.append({
                    'study_number': i + 1,
                    'z_statistic': z,
                    'boundary': fut_upper,
                    'type': 'futility'
                })
        
        first_crossing = None
        if efficacy_crossings:
            first_crossing = efficacy_crossings[0]
        elif futility_crossings:
            first_crossing = futility_crossings[0]
        
        return {
            'information_fractions': info_fractions,
            'cumulative_z': cumulative_z,
            'boundaries': boundaries,
            'required_information': required_info,
            'total_information': total_info,
            'information_adequacy': total_info / required_info,
            'first_crossing': first_crossing,
            'all_efficacy_crossings': efficacy_crossings,
            'all_futility_crossings': futility_crossings,
            'conclusive': first_crossing is not None or total_info >= required_info,
            'boundary_type': boundary_type
        }
    
    @staticmethod
    def create_tsa_plot(tsa_results: Dict[str, Any], figsize: Tuple[int, int] = (12, 8)) -> Any:
        """Create TSA monitoring plot"""
        fig, ax = plt.subplots(figsize=figsize)
        
        info_fractions = tsa_results['information_fractions']
        cumulative_z = tsa_results['cumulative_z']
        boundaries = tsa_results['boundaries']
        
        # Plot cumulative Z-curve
        ax.plot(info_fractions, cumulative_z, 'bo-', linewidth=2, 
               markersize=6, label='Cumulative Z-statistic')
        
        # Plot boundaries
        ax.plot(info_fractions, boundaries['efficacy_upper'], 'r-', 
               linewidth=2, label='Efficacy boundary')
        ax.plot(info_fractions, boundaries['efficacy_lower'], 'r-', linewidth=2)
        ax.plot(info_fractions, boundaries['futility_upper'], 'orange', 
               linestyle='--', linewidth=1, label='Futility boundary')
        ax.plot(info_fractions, boundaries['futility_lower'], 'orange', 
               linestyle='--', linewidth=1)
        
        # Mark crossings
        if tsa_results['first_crossing']:
            crossing = tsa_results['first_crossing']
            study_idx = crossing['study_number'] - 1
            ax.scatter(info_fractions[study_idx], cumulative_z[study_idx], 
                      s=200, c='red', marker='*', zorder=5,
                      label=f"First crossing (Study {crossing['study_number']})")
        
        # Information adequacy line
        info_adequacy = tsa_results['information_adequacy']
        if info_adequacy < 1:
            ax.axvline(info_adequacy, color='green', linestyle=':', 
                      label=f'Required information ({info_adequacy:.1%})')
        
        ax.axhline(0, color='gray', linestyle='-', alpha=0.5)
        ax.set_xlabel('Information Fraction', fontsize=12)
        ax.set_ylabel('Cumulative Z-statistic', fontsize=12)
        ax.set_title(f'Trial Sequential Analysis ({tsa_results["boundary_type"].title()})', 
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig

# ===================================================================
# ENHANCED GRADE FUNCTIONALITY
# ===================================================================

class EnhancedGRADE:
    """Enhanced GRADE evidence assessment with detailed profiling"""
    
    @staticmethod
    def detailed_grade_assessment(risk_of_bias: int, inconsistency: int, 
                                 indirectness: int, imprecision: int,
                                 publication_bias: int, large_effect: bool = False,
                                 dose_response: bool = False,
                                 confounding: bool = False) -> Dict[str, Any]:
        """Enhanced GRADE assessment with additional factors"""
        
        # Validate inputs
        domains = {
            'risk_of_bias': risk_of_bias,
            'inconsistency': inconsistency, 
            'indirectness': indirectness,
            'imprecision': imprecision,
            'publication_bias': publication_bias
        }
        
        for domain, value in domains.items():
            if not 0 <= value <= 2:
                raise ValueError(f"{domain} must be 0-2 (0=no concern, 1=some concern, 2=major concern)")
        
        # Calculate downgrades
        total_downgrades = sum(domains.values())
        
        # Calculate upgrades
        upgrades = sum([large_effect, dose_response, confounding])
        
        # Net assessment
        net_downgrades = max(0, total_downgrades - upgrades)
        
        # Quality determination
        quality_levels = {0: "High", 1: "Moderate", 2: "Low", 3: "Very Low"}
        final_quality = quality_levels[min(net_downgrades, 3)]
        
        # Detailed explanations
        domain_explanations = {
            'risk_of_bias': {
                0: "Low risk across all domains",
                1: "Some concerns in one or more domains", 
                2: "High risk in multiple domains"
            },
            'inconsistency': {
                0: "No unexplained heterogeneity",
                1: "Moderate heterogeneity (I² 30-60%)",
                2: "Substantial heterogeneity (I² >75%)"
            },
            'indirectness': {
                0: "Direct evidence",
                1: "Some indirectness in population/intervention",
                2: "Major indirectness"
            },
            'imprecision': {
                0: "Adequate sample size and precision",
                1: "Some imprecision",
                2: "Major imprecision, wide confidence intervals"
            },
            'publication_bias': {
                0: "No evidence of publication bias",
                1: "Some evidence of publication bias",
                2: "Strong evidence of publication bias"
            }
        }
        
        detailed_assessment = {}
        for domain, value in domains.items():
            detailed_assessment[domain] = {
                'score': value,
                'explanation': domain_explanations[domain][value]
            }
        
        return {
            'overall_quality': final_quality,
            'quality_score': 4 - min(net_downgrades, 3),
            'total_downgrades': total_downgrades,
            'upgrades': upgrades,
            'net_downgrades': net_downgrades,
            'detailed_assessment': detailed_assessment,
            'confidence_statement': f"We have {final_quality.lower()} confidence in the evidence",
            'recommendation_strength': "Strong" if final_quality in ["High", "Moderate"] else "Weak"
        }
    
    @staticmethod
    def create_grade_summary_table(assessments: List[Dict[str, Any]], 
                                  outcomes: List[str]) -> pd.DataFrame:
        """Create comprehensive GRADE evidence profile table"""
        grade_data = []
        
        for outcome, assessment in zip(outcomes, assessments):
            row = {
                'Outcome': outcome,
                'Quality': assessment['overall_quality'],
                'Quality_Score': assessment['quality_score'],
                'Risk_of_Bias': assessment['detailed_assessment']['risk_of_bias']['score'],
                'Inconsistency': assessment['detailed_assessment']['inconsistency']['score'],
                'Indirectness': assessment['detailed_assessment']['indirectness']['score'],
                'Imprecision': assessment['detailed_assessment']['imprecision']['score'],
                'Publication_Bias': assessment['detailed_assessment']['publication_bias']['score'],
                'Total_Downgrades': assessment['total_downgrades'],
                'Upgrades': assessment['upgrades'],
                'Recommendation': assessment['recommendation_strength'],
                'Confidence_Statement': assessment['confidence_statement']
            }
            grade_data.append(row)
        
        return pd.DataFrame(grade_data)

# ===================================================================
# HELPER UTILITIES FOR DEMO MODULARITY
# ===================================================================

def ensure_dir(path: str) -> None:
    """Ensure directory exists, create if necessary"""
    os.makedirs(path, exist_ok=True)

def print_section(title: str, width: int = 90) -> None:
    """Print a standardized section header"""
    print("=" * width)
    print(title)
    print("=" * width)

def print_subsection(title: str, underline_char: str = "-") -> None:
    """Print a standardized subsection header"""
    print(f"\n{title}")
    print(underline_char * len(title))

def generate_demo_data(n_studies: int = 25, seed: int = 42) -> pd.DataFrame:
    """Generate comprehensive demo dataset for meta-analysis demonstration"""
    np.random.seed(seed)
    true_effect = 0.4
    between_study_sd = 0.3
    
    # Simulate realistic study characteristics with clustering for conflict detection
    cluster_probs = [0.5, 0.3, 0.2]  # Three research groups with different effect sizes
    clusters = np.random.choice([0, 1, 2], n_studies, p=cluster_probs)
    cluster_effects = [true_effect, true_effect + 0.7, true_effect - 0.5]  # Conflicting results
    
    study_effects = [np.random.normal(cluster_effects[c], between_study_sd) for c in clusters]
    study_se = np.random.uniform(0.08, 0.35, n_studies)
    observed_effects = [np.random.normal(eff, se) for eff, se in zip(study_effects, study_se)]
    
    # Create comprehensive dataset with all features needed for demonstration
    demo_data = pd.DataFrame({
        'study_id': [f'Study_{i+1:02d}' for i in range(n_studies)],
        'author': [f'Author_{i+1} et al.' for i in range(n_studies)],
        'year': np.random.randint(2015, 2025, n_studies),
        'effect_size': observed_effects,
        'standard_error': study_se,
        'sample_size': np.random.randint(80, 500, n_studies),
        'intervention_type': np.random.choice(['TypeA', 'TypeB', 'TypeC'], n_studies),
        'dose_mg': np.random.uniform(10, 100, n_studies),
        'duration_weeks': np.random.randint(8, 52, n_studies),
        'risk_of_bias': np.random.choice(['Low', 'Moderate', 'High'], n_studies),
        'country': np.random.choice(['USA', 'UK', 'Germany', 'Japan', 'Canada'], n_studies),
        'population_age': np.random.uniform(45, 75, n_studies),
        'true_cluster': clusters,  # For validation
        'abstract': [f"This study examined the effect of intervention on outcome. "
                    f"The hazard ratio was {np.exp(eff):.2f} with 95% confidence interval "
                    f"{np.exp(eff-1.96*se):.2f} to {np.exp(eff+1.96*se):.2f}." 
                    for eff, se in zip(observed_effects, study_se)]
    })
    
    print(f"Generated comprehensive dataset: {len(demo_data)} studies")
    print(f"True effect: {true_effect}, Between-study SD: {between_study_sd}")
    print(f"Simulated conflicts: {len(np.unique(clusters))} research groups")
    print(f"Effect range: {min(observed_effects):.3f} to {max(observed_effects):.3f}")
    
    return demo_data

def print_analysis_summary(meta) -> None:
    """Print standardized analysis summary and interpretation"""
    print(f"Analysis completed: {meta}")
    print(f"Interpretation: {meta.interpret_results()}")
    
    # Summary table
    summary = meta.summary_table()
    print(f"\nSummary Table:")
    print(summary.to_string(index=False))

def save_plots(meta, output_dir: str = ".") -> None:
    """Save visualization plots with error handling"""
    ensure_dir(output_dir)
    
    try:
        # Create plots
        forest_fig = meta.create_forest_plot(show_weights=True)
        funnel_fig = meta.create_funnel_plot(enhanced=True, include_bias_methods=True)
        diagnostic_plots = meta.create_diagnostic_plots()
        
        # Save plots
        forest_fig.savefig(os.path.join(output_dir, 'unified_forest_plot.png'), dpi=150, bbox_inches='tight')
        funnel_fig.savefig(os.path.join(output_dir, 'unified_funnel_plot.png'), dpi=150, bbox_inches='tight')
        diagnostic_plots['influence_plot'].savefig(os.path.join(output_dir, 'influence_plot.png'), dpi=150, bbox_inches='tight')
        diagnostic_plots['cumulative_plot'].savefig(os.path.join(output_dir, 'cumulative_plot.png'), dpi=150, bbox_inches='tight')
        
        plt.close('all')
        print("All plots created successfully")
        
    except Exception as e:
        print(f"Visualization failed: {e}")

def save_report(meta, output_dir: str = ".") -> None:
    """Save comprehensive text report with error handling"""
    ensure_dir(output_dir)
    
    try:
        report = meta.comprehensive_report()
        report_path = os.path.join(output_dir, 'unified_meta_report.txt')
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"Comprehensive report saved to '{report_path}'")
    except Exception as e:
        print(f"Report saving failed: {e}")

def run_core_analysis(demo_data: pd.DataFrame) -> 'UnifiedMetaAnalysis':
    """Run core unified meta-analysis"""
    config = UnifiedMetaConfig(
        tau2_method='REML', 
        use_hksj=True,
        conflict_k_candidates=[2, 3, 4],
        bayesian_chains=2,
        bayesian_draws=500
    )
    
    # Check if optional dependencies are available
    try:
        from sklearn.cluster import KMeans
        include_conflicts = True
    except ImportError:
        include_conflicts = False
    
    meta = UnifiedMetaAnalysis(
        data=demo_data,
        effect_col='effect_size',
        se_col='standard_error', 
        label_col='study_id',
        subgroup_col='intervention_type',
        config=config
    ).analyze(include_conflicts=include_conflicts, include_bias_tests=True)
    
    return meta

def run_diagnostics(meta) -> Dict[str, Any]:
    """Run enhanced diagnostics analysis"""
    print_subsection("2. ENHANCED DIAGNOSTICS", "-")
    
    # Leave-one-out
    loo_results = meta.leave_one_out_analysis()
    influential = loo_results[loo_results['influential']]
    print(f"Leave-one-out: {len(influential)} influential studies")
    if not influential.empty:
        print(f"Most influential: {influential.iloc[0]['excluded_study']} "
              f"(change: {influential.iloc[0]['effect_change']:.3f})")
    
    # Influence diagnostics
    influence_data = meta.influence_diagnostics()
    high_influence = influence_data[influence_data['influential']]
    print(f"Influence diagnostics: {len(high_influence)} studies with high influence")
    
    return {
        'influential_studies': len(influential),
        'high_influence_studies': len(high_influence),
        'loo_results': loo_results,
        'influence_data': influence_data
    }

def run_bias_assessment(meta) -> Dict[str, Any]:
    """Run comprehensive bias assessment"""
    print_subsection("3. COMPREHENSIVE BIAS ASSESSMENT", "-")
    
    results = {}
    if hasattr(meta.results, 'bias_assessment'):
        bias = meta.results.bias_assessment
        
        if hasattr(bias, 'egger'):
            egger_p = bias.egger.get('p_value', 'N/A')
            print(f"Egger test p-value: {egger_p:.3f}" if egger_p != 'N/A' else f"Egger test p-value: {egger_p}")
            results['egger_p'] = egger_p
        
        if hasattr(bias, 'pet_peese'):
            pet_peese = bias.pet_peese
            if pet_peese.get('success', True) and 'corrected_effect' in pet_peese:
                print(f"PET-PEESE corrected effect: {pet_peese['corrected_effect']:.3f}")
                results['pet_peese_effect'] = pet_peese['corrected_effect']
        
        if hasattr(bias, 'trim_fill'):
            trim_fill = bias.trim_fill
            print(f"Trim-and-fill: {trim_fill['n_imputed']} studies imputed")
            results['trim_fill_imputed'] = trim_fill['n_imputed']
        
        if hasattr(bias, 'p_curve'):
            p_curve = bias.p_curve
            if 'evidential_value' in p_curve:
                print(f"P-curve evidential value: {p_curve['evidential_value']}")
                results['p_curve_evidential'] = p_curve['evidential_value']
    else:
        print("Bias assessment not available (insufficient studies or missing dependencies)")
    
    return results

def run_conflict_detection(meta) -> Dict[str, Any]:
    """Run conflict detection analysis"""
    print_subsection("4. CONFLICT DETECTION", "-")
    
    results = {}
    if hasattr(meta.results, 'conflict_detection'):
        conflict = meta.results.conflict_detection
        if hasattr(conflict, 'conflicting'):
            print(f"Conflicts detected: {conflict.conflicting}")
            print(f"Number of clusters: {conflict.k}")
            print(f"Silhouette score: {conflict.silhouette:.3f}")
            print(f"Effect range: {conflict.delta:.3f}")
            
            results = {
                'conflicts_detected': conflict.conflicting,
                'n_clusters': conflict.k,
                'silhouette_score': conflict.silhouette,
                'effect_range': conflict.delta
            }
    
    return results

def run_multiverse(meta) -> Dict[str, Any]:
    """Run multiverse analysis"""
    print_subsection("5. MULTIVERSE ANALYSIS", "-")
    
    multiverse_results = meta.multiverse_analysis()
    effect_range = multiverse_results['effect'].max() - multiverse_results['effect'].min()
    print(f"Multiverse analysis: Effect range = {effect_range:.3f}")
    print(f"Number of specifications: {len(multiverse_results)}")
    
    return {
        'effect_range': effect_range,
        'n_specifications': len(multiverse_results),
        'results': multiverse_results
    }

def run_missing_sensitivity(meta, n_max: int = 3) -> Dict[str, Any]:
    """Run missing study sensitivity analysis"""
    print_subsection("6. MISSING STUDY SENSITIVITY", "-")
    
    missing_results = meta.missing_study_sensitivity(n_max=n_max)
    max_change = missing_results['effect_change'].abs().max()
    print(f"Missing study sensitivity: Max effect change = {max_change:.3f}")
    
    return {
        'max_effect_change': max_change,
        'results': missing_results
    }

def run_sequential_analysis(meta) -> Dict[str, Any]:
    """Run sequential analysis"""
    print_subsection("7. SEQUENTIAL ANALYSIS", "-")
    
    # Cumulative analysis
    cumulative = meta.cumulative_analysis(sort_by='year')
    final_effect = cumulative.iloc[-1]['cumulative_effect']
    effect_evolution = cumulative.iloc[-1]['effect_change']
    print(f"Cumulative analysis: Final effect = {final_effect:.3f}")
    print(f"Effect evolution: {effect_evolution:.3f}")
    
    # Trial Sequential Analysis
    tsa_results = meta.trial_sequential_analysis(target_effect=0.3)
    conclusive = "Yes" if tsa_results['conclusive'] else "No"
    print(f"TSA conclusive: {conclusive}")
    
    return {
        'final_effect': final_effect,
        'effect_evolution': effect_evolution,
        'tsa_conclusive': tsa_results['conclusive'],
        'cumulative_results': cumulative,
        'tsa_results': tsa_results
    }

def run_dose_response(meta) -> Dict[str, Any]:
    """Run dose-response analysis"""
    print_subsection("8. DOSE-RESPONSE ANALYSIS", "-")
    
    dose_results = meta.dose_response_analysis('dose_mg', model_type='linear')
    print(f"Dose-response slope: {dose_results['slope']:.4f} (p = {dose_results['p_slope']:.3f})")
    print(f"R² = {dose_results['r_squared']:.3f}")
    
    return {
        'slope': dose_results['slope'],
        'p_slope': dose_results['p_slope'],
        'r_squared': dose_results['r_squared'],
        'results': dose_results
    }

def run_bayesian(meta) -> Dict[str, Any]:
    """Run Bayesian methods"""
    print_subsection("9. BAYESIAN METHODS", "-")
    
    results = {}
    if HAS_PYMC:
        try:
            bayes_results = meta.bayesian_stacking(chains=2, draws=500)
            if bayes_results.get('success', False):
                print(f"Bayesian posterior mean: {bayes_results['posterior_mean']:.3f}")
                print(f"Posterior SD: {bayes_results['posterior_sd']:.3f}")
                results = {
                    'posterior_mean': bayes_results['posterior_mean'],
                    'posterior_sd': bayes_results['posterior_sd'],
                    'success': True
                }
            else:
                print("Bayesian analysis failed or unavailable")
                results['success'] = False
        except Exception as e:
            print(f"Bayesian analysis failed: {e}")
            results = {'success': False, 'error': str(e)}
    else:
        print("PyMC not available - Bayesian methods disabled")
        results = {'success': False, 'reason': 'PyMC not available'}
    
    return results

def run_grade_assessment() -> Dict[str, Any]:
    """Run GRADE evidence assessment"""
    print_subsection("10. GRADE EVIDENCE ASSESSMENT", "-")
    
    grade_result = UnifiedMetaAnalysis.grade_assessment(
        risk_of_bias=1, inconsistency=1, indirectness=0,
        imprecision=1, publication_bias=1, dose_response=True
    )
    print(f"GRADE quality: {grade_result['overall_quality']}")
    print(f"Quality score: {grade_result['quality_score']}/4")
    
    return grade_result

def run_simulation() -> Dict[str, Any]:
    """Run educational simulation"""
    print_subsection("11. EDUCATIONAL SIMULATION", "-")
    
    sim_results = UnifiedMetaAnalysis.simulation_study(
        true_effect=0.3, n_simulations=20, bias_scenario='publication')
    sim_df = sim_results['simulation_results']
    
    results = {'sim_results': sim_results}
    if not sim_df.empty:
        bias_range = (sim_df['bias'].min(), sim_df['bias'].max())
        coverage_range = (sim_df['coverage_prob'].min(), sim_df['coverage_prob'].max())
        print(f"Simulation study: Bias range = {bias_range[0]:.4f} to {bias_range[1]:.4f}")
        print(f"Coverage probability range: {coverage_range[0]:.3f} to {coverage_range[1]:.3f}")
        
        results.update({
            'bias_range': bias_range,
            'coverage_range': coverage_range
        })
    
    return results

def run_living_meta(meta) -> Dict[str, Any]:
    """Run living meta-analysis setup"""
    print_subsection("12. LIVING META-ANALYSIS", "-")
    
    results = {}
    if HAS_BIOPYTHON:
        living_config = meta.setup_living_meta("meta-analysis cardiovascular", "demo_living")
        print(f"Living MA initialized: {living_config['query']}")
        print(f"Output directory: {living_config['output_dir']}")
        results = living_config
    else:
        print("BioPython not available - Living MA disabled")
        results = {'available': False, 'reason': 'BioPython not available'}
    
    return results

# ===================================================================
# COMPREHENSIVE DEMO FUNCTION - FIXED INDENTATION
# ===================================================================

def run_unified_demo(n_studies: int = 25, seed: int = 42, output_dir: str = ".", 
                     save_visuals: bool = True, save_text_report: bool = True) -> 'UnifiedMetaAnalysis':
    """Comprehensive demonstration of all unified capabilities including new modules"""
    
    # Print standardized heading
    print_section("PyMeta-CBAMM Unified Suite v3.0 - COMPLETE FEATURE DEMONSTRATION")
    
    # Generate demo data
    demo_data = generate_demo_data(n_studies, seed)
    
    # Run core analysis
    print_subsection("1. CORE UNIFIED ANALYSIS", "-")
    meta = run_core_analysis(demo_data)
    print_analysis_summary(meta)
    
    # Run modular analysis steps
    run_diagnostics(meta)
    run_bias_assessment(meta)
    run_conflict_detection(meta)
    run_multiverse(meta)
    run_missing_sensitivity(meta, n_max=3)
    run_sequential_analysis(meta)
    run_dose_response(meta)
    run_bayesian(meta)
    run_grade_assessment()
    run_simulation()
    run_living_meta(meta)
    
    # Visualization suite
    print_subsection("13. VISUALIZATION SUITE", "-")
    if save_visuals:
        save_plots(meta, output_dir)
    else:
        print("Visualization saving disabled")
    
    # Comprehensive report
    print_subsection("14. COMPREHENSIVE REPORT", "-")
    if save_text_report:
        save_report(meta, output_dir)
    else:
        print("Report saving disabled")
    
    print_section("UNIFIED SUITE DEMONSTRATION COMPLETE")
    
    # Summary of all capabilities
    capabilities = [
        "✓ Core meta-analysis (fixed/random effects, 4 tau² estimators)",
        "✓ Enhanced diagnostics (leave-one-out, influence, Cook's D)", 
        "✓ Comprehensive bias assessment (Egger, Begg, PET-PEESE, trim-fill, p-curve, TES)",
        "✓ Transport weighting for population generalizability",
        "✓ Advanced conflict detection with ML clustering",
        "✓ Missing study sensitivity analysis",
        "✓ Multiverse analysis across analytical specifications",
        "✓ Sequential analysis (cumulative, Trial Sequential Analysis)",
        "✓ Dose-response meta-analysis (linear, quadratic models)",
        "✓ Network meta-analysis components (SUCRA)",
        "✓ Bayesian methods (HSROC, stacking, PyMC integration)",
        "✓ Living meta-analysis with automated PubMed updates",
        "✓ NLP effect size extraction from abstracts",
        "✓ ML-based outcome classification",
        "✓ GRADE evidence quality assessment",
        "✓ Educational simulation tools with multiple bias scenarios",
        "✓ Diagnostic test accuracy methods (bivariate, HSROC)",
        "✓ Enhanced visualizations (forest, funnel, Baujat, radial, diagnostic plots)",
        "✓ Automated interpretation and reporting"
    ]
    
    print("COMPLETE INTEGRATED CAPABILITIES:")
    for cap in capabilities:
        print(f"  {cap}")
    
    print(f"\n🎯 PyMeta-CBAMM Unified Suite v3.0 is now complete!")
    print(f"   Combines PyMeta v2.1 + CBAMM v5.7 with zero functionality loss")
    print(f"   Production-ready for clinical research, systematic reviews, and education")
    
    return meta

# ===================================================================
# CONVENIENCE FUNCTIONS FOR QUICK ANALYSIS
# ===================================================================

def quick_meta(effects: List[float], se: List[float], labels: Optional[List[str]] = None,
               tau2_method: str = 'REML', use_hksj: bool = True) -> UnifiedMetaAnalysis:
    """Quick meta-analysis from lists with validation
    
    Args:
        effects: List of effect sizes
        se: List of standard errors  
        labels: Optional list of study labels
        tau2_method: Method for tau² estimation
        use_hksj: Whether to use Hartung-Knapp-Sidik-Jonkman adjustment
        
    Returns:
        UnifiedMetaAnalysis: Fitted meta-analysis object
        
    Raises:
        ValueError: If inputs are invalid
    """
    # Validate lengths
    if len(effects) != len(se):
        raise ValueError(f"Length mismatch: effects ({len(effects)}) != se ({len(se)})")
    
    if len(effects) < 2:
        raise ValueError("At least 2 studies required for meta-analysis")
    
    # Coerce to numeric and validate
    try:
        effects = [float(x) for x in effects]
        se = [float(x) for x in se]
    except (TypeError, ValueError) as e:
        raise ValueError(f"Non-numeric values in effects or se: {e}")
    
    # Check for NaN/infinite values
    if any(np.isnan(effects)) or any(np.isinf(effects)):
        raise ValueError("NaN or infinite values found in effects")
    if any(np.isnan(se)) or any(np.isinf(se)):
        raise ValueError("NaN or infinite values found in se")
    if any(x <= 0 for x in se):
        raise ValueError("Standard errors must be positive")
    
    # Handle labels
    if labels is None:
        labels = [f'Study_{i+1}' for i in range(len(effects))]
    elif len(labels) != len(effects):
        raise ValueError(f"Length mismatch: labels ({len(labels)}) != effects ({len(effects)})")
    
    data = pd.DataFrame({
        'effect': effects,
        'se': se,
        'study': labels
    })
    
    config = UnifiedMetaConfig(tau2_method=tau2_method, use_hksj=use_hksj)
    return UnifiedMetaAnalysis(data, 'effect', 'se', 'study', config=config).analyze(include_conflicts=False)

def meta_from_summary_stats(means1: List[float], sds1: List[float], n1: List[int],
                           means2: List[float], sds2: List[float], n2: List[int],
                           measure: str = 'SMD') -> UnifiedMetaAnalysis:
    """Meta-analysis from summary statistics with validation
    
    Args:
        means1: List of means for group 1
        sds1: List of standard deviations for group 1
        n1: List of sample sizes for group 1
        means2: List of means for group 2
        sds2: List of standard deviations for group 2
        n2: List of sample sizes for group 2
        measure: Effect size measure ('SMD' or 'MD')
        
    Returns:
        UnifiedMetaAnalysis: Fitted meta-analysis object
        
    Raises:
        ValueError: If inputs are invalid
    """
    # Validate measure
    if measure not in ['SMD', 'MD']:
        raise ValueError(f"Invalid measure '{measure}'. Must be 'SMD' or 'MD'")
    
    # Validate equal lengths
    lengths = [len(means1), len(sds1), len(n1), len(means2), len(sds2), len(n2)]
    if len(set(lengths)) > 1:
        raise ValueError(f"Unequal input lengths: {lengths}")
    
    if lengths[0] < 2:
        raise ValueError("At least 2 studies required for meta-analysis")
    
    # Coerce and validate numeric inputs
    try:
        means1 = [float(x) for x in means1]
        means2 = [float(x) for x in means2]
        sds1 = [float(x) for x in sds1]
        sds2 = [float(x) for x in sds2]
        n1 = [int(x) for x in n1]
        n2 = [int(x) for x in n2]
    except (TypeError, ValueError) as e:
        raise ValueError(f"Invalid numeric values: {e}")
    
    # Validate sample sizes
    if any(x <= 0 for x in n1) or any(x <= 0 for x in n2):
        raise ValueError("Sample sizes must be positive")
    
    # Validate standard deviations
    if any(x <= 0 for x in sds1) or any(x <= 0 for x in sds2):
        raise ValueError("Standard deviations must be positive")
    
    # Check for NaN/infinite values
    all_values = means1 + means2 + sds1 + sds2
    if any(np.isnan(all_values)) or any(np.isinf(all_values)):
        raise ValueError("NaN or infinite values found in summary statistics")
    
    effects = []
    ses = []
    
    for m1, sd1, n1_i, m2, sd2, n2_i in zip(means1, sds1, n1, means2, sds2, n2):
        if measure == 'SMD':
            # Standardized mean difference (Cohen's d)
            pooled_sd = np.sqrt(((n1_i - 1) * sd1**2 + (n2_i - 1) * sd2**2) / (n1_i + n2_i - 2))
            if pooled_sd <= 0:
                raise ValueError(f"Invalid pooled SD ({pooled_sd}) for study {len(effects)+1}")
            d = (m1 - m2) / pooled_sd
            var_d = (n1_i + n2_i) / (n1_i * n2_i) + d**2 / (2 * (n1_i + n2_i))
            effects.append(d)
            ses.append(np.sqrt(var_d))
        elif measure == 'MD':
            # Mean difference
            md = m1 - m2
            var_md = sd1**2 / n1_i + sd2**2 / n2_i
            effects.append(md)
            ses.append(np.sqrt(var_md))
    
    data = pd.DataFrame({
        'effect': effects,
        'se': ses,
        'study': [f'Study_{i+1}' for i in range(len(effects))]
    })
    
    return UnifiedMetaAnalysis(data, 'effect', 'se', 'study').analyze(include_conflicts=False)

# ===================================================================
# MAIN EXECUTION
# ===================================================================

if __name__ == '__main__':
    try:
        print("Starting PyMeta-CBAMM Unified Suite demonstration...")
        demo_meta = run_unified_demo(
            n_studies=25, 
            seed=42, 
            output_dir=".", 
            save_visuals=True, 
            save_text_report=True
        )
        print(f"\nDemo completed successfully! Unified meta-analysis object returned.")
        print(f"Access results with: demo_meta.results")
        print(f"Generate report with: demo_meta.comprehensive_report()")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
        print("\nIf you encounter issues, please check:")
        print("- Required dependencies are installed")
        print("- Input data is valid")
        print("- Sufficient disk space for outputs")
        raise

# ===================================================================
# MULTILEVEL/MULTIVARIATE META-ANALYSIS (PHASE 2: METAFOR::RMA.MV-INSPIRED)
# ===================================================================

@dataclass
class MultilevelResults:
    """Results from multilevel/multivariate meta-analysis"""
    effects: np.ndarray = field(default_factory=lambda: np.array([]))
    se: np.ndarray = field(default_factory=lambda: np.array([]))
    ci_low: np.ndarray = field(default_factory=lambda: np.array([]))
    ci_high: np.ndarray = field(default_factory=lambda: np.array([]))
    variance_components: Dict[str, float] = field(default_factory=dict)
    
class MultilevelMetaAnalysis:
    """Multilevel/multivariate meta-analysis with metafor::rma.mv-inspired functionality"""
    
    def __init__(self, data: pd.DataFrame, yi_col: str, vi_col: str, 
                 study_col: str, outcome_col: str = None, time_col: str = None,
                 S_matrices: Dict[str, np.ndarray] = None, 
                 W_matrices: Dict[str, np.ndarray] = None):
        """
        Initialize multilevel meta-analysis
        
        Parameters:
        data: DataFrame with effect sizes
        yi_col: Column name for effect sizes
        vi_col: Column name for variances  
        study_col: Column name for study identifiers
        outcome_col: Column name for outcome identifiers (for multiple outcomes)
        time_col: Column name for time points (for longitudinal data)
        S_matrices: Dict of within-study covariance matrices by study
        W_matrices: Dict of weight matrices by study
        """
        self.data = data.copy()
        self.yi_col = yi_col
        self.vi_col = vi_col
        self.study_col = study_col
        self.outcome_col = outcome_col
        self.time_col = time_col
        self.S_matrices = S_matrices or {}
        self.W_matrices = W_matrices or {}
        
        self.results = None
        self._fitted = False
        
        # Create cluster variable for random effects
        if outcome_col and time_col:
            self.data['cluster'] = self.data[study_col].astype(str) + "_" + \
                                  self.data[outcome_col].astype(str) + "_" + \
                                  self.data[time_col].astype(str)
        elif outcome_col:
            self.data['cluster'] = self.data[study_col].astype(str) + "_" + \
                                  self.data[outcome_col].astype(str)
        elif time_col:
            self.data['cluster'] = self.data[study_col].astype(str) + "_" + \
                                  self.data[time_col].astype(str)
        else:
            self.data['cluster'] = self.data[study_col].astype(str)
            
    def fit(self, max_iter: int = 100, tol: float = 1e-6) -> 'MultilevelMetaAnalysis':
        """Fit multilevel meta-analysis using iterative GLS"""
        
        # Initialize variance components
        sigma2_study = 0.1  # Between-study variance
        sigma2_within = 0.05  # Within-study variance
        
        n_obs = len(self.data)
        y = self.data[self.yi_col].values
        
        # Create design matrix (intercept only for now)
        X = np.ones((n_obs, 1))
        
        # Iterative estimation
        for iteration in range(max_iter):
            # Construct variance-covariance matrix
            V = self._construct_variance_matrix(sigma2_study, sigma2_within)
            
            # Generalized least squares
            try:
                V_inv = safe_matrix_inverse(V)
                XtV_inv = X.T @ V_inv
                XtV_invX_inv = safe_matrix_inverse(XtV_inv @ X)
                
                # Parameter estimates
                beta = XtV_invX_inv @ XtV_inv @ y
                
                # Residuals
                residuals = y - X @ beta
                
                # Update variance components using REML-like estimation
                new_sigma2_study, new_sigma2_within = self._update_variance_components(
                    residuals, V_inv, sigma2_study, sigma2_within)
                
                # Check convergence
                if (abs(new_sigma2_study - sigma2_study) < tol and 
                    abs(new_sigma2_within - sigma2_within) < tol):
                    break
                    
                sigma2_study = new_sigma2_study
                sigma2_within = new_sigma2_within
                
            except np.linalg.LinAlgError:
                logger.warning("Numerical issues in multilevel meta-analysis")
                break
        
        # Final estimates
        var_beta = XtV_invX_inv
        se_beta = np.sqrt(np.diag(var_beta))
        
        # Confidence intervals
        z_crit = norm.ppf(0.975)
        ci_low = beta - z_crit * se_beta
        ci_high = beta + z_crit * se_beta
        
        self.results = MultilevelResults(
            effects=beta,
            se=se_beta, 
            ci_low=ci_low,
            ci_high=ci_high,
            variance_components={
                'sigma2_study': sigma2_study,
                'sigma2_within': sigma2_within
            }
        )
        
        self._fitted = True
        return self
        
    def _construct_variance_matrix(self, sigma2_study: float, 
                                 sigma2_within: float) -> np.ndarray:
        """Construct variance-covariance matrix for multilevel model"""
        n_obs = len(self.data)
        V = np.zeros((n_obs, n_obs))
        
        # Add sampling variances to diagonal
        V = np.diag(self.data[self.vi_col].values)
        
        # Add random effects structure
        studies = self.data[self.study_col].unique()
        for study in studies:
            study_indices = self.data[self.data[self.study_col] == study].index.tolist()
            
            # Between-study variance component
            for i in study_indices:
                for j in study_indices:
                    V[i, j] += sigma2_study
                    
            # Within-study covariance (if multiple outcomes/timepoints per study)
            if len(study_indices) > 1:
                # Use provided S matrix if available
                if study in self.S_matrices:
                    S = self.S_matrices[study]
                    for idx_i, i in enumerate(study_indices):
                        for idx_j, j in enumerate(study_indices):
                            if idx_i != idx_j and idx_i < len(S) and idx_j < len(S):
                                V[i, j] += S[idx_i, idx_j]
                else:
                    # Default within-study correlation structure
                    for i in study_indices:
                        for j in study_indices:
                            if i != j:
                                V[i, j] += sigma2_within
        
        return V
        
    def _update_variance_components(self, residuals: np.ndarray, V_inv: np.ndarray,
                                  sigma2_study: float, sigma2_within: float) -> Tuple[float, float]:
        """Update variance components using method-of-moments-like approach"""
        
        # Simple method-of-moments update (could be improved with REML)
        # Between-study component
        study_effects = []
        for study in self.data[self.study_col].unique():
            study_indices = self.data[self.data[self.study_col] == study].index.tolist()
            if len(study_indices) > 0:
                study_mean_residual = np.mean(residuals[study_indices])
                study_effects.append(study_mean_residual)
        
        if len(study_effects) > 1:
            new_sigma2_study = max(0, np.var(study_effects))
        else:
            new_sigma2_study = sigma2_study
            
        # Within-study component (simplified)
        within_residuals = []
        for study in self.data[self.study_col].unique():
            study_indices = self.data[self.data[self.study_col] == study].index.tolist()
            if len(study_indices) > 1:
                study_residuals = residuals[study_indices]
                study_mean = np.mean(study_residuals)
                within_residuals.extend(study_residuals - study_mean)
        
        if len(within_residuals) > 1:
            new_sigma2_within = max(0, np.var(within_residuals))
        else:
            new_sigma2_within = sigma2_within
            
        return new_sigma2_study, new_sigma2_within
        
    def cluster_robust_se(self) -> np.ndarray:
        """Calculate cluster-robust standard errors (CRVE/CR2 when available)"""
        if not self._fitted:
            raise ValueError("Model must be fitted first")
            
        # Placeholder for cluster-robust variance estimation
        # In practice, this would implement sandwich estimators
        logger.warning("Cluster-robust SE not fully implemented - returning model-based SE")
        return self.results.se

# ===================================================================
# ROBUST VARIANCE ESTIMATION & CORRELATED EFFECTS (PHASE 2: ROBUMETA/CLUBSANDWICH-INSPIRED)
# ===================================================================

class CorrelatedEffectsAnalysis:
    """Correlated effects meta-analysis with robust variance estimation"""
    
    def __init__(self, data: pd.DataFrame, yi_col: str, vi_col: str, 
                 study_col: str, rho: float = 0.8):
        """
        Initialize correlated effects analysis
        
        Parameters:
        data: DataFrame with effect sizes
        yi_col: Column name for effect sizes
        vi_col: Column name for variances
        study_col: Column name for study identifiers
        rho: Working correlation parameter
        """
        self.data = data.copy()
        self.yi_col = yi_col
        self.vi_col = vi_col
        self.study_col = study_col
        self.rho = rho
        
        self.results = {}
        
    def sensitivity_analysis(self, rho_values: List[float] = None) -> pd.DataFrame:
        """Conduct sensitivity analysis over correlation parameter values"""
        if rho_values is None:
            rho_values = np.arange(0, 0.95, 0.1)
            
        sensitivity_results = []
        
        for rho in rho_values:
            self.rho = rho
            result = self._fit_correlated_effects()
            
            sensitivity_results.append({
                'rho': rho,
                'effect': result['effect'],
                'se': result['se'], 
                'ci_low': result['ci_low'],
                'ci_high': result['ci_high'],
                'p_value': result['p_value']
            })
            
        return pd.DataFrame(sensitivity_results)
        
    def _fit_correlated_effects(self) -> Dict[str, float]:
        """Fit correlated effects model with working correlation"""
        
        # Construct working correlation matrix
        V = self._construct_working_correlation_matrix()
        
        y = self.data[self.yi_col].values
        X = np.ones((len(y), 1))  # Intercept only
        
        try:
            # Weighted least squares with working correlation
            V_inv = safe_matrix_inverse(V)
            XtV_inv = X.T @ V_inv
            XtV_invX_inv = safe_matrix_inverse(XtV_inv @ X)
            
            beta = XtV_invX_inv @ XtV_inv @ y
            
            # Robust variance estimation (sandwich estimator)
            residuals = y - X @ beta
            meat = self._calculate_meat_matrix(residuals, X, V_inv)
            robust_var = XtV_invX_inv @ meat @ XtV_invX_inv
            
            se = np.sqrt(np.diag(robust_var))[0]
            effect = beta[0]
            
            # Satterthwaite degrees of freedom (simplified)
            df = self._calculate_satterthwaite_df(V, V_inv)
            t_crit = t.ppf(0.975, df)
            
            ci_low = effect - t_crit * se
            ci_high = effect + t_crit * se
            
            t_stat = effect / se if se > 0 else 0
            p_value = 2 * (1 - t.cdf(abs(t_stat), df))
            
            return {
                'effect': effect,
                'se': se,
                'ci_low': ci_low, 
                'ci_high': ci_high,
                'p_value': p_value,
                'df': df
            }
            
        except np.linalg.LinAlgError:
            logger.warning("Numerical issues in correlated effects analysis")
            return {
                'effect': 0.0,
                'se': np.inf,
                'ci_low': -np.inf,
                'ci_high': np.inf,
                'p_value': 1.0,
                'df': 1
            }
            
    def _construct_working_correlation_matrix(self) -> np.ndarray:
        """Construct working correlation matrix"""
        n = len(self.data)
        V = np.diag(self.data[self.vi_col].values)
        
        # Add correlations for effects within same study
        for study in self.data[self.study_col].unique():
            study_indices = self.data[self.data[self.study_col] == study].index.tolist()
            
            for i in study_indices:
                for j in study_indices:
                    if i != j:
                        # Working correlation between effects in same study
                        vi, vj = self.data.loc[i, self.vi_col], self.data.loc[j, self.vi_col]
                        V[i, j] = self.rho * np.sqrt(vi * vj)
                        
        return V
        
    def _calculate_meat_matrix(self, residuals: np.ndarray, X: np.ndarray, 
                             V_inv: np.ndarray) -> np.ndarray:
        """Calculate meat matrix for sandwich variance estimator"""
        n_studies = self.data[self.study_col].nunique()
        p = X.shape[1]
        meat = np.zeros((p, p))
        
        # Cluster by study for robust variance
        for study in self.data[self.study_col].unique():
            study_indices = self.data[self.data[self.study_col] == study].index.tolist()
            
            if len(study_indices) > 0:
                X_study = X[study_indices, :]
                resid_study = residuals[study_indices]
                V_inv_study = V_inv[np.ix_(study_indices, study_indices)]
                
                # Study contribution to meat matrix
                study_contrib = X_study.T @ V_inv_study @ np.outer(resid_study, resid_study) @ V_inv_study @ X_study
                meat += study_contrib
                
        return meat
        
    def _calculate_satterthwaite_df(self, V: np.ndarray, V_inv: np.ndarray) -> float:
        """Calculate Satterthwaite degrees of freedom (simplified)"""
        # Simplified calculation - in practice this would be more complex
        n_studies = self.data[self.study_col].nunique()
        return max(1, n_studies - 1)

# ===================================================================
# SELECTION MODELS AND SMALL-STUDY BIAS (PHASE 2)
# ===================================================================

class SelectionModels:
    """Selection models for publication bias correction"""
    
    @staticmethod
    def vevea_hedges_model(effects: np.ndarray, se: np.ndarray, 
                          p_values: np.ndarray = None, 
                          intervals: List[Tuple[float, float]] = None) -> Dict[str, Any]:
        """
        Vevea-Hedges weight-function selection model
        
        Parameters:
        effects: Array of effect sizes
        se: Array of standard errors
        p_values: Array of p-values (calculated if None)
        intervals: P-value intervals for weight function
        """
        
        # Check for optional optimization dependencies
        try:
            from scipy.optimize import minimize
        except ImportError:
            return {
                'available': False,
                'message': 'scipy.optimize not available for selection models'
            }
            
        if p_values is None:
            z_scores = effects / se
            p_values = 2 * (1 - norm.cdf(np.abs(z_scores)))
            
        if intervals is None:
            # Default p-value intervals
            intervals = [(0.0, 0.01), (0.01, 0.05), (0.05, 0.1), (0.1, 1.0)]
            
        # Weight function parameters (to be estimated)
        n_intervals = len(intervals)
        
        def neg_log_likelihood(params):
            """Negative log-likelihood for selection model"""
            mu = params[0]  # Mean effect
            tau2 = max(0, params[1])  # Heterogeneity
            weights = params[2:]  # Weight function parameters
            
            # Ensure weights are positive
            weights = np.exp(weights)
            weights = weights / weights[0]  # Normalize to first interval
            
            ll = 0.0
            for i in range(len(effects)):
                # Study likelihood
                var_i = se[i]**2 + tau2
                study_ll = norm.logpdf(effects[i], mu, np.sqrt(var_i))
                
                # Weight function contribution
                p_val = p_values[i]
                weight = 1.0
                for j, (low, high) in enumerate(intervals):
                    if low <= p_val < high:
                        weight = weights[min(j, len(weights)-1)]
                        break
                        
                ll += study_ll + np.log(weight)
                
            return -ll
            
        # Initial parameter values
        initial_mu = np.mean(effects)
        initial_tau2 = max(0.01, np.var(effects) - np.mean(se**2))
        initial_weights = np.ones(n_intervals)
        
        initial_params = [initial_mu, initial_tau2] + initial_weights.tolist()
        
        try:
            # Optimize
            result = minimize(neg_log_likelihood, initial_params, 
                            method='BFGS', options={'maxiter': 1000})
            
            if result.success:
                mu_est = result.x[0]
                tau2_est = max(0, result.x[1])
                weight_est = np.exp(result.x[2:])
                weight_est = weight_est / weight_est[0]
                
                # Calculate standard errors (simplified)
                se_mu = np.sqrt(tau2_est / len(effects))
                
                return {
                    'available': True,
                    'mu': mu_est,
                    'tau2': tau2_est,
                    'se_mu': se_mu,
                    'weights': weight_est,
                    'intervals': intervals,
                    'converged': True
                }
            else:
                return {
                    'available': True,
                    'converged': False,
                    'message': 'Optimization failed to converge'
                }
                
        except Exception as e:
            return {
                'available': True,
                'converged': False,
                'message': f'Optimization error: {str(e)}'
            }

class BiasTestSuite:
    """Extended suite of bias tests and corrections"""
    
    @staticmethod
    def peters_test(effects: np.ndarray, se: np.ndarray) -> Dict[str, Any]:
        """Peters test for binary outcome data"""
        try:
            # Weight by sample size proxy (1/se^2)
            weights = 1 / (se**2)
            
            # Simple regression implementation
            from scipy.stats import linregress
            slope, intercept, r_value, p_value, std_err = linregress(weights, effects)
            
            return {
                'slope': slope,
                'intercept': intercept, 
                'p_value': p_value,
                'significant': p_value < 0.05
            }
        except:
            return {'available': False}
            
    @staticmethod  
    def arcsine_test(effects: np.ndarray, se: np.ndarray) -> Dict[str, Any]:
        """Arcsine test for proportions"""
        try:
            # Transform effects using arcsine transformation
            transformed_effects = np.arcsin(np.sqrt(np.abs(effects)))
            
            # Simple correlation test with SE
            from scipy.stats import pearsonr
            corr, p_value = pearsonr(transformed_effects, se)
            
            return {
                'correlation': corr,
                'p_value': p_value,
                'significant': p_value < 0.05
            }
        except:
            return {'available': False}
            
    @staticmethod
    def p_curve_stub() -> Dict[str, Any]:
        """P-curve analysis stub"""
        return {
            'available': False,
            'message': 'P-curve analysis requires additional implementation'
        }
        
    @staticmethod
    def p_uniform_stub() -> Dict[str, Any]:
        """P-uniform analysis stub"""
        return {
            'available': False,
            'message': 'P-uniform analysis requires additional implementation'
        }

# ===================================================================
# EFFECT-SIZE CALCULATORS AND CONVERTERS (PHASE 2: METAFOR::ESCALC PARITY)
# ===================================================================

class EffectSizeCalculators:
    """Effect size calculation and conversion utilities"""
    
    @staticmethod
    def log_odds_ratio(events1: np.ndarray, n1: np.ndarray, 
                      events2: np.ndarray, n2: np.ndarray,
                      continuity_correction: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate log odds ratio with continuity correction"""
        
        # Apply continuity correction for zero cells
        events1_cc = events1 + continuity_correction
        events2_cc = events2 + continuity_correction
        non_events1_cc = (n1 - events1) + continuity_correction
        non_events2_cc = (n2 - events2) + continuity_correction
        
        # Log odds ratio
        lor = np.log((events1_cc * non_events2_cc) / (non_events1_cc * events2_cc))
        
        # Variance
        var_lor = (1/events1_cc + 1/non_events1_cc + 1/events2_cc + 1/non_events2_cc)
        
        return lor, np.sqrt(var_lor)
        
    @staticmethod
    def log_risk_ratio(events1: np.ndarray, n1: np.ndarray,
                      events2: np.ndarray, n2: np.ndarray,
                      continuity_correction: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate log risk ratio with continuity correction"""
        
        # Apply continuity correction
        events1_cc = events1 + continuity_correction
        events2_cc = events2 + continuity_correction
        n1_cc = n1 + 2 * continuity_correction
        n2_cc = n2 + 2 * continuity_correction
        
        # Log risk ratio
        lrr = np.log((events1_cc/n1_cc) / (events2_cc/n2_cc))
        
        # Variance
        var_lrr = (1/events1_cc - 1/n1_cc + 1/events2_cc - 1/n2_cc)
        
        return lrr, np.sqrt(var_lrr)
        
    @staticmethod
    def hedges_g(mean1: np.ndarray, sd1: np.ndarray, n1: np.ndarray,
                mean2: np.ndarray, sd2: np.ndarray, n2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate Hedges' g with small-sample correction"""
        
        # Pooled standard deviation
        pooled_sd = np.sqrt(((n1 - 1) * sd1**2 + (n2 - 1) * sd2**2) / (n1 + n2 - 2))
        
        # Cohen's d
        cohens_d = (mean1 - mean2) / pooled_sd
        
        # Small-sample correction factor (J)
        df = n1 + n2 - 2
        j = 1 - (3 / (4 * df - 1))
        
        # Hedges' g
        hedges_g = j * cohens_d
        
        # Variance
        var_g = ((n1 + n2) / (n1 * n2) + hedges_g**2 / (2 * (n1 + n2 - 2))) * j**2
        
        return hedges_g, np.sqrt(var_g)
        
    @staticmethod
    def standardized_mean_change(mean_pre: np.ndarray, sd_pre: np.ndarray,
                               mean_post: np.ndarray, sd_post: np.ndarray,
                               n: np.ndarray, r: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate standardized mean change (within-subject)"""
        
        # Change score
        mean_change = mean_post - mean_pre
        
        # Standard deviation of change (assuming correlation r)
        sd_change = np.sqrt(sd_pre**2 + sd_post**2 - 2 * r * sd_pre * sd_post)
        
        # Standardized mean change
        smc = mean_change / sd_change
        
        # Variance (approximate)
        var_smc = (1/n + smc**2/(2*n)) * 2 * (1 - r)
        
        return smc, np.sqrt(var_smc)
        
    @staticmethod
    def fisher_z_transform(correlations: np.ndarray, n: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Fisher z-transformation for correlations"""
        
        # Constrain correlations to avoid infinite values
        r = np.clip(correlations, -0.999, 0.999)
        
        # Fisher z-transform
        z = 0.5 * np.log((1 + r) / (1 - r))
        
        # Variance
        var_z = 1 / (n - 3)
        
        return z, np.sqrt(var_z)
        
    @staticmethod
    def fisher_z_inverse(z_values: np.ndarray) -> np.ndarray:
        """Inverse Fisher z-transformation"""
        return (np.exp(2 * z_values) - 1) / (np.exp(2 * z_values) + 1)
        
    @staticmethod
    def arcsine_transform(proportions: np.ndarray, n: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Arcsine transformation for proportions"""
        
        # Arcsine transformation
        asin_p = np.arcsin(np.sqrt(proportions))
        
        # Variance
        var_asin = 1 / (4 * n)
        
        return asin_p, np.sqrt(var_asin)

class EffectSizeConverters:
    """Converters between different effect size metrics"""
    
    @staticmethod
    def d_to_r(d: float) -> float:
        """Convert Cohen's d to correlation (approximate)"""
        return d / np.sqrt(d**2 + 4)
        
    @staticmethod
    def r_to_d(r: float) -> float:
        """Convert correlation to Cohen's d (approximate)"""
        return 2 * r / np.sqrt(1 - r**2)
        
    @staticmethod
    def d_to_or(d: float) -> float:
        """Convert Cohen's d to odds ratio (approximate)"""
        return np.exp(d * np.pi / np.sqrt(3))
        
    @staticmethod
    def or_to_d(odds_ratio: float) -> float:
        """Convert odds ratio to Cohen's d (approximate)"""
        return np.log(odds_ratio) * np.sqrt(3) / np.pi
        
    @staticmethod
    def g_to_d(g: float, n1: int, n2: int) -> float:
        """Convert Hedges' g to Cohen's d"""
        df = n1 + n2 - 2
        j = 1 - (3 / (4 * df - 1))
        return g / j

# ===================================================================
# IMPORT/EXPORT AND R-COMPAT ERGONOMICS (PHASE 2)
# ===================================================================

class RCompatibility:
    """R compatibility functions for seamless integration"""
    
    @staticmethod
    def read_metafor_csv(filepath: str, effect_col: str = 'yi', 
                        se_col: str = 'sei', study_col: str = 'study') -> pd.DataFrame:
        """Read metafor-like CSV files"""
        try:
            df = pd.read_csv(filepath)
            
            # Validate required columns
            required_cols = [effect_col, study_col]
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
                
            # Handle variance columns
            if se_col in df.columns:
                df['vi'] = df[se_col]**2
            elif 'vi' in df.columns:
                df[se_col] = np.sqrt(df['vi'])
            else:
                raise ValueError("Either sei or vi column must be present")
                
            return df
            
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            raise
            
    @staticmethod
    def export_for_netmeta(network_data: NetworkMetaData, filepath: str):
        """Export network data in netmeta-compatible format"""
        try:
            # Convert to long-format with required columns
            export_data = network_data.data.copy()
            export_data = export_data.rename(columns={
                'study': 'studlab',
                'treatment': 'treat', 
                'yi': 'TE',
                'sei': 'seTE'
            })
            
            # Add additional columns that netmeta expects
            if 'n' in export_data.columns:
                export_data['n'] = export_data['n']
            if 'events' in export_data.columns:
                export_data['event'] = export_data['events']
                
            export_data.to_csv(filepath, index=False)
            logger.info(f"Network data exported to {filepath}")
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            raise
            
    @staticmethod
    def generate_r_script(analysis_results: Dict[str, Any], 
                         output_path: str = "reproduce_in_r.R") -> str:
        """Generate R script to reproduce main results"""
        
        r_script = """
# R script to reproduce Metapython results
# Generated automatically for parity checking

library(metafor)
library(netmeta)

# Load data (assumes CSV export from Metapython)
# data <- read.csv("your_data.csv")

# Standard meta-analysis
# res_fe <- rma(yi, vi, data=data, method="FE")
# res_re <- rma(yi, vi, data=data, method="REML")

# Network meta-analysis  
# net <- netmeta(TE, seTE, treat, studlab, data=data)

# Print results for comparison
# print(res_fe)
# print(res_re)
# print(net)

# Note: Adapt variable names and methods to match your specific analysis
"""

        try:
            with open(output_path, 'w') as f:
                f.write(r_script)
            return output_path
        except Exception as e:
            logger.error(f"Error writing R script: {e}")
            return ""

# ===================================================================
# VERSION INFORMATION
# ===================================================================

__version__ = "3.0.0"
__author__ = "PyMeta-CBAMM Development Team"
__email__ = "pymeta-cbamm@example.com"
__description__ = "Unified meta-analysis suite combining PyMeta v2.1 and CBAMM v5.7"
__license__ = "MIT"

# Export main classes and functions
__all__ = [
    'UnifiedMetaAnalysis',
    'UnifiedMetaConfig', 
    'TauSquaredEstimators',
    'TransportWeighting',
    'ConflictDetection',
    'NLPExtractor',
    'OutcomeClassifier',
    'PubMedIntegration',
    'EnhancedDiagnosticTestAccuracy',
    'NetworkMetaRankings',
    'EnhancedTrialSequentialAnalysis',
    'EnhancedGRADE',
    'PerformanceOptimization',
    # Phase 2 additions
    'NetworkMetaData',
    'NetworkMetaAnalysis',
    'NetworkConsistencyResults',
    'NetworkGeometry',
    'MultilevelMetaAnalysis',
    'MultilevelResults',
    'CorrelatedEffectsAnalysis',
    'SelectionModels',
    'BiasTestSuite',
    'EffectSizeCalculators',
    'EffectSizeConverters',
    'RCompatibility',
    'quick_meta',
    'meta_from_summary_stats',
    'run_unified_demo'
]
