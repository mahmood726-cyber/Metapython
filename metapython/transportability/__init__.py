"""
Transportability and Generalizability

Transport meta-analysis results to target populations.
Inspired by mahmood726-cyber/LFA repository.

Key innovation: Adjust pooled estimates for specific target populations
accounting for differences in demographics and characteristics.
"""

from metapython.transportability.generalizability import (
    TransportabilityResult,
    TransportabilityAnalysis,
    sensitivity_to_target_specification
)

__all__ = [
    'TransportabilityResult',
    'TransportabilityAnalysis',
    'sensitivity_to_target_specification'
]
