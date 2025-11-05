"""
Comprehensive Scenario Generator for Meta-Analysis Testing

Generates 10,000+ validation scenarios covering:
- Different study designs (1,000 scenarios)
- Sample size variations (1,500 scenarios)
- Effect size patterns (2,000 scenarios)
- Heterogeneity patterns (1,500 scenarios)
- Publication bias patterns (1,500 scenarios)
- Edge cases and error conditions (1,000 scenarios)
- Method combinations (1,500 scenarios)

Total: 10,000+ comprehensive test scenarios
"""

from metapython.scenarios.generator import (
    ScenarioGenerator,
    generate_all_scenarios,
    generate_study_design_scenarios,
    generate_heterogeneity_scenarios,
    generate_bias_scenarios,
)

__all__ = [
    'ScenarioGenerator',
    'generate_all_scenarios',
    'generate_study_design_scenarios',
    'generate_heterogeneity_scenarios',
    'generate_bias_scenarios',
]
