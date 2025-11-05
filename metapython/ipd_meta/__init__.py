"""
Individual Participant Data (IPD) Meta-Analysis

Gold standard using raw participant data:
- One-stage analysis
- Two-stage analysis
- Comparison of approaches

References:
- Burke et al. (2017). Statistics in Medicine, 36(5), 855-875
- Cochrane Handbook Chapter 26 (2024)
"""

from metapython.ipd_meta.ipd_analysis import (
    EffectType,
    IPDResult,
    OneStageIPD,
    TwoStageIPD,
    compare_one_vs_two_stage
)

__all__ = [
    'EffectType',
    'IPDResult',
    'OneStageIPD',
    'TwoStageIPD',
    'compare_one_vs_two_stage'
]
