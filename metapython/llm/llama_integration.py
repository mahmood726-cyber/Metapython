"""
Llama 3 Integration for Meta-Analysis Tasks

Provides intelligent automation for:
- Study screening and extraction
- Quality assessment (Cochrane Risk of Bias, GRADE)
- Data extraction from full-text articles
- Report generation following PRISMA guidelines
- Method recommendations based on study characteristics

Supports multiple backends:
- Llama 3 (70B, 8B) via Ollama or HuggingFace
- GPT-4 via OpenAI API (fallback)
- Local models via transformers
"""

from typing import Dict, List, Optional, Any, Union, Tuple
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from metapython.core.config import logger

# Check for LLM dependencies
HAS_TRANSFORMERS = False
HAS_OPENAI = False
HAS_OLLAMA = False

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    import torch
    HAS_TRANSFORMERS = True
except ImportError:
    logger.info("transformers not available - local LLM support disabled")

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    logger.info("openai not available - OpenAI API support disabled")

try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    logger.info("ollama not available - Ollama support disabled")


@dataclass
class StudyData:
    """Extracted study data from LLM."""

    title: str = ""
    authors: List[str] = field(default_factory=list)
    year: int = 0
    study_design: str = ""
    sample_size: int = 0
    intervention: str = ""
    control: str = ""
    outcome: str = ""
    effect_size: Optional[float] = None
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    p_value: Optional[float] = None
    quality_score: Optional[float] = None
    risk_of_bias: Dict[str, str] = field(default_factory=dict)
    extracted_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityAssessment:
    """Quality assessment results from LLM."""

    overall_quality: str = "unclear"  # low, moderate, high, unclear
    risk_of_bias_domains: Dict[str, str] = field(default_factory=dict)
    grade_rating: Optional[str] = None
    justification: str = ""
    recommendations: List[str] = field(default_factory=list)
    confidence: float = 0.0


class LlamaMetaAnalyst:
    """
    Intelligent meta-analysis assistant using Llama 3.

    Provides AI-powered assistance for meta-analysis workflows including
    study screening, data extraction, quality assessment, and reporting.

    Example:
        >>> analyst = LlamaMetaAnalyst(model="llama3:70b")
        >>> study_data = analyst.extract_study_data(full_text)
        >>> quality = analyst.assess_quality(study_data)
        >>> report = analyst.generate_report(meta_results)
    """

    def __init__(
        self,
        model: str = "llama3:8b",
        backend: str = "auto",
        api_key: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ):
        """
        Initialize Llama meta-analyst.

        Args:
            model: Model name (e.g., "llama3:70b", "gpt-4", "llama3:8b")
            backend: Backend to use ("ollama", "openai", "transformers", "auto")
            api_key: API key for OpenAI (if using OpenAI backend)
            temperature: Sampling temperature (0.0-1.0, lower = more deterministic)
            max_tokens: Maximum tokens in response
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Auto-detect backend
        if backend == "auto":
            if "gpt" in model.lower() and HAS_OPENAI:
                backend = "openai"
            elif HAS_OLLAMA:
                backend = "ollama"
            elif HAS_TRANSFORMERS:
                backend = "transformers"
            else:
                raise RuntimeError(
                    "No LLM backend available. Install one of:\n"
                    "  - ollama (recommended): https://ollama.ai\n"
                    "  - transformers: pip install transformers torch\n"
                    "  - openai: pip install openai"
                )

        self.backend = backend
        self.api_key = api_key

        # Initialize backend
        if backend == "ollama":
            if not HAS_OLLAMA:
                raise ImportError("ollama not installed. Install with: pip install ollama")
            self.client = ollama
            logger.info(f"Initialized Llama analyst with Ollama backend (model: {model})")

        elif backend == "openai":
            if not HAS_OPENAI:
                raise ImportError("openai not installed. Install with: pip install openai")
            if api_key:
                openai.api_key = api_key
            self.client = openai
            logger.info(f"Initialized Llama analyst with OpenAI backend (model: {model})")

        elif backend == "transformers":
            if not HAS_TRANSFORMERS:
                raise ImportError(
                    "transformers not installed. "
                    "Install with: pip install transformers torch"
                )
            logger.info(f"Loading model {model} with transformers...")
            self.tokenizer = AutoTokenizer.from_pretrained(model)
            self.model_obj = AutoModelForCausalLM.from_pretrained(
                model,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
            )
            self.pipeline = pipeline(
                "text-generation",
                model=self.model_obj,
                tokenizer=self.tokenizer,
            )
            logger.info(f"Initialized Llama analyst with transformers backend")

    def _generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response from LLM."""

        if self.backend == "ollama":
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                }
            )
            return response['message']['content']

        elif self.backend == "openai":
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.choices[0].message.content

        elif self.backend == "transformers":
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            outputs = self.pipeline(
                full_prompt,
                max_new_tokens=self.max_tokens,
                temperature=self.temperature,
                do_sample=self.temperature > 0,
            )
            return outputs[0]['generated_text'][len(full_prompt):]

        else:
            raise ValueError(f"Unknown backend: {self.backend}")

    def extract_study_data(
        self,
        full_text: str,
        extract_format: str = "structured"
    ) -> StudyData:
        """
        Extract study data from full-text article using LLM.

        Args:
            full_text: Full text of the research article
            extract_format: Output format ("structured", "json", "narrative")

        Returns:
            StudyData object with extracted information
        """
        system_prompt = """You are an expert meta-analyst extracting data from research articles.
Extract the following information accurately:
- Study design (RCT, cohort, case-control, etc.)
- Sample size
- Intervention and control conditions
- Primary outcome
- Effect size (with confidence intervals and p-value if available)
- Key study characteristics

Format the response as JSON."""

        prompt = f"""Extract study data from this article:

{full_text[:4000]}  # Truncate for token limits

Provide a JSON response with these fields:
- title
- authors (list)
- year
- study_design
- sample_size
- intervention
- control
- outcome
- effect_size
- ci_lower
- ci_upper
- p_value"""

        response = self._generate(prompt, system_prompt)

        # Parse JSON response
        try:
            # Extract JSON from response (may be wrapped in markdown code blocks)
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response

            data_dict = json.loads(json_str)

            return StudyData(
                title=data_dict.get('title', ''),
                authors=data_dict.get('authors', []),
                year=data_dict.get('year', 0),
                study_design=data_dict.get('study_design', ''),
                sample_size=data_dict.get('sample_size', 0),
                intervention=data_dict.get('intervention', ''),
                control=data_dict.get('control', ''),
                outcome=data_dict.get('outcome', ''),
                effect_size=data_dict.get('effect_size'),
                ci_lower=data_dict.get('ci_lower'),
                ci_upper=data_dict.get('ci_upper'),
                p_value=data_dict.get('p_value'),
                extracted_data=data_dict,
            )

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM JSON response: {e}")
            # Return with raw response
            return StudyData(extracted_data={'raw_response': response})

    def assess_quality(
        self,
        study_data: Union[StudyData, Dict[str, Any]],
        framework: str = "cochrane"
    ) -> QualityAssessment:
        """
        Assess study quality using specified framework.

        Args:
            study_data: Study data to assess
            framework: Assessment framework ("cochrane", "grade", "newcastle-ottawa")

        Returns:
            QualityAssessment object
        """
        if isinstance(study_data, StudyData):
            study_dict = study_data.extracted_data
        else:
            study_dict = study_data

        system_prompt = f"""You are an expert in assessing study quality using the {framework} framework.
Evaluate the study rigorously and provide detailed justification for each domain."""

        if framework == "cochrane":
            prompt = f"""Assess the risk of bias for this study using Cochrane Risk of Bias tool:

Study: {json.dumps(study_dict, indent=2)}

Evaluate these domains:
1. Random sequence generation
2. Allocation concealment
3. Blinding of participants and personnel
4. Blinding of outcome assessment
5. Incomplete outcome data
6. Selective reporting
7. Other sources of bias

For each domain, rate as: low, high, or unclear risk of bias.
Provide overall quality rating and justification.

Format response as JSON with fields:
- risk_of_bias_domains: {{domain: rating}}
- overall_quality: low/moderate/high/unclear
- justification: detailed explanation
- confidence: 0.0-1.0"""

        elif framework == "grade":
            prompt = f"""Assess evidence quality using GRADE framework:

Study: {json.dumps(study_dict, indent=2)}

Evaluate:
1. Risk of bias
2. Inconsistency
3. Indirectness
4. Imprecision
5. Publication bias

Provide GRADE rating: high, moderate, low, or very low.

Format response as JSON."""

        else:
            prompt = f"Assess study quality using {framework} framework:\n\n{json.dumps(study_dict, indent=2)}"

        response = self._generate(prompt, system_prompt)

        # Parse response
        try:
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response

            data_dict = json.loads(json_str)

            return QualityAssessment(
                overall_quality=data_dict.get('overall_quality', 'unclear'),
                risk_of_bias_domains=data_dict.get('risk_of_bias_domains', {}),
                grade_rating=data_dict.get('grade_rating'),
                justification=data_dict.get('justification', ''),
                recommendations=data_dict.get('recommendations', []),
                confidence=data_dict.get('confidence', 0.0),
            )

        except json.JSONDecodeError:
            logger.warning("Failed to parse quality assessment JSON")
            return QualityAssessment(
                justification=response,
                confidence=0.5,
            )

    def detect_bias(
        self,
        study_data: Union[StudyData, Dict[str, Any]],
        bias_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Detect various types of bias in study.

        Args:
            study_data: Study data to analyze
            bias_types: Types of bias to check (default: all)

        Returns:
            Dictionary with bias detection results
        """
        if bias_types is None:
            bias_types = [
                "selection_bias",
                "performance_bias",
                "detection_bias",
                "attrition_bias",
                "reporting_bias",
            ]

        if isinstance(study_data, StudyData):
            study_dict = study_data.extracted_data
        else:
            study_dict = study_data

        system_prompt = """You are an expert in detecting various types of bias in research studies.
Analyze the study critically and identify potential biases with evidence."""

        prompt = f"""Detect these types of bias in the study:
{', '.join(bias_types)}

Study: {json.dumps(study_dict, indent=2)}

For each bias type, provide:
- present: true/false
- severity: none/low/moderate/high
- evidence: specific evidence from the study
- confidence: 0.0-1.0

Format as JSON."""

        response = self._generate(prompt, system_prompt)

        try:
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response

            return json.loads(json_str)

        except json.JSONDecodeError:
            logger.warning("Failed to parse bias detection JSON")
            return {'raw_response': response}

    def generate_report(
        self,
        meta_results: Dict[str, Any],
        format: str = "prisma",
        include_figures: bool = False
    ) -> str:
        """
        Generate meta-analysis report following guidelines.

        Args:
            meta_results: Meta-analysis results dictionary
            format: Report format ("prisma", "cochrane", "narrative")
            include_figures: Whether to include figure descriptions

        Returns:
            Formatted report text
        """
        system_prompt = f"""You are an expert medical writer generating {format.upper()} compliant meta-analysis reports.
Write clearly, precisely, and follow all reporting guidelines."""

        prompt = f"""Generate a comprehensive meta-analysis report following {format.upper()} guidelines.

Results: {json.dumps(meta_results, indent=2)}

Include:
1. Title and abstract
2. Introduction with research question
3. Methods (search strategy, inclusion criteria, quality assessment)
4. Results (study characteristics, meta-analysis findings)
5. Discussion (interpretation, limitations, implications)
6. Conclusion

Use professional academic writing style."""

        response = self._generate(prompt, system_prompt)
        return response

    def recommend_methods(
        self,
        study_characteristics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Recommend appropriate statistical methods based on study characteristics.

        Args:
            study_characteristics: Dictionary with study info

        Returns:
            Method recommendations with justification
        """
        system_prompt = """You are an expert biostatistician recommending appropriate meta-analysis methods.
Base recommendations on study characteristics, heterogeneity, and best practices."""

        prompt = f"""Recommend appropriate meta-analysis methods for these studies:

{json.dumps(study_characteristics, indent=2)}

Consider:
1. Effect measure (OR, RR, SMD, MD)
2. Pooling method (fixed-effect vs random-effects)
3. Heterogeneity assessment
4. Publication bias tests
5. Sensitivity analyses

Provide JSON with:
- effect_measure: recommended measure
- pooling_method: fixed or random
- heterogeneity_methods: list of methods
- bias_assessment: recommended tests
- sensitivity_analyses: recommended analyses
- justification: detailed reasoning"""

        response = self._generate(prompt, system_prompt)

        try:
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response

            return json.loads(json_str)

        except json.JSONDecodeError:
            logger.warning("Failed to parse method recommendations JSON")
            return {'raw_response': response}


# Convenience functions

def extract_study_data(
    full_text: str,
    model: str = "llama3:8b",
    **kwargs
) -> StudyData:
    """
    Convenience function to extract study data.

    Args:
        full_text: Full text of article
        model: Model to use
        **kwargs: Additional arguments for LlamaMetaAnalyst

    Returns:
        StudyData object
    """
    analyst = LlamaMetaAnalyst(model=model, **kwargs)
    return analyst.extract_study_data(full_text)


def assess_study_quality(
    study_data: Union[StudyData, Dict[str, Any]],
    framework: str = "cochrane",
    model: str = "llama3:8b",
    **kwargs
) -> QualityAssessment:
    """
    Convenience function to assess study quality.

    Args:
        study_data: Study data
        framework: Assessment framework
        model: Model to use
        **kwargs: Additional arguments

    Returns:
        QualityAssessment object
    """
    analyst = LlamaMetaAnalyst(model=model, **kwargs)
    return analyst.assess_quality(study_data, framework)


def detect_bias(
    study_data: Union[StudyData, Dict[str, Any]],
    model: str = "llama3:8b",
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to detect bias.

    Args:
        study_data: Study data
        model: Model to use
        **kwargs: Additional arguments

    Returns:
        Bias detection results
    """
    analyst = LlamaMetaAnalyst(model=model, **kwargs)
    return analyst.detect_bias(study_data)


def generate_report(
    meta_results: Dict[str, Any],
    format: str = "prisma",
    model: str = "llama3:70b",  # Use larger model for report generation
    **kwargs
) -> str:
    """
    Convenience function to generate report.

    Args:
        meta_results: Meta-analysis results
        format: Report format
        model: Model to use
        **kwargs: Additional arguments

    Returns:
        Report text
    """
    analyst = LlamaMetaAnalyst(model=model, **kwargs)
    return analyst.generate_report(meta_results, format)


__all__ = [
    'LlamaMetaAnalyst',
    'StudyData',
    'QualityAssessment',
    'extract_study_data',
    'assess_study_quality',
    'detect_bias',
    'generate_report',
    'HAS_TRANSFORMERS',
    'HAS_OPENAI',
    'HAS_OLLAMA',
]
