from __future__ import annotations
from typing import Optional, List, Union, Tuple, Literal
import numpy as np
import pandas as pd
from scipy import stats

from .models import MetaResult, MetaAnalysis
from .effect_sizes import hedges_g, mean_difference, log_or, log_rr, risk_diff, logit_prop
from .tau2 import estimate_tau2


def _meta_core(y: np.ndarray, vi: np.ndarray, 
               method: Literal["DL", "PM"] = "DL",
               level: float = 0.95,
               hakn: bool = False) -> Tuple[MetaResult, MetaResult]:
    """Core meta-analysis computation for both fixed and random effects"""
    
    k = len(y)
    if k < 2:
        raise ValueError("At least 2 studies required")
    
    alpha = 1 - level
    
    # Fixed-effects analysis
    wi_fixed = 1.0 / vi
    sum_wi = np.sum(wi_fixed)
    fe_effect = np.sum(wi_fixed * y) / sum_wi
    fe_se = np.sqrt(1.0 / sum_wi)
    
    # Q statistic for heterogeneity
    Q = np.sum(wi_fixed * (y - fe_effect) ** 2)
    df = k - 1
    Q_pval = 1 - stats.chi2.cdf(Q, df) if df > 0 else 1.0
    
    # I² and H²
    I2 = max(0, (Q - df) / Q * 100) if Q > 0 else 0
    H2 = Q / df if df > 0 else 1
    
    # Fixed-effects confidence interval
    z_crit = stats.norm.ppf(1 - alpha/2)
    fe_ci_lower = fe_effect - z_crit * fe_se
    fe_ci_upper = fe_effect + z_crit * fe_se
    fe_z = fe_effect / fe_se if fe_se > 0 else 0
    fe_p = 2 * (1 - stats.norm.cdf(abs(fe_z)))
    
    fe_result = MetaResult(
        effect=fe_effect,
        se=fe_se,
        ci_lower=fe_ci_lower,
        ci_upper=fe_ci_upper,
        z_statistic=fe_z,
        p_value=fe_p,
        tau2=0.0,
        Q=Q,
        df=df,
        Q_pval=Q_pval,
        I2=I2,
        H2=H2,
        method=method,
        model="fixed",
        k=k
    )
    
    # Random-effects analysis
    tau2, _, _ = estimate_tau2(y, vi, method)
    
    wi_random = 1.0 / (vi + tau2)
    sum_wi_re = np.sum(wi_random)
    re_effect = np.sum(wi_random * y) / sum_wi_re
    re_se = np.sqrt(1.0 / sum_wi_re)
    
    # Hartung-Knapp adjustment
    if hakn and k > 2:
        Q_re = np.sum(wi_random * (y - re_effect) ** 2)
        df_hk = k - 1
        inflation = max(1, Q_re / df_hk) if df_hk > 0 else 1
        re_se_adj = re_se * np.sqrt(inflation)
        
        # Use t-distribution
        t_crit = stats.t.ppf(1 - alpha/2, df_hk)
        re_ci_lower = re_effect - t_crit * re_se_adj
        re_ci_upper = re_effect + t_crit * re_se_adj
        re_t = re_effect / re_se_adj if re_se_adj > 0 else 0
        re_p = 2 * (1 - stats.t.cdf(abs(re_t), df_hk))
        
        re_se = re_se_adj  # Use adjusted SE
        re_z = re_t  # Actually t-statistic
    else:
        # Normal approximation
        re_ci_lower = re_effect - z_crit * re_se
        re_ci_upper = re_effect + z_crit * re_se
        re_z = re_effect / re_se if re_se > 0 else 0
        re_p = 2 * (1 - stats.norm.cdf(abs(re_z)))
    
    # Prediction interval
    pred_se = np.sqrt(re_se**2 + tau2)
    pred_lower = re_effect - z_crit * pred_se
    pred_upper = re_effect + z_crit * pred_se
    prediction_interval = (pred_lower, pred_upper)
    
    re_result = MetaResult(
        effect=re_effect,
        se=re_se,
        ci_lower=re_ci_lower,
        ci_upper=re_ci_upper,
        z_statistic=re_z,
        p_value=re_p,
        tau2=tau2,
        Q=Q,
        df=df,
        Q_pval=Q_pval,
        I2=I2,
        H2=H2,
        method=method,
        model="random",
        k=k,
        prediction_interval=prediction_interval
    )
    
    return fe_result, re_result


def metagen(effect: Union[List[float], np.ndarray], 
            se: Union[List[float], np.ndarray],
            studlab: Optional[Union[List[str], np.ndarray]] = None,
            data: Optional[pd.DataFrame] = None,
            method: Literal["DL", "PM"] = "DL",
            level: float = 0.95,
            hakn: bool = False) -> MetaAnalysis:
    """
    Generic inverse variance meta-analysis
    
    Parameters:
    -----------
    effect : array-like
        Effect sizes
    se : array-like  
        Standard errors
    studlab : array-like, optional
        Study labels
    data : DataFrame, optional
        Data frame containing the variables
    method : {'DL', 'PM'}, default 'DL'
        Method for tau² estimation
    level : float, default 0.95
        Confidence level
    hakn : bool, default False
        Use Hartung-Knapp adjustment
        
    Returns:
    --------
    MetaAnalysis object with results
    """
    
    # Handle data input
    if data is not None:
        if isinstance(effect, str):
            effect = data[effect].values
        if isinstance(se, str):
            se = data[se].values
        if isinstance(studlab, str):
            studlab = data[studlab].values
    
    # Convert to numpy arrays
    y = np.asarray(effect, dtype=float)
    vi = np.asarray(se, dtype=float) ** 2
    
    if studlab is None:
        studlab = [f"Study {i+1}" for i in range(len(y))]
    else:
        studlab = np.asarray(studlab, dtype=str)
    
    # Validation
    if len(y) != len(vi) or len(y) != len(studlab):
        raise ValueError("effect, se, and studlab must have same length")
    
    if np.any(vi <= 0):
        raise ValueError("Standard errors must be positive")
    
    # Create studies dataframe
    studies_df = pd.DataFrame({
        'effect': y,
        'se': np.sqrt(vi),
        'study': studlab
    })
    
    # Run analysis
    fe_result, re_result = _meta_core(y, vi, method, level, hakn)
    
    # Create MetaAnalysis object
    meta = MetaAnalysis(
        studies=studies_df,
        effect_col='effect',
        se_col='se', 
        study_col='study',
        alpha=1-level
    )
    meta.fixed_result = fe_result
    meta.random_result = re_result
    
    return meta


def metacont(m1: Union[List[float], np.ndarray],
             sd1: Union[List[float], np.ndarray], 
             n1: Union[List[int], np.ndarray],
             m2: Union[List[float], np.ndarray],
             sd2: Union[List[float], np.ndarray],
             n2: Union[List[int], np.ndarray],
             studlab: Optional[Union[List[str], np.ndarray]] = None,
             data: Optional[pd.DataFrame] = None,
             sm: Literal["SMD", "MD"] = "SMD",
             method: Literal["DL", "PM"] = "DL",
             level: float = 0.95,
             hakn: bool = False) -> MetaAnalysis:
    """
    Meta-analysis of continuous outcomes
    
    Parameters:
    -----------
    m1, sd1, n1 : array-like
        Mean, SD, sample size for group 1
    m2, sd2, n2 : array-like  
        Mean, SD, sample size for group 2
    studlab : array-like, optional
        Study labels
    data : DataFrame, optional
        Data frame containing the variables
    sm : {'SMD', 'MD'}, default 'SMD'
        Summary measure (Standardized Mean Difference or Mean Difference)
    method : {'DL', 'PM'}, default 'DL'
        Method for tau² estimation
    level : float, default 0.95
        Confidence level
    hakn : bool, default False
        Use Hartung-Knapp adjustment
        
    Returns:
    --------
    MetaAnalysis object with results
    """
    
    # Handle data input
    if data is not None:
        variables = [m1, sd1, n1, m2, sd2, n2]
        var_names = ['m1', 'sd1', 'n1', 'm2', 'sd2', 'n2']
        for i, var in enumerate(variables):
            if isinstance(var, str):
                variables[i] = data[var].values
        m1, sd1, n1, m2, sd2, n2 = variables
        
        if isinstance(studlab, str):
            studlab = data[studlab].values
    
    # Convert to numpy arrays
    m1 = np.asarray(m1, dtype=float)
    sd1 = np.asarray(sd1, dtype=float)
    n1 = np.asarray(n1, dtype=int)
    m2 = np.asarray(m2, dtype=float)
    sd2 = np.asarray(sd2, dtype=float)
    n2 = np.asarray(n2, dtype=int)
    
    if studlab is None:
        studlab = [f"Study {i+1}" for i in range(len(m1))]
    else:
        studlab = np.asarray(studlab, dtype=str)
    
    # Calculate effect sizes
    effects = []
    ses = []
    
    for i in range(len(m1)):
        if sm == "SMD":
            eff, se = hedges_g(m1[i], sd1[i], n1[i], m2[i], sd2[i], n2[i])
        elif sm == "MD":
            eff, se = mean_difference(m1[i], sd1[i], n1[i], m2[i], sd2[i], n2[i])
        else:
            raise ValueError("sm must be 'SMD' or 'MD'")
        
        effects.append(eff)
        ses.append(se)
    
    return metagen(effects, ses, studlab, method=method, level=level, hakn=hakn)


def metabin(event1: Union[List[int], np.ndarray],
            n1: Union[List[int], np.ndarray],
            event2: Union[List[int], np.ndarray], 
            n2: Union[List[int], np.ndarray],
            studlab: Optional[Union[List[str], np.ndarray]] = None,
            data: Optional[pd.DataFrame] = None,
            sm: Literal["OR", "RR", "RD"] = "OR",
            method: Literal["DL", "PM"] = "DL",
            level: float = 0.95,
            hakn: bool = False,
            incr: float = 0.5) -> MetaAnalysis:
    """
    Meta-analysis of binary outcomes
    
    Parameters:
    -----------
    event1, n1 : array-like
        Events and total in group 1
    event2, n2 : array-like
        Events and total in group 2
    studlab : array-like, optional
        Study labels
    data : DataFrame, optional
        Data frame containing the variables  
    sm : {'OR', 'RR', 'RD'}, default 'OR'
        Summary measure (Odds Ratio, Risk Ratio, Risk Difference)
    method : {'DL', 'PM'}, default 'DL'
        Method for tau² estimation
    level : float, default 0.95
        Confidence level
    hakn : bool, default False
        Use Hartung-Knapp adjustment
    incr : float, default 0.5
        Increment for continuity correction
        
    Returns:
    --------
    MetaAnalysis object with results
    """
    
    # Handle data input
    if data is not None:
        variables = [event1, n1, event2, n2]
        var_names = ['event1', 'n1', 'event2', 'n2']
        for i, var in enumerate(variables):
            if isinstance(var, str):
                variables[i] = data[var].values
        event1, n1, event2, n2 = variables
        
        if isinstance(studlab, str):
            studlab = data[studlab].values
    
    # Convert to numpy arrays
    event1 = np.asarray(event1, dtype=int)
    n1 = np.asarray(n1, dtype=int)
    event2 = np.asarray(event2, dtype=int)
    n2 = np.asarray(n2, dtype=int)
    
    if studlab is None:
        studlab = [f"Study {i+1}" for i in range(len(event1))]
    else:
        studlab = np.asarray(studlab, dtype=str)
    
    # Calculate effect sizes
    effects = []
    ses = []
    
    for i in range(len(event1)):
        # Create 2x2 table: a, b, c, d
        a = event1[i]
        b = n1[i] - event1[i]  # non-events in group 1
        c = event2[i] 
        d = n2[i] - event2[i]  # non-events in group 2
        
        if sm == "OR":
            eff, se = log_or(a, b, c, d, incr)
        elif sm == "RR":
            eff, se = log_rr(a, b, c, d, incr)
        elif sm == "RD":
            eff, se = risk_diff(a, b, c, d, incr if sm == "RD" else 0.0)
        else:
            raise ValueError("sm must be 'OR', 'RR', or 'RD'")
        
        effects.append(eff)
        ses.append(se)
    
    return metagen(effects, ses, studlab, method=method, level=level, hakn=hakn)


def metaprop(event: Union[List[int], np.ndarray],
             n: Union[List[int], np.ndarray], 
             studlab: Optional[Union[List[str], np.ndarray]] = None,
             data: Optional[pd.DataFrame] = None,
             method: Literal["DL", "PM"] = "DL",
             level: float = 0.95,
             hakn: bool = False,
             incr: float = 0.5) -> MetaAnalysis:
    """
    Meta-analysis of proportions
    
    Parameters:
    -----------
    event : array-like
        Number of events
    n : array-like
        Total sample sizes
    studlab : array-like, optional
        Study labels
    data : DataFrame, optional
        Data frame containing the variables
    method : {'DL', 'PM'}, default 'DL'
        Method for tau² estimation
    level : float, default 0.95
        Confidence level
    hakn : bool, default False
        Use Hartung-Knapp adjustment
    incr : float, default 0.5
        Increment for continuity correction
        
    Returns:
    --------
    MetaAnalysis object with results
    """
    
    # Handle data input
    if data is not None:
        if isinstance(event, str):
            event = data[event].values
        if isinstance(n, str):
            n = data[n].values
        if isinstance(studlab, str):
            studlab = data[studlab].values
    
    # Convert to numpy arrays
    event = np.asarray(event, dtype=int)
    n = np.asarray(n, dtype=int)
    
    if studlab is None:
        studlab = [f"Study {i+1}" for i in range(len(event))]
    else:
        studlab = np.asarray(studlab, dtype=str)
    
    # Calculate logit-transformed proportions
    effects = []
    ses = []
    
    for i in range(len(event)):
        eff, se = logit_prop(event[i], n[i], incr)
        effects.append(eff)
        ses.append(se)
    
    return metagen(effects, ses, studlab, method=method, level=level, hakn=hakn)


def rma(yi: Union[List[float], np.ndarray],
        vi: Optional[Union[List[float], np.ndarray]] = None,
        sei: Optional[Union[List[float], np.ndarray]] = None,
        slab: Optional[Union[List[str], np.ndarray]] = None,
        data: Optional[pd.DataFrame] = None,
        method: Literal["DL", "PM"] = "DL",
        level: float = 0.95,
        knha: bool = False) -> MetaAnalysis:
    """
    Random-effects meta-analysis (metafor-like interface)
    
    Parameters:
    -----------
    yi : array-like
        Effect sizes (or outcome measures)
    vi : array-like, optional
        Variances (either vi or sei must be specified)
    sei : array-like, optional
        Standard errors (either vi or sei must be specified)
    slab : array-like, optional
        Study labels
    data : DataFrame, optional
        Data frame containing the variables
    method : {'DL', 'PM'}, default 'DL'
        Method for tau² estimation
    level : float, default 0.95
        Confidence level
    knha : bool, default False
        Use Knapp-Hartung adjustment
        
    Returns:
    --------
    MetaAnalysis object with results
    """
    
    # Handle data input
    if data is not None:
        if isinstance(yi, str):
            yi = data[yi].values
        if isinstance(vi, str) and vi is not None:
            vi = data[vi].values
        if isinstance(sei, str) and sei is not None:
            sei = data[sei].values
        if isinstance(slab, str):
            slab = data[slab].values
    
    # Convert to numpy arrays
    yi = np.asarray(yi, dtype=float)
    
    # Handle vi/sei
    if vi is not None and sei is not None:
        raise ValueError("Cannot specify both vi and sei")
    elif vi is not None:
        sei = np.sqrt(np.asarray(vi, dtype=float))
    elif sei is not None:
        sei = np.asarray(sei, dtype=float)
    else:
        raise ValueError("Must specify either vi or sei")
    
    if slab is None:
        slab = [f"Study {i+1}" for i in range(len(yi))]
    else:
        slab = np.asarray(slab, dtype=str)
    
    return metagen(yi, sei, slab, method=method, level=level, hakn=knha)