"""
Classic Meta-Analysis Methods

Foundational methods that remain gold standards:
- Mantel-Haenszel (1959)
- Peto (1980s)

Essential for binary outcomes, rare events, and sparse data.
"""

from metapython.classic_methods.mantel_haenszel_peto import (
    ClassicMAResult,
    MantelHaenszelMethod,
    PetoMethod,
    choose_method_for_binary_data
)

__all__ = [
    'ClassicMAResult',
    'MantelHaenszelMethod',
    'PetoMethod',
    'choose_method_for_binary_data'
]
