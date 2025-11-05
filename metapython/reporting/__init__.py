"""
Automated Reporting Module for Meta-Analysis

AI + rules-based generation of:
- Methods sections (500+ rules for PRISMA/Cochrane compliance)
- Results sections (500+ rules for complete reporting)
- Discussion and interpretation
- Publication-ready manuscripts
"""

from metapython.reporting.methods_generator import (
    MethodsSectionGenerator,
    generate_methods_section,
)

from metapython.reporting.results_generator import (
    ResultsSectionGenerator,
    generate_results_section,
)

from metapython.reporting.methods_rules import (
    METHODS_RULES,
    validate_methods_section,
)

from metapython.reporting.results_rules import (
    RESULTS_RULES,
    validate_results_section,
)

__all__ = [
    # Methods generation
    'MethodsSectionGenerator',
    'generate_methods_section',

    # Results generation
    'ResultsSectionGenerator',
    'generate_results_section',

    # Validation
    'METHODS_RULES',
    'RESULTS_RULES',
    'validate_methods_section',
    'validate_results_section',
]
