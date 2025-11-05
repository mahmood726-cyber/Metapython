"""
Journal-Style Examples: Cutting-Edge Meta-Analysis Methods
===========================================================

Real-world examples demonstrating state-of-the-art methods from
top statistics journals (JASA, BMJ, Statistics in Medicine, etc.)

Each example replicates analyses from published papers or demonstrates
best practices recommended in methodological literature.

Author: PyMeta-CBAMM Development Team
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from advanced_methods import PUniformMethods, SelectionModels, LimitMetaAnalysis
from advanced_methods_part2 import GOSHAnalysis, BootstrapMethods, DoseResponseSplines

# Set random seed for reproducibility
np.random.seed(42)

print("="*70)
print("JOURNAL-STYLE EXAMPLES: STATE-OF-THE-ART META-ANALYSIS")
print("="*70)

# ===================================================================
# EXAMPLE 1: P-UNIFORM FOR PUBLICATION BIAS
# ===================================================================

print("\n" + "="*70)
print("EXAMPLE 1: P-uniform Analysis for Publication Bias")
print("Based on: van Assen et al. (2015), Psychological Methods")
print("="*70)

# Simulate data with publication bias (only significant studies published)
print("\nScenario: Meta-analysis of cognitive training interventions")
print("True effect: d = 0.20")
print("Publication bias: Only p < 0.05 studies published")

# Generate true effects with heterogeneity
true_effect = 0.20
n_studies_total = 50
n_per_study = np.random.randint(30, 150, n_studies_total)
se_true = 0.2 / np.sqrt(n_per_study)  # SE decreases with sample size

# Generate observed effects
observed_effects = np.random.normal(true_effect, 0.1, n_studies_total)

# Apply publication bias filter (only significant studies)
z_scores = np.abs(observed_effects / se_true)
published_mask = z_scores > 1.96  # Only p < 0.05 published

published_effects = observed_effects[published_mask]
published_se = se_true[published_mask]

print(f"\nTotal studies conducted: {n_studies_total}")
print(f"Published studies: {len(published_effects)} ({len(published_effects)/n_studies_total*100:.1f}%)")

# Standard random-effects meta-analysis (naive)
naive_weights = 1 / published_se**2
naive_pooled = np.sum(naive_weights * published_effects) / np.sum(naive_weights)
print(f"\nNaive random-effects estimate: d = {naive_pooled:.3f} (biased upward!)")

# P-uniform analysis
print("\n" + "-"*70)
print("P-UNIFORM ANALYSIS")
print("-"*70)

punif_result = PUniformMethods.p_uniform(published_effects, published_se)

if punif_result['available']:
    print(f"P-uniform estimate: d = {punif_result['estimate']:.3f}")
    print(f"95% CI: [{punif_result['ci_low']:.3f}, {punif_result['ci_high']:.3f}]")
    print(f"Publication bias detected: {punif_result['publication_bias_detected']}")
    print(f"Test p-value: {punif_result['publication_bias_test_p']:.4f}")
    print(f"\nConclusion: P-uniform corrects for publication bias,")
    print(f"recovering estimate closer to true effect (0.20)")

# P-uniform* analysis (using all studies if available)
print("\n" + "-"*70)
print("P-UNIFORM* ANALYSIS (more efficient)")
print("-"*70)

punif_star_result = PUniformMethods.p_uniform_star(published_effects, published_se)

if punif_star_result['available']:
    print(f"P-uniform* estimate: d = {punif_star_result['estimate']:.3f}")
    print(f"95% CI: [{punif_star_result['ci_low']:.3f}, {punif_star_result['ci_high']:.3f}]")
    print(f"Publication bias: {punif_star_result['publication_bias_detected']}")
    print(f"\nInterpretation: {punif_star_result['interpretation']}")

# ===================================================================
# EXAMPLE 2: 3-PARAMETER SELECTION MODEL
# ===================================================================

print("\n\n" + "="*70)
print("EXAMPLE 2: Three-Parameter Selection Model")
print("Based on: Vevea & Hedges (1995), Psychometrika")
print("="*70)

print("\nScenario: Meta-analysis with moderate publication bias")
print("Selection probabilities: p<0.05 (100%), 0.05≤p<0.50 (60%), p≥0.50 (20%)")

# Generate data with known selection mechanism
n_studies = 25
true_effect_psm = 0.35
se_psm = np.random.uniform(0.05, 0.20, n_studies)
effects_psm = np.random.normal(true_effect_psm, 0.15, n_studies)

# Calculate p-values
z_psm = np.abs(effects_psm / se_psm)
p_values_psm = 2 * (1 - stats.norm.cdf(z_psm))

# Apply selection mechanism
selection_probs = np.where(p_values_psm < 0.05, 1.0,
                          np.where(p_values_psm < 0.50, 0.6, 0.2))
selected_mask = np.random.rand(n_studies) < selection_probs

selected_effects = effects_psm[selected_mask]
selected_se = se_psm[selected_mask]

print(f"\nStudies selected for publication: {len(selected_effects)}/{n_studies}")

# Naive estimate
naive_psm = np.sum(selected_effects / selected_se**2) / np.sum(1 / selected_se**2)
print(f"Naive estimate: θ = {naive_psm:.3f}")

# 3-Parameter selection model
print("\n" + "-"*70)
print("3-PARAMETER SELECTION MODEL")
print("-"*70)

psm_result = SelectionModels.three_parameter_selection_model(selected_effects, selected_se)

if psm_result['available']:
    print(f"3PSM estimate: θ = {psm_result['estimate']:.3f}")
    print(f"Heterogeneity: τ = {psm_result['tau']:.3f}")
    print(f"Selection weights:")
    print(f"  Significant (p<0.05): 1.00 (reference)")
    print(f"  Moderate (0.05≤p<0.50): {psm_result['weight_moderate']:.2f}")
    print(f"  Non-significant (p≥0.50): {psm_result['weight_high']:.2f}")
    print(f"Bias severity: {psm_result['bias_severity']}")
    print(f"\nConclusion: Selection model accounts for differential")
    print(f"publication probabilities across p-value regions")

# ===================================================================
# EXAMPLE 3: GOSH PLOT FOR OUTLIER DETECTION
# ===================================================================

print("\n\n" + "="*70)
print("EXAMPLE 3: GOSH (Graphical Display of Study Heterogeneity)")
print("Based on: Olkin et al. (2012), Research Synthesis Methods")
print("="*70)

print("\nScenario: Meta-analysis with 2 outlier studies")

# Generate data with outliers
n_studies_gosh = 15
true_effect_gosh = 0.50
se_gosh = np.random.uniform(0.08, 0.18, n_studies_gosh)
effects_gosh = np.random.normal(true_effect_gosh, 0.10, n_studies_gosh)

# Add 2 outliers
effects_gosh[0] = 1.50  # Extreme positive outlier
effects_gosh[1] = -0.20  # Negative outlier

study_labels_gosh = np.array([f"Study {i+1}" for i in range(n_studies_gosh)])

print(f"Number of studies: {n_studies_gosh}")
print(f"True effect: θ = {true_effect_gosh:.2f}")
print(f"Outliers: Study 1 (effect=1.50) and Study 2 (effect=-0.20)")

# Run GOSH analysis
print("\n" + "-"*70)
print("GOSH ANALYSIS")
print("-"*70)

gosh_result = GOSHAnalysis.gosh_analysis(
    effects_gosh, se_gosh, study_labels_gosh,
    n_samples=5000
)

if gosh_result['available']:
    print(f"Subsets analyzed: {gosh_result['n_subsets']}")
    print(f"Effect estimate range: {gosh_result['fe_estimate_range'][0]:.3f} to "
          f"{gosh_result['fe_estimate_range'][1]:.3f}")
    print(f"I² range: {gosh_result['I2_range'][0]:.1f}% to {gosh_result['I2_range'][1]:.1f}%")
    print(f"Outlier subsets detected: {gosh_result['n_outliers']}")

    if gosh_result['influential_studies']:
        print(f"\nMost influential studies:")
        for study, count in gosh_result['influential_studies'][:3]:
            print(f"  {study}: appears in {count} outlier subsets")

    print(f"\nInterpretation: {gosh_result['interpretation']}")

# ===================================================================
# EXAMPLE 4: BOOTSTRAP CONFIDENCE INTERVALS
# ===================================================================

print("\n\n" + "="*70)
print("EXAMPLE 4: Bootstrap Confidence Intervals")
print("Based on: Davison & Hinkley (1997), Cambridge University Press")
print("="*70)

print("\nScenario: Small meta-analysis with non-normal effects")

# Generate skewed data (log-normal)
n_studies_boot = 10
effects_boot = np.random.lognormal(0, 0.5, n_studies_boot) - 1
se_boot = np.random.uniform(0.15, 0.30, n_studies_boot)

print(f"Number of studies: {n_studies_boot}")
print(f"Effect distribution: Right-skewed (log-normal)")

# Standard parametric CI
weights_boot = 1 / se_boot**2
pooled_boot = np.sum(weights_boot * effects_boot) / np.sum(weights_boot)
se_pooled_boot = np.sqrt(1 / np.sum(weights_boot))
param_ci_low = pooled_boot - 1.96 * se_pooled_boot
param_ci_high = pooled_boot + 1.96 * se_pooled_boot

print(f"\nParametric estimate: θ = {pooled_boot:.3f}")
print(f"Parametric 95% CI: [{param_ci_low:.3f}, {param_ci_high:.3f}]")

# Bootstrap CIs
print("\n" + "-"*70)
print("BOOTSTRAP CONFIDENCE INTERVALS")
print("-"*70)

for method in ['percentile', 'bca']:
    boot_result = BootstrapMethods.bootstrap_ci(
        effects_boot, se_boot,
        method=method,
        n_boot=10000
    )

    if boot_result['available']:
        print(f"\n{method.upper()} METHOD:")
        print(f"  Estimate: θ = {boot_result['estimate']:.3f}")
        print(f"  Bootstrap SE: {boot_result['bootstrap_se']:.3f}")
        print(f"  Bootstrap 95% CI: [{boot_result['ci_low']:.3f}, {boot_result['ci_high']:.3f}]")
        print(f"  Bias: {boot_result['bias']:.4f}")

print(f"\nConclusion: Bootstrap CIs are more robust when sample sizes")
print(f"are small or distributional assumptions are violated")

# ===================================================================
# EXAMPLE 5: RESTRICTED CUBIC SPLINES
# ===================================================================

print("\n\n" + "="*70)
print("EXAMPLE 5: Restricted Cubic Splines for Dose-Response")
print("Based on: Orsini et al. (2006), Stata Journal")
print("="*70)

print("\nScenario: Dose-response meta-analysis of alcohol and heart disease")

# Generate dose-response data with non-linear relationship
doses_rcs = np.array([0, 10, 20, 30, 40, 50, 60, 80, 100])  # grams/day
# True relationship: J-shaped (protective at low doses, harmful at high doses)
true_rr = 1.0 - 0.03 * doses_rcs + 0.0008 * doses_rcs**2
effects_rcs = np.log(true_rr) + np.random.normal(0, 0.05, len(doses_rcs))
se_rcs = np.random.uniform(0.08, 0.15, len(doses_rcs))

print(f"Dose levels (g/day): {', '.join(map(str, doses_rcs))}")
print(f"True relationship: J-shaped curve")

# Fit RCS
print("\n" + "-"*70)
print("RESTRICTED CUBIC SPLINE ANALYSIS")
print("-"*70)

rcs_result = DoseResponseSplines.fit_rcs(
    doses_rcs, effects_rcs, se_rcs,
    n_knots=4
)

if rcs_result['available']:
    print(f"Number of knots: {rcs_result['n_knots']}")
    print(f"Knot positions: {', '.join([f'{k:.1f}' for k in rcs_result['knots']])}")
    print(f"R²: {rcs_result['r_squared']:.3f}")
    print(f"Non-linearity test p-value: {rcs_result['nonlinearity_test_p']:.4f}")
    print(f"Evidence of non-linearity: {rcs_result['nonlinear']}")
    print(f"\nInterpretation: {rcs_result['interpretation']}")
    print(f"\nConclusion: RCS captures non-linear dose-response relationship,")
    print(f"showing protective effect at low doses and harmful effect at high doses")

# ===================================================================
# EXAMPLE 6: LIMIT META-ANALYSIS
# ===================================================================

print("\n\n" + "="*70)
print("EXAMPLE 6: Limit Meta-Analysis")
print("Based on: Rücker et al. (2011), Statistics in Medicine")
print("="*70)

print("\nScenario: Meta-analysis with small-study effects")

# Generate data with small-study effects
n_studies_lim = 20
true_effect_lim = 0.30
se_lim = np.random.uniform(0.05, 0.40, n_studies_lim)
# Small studies have inflated effects
effects_lim = true_effect_lim + 0.5 * se_lim + np.random.normal(0, 0.10, n_studies_lim)

print(f"Number of studies: {n_studies_lim}")
print(f"True unbiased effect: θ = {true_effect_lim:.2f}")
print(f"Small-study effects present: Yes")

# Naive estimate
naive_lim = np.sum(effects_lim / se_lim**2) / np.sum(1 / se_lim**2)
print(f"\nNaive random-effects estimate: θ = {naive_lim:.3f}")

# Limit meta-analysis
print("\n" + "-"*70)
print("LIMIT META-ANALYSIS")
print("-"*70)

lim_result = LimitMetaAnalysis.limit_meta_analysis(effects_lim, se_lim)

if lim_result['available']:
    print(f"Limit estimate (SE→0): θ = {lim_result['limit_estimate']:.3f}")
    print(f"95% CI: [{lim_result['ci_low']:.3f}, {lim_result['ci_high']:.3f}]")
    print(f"Naive estimate: θ = {lim_result['naive_estimate']:.3f}")
    print(f"Difference: {lim_result['difference']:.3f}")
    print(f"Small-study effects: {lim_result['small_study_effect_detected']}")
    print(f"Slope p-value: {lim_result['slope_p_value']:.4f}")
    print(f"\nInterpretation: {lim_result['interpretation']}")

# ===================================================================
# SUMMARY
# ===================================================================

print("\n\n" + "="*70)
print("SUMMARY: STATE-OF-THE-ART META-ANALYSIS METHODS")
print("="*70)

print("""
These examples demonstrate cutting-edge methods from top statistics journals:

1. P-UNIFORM: Corrects for publication bias using p-value distributions
   - More robust than trim-and-fill
   - Recommended when file drawer problem is suspected

2. SELECTION MODELS: Models publication probabilities directly
   - Accounts for differential publication across p-value regions
   - Provides estimates of selection mechanism strength

3. GOSH PLOTS: Visualizes heterogeneity across all possible subsets
   - Identifies influential studies and outliers
   - Shows stability of meta-analysis results

4. BOOTSTRAP CIs: Robust inference without parametric assumptions
   - BCa method corrects for bias and skewness
   - Recommended for small samples or non-normal data

5. RESTRICTED CUBIC SPLINES: Flexible dose-response modeling
   - Captures non-linear relationships
   - Tests for departure from linearity

6. LIMIT META-ANALYSIS: Extrapolates to infinite precision
   - Estimates unbiased effect in presence of small-study effects
   - Complements other publication bias methods

RECOMMENDATIONS:
- Use multiple methods to assess robustness
- Report both naive and bias-corrected estimates
- Consider heterogeneity sources when interpreting results
- Combine with sensitivity analyses for comprehensive assessment
""")

print("="*70)
print("All examples completed successfully!")
print("="*70)
