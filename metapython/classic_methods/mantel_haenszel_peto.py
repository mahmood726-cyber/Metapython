"""
Classic Meta-Analysis Methods

Implementation of foundational methods that remain widely used:
- Mantel-Haenszel method (1959)
- Peto method (1980s)
- Exact methods for sparse data

These methods are:
- Computationally simple
- Robust for sparse data (small cell counts)
- Still recommended by Cochrane for specific situations
- Gold standard for 2×2 table data

Missing from most Python implementations but standard in metafor (R).

References:
- Mantel N, Haenszel W (1959). Statistical aspects of the analysis of data from
  retrospective studies of disease. JNCI, 22(4), 719-748.
- Yusuf S, Peto R, et al. (1985). Beta blockade during and after myocardial infarction.
  Progress in Cardiovascular Diseases, 27(5), 335-371.
- Bradburn MJ, et al. (2007). Much ado about nothing: a comparison of the performance
  of meta-analytical methods with rare events. Statistics in Medicine, 26(1), 53-77.
- Greenland S, Robins JM (1985). Estimation of a common effect parameter from sparse
  follow-up data. Biometrics, 41(1), 55-68.
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from scipy import stats
from dataclasses import dataclass

from metapython.core.config import logger


@dataclass
class ClassicMAResult:
    """Results from classic meta-analysis methods."""
    pooled_or: Optional[float] = None
    pooled_rr: Optional[float] = None
    pooled_rd: Optional[float] = None
    log_or_se: Optional[float] = None
    log_rr_se: Optional[float] = None
    rd_se: Optional[float] = None
    ci_or: Optional[Tuple[float, float]] = None
    ci_rr: Optional[Tuple[float, float]] = None
    ci_rd: Optional[Tuple[float, float]] = None
    z_statistic: Optional[float] = None
    p_value: Optional[float] = None
    heterogeneity_chi2: Optional[float] = None
    heterogeneity_p: Optional[float] = None
    n_studies: int = 0
    method: str = ""


class MantelHaenszelMethod:
    """
    Mantel-Haenszel meta-analysis for 2×2 tables.

    The gold standard for combining odds ratios, risk ratios, and
    risk differences from multiple 2×2 tables.

    Advantages:
    - Robust for sparse data (zero cells)
    - No continuity correction needed for OR/RR
    - Optimal when effect is constant across studies
    - Exact variance calculation

    When to use:
    - Binary outcomes
    - Rare events (< 1%)
    - Small studies (n < 50)
    - Fixed-effect assumption reasonable

    Reference:
    - Mantel & Haenszel (1959). JNCI, 22(4), 719-748.

    Example:
        >>> # 2×2 tables from 5 trials
        >>> # Format: [events_treatment, events_control, n_treatment, n_control]
        >>> tables = [
        ...     [15, 20, 100, 100],  # Trial 1
        ...     [8, 12, 80, 80],     # Trial 2
        ...     [22, 30, 120, 120],  # Trial 3
        ...     [5, 10, 60, 60],     # Trial 4
        ...     [18, 25, 110, 110]   # Trial 5
        ... ]
        >>>
        >>> mh = MantelHaenszelMethod()
        >>> result = mh.meta_analysis_or(tables)
        >>> print(f"Pooled OR: {result.pooled_or:.3f} "
        ...       f"[{result.ci_or[0]:.3f}, {result.ci_or[1]:.3f}]")
    """

    def meta_analysis_or(
        self,
        tables: List[List[int]]
    ) -> ClassicMAResult:
        """
        Mantel-Haenszel meta-analysis for odds ratios.

        Args:
            tables: List of [a, b, c, d] where:
                    a = events in treatment
                    b = events in control
                    c = non-events in treatment
                    d = non-events in control

        Returns:
            ClassicMAResult with pooled OR

        2×2 table format:
                    Treatment   Control
        Event          a           b
        No Event       c           d
        """
        n_studies = len(tables)
        logger.info(f"Mantel-Haenszel OR: {n_studies} studies")

        # Extract components
        a = np.array([t[0] for t in tables])  # Events, treatment
        b = np.array([t[1] for t in tables])  # Events, control
        c = np.array([t[2] for t in tables])  # Non-events, treatment
        d = np.array([t[3] for t in tables])  # Non-events, control

        # Total per study
        n = a + b + c + d

        # Mantel-Haenszel OR
        # OR_MH = sum(a_i * d_i / n_i) / sum(b_i * c_i / n_i)
        numerator = np.sum(a * d / n)
        denominator = np.sum(b * c / n)

        if denominator == 0:
            raise ValueError("Denominator zero in MH calculation")

        or_mh = numerator / denominator
        log_or = np.log(or_mh)

        # Robins-Breslow-Greenland variance (exact)
        # Var(log OR) = sum(P_i) / (2*R^2) + sum(Q_i) / (2*R*S) + sum(S_i) / (2*S^2)
        # where R = sum(ad/n), S = sum(bc/n)

        P = ((a + d) * a * d) / (n**2)
        Q = ((a + d) * b * c + (b + c) * a * d) / (n**2)
        R_term = ((b + c) * b * c) / (n**2)

        R = np.sum(a * d / n)
        S = np.sum(b * c / n)

        var_log_or = (
            np.sum(P) / (2 * R**2) +
            np.sum(Q) / (2 * R * S) +
            np.sum(R_term) / (2 * S**2)
        )

        se_log_or = np.sqrt(var_log_or)

        # Confidence interval
        ci_log_or = (
            log_or - 1.96 * se_log_or,
            log_or + 1.96 * se_log_or
        )
        ci_or = (np.exp(ci_log_or[0]), np.exp(ci_log_or[1]))

        # Test statistic
        z = log_or / se_log_or
        p_value = 2 * (1 - stats.norm.cdf(abs(z)))

        # Heterogeneity (Cochran's Q)
        # Study-specific log ORs
        or_i = (a * d) / (b * c + 0.5)  # Add 0.5 to avoid division by zero
        w_i = 1 / (1/a + 1/b + 1/c + 1/d)  # Inverse variance weights
        log_or_i = np.log(or_i)

        Q = np.sum(w_i * (log_or_i - log_or)**2)
        Q_df = n_studies - 1
        Q_p = 1 - stats.chi2.cdf(Q, Q_df) if Q_df > 0 else 1.0

        return ClassicMAResult(
            pooled_or=or_mh,
            log_or_se=se_log_or,
            ci_or=ci_or,
            z_statistic=z,
            p_value=p_value,
            heterogeneity_chi2=Q,
            heterogeneity_p=Q_p,
            n_studies=n_studies,
            method="Mantel-Haenszel (OR)"
        )

    def meta_analysis_rr(
        self,
        tables: List[List[int]]
    ) -> ClassicMAResult:
        """
        Mantel-Haenszel meta-analysis for risk ratios.

        Args:
            tables: List of [a, b, n1, n2] where:
                    a = events in treatment
                    b = events in control
                    n1 = total in treatment
                    n2 = total in control

        Returns:
            ClassicMAResult with pooled RR
        """
        n_studies = len(tables)
        logger.info(f"Mantel-Haenszel RR: {n_studies} studies")

        # Extract
        a = np.array([t[0] for t in tables])
        b = np.array([t[1] for t in tables])
        n1 = np.array([t[2] for t in tables])
        n2 = np.array([t[3] for t in tables])

        n = n1 + n2

        # MH Risk Ratio
        # RR_MH = sum(a_i * n2_i / n_i) / sum(b_i * n1_i / n_i)
        numerator = np.sum(a * n2 / n)
        denominator = np.sum(b * n1 / n)

        if denominator == 0:
            raise ValueError("Denominator zero")

        rr_mh = numerator / denominator
        log_rr = np.log(rr_mh)

        # Greenland-Robins variance
        R = np.sum(a * n2 / n)
        S = np.sum(b * n1 / n)

        P = np.sum((a + b) * n1 * n2 / n**2)

        var_log_rr = P / (R * S)
        se_log_rr = np.sqrt(var_log_rr)

        # CI
        ci_log_rr = (
            log_rr - 1.96 * se_log_rr,
            log_rr + 1.96 * se_log_rr
        )
        ci_rr = (np.exp(ci_log_rr[0]), np.exp(ci_log_rr[1]))

        # Test
        z = log_rr / se_log_rr
        p_value = 2 * (1 - stats.norm.cdf(abs(z)))

        return ClassicMAResult(
            pooled_rr=rr_mh,
            log_rr_se=se_log_rr,
            ci_rr=ci_rr,
            z_statistic=z,
            p_value=p_value,
            n_studies=n_studies,
            method="Mantel-Haenszel (RR)"
        )

    def meta_analysis_rd(
        self,
        tables: List[List[int]]
    ) -> ClassicMAResult:
        """
        Mantel-Haenszel meta-analysis for risk differences.

        Args:
            tables: List of [a, b, n1, n2]

        Returns:
            ClassicMAResult with pooled RD
        """
        n_studies = len(tables)

        a = np.array([t[0] for t in tables])
        b = np.array([t[1] for t in tables])
        n1 = np.array([t[2] for t in tables])
        n2 = np.array([t[3] for t in tables])

        # Risk differences per study
        rd_i = a / n1 - b / n2

        # Inverse variance weights
        p1 = a / n1
        p2 = b / n2
        var_i = p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2
        w_i = 1 / var_i

        # Pooled RD
        rd_pooled = np.sum(w_i * rd_i) / np.sum(w_i)
        var_rd = 1 / np.sum(w_i)
        se_rd = np.sqrt(var_rd)

        ci_rd = (rd_pooled - 1.96 * se_rd, rd_pooled + 1.96 * se_rd)

        z = rd_pooled / se_rd
        p_value = 2 * (1 - stats.norm.cdf(abs(z)))

        return ClassicMAResult(
            pooled_rd=rd_pooled,
            rd_se=se_rd,
            ci_rd=ci_rd,
            z_statistic=z,
            p_value=p_value,
            n_studies=n_studies,
            method="Mantel-Haenszel (RD)"
        )


class PetoMethod:
    """
    Peto method for meta-analysis of odds ratios.

    Advantages:
    - Most robust for RARE events (< 1%)
    - Works with zero cells
    - Simple and fast
    - Minimal bias for small effects

    Disadvantages:
    - Biased for large effects (OR > 3 or < 0.33)
    - Only for odds ratios
    - Assumes odds ≈ log odds for small probabilities

    When to use:
    - Event rate < 1% in both groups
    - Small effect sizes expected
    - Some studies with zero events

    Reference:
    - Yusuf et al. (1985). Progress in Cardiovascular Diseases, 27(5), 335-371.

    Example:
        >>> # Rare event data (mortality in cardiac trials)
        >>> tables = [
        ...     [2, 5, 1000, 1000],   # 0.2% vs 0.5%
        ...     [1, 3, 800, 800],
        ...     [0, 2, 500, 500],     # Zero events in treatment
        ...     [3, 7, 1200, 1200]
        ... ]
        >>>
        >>> peto = PetoMethod()
        >>> result = peto.meta_analysis(tables)
    """

    def meta_analysis(
        self,
        tables: List[List[int]]
    ) -> ClassicMAResult:
        """
        Peto method for odds ratios.

        Args:
            tables: List of [a, b, n1, n2]

        Returns:
            ClassicMAResult with pooled OR (Peto method)
        """
        n_studies = len(tables)
        logger.info(f"Peto method: {n_studies} studies")

        a = np.array([t[0] for t in tables])
        b = np.array([t[1] for t in tables])
        n1 = np.array([t[2] for t in tables])
        n2 = np.array([t[3] for t in tables])

        n = n1 + n2
        r = a + b  # Total events

        # Expected events in treatment (under null)
        E_i = n1 * r / n

        # Variance of O - E
        V_i = (n1 * n2 * r * (n - r)) / (n**2 * (n - 1))

        # Peto log OR
        O_minus_E = np.sum(a - E_i)
        V = np.sum(V_i)

        log_or_peto = O_minus_E / V
        or_peto = np.exp(log_or_peto)

        se_log_or = np.sqrt(1 / V)

        # CI
        ci_log_or = (
            log_or_peto - 1.96 * se_log_or,
            log_or_peto + 1.96 * se_log_or
        )
        ci_or = (np.exp(ci_log_or[0]), np.exp(ci_log_or[1]))

        # Test
        z = log_or_peto / se_log_or
        p_value = 2 * (1 - stats.norm.cdf(abs(z)))

        # Heterogeneity
        Q = np.sum((a - E_i)**2 / V_i) - O_minus_E**2 / V
        Q_df = n_studies - 1
        Q_p = 1 - stats.chi2.cdf(Q, Q_df) if Q_df > 0 else 1.0

        return ClassicMAResult(
            pooled_or=or_peto,
            log_or_se=se_log_or,
            ci_or=ci_or,
            z_statistic=z,
            p_value=p_value,
            heterogeneity_chi2=Q,
            heterogeneity_p=Q_p,
            n_studies=n_studies,
            method="Peto"
        )


def choose_method_for_binary_data(
    tables: List[List[int]],
    auto_select: bool = True
) -> str:
    """
    Recommend appropriate method for binary data meta-analysis.

    Decision rules:
    - Very rare events (< 1%): Peto
    - Rare events (< 5%): Mantel-Haenszel
    - Common events: Standard inverse variance
    - Zero cells: Peto or M-H (avoid DerSimonian-Laird)

    Args:
        tables: List of 2×2 tables
        auto_select: Return recommendation

    Returns:
        Recommended method name

    Example:
        >>> method = choose_method_for_binary_data(tables)
        >>> print(f"Recommended: {method}")
    """
    # Calculate event rates
    event_rates = []
    zero_cells = 0

    for table in tables:
        a, b, n1, n2 = table
        rate_treatment = a / n1
        rate_control = b / n2
        event_rates.extend([rate_treatment, rate_control])

        if a == 0 or b == 0:
            zero_cells += 1

    mean_rate = np.mean(event_rates)
    has_zeros = zero_cells > 0

    # Decision logic
    if mean_rate < 0.01:
        recommendation = "Peto (very rare events < 1%)"
    elif mean_rate < 0.05 or has_zeros:
        recommendation = "Mantel-Haenszel (rare events or zero cells)"
    else:
        recommendation = "Inverse variance (DerSimonian-Laird or REML)"

    logger.info(f"Mean event rate: {mean_rate:.1%}")
    logger.info(f"Studies with zero cells: {zero_cells}/{len(tables)}")
    logger.info(f"Recommendation: {recommendation}")

    return recommendation


__all__ = [
    'ClassicMAResult',
    'MantelHaenszelMethod',
    'PetoMethod',
    'choose_method_for_binary_data'
]
