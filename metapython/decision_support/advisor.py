"""
Intelligent Meta-Analysis Advisor

Combines LLM reasoning with rule-based validation to provide
expert-level decision support for meta-analysis workflows.
"""

from typing import Dict, List, Any, Optional
import json

from metapython.core.config import logger
from metapython.rules.engine import RulesEngine, RuleCategory, RuleSeverity
from metapython.llm.llama_integration import LlamaMetaAnalyst

# Import rules
try:
    from metapython.rules.inclusion_rules import INCLUSION_RULES
    from metapython.rules.statistical_rules import STATISTICAL_RULES
    HAS_RULES = True
except ImportError:
    HAS_RULES = False
    logger.warning("Rules modules not fully loaded")


class MetaAnalysisAdvisor:
    """
    Intelligent advisor combining LLM and rules for meta-analysis guidance.

    Provides comprehensive decision support integrating:
    - Llama 3 for natural language understanding and generation
    - 500+ evidence-based rules for validation
    - 10,000+ scenarios for method testing

    Example:
        >>> advisor = MetaAnalysisAdvisor(model="llama3:70b")
        >>> recommendation = advisor.recommend_methods(study_characteristics)
        >>> quality_issues = advisor.validate_analysis(analysis_data)
        >>> report = advisor.generate_interpretation(results)
    """

    def __init__(
        self,
        model: str = "llama3:8b",
        use_llm: bool = True,
        use_rules: bool = True,
        **llm_kwargs
    ):
        """
        Initialize advisor.

        Args:
            model: LLM model to use
            use_llm: Whether to use LLM for reasoning
            use_rules: Whether to apply rules validation
            **llm_kwargs: Additional arguments for LlamaMetaAnalyst
        """
        self.use_llm = use_llm
        self.use_rules = use_rules

        # Initialize LLM
        if use_llm:
            try:
                self.llm = LlamaMetaAnalyst(model=model, **llm_kwargs)
                logger.info(f"Initialized LLM advisor with {model}")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM: {e}")
                self.use_llm = False
                self.llm = None
        else:
            self.llm = None

        # Initialize rules engine
        if use_rules and HAS_RULES:
            self.rules_engine = RulesEngine()
            self.rules_engine.add_rules(INCLUSION_RULES)
            self.rules_engine.add_rules(STATISTICAL_RULES)
            logger.info(f"Loaded {len(self.rules_engine.rules)} rules")
        else:
            self.rules_engine = None

    def recommend_methods(
        self,
        study_characteristics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Recommend appropriate statistical methods.

        Combines LLM reasoning with rules-based validation.

        Args:
            study_characteristics: Dictionary with study information

        Returns:
            Comprehensive method recommendations
        """
        recommendations = {
            'llm_recommendations': None,
            'rules_validation': None,
            'final_recommendations': {},
        }

        # Get LLM recommendations
        if self.use_llm and self.llm:
            try:
                llm_rec = self.llm.recommend_methods(study_characteristics)
                recommendations['llm_recommendations'] = llm_rec
                logger.info("Generated LLM method recommendations")
            except Exception as e:
                logger.warning(f"LLM recommendation failed: {e}")

        # Validate with rules
        if self.use_rules and self.rules_engine:
            try:
                rule_results = self.rules_engine.evaluate(
                    study_characteristics,
                    categories=[RuleCategory.STATISTICAL]
                )
                recommendations['rules_validation'] = {
                    'passed': sum(1 for r in rule_results.results if r.passed),
                    'failed': sum(1 for r in rule_results.results if not r.passed),
                    'critical_issues': [
                        {'rule_id': r.rule_id, 'message': r.message, 'recommendation': r.recommendation}
                        for r in rule_results.get_critical_issues()
                    ],
                    'warnings': [
                        {'rule_id': r.rule_id, 'message': r.message}
                        for r in rule_results.get_by_severity(RuleSeverity.WARNING)[:5]
                    ]
                }
                logger.info("Completed rules validation")
            except Exception as e:
                logger.warning(f"Rules validation failed: {e}")

        # Synthesize final recommendations
        recommendations['final_recommendations'] = self._synthesize_recommendations(
            recommendations
        )

        return recommendations

    def validate_analysis(
        self,
        analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate meta-analysis data and methods.

        Args:
            analysis_data: Analysis configuration and data

        Returns:
            Validation results with issues and recommendations
        """
        validation = {
            'overall_quality': 'pending',
            'critical_issues': [],
            'warnings': [],
            'recommendations': [],
            'passed_checks': 0,
            'failed_checks': 0,
        }

        if self.use_rules and self.rules_engine:
            # Evaluate all rules
            results = self.rules_engine.evaluate(analysis_data)

            validation['passed_checks'] = sum(1 for r in results.results if r.passed)
            validation['failed_checks'] = sum(1 for r in results.results if not r.passed)

            # Get critical issues
            critical = results.get_critical_issues()
            validation['critical_issues'] = [
                {
                    'rule_id': r.rule_id,
                    'message': r.message,
                    'recommendation': r.recommendation,
                    'category': r.category.value
                }
                for r in critical
            ]

            # Get warnings
            warnings = results.get_by_severity(RuleSeverity.WARNING)
            validation['warnings'] = [
                {
                    'rule_id': r.rule_id,
                    'message': r.message,
                    'category': r.category.value
                }
                for r in warnings[:10]  # Limit to top 10
            ]

            # Determine overall quality
            if len(critical) == 0 and len(warnings) <= 5:
                validation['overall_quality'] = 'excellent'
            elif len(critical) == 0:
                validation['overall_quality'] = 'good'
            elif len(critical) <= 3:
                validation['overall_quality'] = 'acceptable'
            else:
                validation['overall_quality'] = 'poor'

            # Generate recommendations
            validation['recommendations'] = self._generate_validation_recommendations(
                critical, warnings
            )

        return validation

    def interpret_results(
        self,
        meta_results: Dict[str, Any],
        include_clinical_guidance: bool = True
    ) -> Dict[str, Any]:
        """
        Interpret meta-analysis results with clinical and statistical context.

        Args:
            meta_results: Meta-analysis results dictionary
            include_clinical_guidance: Whether to include clinical recommendations

        Returns:
            Comprehensive interpretation
        """
        interpretation = {
            'summary': '',
            'statistical_interpretation': {},
            'clinical_interpretation': {},
            'certainty_of_evidence': '',
            'recommendations': [],
        }

        # Get LLM interpretation
        if self.use_llm and self.llm:
            try:
                system_prompt = """You are an expert clinician and statistician interpreting meta-analysis results.
Provide clear, actionable interpretation considering both statistical and clinical significance."""

                # Build interpretation prompt
                prompt = f"""Interpret these meta-analysis results:

{json.dumps(meta_results, indent=2)}

Provide:
1. **Summary**: One paragraph overview
2. **Statistical significance**: Interpretation of p-values, CIs, heterogeneity
3. **Clinical significance**: Real-world importance and applicability
4. **Certainty of evidence**: GRADE assessment
5. **Recommendations**: Clear guidance for practice and research

Format as JSON with these fields."""

                response = self.llm._generate(prompt, system_prompt)

                # Parse JSON response
                try:
                    import re
                    json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
                    if json_match:
                        interpretation = json.loads(json_match.group(1))
                    else:
                        interpretation['summary'] = response
                except json.JSONDecodeError:
                    interpretation['summary'] = response

                logger.info("Generated LLM interpretation")

            except Exception as e:
                logger.warning(f"LLM interpretation failed: {e}")

        # Add rules-based validation of interpretation
        if self.use_rules:
            interpretation['validation_notes'] = self._validate_interpretation(meta_results)

        return interpretation

    def generate_report(
        self,
        meta_results: Dict[str, Any],
        format: str = "prisma",
        include_figures: bool = True
    ) -> str:
        """
        Generate comprehensive meta-analysis report.

        Args:
            meta_results: Analysis results
            format: Report format (prisma, cochrane, narrative)
            include_figures: Whether to describe figures

        Returns:
            Formatted report
        """
        if self.use_llm and self.llm:
            return self.llm.generate_report(meta_results, format, include_figures)
        else:
            return self._generate_basic_report(meta_results)

    def _synthesize_recommendations(
        self,
        recommendations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesize LLM and rules recommendations."""

        final = {
            'effect_measure': 'SMD',  # Default
            'pooling_method': 'random',  # Default
            'heterogeneity_assessment': ['I2', 'tau2', 'Q_test'],
            'publication_bias_tests': [],
            'sensitivity_analyses': ['leave-one-out'],
            'justification': '',
        }

        # Extract from LLM recommendations
        if recommendations.get('llm_recommendations'):
            llm_rec = recommendations['llm_recommendations']
            if isinstance(llm_rec, dict):
                final.update({
                    k: v for k, v in llm_rec.items()
                    if k in final and v is not None
                })

        # Apply rules constraints
        rules_val = recommendations.get('rules_validation')
        if rules_val and rules_val.get('critical_issues'):
            final['justification'] += "\n\nCritical issues to address: " + "; ".join(
                issue['message'] for issue in rules_val['critical_issues'][:3]
            )

        return final

    def _generate_validation_recommendations(
        self,
        critical_issues: List,
        warnings: List
    ) -> List[str]:
        """Generate actionable recommendations from validation."""

        recommendations = []

        # Address critical issues first
        if critical_issues:
            recommendations.append(
                f"CRITICAL: Address {len(critical_issues)} critical issues before proceeding"
            )
            for issue in critical_issues[:3]:
                if issue.get('recommendation'):
                    recommendations.append(f"- {issue['recommendation']}")

        # Address warnings
        if warnings:
            recommendations.append(
                f"Review {len(warnings)} warnings to improve analysis quality"
            )

        # General recommendations
        if len(critical_issues) == 0 and len(warnings) <= 5:
            recommendations.append(
                "Analysis meets quality standards. Proceed with interpretation."
            )

        return recommendations

    def _validate_interpretation(
        self,
        results: Dict[str, Any]
    ) -> List[str]:
        """Validate interpretation against results."""

        notes = []

        # Check effect size interpretation
        effect = results.get('pooled_effect', 0)
        ci_low = results.get('ci_low', effect)
        ci_high = results.get('ci_high', effect)

        if ci_low * ci_high < 0:
            notes.append("CI crosses null value - interpret non-significant result cautiously")

        # Check heterogeneity
        I2 = results.get('I2', 0)
        if I2 > 75:
            notes.append("Substantial heterogeneity - pooled estimate may not be meaningful")

        # Check sample size
        n_studies = results.get('n_studies', 0)
        if n_studies < 5:
            notes.append("Small number of studies - interpret with caution")

        return notes

    def _generate_basic_report(self, results: Dict[str, Any]) -> str:
        """Generate basic report without LLM."""

        report = f"""
# Meta-Analysis Report

## Results

- Number of studies: {results.get('n_studies', 'N/A')}
- Pooled effect: {results.get('pooled_effect', 'N/A'):.3f}
- 95% CI: [{results.get('ci_low', 'N/A'):.3f}, {results.get('ci_high', 'N/A'):.3f}]
- P-value: {results.get('p_value', 'N/A')}
- I²: {results.get('I2', 'N/A')}%

## Interpretation

{'Significant effect detected' if results.get('p_value', 1) < 0.05 else 'No significant effect'}
"""

        return report


# Convenience functions

def get_method_recommendation(
    study_characteristics: Dict[str, Any],
    model: str = "llama3:8b"
) -> Dict[str, Any]:
    """Get method recommendations quickly."""
    advisor = MetaAnalysisAdvisor(model=model)
    return advisor.recommend_methods(study_characteristics)


def assess_analysis_quality(
    analysis_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Assess analysis quality quickly."""
    advisor = MetaAnalysisAdvisor(use_llm=False, use_rules=True)
    return advisor.validate_analysis(analysis_data)


def interpret_results(
    meta_results: Dict[str, Any],
    model: str = "llama3:70b"
) -> Dict[str, Any]:
    """Interpret results quickly."""
    advisor = MetaAnalysisAdvisor(model=model)
    return advisor.interpret_results(meta_results)


__all__ = [
    'MetaAnalysisAdvisor',
    'get_method_recommendation',
    'assess_analysis_quality',
    'interpret_results',
]
