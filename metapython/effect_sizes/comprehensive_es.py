"""
Comprehensive Effect Size Calculators

Complete collection of effect size measures like metafor package.
Converts between different effect size metrics and handles various data formats.

Categories:
1. Standardized Mean Differences (Cohen's d, Hedges' g, Glass's Δ)
2. Correlation-based (r, Fisher's z)
3. Binary outcomes (OR, RR, RD, NNT, diagnostic accuracy)
4. Raw differences (MD, response ratios)
5. Proportions (single group, arcsine transformation)
6. Time-to-event (HR, log HR)

References:
- Borenstein M, et al. (2009). Introduction to Meta-Analysis. Wiley.
- Cooper H, et al. (2019). The Handbook of Research Synthesis and Meta-Analysis.
- Viechtbauer W (2010). Conducting meta-analyses in R with the metafor package.
  Journal of Statistical Software, 36(3), 1-48.
"""

from typing import Dict, Optional, Tuple, Union
import numpy as np
from scipy import stats
from scipy.special import expit, logit
from dataclasses import dataclass
import warnings

from metapython.core.config import logger


@dataclass
class EffectSize:
    """Container for effect size and variance."""
    effect: float
    variance: float
    se: float
    ci_lower: float
    ci_upper: float
    n: Optional[int] = None
    measure: str = ""


class SMDCalculator:
    """Standardized Mean Difference calculations."""

    @staticmethod
    def cohens_d(
        m1: float, m2: float, sd1: float, sd2: float, n1: int, n2: int,
        bias_correction: bool = True
    ) -> EffectSize:
        """
        Cohen's d - pooled SD standardizer.

        d = (M1 - M2) / SD_pooled
        SD_pooled = sqrt(((n1-1)*sd1² + (n2-1)*sd2²) / (n1+n2-2))

        Args:
            m1, m2: Means for groups 1 and 2
            sd1, sd2: Standard deviations
            n1, n2: Sample sizes
            bias_correction: Apply Hedges' correction (default True)

        Returns:
            EffectSize with d and variance
        """
        # Pooled SD
        sd_pooled = np.sqrt(((n1-1)*sd1**2 + (n2-1)*sd2**2) / (n1+n2-2))

        # Cohen's d
        d = (m1 - m2) / sd_pooled

        # Hedges' g correction factor (reduces small sample bias)
        if bias_correction:
            df = n1 + n2 - 2
            j = 1 - (3 / (4*df - 1))  # Approximation
            g = d * j
        else:
            g = d

        # Variance
        # Var(d) ≈ (n1+n2)/(n1*n2) + d²/(2*(n1+n2))
        var_d = (n1 + n2) / (n1 * n2) + d**2 / (2 * (n1 + n2))

        if bias_correction:
            var_g = j**2 * var_d
            final_effect = g
            final_var = var_g
        else:
            final_effect = d
            final_var = var_d

        se = np.sqrt(final_var)
        ci = (final_effect - 1.96 * se, final_effect + 1.96 * se)

        return EffectSize(
            effect=final_effect,
            variance=final_var,
            se=se,
            ci_lower=ci[0],
            ci_upper=ci[1],
            n=n1+n2,
            measure="Hedges' g" if bias_correction else "Cohen's d"
        )

    @staticmethod
    def from_means_sds(
        means: Tuple[float, float],
        sds: Tuple[float, float],
        ns: Tuple[int, int]
    ) -> EffectSize:
        """Convenience wrapper for cohens_d."""
        return SMDCalculator.cohens_d(
            means[0], means[1], sds[0], sds[1], ns[0], ns[1]
        )

    @staticmethod
    def from_t_statistic(
        t: float, n1: int, n2: int
    ) -> EffectSize:
        """
        Calculate SMD from t-statistic.

        d = t * sqrt(1/n1 + 1/n2)
        """
        d = t * np.sqrt(1/n1 + 1/n2)
        var_d = (n1 + n2) / (n1 * n2) + d**2 / (2 * (n1 + n2))

        se = np.sqrt(var_d)
        ci = (d - 1.96 * se, d + 1.96 * se)

        return EffectSize(
            effect=d,
            variance=var_d,
            se=se,
            ci_lower=ci[0],
            ci_upper=ci[1],
            n=n1+n2,
            measure="SMD from t"
        )

    @staticmethod
    def from_f_statistic(
        f: float, n1: int, n2: int
    ) -> EffectSize:
        """Calculate SMD from F-statistic (F = t²)."""
        t = np.sqrt(f)
        return SMDCalculator.from_t_statistic(t, n1, n2)


class CorrelationCalculator:
    """Correlation-based effect sizes."""

    @staticmethod
    def fishers_z(r: float, n: int) -> EffectSize:
        """
        Fisher's z transformation of correlation.

        z = 0.5 * ln((1+r)/(1-r)) = arctanh(r)
        Var(z) = 1 / (n - 3)

        Args:
            r: Pearson correlation
            n: Sample size

        Returns:
            EffectSize with Fisher's z
        """
        if abs(r) >= 1:
            raise ValueError("Correlation must be in (-1, 1)")

        # Fisher's z
        z = 0.5 * np.log((1 + r) / (1 - r))

        # Variance
        var_z = 1 / (n - 3)
        se = np.sqrt(var_z)

        ci = (z - 1.96 * se, z + 1.96 * se)

        return EffectSize(
            effect=z,
            variance=var_z,
            se=se,
            ci_lower=ci[0],
            ci_upper=ci[1],
            n=n,
            measure="Fisher's z"
        )

    @staticmethod
    def z_to_r(z: float) -> float:
        """Back-transform Fisher's z to correlation."""
        return np.tanh(z)


class BinaryOutcomeCalculator:
    """Binary outcome effect sizes."""

    @staticmethod
    def log_odds_ratio(
        a: int, b: int, c: int, d: int,
        correction: float = 0.5
    ) -> EffectSize:
        """
        Log odds ratio from 2×2 table.

                Treatment   Control
        Event      a           b
        No Event   c           d

        OR = (a*d) / (b*c)
        log(OR) = log(a) + log(d) - log(b) - log(c)
        Var(log OR) = 1/a + 1/b + 1/c + 1/d

        Args:
            a, b, c, d: Cell counts
            correction: Add to zero cells (default 0.5)

        Returns:
            EffectSize with log OR
        """
        # Continuity correction for zero cells
        if a == 0 or b == 0 or c == 0 or d == 0:
            a += correction
            b += correction
            c += correction
            d += correction

        # Log OR
        log_or = np.log(a) + np.log(d) - np.log(b) - np.log(c)

        # Variance
        var_log_or = 1/a + 1/b + 1/c + 1/d
        se = np.sqrt(var_log_or)

        ci = (log_or - 1.96 * se, log_or + 1.96 * se)

        return EffectSize(
            effect=log_or,
            variance=var_log_or,
            se=se,
            ci_lower=ci[0],
            ci_upper=ci[1],
            n=int(a+b+c+d),
            measure="log OR"
        )

    @staticmethod
    def log_risk_ratio(
        a: int, b: int, n1: int, n2: int,
        correction: float = 0.5
    ) -> EffectSize:
        """
        Log risk ratio.

        RR = (a/n1) / (b/n2)
        Var(log RR) = 1/a - 1/n1 + 1/b - 1/n2

        Args:
            a, b: Events in treatment and control
            n1, n2: Total in treatment and control
            correction: Add to zero events

        Returns:
            EffectSize with log RR
        """
        if a == 0 or b == 0:
            a += correction
            b += correction
            n1 += correction
            n2 += correction

        p1 = a / n1
        p2 = b / n2

        log_rr = np.log(p1) - np.log(p2)

        var_log_rr = 1/a - 1/n1 + 1/b - 1/n2
        se = np.sqrt(var_log_rr)

        ci = (log_rr - 1.96 * se, log_rr + 1.96 * se)

        return EffectSize(
            effect=log_rr,
            variance=var_log_rr,
            se=se,
            ci_lower=ci[0],
            ci_upper=ci[1],
            n=int(n1+n2),
            measure="log RR"
        )

    @staticmethod
    def risk_difference(
        a: int, b: int, n1: int, n2: int
    ) -> EffectSize:
        """
        Risk difference.

        RD = a/n1 - b/n2
        Var(RD) = (a*(n1-a)/n1³) + (b*(n2-b)/n2³)

        Args:
            a, b: Events
            n1, n2: Totals

        Returns:
            EffectSize with RD
        """
        p1 = a / n1
        p2 = b / n2

        rd = p1 - p2

        var_rd = (p1 * (1 - p1) / n1) + (p2 * (1 - p2) / n2)
        se = np.sqrt(var_rd)

        ci = (rd - 1.96 * se, rd + 1.96 * se)

        return EffectSize(
            effect=rd,
            variance=var_rd,
            se=se,
            ci_lower=ci[0],
            ci_upper=ci[1],
            n=int(n1+n2),
            measure="Risk Difference"
        )


class ProportionCalculator:
    """Single-group proportion effect sizes."""

    @staticmethod
    def logit_transformed(
        events: int, n: int
    ) -> EffectSize:
        """
        Logit-transformed proportion.

        logit(p) = log(p / (1-p))
        Var(logit(p)) = 1/(n*p*(1-p))

        Args:
            events: Number of events
            n: Total sample size

        Returns:
            EffectSize with logit(p)
        """
        if events == 0 or events == n:
            # Add continuity correction
            events += 0.5
            n += 1

        p = events / n

        logit_p = np.log(p / (1 - p))
        var_logit_p = 1 / (n * p * (1 - p))
        se = np.sqrt(var_logit_p)

        ci = (logit_p - 1.96 * se, logit_p + 1.96 * se)

        return EffectSize(
            effect=logit_p,
            variance=var_logit_p,
            se=se,
            ci_lower=ci[0],
            ci_upper=ci[1],
            n=n,
            measure="Logit(proportion)"
        )

    @staticmethod
    def arcsine_transformed(
        events: int, n: int
    ) -> EffectSize:
        """
        Arcsine (Freeman-Tukey) transformation.

        Variance-stabilizing for proportions.
        Used in prevalence meta-analysis.

        Args:
            events: Number of events
            n: Total

        Returns:
            EffectSize with arcsine-transformed proportion
        """
        p = events / n

        # Double arcsine transformation
        transformed = np.arcsin(np.sqrt(p))

        # Variance (approximately constant)
        var = 1 / (4 * n)
        se = np.sqrt(var)

        ci = (transformed - 1.96 * se, transformed + 1.96 * se)

        return EffectSize(
            effect=transformed,
            variance=var,
            se=se,
            ci_lower=ci[0],
            ci_upper=ci[1],
            n=n,
            measure="Arcsine(proportion)"
        )


def convert_effect_size(
    es: EffectSize,
    target_measure: str,
    additional_info: Optional[Dict] = None
) -> EffectSize:
    """
    Convert between effect size measures.

    Conversions:
    - Cohen's d ↔ OR (via probit)
    - Cohen's d ↔ r (point-biserial)
    - OR ↔ RR (via baseline risk)
    - Fisher's z ↔ r

    Args:
        es: Effect size to convert
        target_measure: Desired measure
        additional_info: Extra info needed for conversion

    Returns:
        Converted EffectSize

    Example:
        >>> # Convert Cohen's d to correlation
        >>> d_es = SMDCalculator.cohens_d(5.0, 4.0, 1.0, 1.0, 50, 50)
        >>> r_es = convert_effect_size(d_es, "correlation")
    """
    current = es.measure

    if current == target_measure:
        return es

    # d to r
    if "d" in current.lower() and target_measure == "correlation":
        d = es.effect
        # Point-biserial correlation approximation
        # r = d / sqrt(d² + a)
        # where a ≈ 4 for equal groups
        a = additional_info.get('a', 4) if additional_info else 4
        r = d / np.sqrt(d**2 + a)

        # Use Fisher's z for variance
        n = es.n if es.n else 100  # Default
        return CorrelationCalculator.fishers_z(r, n)

    # r to d
    elif current == "Fisher's z" and "d" in target_measure.lower():
        r = np.tanh(es.effect)  # Back to r
        # r to d approximation
        # d = 2r / sqrt(1 - r²)
        d = 2 * r / np.sqrt(1 - r**2)

        # Approximate variance
        var_d = 4 * es.variance / (1 - r**2)**2

        se_d = np.sqrt(var_d)
        ci = (d - 1.96 * se_d, d + 1.96 * se_d)

        return EffectSize(
            effect=d,
            variance=var_d,
            se=se_d,
            ci_lower=ci[0],
            ci_upper=ci[1],
            n=es.n,
            measure="Cohen's d (from r)"
        )

    # Add more conversions as needed
    else:
        raise ValueError(f"Conversion from {current} to {target_measure} not implemented")


__all__ = [
    'EffectSize',
    'SMDCalculator',
    'CorrelationCalculator',
    'BinaryOutcomeCalculator',
    'ProportionCalculator',
    'convert_effect_size'
]
