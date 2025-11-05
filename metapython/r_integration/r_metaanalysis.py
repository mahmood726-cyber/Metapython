"""
R Meta-Analysis Functions

Python wrappers for R meta-analysis packages:
- meta, metafor, netmeta packages
- Integration with mahmood789 Shiny apps
- Advanced R-based methods not in Python
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd

from metapython.core.config import logger
from metapython.r_integration.rpy2_bridge import RPythonBridge, HAS_RPY2, convert_to_r, convert_from_r


def r_network_meta_analysis(
    studies: pd.DataFrame,
    outcome_col: str = 'effect',
    se_col: str = 'se',
    treatment_col: str = 'treatment',
    study_col: str = 'study',
    reference: Optional[str] = None,
    method: str = 'frequentist'
) -> Dict[str, Any]:
    """
    Network meta-analysis using R netmeta package.

    Args:
        studies: DataFrame with study data
        outcome_col: Column name for effect sizes
        se_col: Column name for standard errors
        treatment_col: Column name for treatments
        study_col: Column name for study IDs
        reference: Reference treatment
        method: 'frequentist' or 'bayesian'

    Returns:
        Network meta-analysis results
    """
    if not HAS_RPY2:
        raise ImportError("rpy2 required for R integration")

    bridge = RPythonBridge(auto_install_packages=True)

    if method == 'frequentist':
        # Install and load netmeta
        bridge.ensure_packages(['netmeta'])

        # Prepare data
        bridge.set_r_variable('data', studies)

        # Run network meta-analysis
        r_code = f"""
library(netmeta)
nma <- netmeta(
    TE = data${outcome_col},
    seTE = data${se_col},
    treat1 = data$treat1,
    treat2 = data$treat2,
    studlab = data${study_col},
    reference.group = {f"'{reference}'" if reference else 'NULL'}
)
summary(nma)
"""
        result = bridge.run_r_code(r_code)

        # Extract results
        return {
            'method': 'Network meta-analysis (frequentist)',
            'reference': reference,
            'results': result,
            'package': 'netmeta'
        }

    elif method == 'bayesian':
        # Install and load gemtc
        bridge.ensure_packages(['gemtc', 'rjags'])

        # Prepare data for JAGS
        bridge.set_r_variable('data', studies)

        r_code = """
library(gemtc)
network <- mtc.network(data.ab=data)
model <- mtc.model(network, type='consistency')
results <- mtc.run(model, n.adapt=5000, n.iter=20000)
summary(results)
"""
        result = bridge.run_r_code(r_code)

        return {
            'method': 'Network meta-analysis (Bayesian)',
            'results': result,
            'package': 'gemtc'
        }

    else:
        raise ValueError(f"Unknown method: {method}")


def r_dose_response(
    doses: np.ndarray,
    effects: np.ndarray,
    se: np.ndarray,
    model: str = 'linear',
    covariates: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    Dose-response meta-analysis using R dosresmeta package.

    Args:
        doses: Dose levels
        effects: Effect sizes
        se: Standard errors
        model: 'linear', 'quadratic', 'restricted_spline'
        covariates: Optional covariates

    Returns:
        Dose-response results
    """
    if not HAS_RPY2:
        raise ImportError("rpy2 required")

    bridge = RPythonBridge(auto_install_packages=True)
    bridge.ensure_packages(['dosresmeta'])

    # Create data frame
    data = pd.DataFrame({
        'dose': doses,
        'effect': effects,
        'se': se
    })

    if covariates is not None:
        data = pd.concat([data, covariates], axis=1)

    bridge.set_r_variable('data', data)

    # Model specification
    if model == 'linear':
        formula = 'effect ~ dose'
    elif model == 'quadratic':
        formula = 'effect ~ dose + I(dose^2)'
    elif model == 'restricted_spline':
        formula = 'effect ~ rcs(dose, 3)'
    else:
        formula = model

    r_code = f"""
library(dosresmeta)
library(rms)  # For rcs()
model <- dosresmeta(formula = {formula}, se = se, data = data)
summary(model)
pred <- predict(model, newdata = data.frame(dose = seq(min(data$dose), max(data$dose), length.out = 100)))
list(model = model, predictions = pred)
"""
    result = bridge.run_r_code(r_code)

    return {
        'method': 'Dose-response meta-analysis',
        'model': model,
        'results': result,
        'package': 'dosresmeta'
    }


def r_bayesian_nma(
    studies: pd.DataFrame,
    outcome_type: str = 'continuous',
    n_adapt: int = 5000,
    n_iter: int = 20000,
    n_chains: int = 3
) -> Dict[str, Any]:
    """
    Bayesian network meta-analysis using JAGS.

    Args:
        studies: Study data
        outcome_type: 'continuous', 'binary', 'rate'
        n_adapt: Adaptation iterations
        n_iter: Sampling iterations
        n_chains: Number of MCMC chains

    Returns:
        Bayesian NMA results with posterior distributions
    """
    if not HAS_RPY2:
        raise ImportError("rpy2 required")

    bridge = RPythonBridge(auto_install_packages=True)
    bridge.ensure_packages(['gemtc', 'rjags', 'coda'])

    bridge.set_r_variable('data', studies)

    r_code = f"""
library(gemtc)
library(rjags)
library(coda)

# Create network
network <- mtc.network(data.ab=data)

# Define model
model <- mtc.model(
    network,
    type='consistency',
    likelihood='{outcome_type}',
    link='identity'
)

# Run MCMC
results <- mtc.run(
    model,
    n.adapt={n_adapt},
    n.iter={n_iter},
    thin=10
)

# Summarize
summary_results <- summary(results)
rank_prob <- rank.probability(results)
sucra <- relative.effect.table(results)

list(
    summary = summary_results,
    rank_probability = rank_prob,
    sucra = sucra,
    mcmc = as.matrix(results$samples[[1]])
)
"""
    result = bridge.run_r_code(r_code)

    return {
        'method': 'Bayesian network meta-analysis',
        'outcome_type': outcome_type,
        'n_iterations': n_iter,
        'n_chains': n_chains,
        'results': result,
        'package': 'gemtc/JAGS'
    }


def r_multilevel_meta(
    effects: np.ndarray,
    variances: np.ndarray,
    study_ids: np.ndarray,
    effect_ids: np.ndarray,
    method: str = 'REML'
) -> Dict[str, Any]:
    """
    Three-level meta-analysis using R metafor package.

    Accounts for clustering of effects within studies.

    Args:
        effects: Effect sizes
        variances: Sampling variances
        study_ids: Study identifiers
        effect_ids: Effect-within-study identifiers
        method: Estimation method

    Returns:
        Multilevel meta-analysis results
    """
    if not HAS_RPY2:
        raise ImportError("rpy2 required")

    bridge = RPythonBridge(auto_install_packages=True)
    bridge.ensure_packages(['metafor'])

    # Create data frame
    data = pd.DataFrame({
        'yi': effects,
        'vi': variances,
        'study': study_ids,
        'effect': effect_ids
    })

    bridge.set_r_variable('data', data)

    r_code = f"""
library(metafor)

# Three-level model
model <- rma.mv(
    yi = yi,
    V = vi,
    random = ~ 1 | study/effect,
    data = data,
    method = "{method}"
)

summary(model)

# Extract variance components
sigma2_level2 <- model$sigma2[1]  # Within-study variance
sigma2_level3 <- model$sigma2[2]  # Between-study variance

# Calculate I² for each level
W <- diag(1/data$vi)
X <- model.matrix(model)
P <- W - W %*% X %*% solve(t(X) %*% W %*% X) %*% t(X) %*% W
I2_level2 <- sigma2_level2 / (sigma2_level2 + sigma2_level3 + sum(diag(P))/nrow(data)) * 100
I2_level3 <- sigma2_level3 / (sigma2_level2 + sigma2_level3 + sum(diag(P))/nrow(data)) * 100

list(
    model = model,
    sigma2_level2 = sigma2_level2,
    sigma2_level3 = sigma2_level3,
    I2_level2 = I2_level2,
    I2_level3 = I2_level3
)
"""
    result = bridge.run_r_code(r_code)

    return {
        'method': 'Three-level meta-analysis',
        'estimation_method': method,
        'results': result,
        'package': 'metafor'
    }


def r_diagnostic_accuracy(
    tp: np.ndarray,
    fp: np.ndarray,
    fn: np.ndarray,
    tn: np.ndarray,
    study_labels: Optional[np.ndarray] = None
) -> Dict[str, Any]:
    """
    Diagnostic test accuracy meta-analysis using R mada package.

    Args:
        tp: True positives
        fp: False positives
        fn: False negatives
        tn: True negatives
        study_labels: Study labels

    Returns:
        DTA meta-analysis results with SROC curve
    """
    if not HAS_RPY2:
        raise ImportError("rpy2 required")

    bridge = RPythonBridge(auto_install_packages=True)
    bridge.ensure_packages(['mada'])

    # Create data frame
    data = pd.DataFrame({
        'TP': tp,
        'FP': fp,
        'FN': fn,
        'TN': tn
    })

    if study_labels is not None:
        data['study'] = study_labels

    bridge.set_r_variable('data', data)

    r_code = """
library(mada)

# Fit bivariate model
fit <- reitsma(data)

# SROC curve
sroc_data <- SROCplot(fit, return.data=TRUE)

# Summary estimates
summary_fit <- summary(fit)

# Calculate sensitivity and specificity
sens <- data$TP / (data$TP + data$FN)
spec <- data$TN / (data$TN + data$FP)

list(
    model = fit,
    summary = summary_fit,
    sroc = sroc_data,
    sensitivity = sens,
    specificity = spec,
    pooled_sensitivity = summary_fit$coefficients['tsens', 'Estimate'],
    pooled_specificity = summary_fit$coefficients['tfpr', 'Estimate']
)
"""
    result = bridge.run_r_code(r_code)

    return {
        'method': 'Diagnostic test accuracy meta-analysis',
        'model': 'Bivariate (Reitsma)',
        'results': result,
        'package': 'mada'
    }


__all__ = [
    'r_network_meta_analysis',
    'r_dose_response',
    'r_bayesian_nma',
    'r_multilevel_meta',
    'r_diagnostic_accuracy',
]
