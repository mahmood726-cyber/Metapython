# Advanced Meta-Analysis Methods: Comprehensive Guide

## Overview

This guide covers state-of-the-art meta-analysis methods from top statistics journals including:
- Journal of the American Statistical Association (JASA)
- Statistics in Medicine
- BMJ
- Biometrics
- Research Synthesis Methods
- Psychological Methods

All methods are production-ready with complete implementations, examples, and references to original papers.

---

## Table of Contents

1. [P-uniform Methods](#p-uniform-methods)
2. [Selection Models](#selection-models)
3. [Limit Meta-Analysis](#limit-meta-analysis)
4. [GOSH Plots](#gosh-plots)
5. [Bootstrap Methods](#bootstrap-methods)
6. [Restricted Cubic Splines](#restricted-cubic-splines)
7. [Best Practices](#best-practices)
8. [References](#references)

---

## P-uniform Methods

### Background

**Reference:** van Assen, M. A., van Aert, R. C., & Wicherts, J. M. (2015). Meta-analysis using effect size distributions of only statistically significant studies. *Psychological Methods, 20*(3), 293.

P-uniform methods correct for publication bias by testing whether p-values from significant studies are uniformly distributed. If publication bias exists, p-values will be non-uniform.

### When to Use

- ✅ When file drawer problem is suspected
- ✅ When most published studies are significant
- ✅ As complement to other publication bias tests
- ❌ When very few significant studies (<5)
- ❌ When heterogeneity is extreme

### Methods

#### P-uniform (Original)
Uses only statistically significant studies (p < 0.05).

```python
from advanced_methods import PUniformMethods

result = PUniformMethods.p_uniform(effects, se, alpha=0.05)

print(f"P-uniform estimate: {result['estimate']:.3f}")
print(f"95% CI: [{result['ci_low']:.3f}, {result['ci_high']:.3f}]")
print(f"Publication bias detected: {result['publication_bias_detected']}")
```

**Advantages:**
- Simple and intuitive
- Well-validated
- Tests for publication bias

**Limitations:**
- Requires significant studies
- May be less efficient than p-uniform*

#### P-uniform* (Extended)

**Reference:** van Aert, R. C., & van Assen, M. A. (2018). Examining publication bias in meta-analysis in the presence of heterogeneity. *Statistics in Medicine, 37*(25), 3683-3695.

Uses all studies (both significant and non-significant) for greater efficiency.

```python
result = PUniformMethods.p_uniform_star(effects, se, alpha=0.05)

print(f"P-uniform* estimate: {result['estimate']:.3f}")
print(f"Naive estimate: {result['naive_estimate']:.3f}")
print(f"Publication bias test p: {result['publication_bias_test_p']:.4f}")
```

**Advantages:**
- More efficient than original p-uniform
- Uses all available studies
- Less biased with heterogeneity

**Interpretation:**
- Compare p-uniform* estimate with naive estimate
- Large differences suggest publication bias
- Use likelihood ratio test for formal inference

---

## Selection Models

### Background

**Reference:** Vevea, J. L., & Hedges, L. V. (1995). A general linear model for estimating effect size in the presence of publication bias. *Psychometrika, 60*(3), 419-435.

Selection models explicitly model the publication process by assigning different selection probabilities to studies based on their p-values.

### 3-Parameter Selection Model (3PSM)

Divides p-value space into three regions:
1. **Significant (p < 0.05):** Selection weight = 1.0 (reference)
2. **Moderate (0.05 ≤ p < 0.50):** Selection weight = w₁ (estimated)
3. **Non-significant (p ≥ 0.50):** Selection weight = w₂ (estimated)

```python
from advanced_methods import SelectionModels

result = SelectionModels.three_parameter_selection_model(effects, se, alpha=0.05)

print(f"Estimated effect: {result['estimate']:.3f}")
print(f"Heterogeneity (τ): {result['tau']:.3f}")
print(f"Selection weight (moderate): {result['weight_moderate']:.2f}")
print(f"Selection weight (non-sig): {result['weight_high']:.2f}")
print(f"Bias severity: {result['bias_severity']}")
```

### Interpretation

**Selection Weights:**
- **w₁ = 1.0:** No publication bias for moderate p-values
- **w₁ = 0.5:** Moderate p-values 50% as likely to be published
- **w₁ < 0.3:** Severe publication bias

**Bias Severity:**
- **Mild:** w₁ > 0.6
- **Moderate:** 0.3 ≤ w₁ ≤ 0.6
- **Severe:** w₁ < 0.3

### When to Use

- ✅ When publication mechanism is complex
- ✅ For sensitivity analysis
- ✅ When p-value distribution shows clear patterns
- ❌ With very small samples (n < 10)
- ❌ When computational resources are limited

---

## Limit Meta-Analysis

### Background

**Reference:** Rücker, G., Schwarzer, G., Carpenter, J., & Olkin, I. (2011). Why add anything to nothing? The arcsine difference as a measure of treatment effect in meta-analysis with zero cells. *Statistics in Medicine, 30*(7), 721-734.

Limit meta-analysis extrapolates to infinite precision (SE → 0) to obtain an unbiased estimate when small-study effects are present.

### Method

```python
from advanced_methods import LimitMetaAnalysis

result = LimitMetaAnalysis.limit_meta_analysis(effects, se)

print(f"Limit estimate (SE→0): {result['limit_estimate']:.3f}")
print(f"Naive estimate: {result['naive_estimate']:.3f}")
print(f"Difference: {result['difference']:.3f}")
print(f"Small-study effects detected: {result['small_study_effect_detected']}")
```

### Interpretation

**Limit Estimate vs Naive Estimate:**
- **Similar:** No evidence of small-study effects
- **Limit < Naive:** Small studies overestimate effect
- **Limit > Naive:** Small studies underestimate effect (rare)

**Regression Slope:**
- **Positive slope:** Small studies have larger effects
- **Negative slope:** Small studies have smaller effects
- **p < 0.10:** Significant small-study effect

### When to Use

- ✅ When small-study effects suspected
- ✅ As complement to Egger's test
- ✅ For continuous outcomes
- ❌ With few studies (n < 8)
- ❌ When heterogeneity is very high

---

## GOSH Plots

### Background

**Reference:** Olkin, I., Dahabreh, I. J., & Trikalinos, T. A. (2012). GOSH - a graphical display of study heterogeneity. *Research Synthesis Methods, 3*(3), 214-223.

GOSH (Graphical Display of Study Heterogeneity) examines all possible combinations of studies to identify influential subsets and patterns of heterogeneity.

### Method

```python
from advanced_methods_part2 import GOSHAnalysis

result = GOSHAnalysis.gosh_analysis(
    effects, se, study_labels,
    max_subset_size=None,  # Use n-1
    n_samples=10000  # Sample if combinations > 10000
)

print(f"Subsets analyzed: {result['n_subsets']}")
print(f"Effect range: {result['fe_estimate_range']}")
print(f"I² range: {result['I2_range']}")
print(f"Outlier subsets: {result['n_outliers']}")

# Plot results
fig = GOSHAnalysis.plot_gosh(result, figsize=(14, 10))
plt.savefig('gosh_plot.png', dpi=300, bbox_inches='tight')
```

### Interpretation

**GOSH Plot Features:**
1. **Effect vs I² scatter:** Shows relationship between heterogeneity and effect size
2. **Effect distribution:** Histogram of all subset estimates
3. **I² distribution:** Distribution of heterogeneity across subsets
4. **Effect vs subset size:** Shows if effect changes with subset size

**Patterns to Look For:**
- **Bimodal distribution:** Suggests two distinct populations
- **Extreme outliers:** Identifies influential studies
- **Wide range:** Indicates instability
- **Narrow range:** Suggests robust results

### When to Use

- ✅ To identify influential studies
- ✅ To visualize heterogeneity patterns
- ✅ For sensitivity analysis
- ✅ When outliers suspected
- ❌ With very large samples (>30) due to computational cost

---

## Bootstrap Methods

### Background

**Reference:** Davison, A. C., & Hinkley, D. V. (1997). *Bootstrap Methods and Their Application*. Cambridge University Press.

Bootstrap methods provide robust confidence intervals without relying on parametric assumptions, particularly useful for small samples or non-normal distributions.

### Methods

#### Percentile Bootstrap
Simple, intuitive method using percentiles of bootstrap distribution.

```python
from advanced_methods_part2 import BootstrapMethods

result = BootstrapMethods.bootstrap_ci(
    effects, se,
    method='percentile',
    n_boot=10000,
    alpha=0.05
)

print(f"Bootstrap estimate: {result['estimate']:.3f}")
print(f"Bootstrap SE: {result['bootstrap_se']:.3f}")
print(f"95% CI: [{result['ci_low']:.3f}, {result['ci_high']:.3f}]")
print(f"Bias: {result['bias']:.4f}")
```

#### BCa Bootstrap (Bias-Corrected and Accelerated)
More sophisticated method that corrects for bias and skewness.

```python
result = BootstrapMethods.bootstrap_ci(
    effects, se,
    method='bca',
    n_boot=10000,
    alpha=0.05
)
```

**Advantages of BCa:**
- Corrects for bias in bootstrap distribution
- Accounts for skewness
- Better coverage properties
- Recommended for publication

### When to Use

- ✅ Small samples (n < 15)
- ✅ Non-normal effect distributions
- ✅ Extreme heterogeneity
- ✅ When parametric assumptions questionable
- ❌ When computational time is critical

### Interpretation

**Bootstrap Bias:**
- **Small bias (<0.05):** Bootstrap and parametric similar
- **Moderate bias (0.05-0.15):** Bootstrap preferred
- **Large bias (>0.15):** Investigate data quality

**CI Width:**
- BCa CIs may be asymmetric (appropriate for skewed data)
- Compare with parametric CIs for robustness check

---

## Restricted Cubic Splines

### Background

**Reference:** Orsini, N., Bellocco, R., & Greenland, S. (2006). Generalized least squares for trend estimation of summarized dose-response data. *Stata Journal, 6*(1), 40-57.

Restricted cubic splines (RCS) allow flexible modeling of non-linear dose-response relationships while controlling overfitting through knot placement.

### Method

```python
from advanced_methods_part2 import DoseResponseSplines

result = DoseResponseSplines.fit_rcs(
    doses, effects, se,
    n_knots=4  # Typically 3-5 knots
)

print(f"Number of knots: {result['n_knots']}")
print(f"Knot positions: {result['knots']}")
print(f"R²: {result['r_squared']:.3f}")
print(f"Non-linearity p-value: {result['nonlinearity_test_p']:.4f}")
print(f"Non-linear relationship: {result['nonlinear']}")

# Plot smooth curve
plt.figure(figsize=(10, 6))
plt.scatter(doses, effects, s=100, alpha=0.7, label='Observed')
plt.plot(result['smooth_doses'], result['smooth_effects'],
         'r-', linewidth=2, label='RCS fit')
plt.xlabel('Dose')
plt.ylabel('Effect')
plt.legend()
plt.title('Dose-Response Relationship (RCS)')
```

### Knot Selection

**Number of Knots:**
- **3 knots:** Simple curves, minimal overfitting
- **4 knots:** Standard choice, balances flexibility and stability
- **5 knots:** More flexibility, requires more data points

**Knot Placement:**
- Default: Percentiles (5th, 35th, 65th, 95th for 4 knots)
- Alternative: Equal spacing
- Custom: Based on domain knowledge

### Interpretation

**Non-linearity Test:**
- **p < 0.05:** Significant non-linear relationship
- **p ≥ 0.05:** Linear model may be adequate

**Common Patterns:**
- **J-shaped:** Protective at low doses, harmful at high doses
- **U-shaped:** Harmful at extremes, optimal at mid-range
- **Threshold:** No effect below threshold, linear above
- **Plateau:** Increasing effect that levels off

### When to Use

- ✅ Dose-response meta-analysis
- ✅ When non-linearity suspected
- ✅ At least 8-10 dose levels
- ❌ Sparse dose data (<6 levels)
- ❌ When dose is categorical

---

## Best Practices

### Method Selection Guide

| Scenario | Recommended Methods | Why |
|----------|---------------------|-----|
| **Small sample (n<15)** | Bootstrap BCa, P-uniform* | Robust to non-normality |
| **Publication bias suspected** | P-uniform, Selection models, Limit MA | Multiple perspectives |
| **Outliers present** | GOSH, Leave-one-out | Identifies influential studies |
| **Dose-response** | RCS, Meta-regression | Flexible non-linear modeling |
| **High heterogeneity** | GOSH, Subgroup analysis | Explores heterogeneity sources |
| **Sensitivity analysis** | All methods | Comprehensive assessment |

### Reporting Recommendations

**Minimum Reporting:**
1. Naive random-effects estimate (for comparison)
2. At least 2 publication bias methods
3. Sensitivity analysis (leave-one-out or GOSH)
4. Heterogeneity assessment (I², τ², prediction intervals)

**Gold Standard Reporting:**
1. Multiple effect estimates (naive, p-uniform, selection model)
2. Comprehensive publication bias assessment (4+ methods)
3. GOSH plots or similar visualization
4. Bootstrap CIs for robustness
5. Influence diagnostics
6. Pre-specified protocol

### Statistical Reporting

Example comprehensive results section:

```
We conducted a random-effects meta-analysis of 25 studies (naive pooled
effect = 0.45, 95% CI [0.32, 0.58], I² = 68%). Publication bias was assessed
using multiple methods: Egger's test (p = 0.023), p-uniform (corrected
effect = 0.32, 95% CI [0.18, 0.46]), and 3-parameter selection model
(corrected effect = 0.35, τ = 0.15, moderate selection: w = 0.48). GOSH
analysis of 10,000 subsets identified 2 influential studies (Study A and
Study B). Leave-one-out analysis confirmed results were robust (effect range:
0.41-0.48). Bootstrap BCa confidence intervals (10,000 replicates) yielded
similar results [0.31, 0.57], indicating parametric assumptions were
reasonable. Taking publication bias into account, we estimate the true effect
to be approximately 0.32-0.35 (moderate evidence of publication bias).
```

---

## References

### Core References

1. **P-uniform:** van Assen, M. A., van Aert, R. C., & Wicherts, J. M. (2015). Meta-analysis using effect size distributions of only statistically significant studies. *Psychological Methods, 20*(3), 293-309.

2. **P-uniform*:** van Aert, R. C., & van Assen, M. A. (2018). Examining publication bias in meta-analysis in the presence of heterogeneity. *Statistics in Medicine, 37*(25), 3683-3695.

3. **Selection Models:** Vevea, J. L., & Hedges, L. V. (1995). A general linear model for estimating effect size in the presence of publication bias. *Psychometrika, 60*(3), 419-435.

4. **GOSH:** Olkin, I., Dahabreh, I. J., & Trikalinos, T. A. (2012). GOSH - a graphical display of study heterogeneity. *Research Synthesis Methods, 3*(3), 214-223.

5. **Bootstrap:** Davison, A. C., & Hinkley, D. V. (1997). *Bootstrap Methods and Their Application*. Cambridge University Press.

6. **RCS:** Orsini, N., Bellocco, R., & Greenland, S. (2006). Generalized least squares for trend estimation of summarized dose-response data. *Stata Journal, 6*(1), 40-57.

### Additional Resources

7. Hedges, L. V., & Vevea, J. L. (2005). Selection method approaches. In *Publication Bias in Meta-Analysis* (pp. 145-174).

8. IntHout, J., Ioannidis, J. P., & Borm, G. F. (2014). The Hartung-Knapp-Sidik-Jonkman method for random effects meta-analysis is straightforward and considerably outperforms the standard DerSimonian-Laird method. *BMC Medical Research Methodology, 14*(1), 25.

9. Kontopantelis, E., & Reeves, D. (2012). Performance of statistical methods for meta-analysis when true study effects are non-normally distributed. *Statistical Methods in Medical Research, 21*(4), 409-426.

10. Rücker, G., Schwarzer, G., Carpenter, J., & Olkin, I. (2011). Why add anything to nothing? The arcsine difference as a measure of treatment effect in meta-analysis with zero cells. *Statistics in Medicine, 30*(7), 721-734.

---

## Software Implementation

All methods are implemented in pure Python with minimal dependencies:

**Required:**
- NumPy ≥ 1.18
- SciPy ≥ 1.5
- pandas ≥ 1.0
- matplotlib ≥ 3.0

**Optional:**
- statsmodels (for enhanced regression diagnostics)
- seaborn (for enhanced visualizations)

**Installation:**
```bash
pip install numpy scipy pandas matplotlib
pip install statsmodels seaborn  # optional
```

---

## Support & Citation

If you use these methods in published research, please cite:

```bibtex
@software{metapython2024,
  title = {MetaPython: Advanced Meta-Analysis Methods},
  author = {PyMeta-CBAMM Development Team},
  year = {2024},
  version = {0.5.0},
  url = {https://github.com/mahmood726-cyber/Metapython}
}
```

---

**Last Updated:** November 2024
**Version:** 0.5.0
**License:** MIT
