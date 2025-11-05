"""
AI-Powered Decision Support System for Meta-Analysis

Integrates LLM intelligence with 500+ rules and 10,000+ scenarios to provide:
- Automated method selection
- Quality assessment
- Bias detection
- Result interpretation
- Reporting recommendations
"""

from metapython.decision_support.advisor import (
    MetaAnalysisAdvisor,
    get_method_recommendation,
    assess_analysis_quality,
    interpret_results,
)

__all__ = [
    'MetaAnalysisAdvisor',
    'get_method_recommendation',
    'assess_analysis_quality',
    'interpret_results',
]
