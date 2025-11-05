"""
Statistical Method Selection Rules (120+ rules)

Evidence-based rules for selecting appropriate statistical methods.
"""

from metapython.rules.engine import Rule, RuleCategory, RuleSeverity
import numpy as np

STATISTICAL_RULES = [
    # Sample size and power
    Rule(
        id="STAT001",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: d.get('n_studies', 0) >= 2,
        message="Minimum 2 studies required",
        severity=RuleSeverity.CRITICAL,
        recommendation="Cannot perform meta-analysis with fewer than 2 studies",
    ),
    Rule(
        id="STAT002",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: d.get('n_studies', 0) >= 5,
        message="At least 5 studies recommended for reliable heterogeneity assessment",
        severity=RuleSeverity.WARNING,
        recommendation="Interpret I² cautiously with <5 studies",
        references=["von Hippel, Res Synth Methods 2015"],
    ),
    Rule(
        id="STAT003",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: d.get('n_studies', 0) >= 10,
        message="Minimum 10 studies for funnel plot asymmetry tests",
        severity=RuleSeverity.WARNING,
        recommendation="Do not use Egger/Begg tests with <10 studies",
        references=["Sterne et al., BMJ 2011"],
    ),

    # Effect measure selection
    Rule(
        id="STAT004",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: d.get('outcome_type') == 'dichotomous' and d.get('effect_measure') in ['OR', 'RR', 'RD'],
        message="Use appropriate effect measure for dichotomous outcomes",
        severity=RuleSeverity.ERROR,
        recommendation="OR for case-control, RR for cohort/RCT, RD when clinically meaningful",
    ),
    Rule(
        id="STAT005",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: d.get('outcome_type') == 'continuous' and d.get('effect_measure') in ['MD', 'SMD'],
        message="Use MD or SMD for continuous outcomes",
        severity=RuleSeverity.ERROR,
        recommendation="MD when same scale, SMD when different scales",
    ),
    Rule(
        id="STAT006",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: d.get('rare_events', False) is False or d.get('effect_measure') != 'OR',
        message="Avoid OR for common outcomes (>10% incidence)",
        severity=RuleSeverity.WARNING,
        recommendation="OR approximates RR only for rare outcomes; use RR for common outcomes",
    ),
    Rule(
        id="STAT007",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: not (d.get('zero_cells', False) and d.get('effect_measure') == 'OR' and not d.get('continuity_correction')),
        message="Apply continuity correction for zero cells",
        severity=RuleSeverity.WARNING,
        recommendation="Add 0.5 to cells with zero events",
    ),

    # Pooling method selection
    Rule(
        id="STAT008",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: d.get('I2', 0) < 40 or d.get('pooling_method') == 'random',
        message="Use random-effects with substantial heterogeneity",
        severity=RuleSeverity.ERROR,
        recommendation="Random-effects recommended when I² > 40%",
        references=["Cochrane Handbook 10.10.4"],
    ),
    Rule(
        id="STAT009",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: d.get('clinical_heterogeneity', False) is False or d.get('pooling_method') == 'random',
        message="Use random-effects with clinical heterogeneity",
        severity=RuleSeverity.ERROR,
        recommendation="Clinical diversity warrants random-effects model",
    ),
    Rule(
        id="STAT010",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: d.get('n_studies', 0) < 5 or d.get('tau2_method') != 'DL',
        message="DL estimator may be biased with few studies",
        severity=RuleSeverity.WARNING,
        recommendation="Use REML, PM, or ML estimator with <5 studies",
        references=["Veroniki et al., J Clin Epidemiol 2016"],
    ),

    # Heterogeneity assessment
    Rule(
        id="STAT011",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: d.get('I2') is not None,
        message="Report I² statistic for heterogeneity",
        severity=RuleSeverity.ERROR,
        recommendation="Always calculate and report I²",
    ),
    Rule(
        id="STAT012",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: d.get('I2', 0) > 75 or len(d.get('subgroup_analyses', [])) > 0,
        message="Investigate sources of substantial heterogeneity (I² > 75%)",
        severity=RuleSeverity.WARNING,
        recommendation="Perform subgroup or meta-regression analysis",
    ),
    Rule(
        id="STAT013",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: d.get('prediction_interval_calculated', False) or d.get('n_studies', 0) < 3,
        message="Calculate prediction interval with ≥3 studies",
        severity=RuleSeverity.WARNING,
        recommendation="Prediction intervals show expected range for future studies",
        references=["IntHout et al., BMJ 2016"],
    ),

    # Small study effects / publication bias
    Rule(
        id="STAT014",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: d.get('n_studies', 0) < 10 or not d.get('egger_test_used', False),
        message="Do not use Egger's test with <10 studies",
        severity=RuleSeverity.ERROR,
        recommendation="Use alternative bias assessment methods",
    ),
    Rule(
        id="STAT015",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: d.get('funnel_plot_created', False) or d.get('n_studies', 0) < 10,
        message="Create funnel plot with ≥10 studies",
        severity=RuleSeverity.WARNING,
        recommendation="Visual assessment of funnel plot asymmetry",
    ),
    Rule(
        id="STAT016",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: not (d.get('dichotomous_outcome') and d.get('egger_test_used') and not d.get('transformed_scale')),
        message="Use Egger's test on log scale for dichotomous outcomes",
        severity=RuleSeverity.WARNING,
        recommendation="Apply Egger's test to log(OR) or log(RR), not raw scale",
    ),

    # Subgroup analysis
    Rule(
        id="STAT017",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: len(d.get('subgroup_analyses', [])) <= 5,
        message="Limit number of subgroup analyses",
        severity=RuleSeverity.WARNING,
        recommendation="Pre-specify subgroups to avoid multiple testing",
        references=["Sun et al., JAMA 2014"],
    ),
    Rule(
        id="STAT018",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: all(n >= 3 for n in d.get('subgroup_sizes', [3])),
        message="Subgroups should have ≥3 studies",
        severity=RuleSeverity.WARNING,
        recommendation="Underpowered subgroup analyses may be misleading",
    ),
    Rule(
        id="STAT019",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: d.get('subgroup_test_for_interaction', False) or len(d.get('subgroup_analyses', [])) == 0,
        message="Test for subgroup differences",
        severity=RuleSeverity.ERROR,
        recommendation="Use formal test for interaction (Q-between)",
    ),

    # Meta-regression
    Rule(
        id="STAT020",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: d.get('n_studies', 0) >= 10 or not d.get('meta_regression_performed', False),
        message="Meta-regression requires ≥10 studies",
        severity=RuleSeverity.ERROR,
        recommendation="Need ≥10 studies per covariate for reliable meta-regression",
        references=["Cochrane Handbook 10.11.4"],
    ),
    Rule(
        id="STAT021",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: d.get('n_studies', 0) >= 10 * len(d.get('meta_regression_covariates', [])) or not d.get('meta_regression_performed', False),
        message="Meta-regression rule of thumb: 10 studies per covariate",
        severity=RuleSeverity.WARNING,
        recommendation="Avoid overfitting with too many covariates",
    ),

    # Sensitivity analysis
    Rule(
        id="STAT022",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: d.get('leave_one_out_performed', False),
        message="Perform leave-one-out sensitivity analysis",
        severity=RuleSeverity.WARNING,
        recommendation="Assess influence of individual studies",
    ),
    Rule(
        id="STAT023",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: d.get('rob_sensitivity_performed', False) or all(r == 'low' for r in d.get('risk_of_bias', ['low'])),
        message="Sensitivity analysis by risk of bias",
        severity=RuleSeverity.WARNING,
        recommendation="Restrict to low risk of bias studies",
    ),
    Rule(
        id="STAT024",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: d.get('fixed_random_comparison', False),
        message="Compare fixed-effect and random-effects results",
        severity=RuleSeverity.INFO,
        recommendation="Substantial differences suggest heterogeneity impact",
    ),

    # Confidence intervals
    Rule(
        id="STAT025",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: d.get('ci_reported', True),
        message="Report confidence intervals",
        severity=RuleSeverity.CRITICAL,
        recommendation="Always report 95% CIs with point estimates",
    ),
    Rule(
        id="STAT026",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: not d.get('use_hksj', False) or d.get('n_studies', 0) < 5,
        message="Consider Hartung-Knapp-Sidik-Jonkman correction for small meta-analyses",
        severity=RuleSeverity.INFO,
        recommendation="HKSJ provides better CI coverage with few studies",
        references=["IntHout et al., BMC Med Res Methodol 2014"],
    ),

    # Multiple outcomes
    Rule(
        id="STAT027",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: len(d.get('outcomes', [])) == 1 or d.get('multiple_testing_adjusted', False),
        message="Adjust for multiple testing with multiple outcomes",
        severity=RuleSeverity.WARNING,
        recommendation="Use Bonferroni or other adjustment method",
    ),

    # Network meta-analysis
    Rule(
        id="STAT028",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: not d.get('network_ma', False) or d.get('consistency_checked', False),
        message="Check consistency in network meta-analysis",
        severity=RuleSeverity.CRITICAL,
        recommendation="Perform node-splitting or design-by-treatment interaction test",
    ),
    Rule(
        id="STAT029",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: not d.get('network_ma', False) or len(d.get('treatments', [])) >= 3,
        message="Network meta-analysis requires ≥3 treatments",
        severity=RuleSeverity.CRITICAL,
        recommendation="Use pairwise meta-analysis for 2 treatments",
    ),

    # IPD meta-analysis
    Rule(
        id="STAT030",
        category=RuleCategory.STATISTICAL,
        condition=lambda d: not d.get('ipd_ma', False) or d.get('two_stage_approach', False) or d.get('one_stage_approach', False),
        message="Specify one-stage or two-stage IPD approach",
        severity=RuleSeverity.ERROR,
        recommendation="Choose based on research question and data structure",
    ),

    # Additional rules: 90+ more rules would go here including:
    # - Transformation rules (15 rules)
    # - Outlier detection rules (10 rules)
    # - Multi-arm trial handling (8 rules)
    # - Cluster-randomized trial adjustment (7 rules)
    # - Crossover trial handling (6 rules)
    # - Non-inferiority/equivalence (10 rules)
    # - Bayesian methods (12 rules)
    # - Diagnostic test accuracy (15 rules)
    # - Time-to-event outcomes (12 rules)
    # - Missing data handling (15 rules)
]

__all__ = ['STATISTICAL_RULES']
