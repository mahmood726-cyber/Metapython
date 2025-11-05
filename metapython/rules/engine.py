"""
Rules Engine for Evidence-Based Meta-Analysis Decision Support

Implements a flexible, extensible rules engine with 600+ expert rules.
"""

from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import json


class RuleCategory(Enum):
    """Categories of meta-analysis rules."""
    INCLUSION = "inclusion"
    QUALITY = "quality"
    STATISTICAL = "statistical"
    HETEROGENEITY = "heterogeneity"
    BIAS = "bias"
    INTERPRETATION = "interpretation"
    REPORTING = "reporting"


class RuleSeverity(Enum):
    """Severity levels for rule violations."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Rule:
    """
    Individual meta-analysis rule.

    Example:
        >>> rule = Rule(
        ...     id="MIN_STUDIES_001",
        ...     category=RuleCategory.STATISTICAL,
        ...     condition=lambda data: data['n_studies'] >= 2,
        ...     message="At least 2 studies required",
        ...     severity=RuleSeverity.CRITICAL
        ... )
    """
    id: str
    category: RuleCategory
    condition: Callable[[Dict[str, Any]], bool]
    message: str
    severity: RuleSeverity = RuleSeverity.WARNING
    recommendation: str = ""
    references: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RuleResult:
    """Result of rule evaluation."""
    rule_id: str
    passed: bool
    severity: RuleSeverity
    message: str
    recommendation: str
    category: RuleCategory
    metadata: Dict[str, Any] = field(default_factory=dict)


class RulesEngine:
    """
    Comprehensive rules engine for meta-analysis.

    Manages and evaluates 600+ expert rules across all aspects of
    meta-analysis workflow.

    Example:
        >>> engine = RulesEngine()
        >>> engine.load_all_rules()
        >>> results = engine.evaluate(data)
        >>> critical_issues = results.get_critical_issues()
    """

    def __init__(self):
        """Initialize rules engine."""
        self.rules: Dict[str, Rule] = {}
        self.rule_counts: Dict[RuleCategory, int] = {cat: 0 for cat in RuleCategory}

    def add_rule(self, rule: Rule) -> None:
        """Add a rule to the engine."""
        self.rules[rule.id] = rule
        self.rule_counts[rule.category] += 1

    def add_rules(self, rules: List[Rule]) -> None:
        """Add multiple rules."""
        for rule in rules:
            self.add_rule(rule)

    def evaluate(
        self,
        data: Dict[str, Any],
        categories: Optional[List[RuleCategory]] = None
    ) -> 'RuleEvaluationResults':
        """
        Evaluate data against rules.

        Args:
            data: Data to evaluate
            categories: Specific categories to check (default: all)

        Returns:
            RuleEvaluationResults object
        """
        results = []

        for rule_id, rule in self.rules.items():
            # Skip if category filter specified and doesn't match
            if categories and rule.category not in categories:
                continue

            try:
                passed = rule.condition(data)

                result = RuleResult(
                    rule_id=rule_id,
                    passed=passed,
                    severity=rule.severity,
                    message=rule.message,
                    recommendation=rule.recommendation,
                    category=rule.category,
                    metadata=rule.metadata.copy(),
                )
                results.append(result)

            except Exception as e:
                # Rule evaluation failed - treat as error
                result = RuleResult(
                    rule_id=rule_id,
                    passed=False,
                    severity=RuleSeverity.ERROR,
                    message=f"Rule evaluation failed: {str(e)}",
                    recommendation="Check input data format",
                    category=rule.category,
                )
                results.append(result)

        return RuleEvaluationResults(results)

    def get_rules_summary(self) -> Dict[str, Any]:
        """Get summary of loaded rules."""
        return {
            'total_rules': len(self.rules),
            'by_category': {
                cat.value: count
                for cat, count in self.rule_counts.items()
            },
            'by_severity': {
                severity.value: sum(
                    1 for r in self.rules.values()
                    if r.severity == severity
                )
                for severity in RuleSeverity
            },
        }

    def export_rules(self, filepath: str) -> None:
        """Export rules to JSON file."""
        rules_data = [
            {
                'id': r.id,
                'category': r.category.value,
                'message': r.message,
                'severity': r.severity.value,
                'recommendation': r.recommendation,
                'references': r.references,
                'metadata': r.metadata,
            }
            for r in self.rules.values()
        ]

        with open(filepath, 'w') as f:
            json.dump(rules_data, f, indent=2)


class RuleEvaluationResults:
    """Results from rules evaluation."""

    def __init__(self, results: List[RuleResult]):
        """Initialize with results."""
        self.results = results

    def get_failed_rules(self) -> List[RuleResult]:
        """Get all failed rules."""
        return [r for r in self.results if not r.passed]

    def get_by_severity(self, severity: RuleSeverity) -> List[RuleResult]:
        """Get rules by severity."""
        return [r for r in self.results if r.severity == severity and not r.passed]

    def get_critical_issues(self) -> List[RuleResult]:
        """Get critical issues that must be addressed."""
        return self.get_by_severity(RuleSeverity.CRITICAL)

    def get_by_category(self, category: RuleCategory) -> List[RuleResult]:
        """Get results by category."""
        return [r for r in self.results if r.category == category]

    def has_critical_issues(self) -> bool:
        """Check if there are any critical issues."""
        return len(self.get_critical_issues()) > 0

    def generate_report(self, format: str = "text") -> str:
        """
        Generate summary report.

        Args:
            format: Output format ("text", "markdown", "html")

        Returns:
            Formatted report
        """
        if format == "markdown":
            return self._generate_markdown_report()
        elif format == "html":
            return self._generate_html_report()
        else:
            return self._generate_text_report()

    def _generate_text_report(self) -> str:
        """Generate plain text report."""
        lines = ["=" * 70, "META-ANALYSIS RULES EVALUATION REPORT", "=" * 70, ""]

        # Summary
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed

        lines.append(f"Total Rules Evaluated: {total}")
        lines.append(f"Passed: {passed} ({passed/total*100:.1f}%)")
        lines.append(f"Failed: {failed} ({failed/total*100:.1f}%)")
        lines.append("")

        # By severity
        lines.append("Failed Rules by Severity:")
        for severity in RuleSeverity:
            count = len(self.get_by_severity(severity))
            if count > 0:
                lines.append(f"  {severity.value.upper()}: {count}")
        lines.append("")

        # Critical issues
        critical = self.get_critical_issues()
        if critical:
            lines.append("=" * 70)
            lines.append("CRITICAL ISSUES (MUST BE ADDRESSED)")
            lines.append("=" * 70)
            for result in critical:
                lines.append(f"\n[{result.rule_id}] {result.message}")
                if result.recommendation:
                    lines.append(f"  → Recommendation: {result.recommendation}")
            lines.append("")

        # Warnings
        warnings = self.get_by_severity(RuleSeverity.WARNING)
        if warnings:
            lines.append("=" * 70)
            lines.append("WARNINGS")
            lines.append("=" * 70)
            for result in warnings[:10]:  # Limit to 10
                lines.append(f"\n[{result.rule_id}] {result.message}")
                if result.recommendation:
                    lines.append(f"  → {result.recommendation}")
            if len(warnings) > 10:
                lines.append(f"\n... and {len(warnings) - 10} more warnings")

        return "\n".join(lines)

    def _generate_markdown_report(self) -> str:
        """Generate Markdown report."""
        lines = ["# Meta-Analysis Rules Evaluation Report\n"]

        # Summary
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed

        lines.append("## Summary\n")
        lines.append(f"- **Total Rules**: {total}")
        lines.append(f"- **Passed**: {passed} ({passed/total*100:.1f}%)")
        lines.append(f"- **Failed**: {failed} ({failed/total*100:.1f}%)\n")

        # Critical issues
        critical = self.get_critical_issues()
        if critical:
            lines.append("## ⚠️ Critical Issues\n")
            for result in critical:
                lines.append(f"### {result.rule_id}")
                lines.append(f"\n**Issue**: {result.message}\n")
                if result.recommendation:
                    lines.append(f"**Recommendation**: {result.recommendation}\n")

        # Warnings
        warnings = self.get_by_severity(RuleSeverity.WARNING)
        if warnings:
            lines.append("## Warnings\n")
            for result in warnings[:20]:
                lines.append(f"- **[{result.rule_id}]** {result.message}")

        return "\n".join(lines)

    def _generate_html_report(self) -> str:
        """Generate HTML report."""
        # Basic HTML report implementation
        html = ["<html><head><title>Meta-Analysis Rules Report</title></head><body>"]
        html.append("<h1>Meta-Analysis Rules Evaluation Report</h1>")

        # Summary
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)

        html.append(f"<p>Total: {total} | Passed: {passed} | Failed: {total - passed}</p>")

        # Critical issues
        critical = self.get_critical_issues()
        if critical:
            html.append("<h2 style='color: red;'>Critical Issues</h2>")
            html.append("<ul>")
            for result in critical:
                html.append(f"<li><strong>{result.rule_id}</strong>: {result.message}</li>")
            html.append("</ul>")

        html.append("</body></html>")
        return "\n".join(html)


def evaluate_rules(
    data: Dict[str, Any],
    rule_categories: Optional[List[RuleCategory]] = None
) -> RuleEvaluationResults:
    """
    Convenience function to evaluate data against all rules.

    Args:
        data: Data to evaluate
        rule_categories: Specific categories to check

    Returns:
        RuleEvaluationResults
    """
    engine = RulesEngine()

    # Load all rule modules
    from metapython.rules.inclusion_rules import INCLUSION_RULES
    from metapython.rules.statistical_rules import STATISTICAL_RULES

    engine.add_rules(INCLUSION_RULES)
    engine.add_rules(STATISTICAL_RULES)

    return engine.evaluate(data, rule_categories)


__all__ = [
    'Rule',
    'RuleCategory',
    'RuleSeverity',
    'RuleResult',
    'RulesEngine',
    'RuleEvaluationResults',
    'evaluate_rules',
]
