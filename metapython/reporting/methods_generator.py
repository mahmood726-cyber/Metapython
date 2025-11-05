"""
Methods Section Generator

AI + Rules-based generation of PRISMA/Cochrane compliant methods sections.
Combines LLM narrative generation with 500+ validation rules.
"""

from typing import Dict, List, Any, Optional
import json

from metapython.core.config import logger
from metapython.reporting.methods_rules import METHODS_RULES, validate_methods_section

try:
    from metapython.llm.llama_integration import LlamaMetaAnalyst
    HAS_LLM = True
except ImportError:
    HAS_LLM = False
    logger.warning("LLM integration not available")


class MethodsSectionGenerator:
    """
    Generate PRISMA-compliant methods sections with AI + rules validation.

    Combines:
    - LLM for natural language generation
    - 500+ rules for completeness and compliance
    - Templates for different review types

    Example:
        >>> generator = MethodsSectionGenerator(model="llama3:70b")
        >>> methods = generator.generate(methods_data)
        >>> validation = generator.validate(methods_data)
    """

    def __init__(
        self,
        model: str = "llama3:8b",
        use_llm: bool = True,
        review_type: str = "intervention",
        **llm_kwargs
    ):
        """
        Initialize methods generator.

        Args:
            model: LLM model to use
            use_llm: Whether to use LLM for generation
            review_type: Type of review (intervention, diagnostic, prognostic, etc.)
            **llm_kwargs: Additional LLM arguments
        """
        self.use_llm = use_llm and HAS_LLM
        self.review_type = review_type

        if self.use_llm:
            try:
                self.llm = LlamaMetaAnalyst(model=model, **llm_kwargs)
                logger.info(f"Initialized LLM for methods generation: {model}")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM: {e}")
                self.use_llm = False
                self.llm = None
        else:
            self.llm = None

    def generate(
        self,
        methods_data: Dict[str, Any],
        format: str = "markdown",
        validate_first: bool = True
    ) -> Dict[str, Any]:
        """
        Generate complete methods section.

        Args:
            methods_data: Dictionary with all methods information
            format: Output format (markdown, latex, html, docx)
            validate_first: Whether to validate before generation

        Returns:
            Dictionary with generated text and validation results
        """
        result = {
            'text': '',
            'validation': {},
            'sections': {},
            'compliance_score': 0,
        }

        # Validate first
        if validate_first:
            result['validation'] = validate_methods_section(methods_data)
            result['compliance_score'] = result['validation']['score']

            # Log critical issues
            if result['validation']['critical_issues']:
                logger.warning(
                    f"Found {len(result['validation']['critical_issues'])} critical issues"
                )

        # Generate sections
        result['sections']['search'] = self._generate_search_section(methods_data)
        result['sections']['selection'] = self._generate_selection_section(methods_data)
        result['sections']['extraction'] = self._generate_extraction_section(methods_data)
        result['sections']['rob'] = self._generate_rob_section(methods_data)
        result['sections']['statistics'] = self._generate_statistics_section(methods_data)
        result['sections']['additional'] = self._generate_additional_sections(methods_data)

        # Combine sections
        result['text'] = self._format_sections(result['sections'], format)

        # Add recommendations if validation failed
        if result['compliance_score'] < 80:
            result['text'] += self._generate_improvement_recommendations(result['validation'])

        return result

    def _generate_search_section(self, data: Dict[str, Any]) -> str:
        """Generate search strategy section."""
        if self.use_llm and self.llm:
            prompt = f"""Generate a PRISMA-compliant search strategy section with these details:

Databases: {data.get('databases_searched', [])}
Date range: {data.get('search_dates', {})}
Search terms: {data.get('search_terms', [])}
Grey literature: {data.get('grey_literature_searched', False)}
Language restrictions: {data.get('language_restrictions', 'None')}

Format as a clear paragraph suitable for a scientific manuscript."""

            try:
                return self.llm._generate(prompt, "You are an expert in systematic review methodology.")
            except:
                pass

        # Fallback template
        return self._search_template(data)

    def _search_template(self, data: Dict[str, Any]) -> str:
        """Template-based search section."""
        databases = ', '.join(data.get('databases_searched', ['PubMed', 'Embase']))
        start_date = data.get('search_dates', {}).get('start', 'inception')
        end_date = data.get('search_dates', {}).get('end', 'present')

        text = f"""## Search Strategy

We conducted a comprehensive systematic search of {databases} from {start_date} to {end_date}. """

        if data.get('mesh_terms_used'):
            text += "Medical Subject Headings (MeSH) terms and free-text words were combined using Boolean operators. "

        if data.get('grey_literature_searched'):
            text += "Grey literature was searched including conference proceedings and clinical trial registries. "

        if data.get('reference_screening'):
            text += "Reference lists of included studies were manually screened for additional eligible studies. "

        text += "The complete search strategy is provided in Supplementary Appendix 1."

        return text

    def _generate_selection_section(self, data: Dict[str, Any]) -> str:
        """Generate study selection section."""
        if self.use_llm and self.llm:
            prompt = f"""Generate study selection methods following PRISMA:

PICOS criteria:
- Population: {data.get('population_defined', 'Not specified')}
- Intervention: {data.get('intervention_defined', 'Not specified')}
- Comparator: {data.get('comparator_defined', 'Not specified')}
- Outcomes: {data.get('outcome_defined', 'Not specified')}
- Study design: {data.get('study_design_specified', 'Not specified')}

Screening process:
- Dual screening: {data.get('dual_screening', True)}
- Disagreement resolution: {data.get('disagreement_resolution', 'consensus')}

Format as clear methods paragraph."""

            try:
                return self.llm._generate(prompt, "You are an expert in systematic review methodology.")
            except:
                pass

        return self._selection_template(data)

    def _selection_template(self, data: Dict[str, Any]) -> str:
        """Template-based selection section."""
        text = """## Study Selection

Studies were included if they met the following PICOS criteria: """

        if data.get('population_defined'):
            text += f"Population: {data['population_defined']}; "
        if data.get('intervention_defined'):
            text += f"Intervention: {data['intervention_defined']}; "
        if data.get('outcome_defined'):
            text += f"Outcomes: {data['outcome_defined']}; "
        if data.get('study_design_specified'):
            text += f"Study design: {data['study_design_specified']}. "

        if data.get('dual_screening'):
            text += "Two reviewers independently screened titles and abstracts, followed by full-text review. "

        if data.get('disagreement_resolution'):
            text += f"Disagreements were resolved by {data['disagreement_resolution']}. "

        return text

    def _generate_extraction_section(self, data: Dict[str, Any]) -> str:
        """Generate data extraction section."""
        return """## Data Extraction

Two reviewers independently extracted data using a standardized form. Extracted data included study characteristics, participant demographics, intervention details, and outcome measures. Disagreements were resolved through discussion or consultation with a third reviewer."""

    def _generate_rob_section(self, data: Dict[str, Any]) -> str:
        """Generate risk of bias section."""
        rob_tool = data.get('rob_tool', 'Cochrane Risk of Bias tool')

        text = f"""## Risk of Bias Assessment

Risk of bias was assessed using the {rob_tool}. """

        if data.get('dual_rob_assessment'):
            text += "Two reviewers independently assessed each study, with disagreements resolved through consensus. "

        domains = data.get('rob_domains', [
            'random sequence generation',
            'allocation concealment',
            'blinding',
            'incomplete outcome data',
            'selective reporting'
        ])

        text += f"Assessed domains included: {', '.join(domains)}. "
        text += "Each domain was judged as low, high, or unclear risk of bias."

        return text

    def _generate_statistics_section(self, data: Dict[str, Any]) -> str:
        """Generate statistical methods section."""
        if self.use_llm and self.llm:
            prompt = f"""Generate statistical methods section:

Meta-analysis method: {data.get('meta_analysis_method', 'random-effects')}
Effect measure: {data.get('effect_measure', 'standardized mean difference')}
Software: {data.get('software', 'R metafor package')}
Heterogeneity: {data.get('heterogeneity_measures', 'I², τ², Q-test')}
Publication bias: {data.get('publication_bias_tests', 'Egger test, funnel plot')}

Format following PRISMA statistical reporting guidelines."""

            try:
                return self.llm._generate(prompt, "You are a biostatistician expert in meta-analysis.")
            except:
                pass

        return self._statistics_template(data)

    def _statistics_template(self, data: Dict[str, Any]) -> str:
        """Template-based statistics section."""
        method = data.get('meta_analysis_method', 'random-effects')
        effect = data.get('effect_measure', 'standardized mean difference')
        software = data.get('software', 'R metafor package')

        text = f"""## Statistical Analysis

Meta-analyses were performed using {method} models. Effect sizes were calculated as {effect} with 95% confidence intervals. """

        text += f"All analyses were conducted using {software}. "

        text += "Statistical heterogeneity was assessed using I² statistic, τ², and Cochran's Q test. "

        if data.get('subgroup_analysis'):
            text += "Subgroup analyses were performed to explore sources of heterogeneity. "

        if data.get('sensitivity_analysis'):
            text += "Sensitivity analyses included leave-one-out analysis and restriction to low risk of bias studies. "

        text += "Publication bias was assessed using funnel plots and Egger's regression test. "

        text += "Statistical significance was set at p < 0.05 for all tests."

        return text

    def _generate_additional_sections(self, data: Dict[str, Any]) -> str:
        """Generate additional methods sections."""
        text = ""

        if data.get('grade_assessment'):
            text += """

## Certainty of Evidence

The GRADE (Grading of Recommendations Assessment, Development and Evaluation) approach was used to assess the certainty of evidence for each outcome."""

        if data.get('protocol_registered'):
            text += f"""

## Protocol Registration

This systematic review was registered with PROSPERO (registration number: {data.get('registration_number', 'CRD42024XXXXX')})."""

        return text

    def _format_sections(self, sections: Dict[str, str], format: str) -> str:
        """Format all sections according to output format."""
        full_text = "# METHODS\n\n"

        for section_name, section_text in sections.items():
            if section_text:
                full_text += section_text + "\n\n"

        if format == "latex":
            # Convert markdown to LaTeX
            full_text = full_text.replace('#', '\\section')
            full_text = full_text.replace('##', '\\subsection')

        elif format == "html":
            # Convert markdown to HTML (simplified)
            full_text = full_text.replace('# ', '<h1>').replace('\n', '</h1>\n', 1)
            full_text = full_text.replace('## ', '<h2>').replace('\n', '</h2>\n')

        return full_text

    def _generate_improvement_recommendations(self, validation: Dict[str, Any]) -> str:
        """Generate recommendations for improving methods section."""
        text = "\n\n---\n## RECOMMENDATIONS FOR IMPROVEMENT\n\n"

        if validation['critical_issues']:
            text += "### Critical Issues to Address:\n\n"
            for issue in validation['critical_issues'][:5]:
                text += f"- **{issue['message']}**: {issue['recommendation']}\n"

        if validation['warnings']:
            text += "\n### Warnings:\n\n"
            for warning in validation['warnings'][:10]:
                text += f"- {warning['message']}\n"

        return text

    def validate(self, methods_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate methods section against 500+ rules."""
        return validate_methods_section(methods_data)


def generate_methods_section(
    methods_data: Dict[str, Any],
    model: str = "llama3:8b",
    format: str = "markdown"
) -> Dict[str, Any]:
    """
    Quick function to generate methods section.

    Args:
        methods_data: Methods information
        model: LLM model
        format: Output format

    Returns:
        Generated methods with validation
    """
    generator = MethodsSectionGenerator(model=model)
    return generator.generate(methods_data, format=format)


__all__ = [
    'MethodsSectionGenerator',
    'generate_methods_section',
]
