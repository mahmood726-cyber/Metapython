from __future__ import annotations
from typing import Tuple
import numpy as np

# Continuous outcomes

def hedges_g(m1: float, sd1: float, n1: int,
             m2: float, sd2: float, n2: int,
             use_hedges_correction: bool = True) -> Tuple[float, float]:
    if n1 <= 1 or n2 <= 1:
        raise ValueError("Group sizes must be > 1")
    df = n1 + n2 - 2
    if df <= 0:
        raise ValueError("Degrees of freedom must be positive")
    pooled_sd = np.sqrt(((n1 - 1) * sd1**2 + (n2 - 1) * sd2**2) / df)
    if pooled_sd <= 0 or not np.isfinite(pooled_sd):
        raise ValueError("Invalid pooled SD for SMD")
    d = (m1 - m2) / pooled_sd
    # Small sample Hedges correction
    J = 1.0
    if use_hedges_correction:
        J = 1 - 3.0 / (4.0 * df - 1)
    g = J * d
    var_d = (n1 + n2) / (n1 * n2) + (d**2) / (2 * df)
    var_g = J**2 * var_d
    se_g = float(np.sqrt(var_g))
    return float(g), se_g


def mean_difference(m1: float, sd1: float, n1: int,
                    m2: float, sd2: float, n2: int) -> Tuple[float, float]:
    if n1 <= 0 or n2 <= 0:
        raise ValueError("Group sizes must be > 0")
    md = float(m1 - m2)
    var_md = sd1**2 / n1 + sd2**2 / n2
    if var_md <= 0 or not np.isfinite(var_md):
        raise ValueError("Invalid variance for MD")
    return md, float(np.sqrt(var_md))


# Binary outcomes from 2x2: a,b,c,d (events/non-events in groups 1 and 2)

def continuity_correct(a: float, b: float, c: float, d: float, cc: float = 0.5):
    # Apply Haldane-Anscombe if any cell is zero
    if min(a, b, c, d) == 0:
        return a + cc, b + cc, c + cc, d + cc
    return a, b, c, d


def log_or(a: int, b: int, c: int, d: int, cc: float = 0.5) -> Tuple[float, float]:
    a, b, c, d = continuity_correct(a, b, c, d, cc)
    lor = np.log((a * d) / (b * c))
    se = np.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    return float(lor), float(se)


def log_rr(a: int, b: int, c: int, d: int, cc: float = 0.5) -> Tuple[float, float]:
    a, b, c, d = continuity_correct(a, b, c, d, cc)
    p1 = a / (a + b)
    p2 = c / (c + d)
    lrr = np.log(p1 / p2)
    # Approx variance for log RR
    se = np.sqrt(1 / a - 1 / (a + b) + 1 / c - 1 / (c + d))
    return float(lrr), float(se)


def risk_diff(a: int, b: int, c: int, d: int, cc: float = 0.0) -> Tuple[float, float]:
    # Optional CC for RD; default none as in many implementations
    if cc:
        a, b, c, d = continuity_correct(a, b, c, d, cc)
    p1 = a / (a + b)
    p2 = c / (c + d)
    rd = p1 - p2
    var = p1 * (1 - p1) / (a + b) + p2 * (1 - p2) / (c + d)
    return float(rd), float(np.sqrt(var))


# Proportions (single-arm)

def logit_prop(a: int, n: int, cc: float = 0.5) -> Tuple[float, float]:
    if a <= 0 or a >= n:
        # Use continuity correction for extremes
        a = a + cc if a == 0 else a
        n = n + 2 * cc if a == 0 else n
        a = a - cc if a == n else a
        n = n + 2 * cc if a == n else n
    p = a / n
    y = np.log(p / (1 - p))
    vi = 1 / (a) + 1 / (n - a)
    return float(y), float(np.sqrt(vi))


def inv_logit(x: float) -> float:
    return float(1.0 / (1.0 + np.exp(-x)))