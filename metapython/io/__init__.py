"""
Data import and export utilities.

Supports reading meta-analysis data from various formats:
- CSV, Excel (xlsx)
- SPSS (sav)
- Stata (dta)
- RevMan format
"""

from metapython.io.readers import (
    read_csv,
    read_excel,
    read_spss,
    read_stata,
    export_results,
)

__all__ = [
    'read_csv',
    'read_excel',
    'read_spss',
    'read_stata',
    'export_results',
]
