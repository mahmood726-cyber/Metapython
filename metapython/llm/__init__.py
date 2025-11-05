"""
LLM Integration Module for MetaPython

Integrates large language models (Llama 3, GPT-4, etc.) for:
- Automated study extraction from full-text
- Quality assessment automation
- Risk of bias detection
- Data extraction assistance
- Report generation
- Recommendations and insights
"""

from metapython.llm.llama_integration import (
    LlamaMetaAnalyst,
    extract_study_data,
    assess_study_quality,
    detect_bias,
    generate_report,
)

from metapython.llm.prompts import (
    STUDY_EXTRACTION_PROMPT,
    QUALITY_ASSESSMENT_PROMPT,
    BIAS_DETECTION_PROMPT,
    REPORT_GENERATION_PROMPT,
)

__all__ = [
    'LlamaMetaAnalyst',
    'extract_study_data',
    'assess_study_quality',
    'detect_bias',
    'generate_report',
    'STUDY_EXTRACTION_PROMPT',
    'QUALITY_ASSESSMENT_PROMPT',
    'BIAS_DETECTION_PROMPT',
    'REPORT_GENERATION_PROMPT',
]
