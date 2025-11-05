"""
Component-Based Network Meta-Analysis (CBAMM)

Decompose complex interventions into components and estimate
individual component effects.

Inspired by mahmood726-cyber/HFN786 repository.
"""

from metapython.component_network.cbamm import (
    ComponentMAResult,
    ComponentNetworkMA,
    component_ranking
)

__all__ = [
    'ComponentMAResult',
    'ComponentNetworkMA',
    'component_ranking'
]
