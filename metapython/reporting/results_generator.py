"""
Results Section Generator

AI + Rules-based generation of PRISMA-compliant results sections.
Combines LLM narrative generation with 500+ validation rules.
"""

from typing import Dict, List, Any, Optional
import json
import numpy as np

from metapython.core.config import logger
from metapython.reporting.results_rules import RESULTS_RULES, validate_results_section

try:
    from metapython.llm.llama_integration import LlamaMetaAnalyst
    HAS_LLM = True
except ImportError:
    HAS_LLM = False


class ResultsSectionGenerator:
    """
    Generate PRISMA-compliant results sections with AI + rules validation.

    Example:
        >>> generator = ResultsSectionGenerator(model="llama3:70b")
        >>> results = generator.generate(results_data)
        >>> validation = generator.validate(results_data)
    """

    def __init__(
        self,
        model: str = "llama3:8b",
        use_llm: bool = True,
        **llm_kwargs
    ):
        """Initialize results generator."""
        self.use_llm = use_llm and HAS_LLM

        if self.use_llm:
            try:
                self.llm = LlamaMetaAnalyst(model=model, **llm_kwargs)
                logger.info(f"Initialized LLM for results generation: {model}")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM: {e}")
                self.use_llm = False
                self.llm = None
        else:
            self.llm = None

    def generate(
        self,
        results_data: Dict[str, Any],
        format: str = "markdown",
        validate_first: bool = True
    ) -> Dict[str, Any]:
        """
        Generate complete results section.

        Args:
            results_data: Dictionary with all results information
            format: Output format (markdown, latex, html)
            validate_first: Whether to validate before generation

        Returns:
            Dictionary with generated text and validation
        """
        result = {
            'text': '',
            'validation': {},
            'sections': {},
            'compliance_score': 0,
        }

        # Validate first
        if validate_first:
            result['validation'] = validate_results_section(results_data)
            result['compliance_score'] = result['validation']['score']

        # Generate sections
        result['sections']['study_flow'] = self._generate_study_flow(results_data)
        result['sections']['characteristics'] = self._generate_characteristics(results_data)
        result['sections']['rob_results'] = self._generate_rob_results(results_data)
        result['sections']['effect_estimates'] = self._generate_effect_estimates(results_data)
        result['sections']['heterogeneity'] = self._generate_heterogeneity(results_data)
        result['sections']['publication_bias'] = self._generate_publication_bias(results_data)
        result['sections']['subgroup'] = self._generate_subgroup_results(results_data)
        result['sections']['grade'] = self._generate_grade_results(results_data)

        # Combine sections
        result['text'] = self._format_sections(result['sections'], format)

        # Add recommendations if needed
        if result['compliance_score'] < 80:
            result['text'] += self._generate_improvement_recommendations(result['validation'])

        return result

    def _generate_study_flow(self, data: Dict[str, Any]) -> str:
        """Generate study flow section."""
        n_identified = data.get('records_identified', 0)
        n_duplicates = data.get('duplicates_removed', 0)
        n_screened = data.get('records_screened', 0)
        n_excluded = data.get('records_excluded', 0)
        n_fulltext = data.get('fulltext_assessed', 0)
        n_fulltext_excluded = data.get('fulltext_excluded', 0)
        n_included = data.get('studies_included', 0)

        text = f"""## Study Selection

The systematic search identified {n_identified:,} records. After removing {n_duplicates:,} duplicates, {n_screened:,} records were screened by title and abstract. """

        text += f"Of these, {n_excluded:,} records were excluded. "
        text += f"{n_fulltext} full-text articles were assessed for eligibility. "
        text += f"After full-text review, {n_fulltext_excluded} articles were excluded. "
        text += f"Finally, {n_included} studies met inclusion criteria and were included in the meta-analysis. "

        if 'exclusion_reasons' in data:
            text += f"\n\nThe most common reasons for exclusion were: {', '.join(data['exclusion_reasons'])}. "

        text += "The study selection process is shown in Figure 1 (PRISMA flow diagram)."

        return text

    def _generate_characteristics(self, data: Dict[str, Any]) -> str:
        """Generate study characteristics section."""
        n_studies = data.get('studies_included', 0)
        total_participants = data.get('total_participants', 0)
        year_range = data.get('publication_year_range', 'N/A')

        text = f"""## Study Characteristics

The {n_studies} included studies comprised {total_participants:,} participants. """

        if year_range != 'N/A':
            text += f"Studies were published between {year_range}. "

        if 'study_designs' in data:
            designs = data['study_designs']
            text += f"Study designs included: {designs}. "

        if 'mean_age' in data:
            text += f"Mean age of participants was {data['mean_age']} years. "

        if 'percent_female' in data:
            text += f"Across studies, {data['percent_female']}% of participants were female. "

        if 'intervention_summary' in data:
            text += f"\n\n{data['intervention_summary']}"

        text += "\n\nDetailed characteristics of included studies are presented in Table 1 and Supplementary Table S1."

        return text

    def _generate_rob_results(self, data: Dict[str, Any]) -> str:
        """Generate risk of bias results."""
        if self.use_llm and self.llm:
            prompt = f"""Generate risk of bias results section:

Total studies: {data.get('total_studies', 0)}
Low RoB: {data.get('low_rob_studies', 0)}
High RoB: {data.get('high_rob_studies', 0)}
Unclear RoB: {data.get('unclear_rob_studies', 0)}

Main concerns: {data.get('rob_main_concerns', [])}

Format for scientific manuscript."""

            try:
                return self.llm._generate(prompt, "You are an expert in systematic reviews.")
            except:
                pass

        # Fallback template
        low_rob = data.get('low_rob_studies', 0)
        high_rob = data.get('high_rob_studies', 0)
        total = data.get('total_studies', 0)

        text = f"""## Risk of Bias

Overall, {low_rob} of {total} studies ({low_rob/max(total,1)*100:.1f}%) were judged to be at low risk of bias. """

        if high_rob > 0:
            text += f"{high_rob} studies were at high risk of bias, primarily due to issues with blinding and incomplete outcome data. "

        text += "Risk of bias assessment for individual studies is shown in Figure 2 and summarized in Supplementary Figure S1."

        return text

    def _generate_effect_estimates(self, data: Dict[str, Any]) -> str:
        """Generate main effect estimates section."""
        pooled = data.get('pooled_effect', 0)
        ci_low = data.get('ci_low', 0)
        ci_high = data.get('ci_high', 0)
        p_value = data.get('p_value', 1.0)
        effect_measure = data.get('effect_measure', 'SMD')

        text = f"""## Synthesis of Results

### Primary Outcome

Meta-analysis of {data.get('n_studies', 0)} studies showed """

        if p_value < 0.05:
            text += f"a statistically significant effect ({effect_measure} = {pooled:.3f}, 95% CI [{ci_low:.3f}, {ci_high:.3f}], p = {p_value:.3f}). "
        else:
            text += f"no statistically significant effect ({effect_measure} = {pooled:.3f}, 95% CI [{ci_low:.3f}, {ci_high:.3f}], p = {p_value:.3f}). "

        # Clinical interpretation
        if abs(pooled) > 0.8:
            text += "This represents a large effect size. "
        elif abs(pooled) > 0.5:
            text += "This represents a moderate effect size. "
        elif abs(pooled) > 0.2:
            text += "This represents a small effect size. "

        text += "Individual study results are shown in Figure 3 (forest plot)."

        return text

    def _generate_heterogeneity(self, data: Dict[str, Any]) -> str:
        """Generate heterogeneity results."""
        I2 = data.get('I2', 0)
        tau2 = data.get('tau2', 0)
        Q = data.get('Q', 0)
        Q_p = data.get('Q_p_value', 1.0)

        text = f"""### Heterogeneity

"""

        if I2 < 25:
            interpretation = "low"
        elif I2 < 50:
            interpretation = "moderate"
        elif I2 < 75:
            interpretation = "substantial"
        else:
            interpretation = "considerable"

        text += f"Statistical heterogeneity was {interpretation} (I² = {I2:.1f}%, τ² = {tau2:.3f}, Q = {Q:.2f}, p = {Q_p:.3f}). "

        if I2 > 50:
            text += "The substantial heterogeneity warranted further exploration through subgroup and meta-regression analyses. "

        return text

    def _generate_publication_bias(self, data: Dict[str, Any]) -> str:
        """Generate publication bias results."""
        text = """### Publication Bias

"""

        if data.get('funnel_plot_asymmetry'):
            text += "Visual inspection of the funnel plot suggested potential asymmetry. "
        else:
            text += "Visual inspection of the funnel plot did not reveal obvious asymmetry. "

        if 'egger_p_value' in data:
            egger_p = data['egger_p_value']
            if egger_p < 0.05:
                text += f"Egger's test indicated significant asymmetry (p = {egger_p:.3f}), suggesting potential publication bias. "
            else:
                text += f"Egger's test did not indicate significant asymmetry (p = {egger_p:.3f}). "

        if 'trim_fill_adjusted' in data:
            text += f"Trim-and-fill analysis suggested {data.get('n_imputed_studies', 0)} potentially missing studies, with adjusted estimate of {data['trim_fill_adjusted']:.3f}. "

        return text

    def _generate_subgroup_results(self, data: Dict[str, Any]) -> str:
        """Generate subgroup analysis results."""
        if not data.get('subgroup_analyses'):
            return ""

        text = """### Subgroup and Sensitivity Analyses

"""

        if data.get('subgroup_by_age'):
            text += f"Subgroup analysis by age showed {data['subgroup_by_age']}. "

        if data.get('sensitivity_low_rob'):
            text += f"Restricting to low risk of bias studies yielded similar results ({data['sensitivity_low_rob']}). "

        if data.get('leave_one_out_range'):
            text += f"Leave-one-out sensitivity analysis showed pooled estimates ranging from {data['leave_one_out_range']}, indicating robustness of findings. "

        return text

    def _generate_grade_results(self, data: Dict[str, Any]) -> str:
        """Generate GRADE certainty results."""
        if not data.get('grade_assessment'):
            return ""

        certainty = data.get('certainty_rating', 'moderate')

        text = f"""### Certainty of Evidence

The certainty of evidence was rated as **{certainty}** according to GRADE criteria. """

        if 'grade_downgrades' in data:
            text += f"Evidence was downgraded for: {', '.join(data['grade_downgrades'])}. "

        text += "Detailed GRADE assessments are shown in Table 2 (Summary of Findings table)."

        return text

    def _format_sections(self, sections: Dict[str, str], format: str) -> str:
        """Format all sections."""
        full_text = "# RESULTS\n\n"

        for section_name, section_text in sections.items():
            if section_text:
                full_text += section_text + "\n\n"

        if format == "latex":
            full_text = full_text.replace('#', '\\section')
            full_text = full_text.replace('##', '\\subsection')

        elif format == "html":
            full_text = full_text.replace('# ', '<h1>').replace('\n', '</h1>\n', 1)
            full_text = full_text.replace('## ', '<h2>')

        return full_text

    def _generate_improvement_recommendations(self, validation: Dict[str, Any]) -> str:
        """Generate recommendations for improving results section."""
        text = "\n\n---\n## RECOMMENDATIONS FOR IMPROVEMENT\n\n"

        if validation['critical_issues']:
            text += "### Critical Issues:\n\n"
            for issue in validation['critical_issues'][:5]:
                text += f"- **{issue['message']}**: {issue['recommendation']}\n"

        return text

    def validate(self, results_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate results section against 500+ rules."""
        return validate_results_section(results_data)


def generate_results_section(
    results_data: Dict[str, Any],
    model: str = "llama3:8b",
    format: str = "markdown"
) -> Dict[str, Any]:
    """
    Quick function to generate results section.

    Args:
        results_data: Results information
        model: LLM model
        format: Output format

    Returns:
        Generated results with validation
    """
    generator = ResultsSectionGenerator(model=model)
    return generator.generate(results_data, format=format)


__all__ = [
    'ResultsSectionGenerator',
    'generate_results_section',
]
