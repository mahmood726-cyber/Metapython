"""
Comprehensive Rules Engine for Meta-Analysis

Implements 500+ expert rules covering every aspect of meta-analysis:
- Study inclusion/exclusion (100+ rules)
- Quality assessment (80+ rules)
- Statistical method selection (120+ rules)
- Heterogeneity interpretation (60+ rules)
- Publication bias detection (70+ rules)
- Effect size interpretation (80+ rules)
- Reporting guidelines (90+ rules)

Total: 600+ rules with evidence-based thresholds
"""

from metapython.rules.engine import (
    RulesEngine,
    Rule,
    RuleCategory,
    RuleResult,
    evaluate_rules,
)

from metapython.rules.inclusion_rules import INCLUSION_RULES
from metapython.rules.quality_rules import QUALITY_RULES
from metapython.rules.statistical_rules import STATISTICAL_RULES
from metapython.rules.heterogeneity_rules import HETEROGENEITY_RULES
from metapython.rules.bias_rules import BIAS_RULES
from metapython.rules.interpretation_rules import INTERPRETATION_RULES
from metapython.rules.reporting_rules import REPORTING_RULES

__all__ = [
    'RulesEngine',
    'Rule',
    'RuleCategory',
    'RuleResult',
    'evaluate_rules',
    'INCLUSION_RULES',
    'QUALITY_RULES',
    'STATISTICAL_RULES',
    'HETEROGENEITY_RULES',
    'BIAS_RULES',
    'INTERPRETATION_RULES',
    'REPORTING_RULES',
]
