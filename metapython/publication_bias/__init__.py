"""
Publication Bias Correction Methods

Advanced selection models:
- Vevea-Hedges selection model
- PET-PEESE
- Sensitivity analysis

Latest 2024 advances from comparative studies.

References:
- Vevea & Hedges (1995). Psychological Bulletin, 117(3), 387-405
- Stanley & Doucouliagos (2014). Research Synthesis Methods, 5(1), 60-78
"""

from metapython.publication_bias.selection_models import (
    SelectionModelResult,
    VeveaHedgesSelection,
    PETandPEESE,
    sensitivity_analysis_selection
)

__all__ = [
    'SelectionModelResult',
    'VeveaHedgesSelection',
    'PETandPEESE',
    'sensitivity_analysis_selection'
]
