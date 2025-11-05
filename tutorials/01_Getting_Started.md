# MetaPython Tutorial: Getting Started

## Installation

### Basic Installation

Install MetaPython with core dependencies:

```bash
pip install metapython
```

### Full Installation

For all features including Bayesian methods and interactive visualizations:

```bash
pip install metapython[full]
```

### Development Installation

For development with testing and documentation tools:

```bash
git clone https://github.com/mahmood726-cyber/Metapython.git
cd Metapython
pip install -e ".[dev]"
```

## Quick Start

### Basic Meta-Analysis

```python
import numpy as np
from metapython.core import calculate_pooled_estimate, calculate_confidence_interval

# Example data: Effect sizes and standard errors
effects = np.array([0.25, 0.35, 0.20, 0.40, 0.30])
se = np.array([0.10, 0.12, 0.08, 0.15, 0.11])

# Calculate pooled estimate
variances = se ** 2
pooled_effect, pooled_se = calculate_pooled_estimate(
    effects, variances, use_variances=True
)

# Calculate 95% CI
ci_low, ci_high = calculate_confidence_interval(pooled_effect, pooled_se)

print(f"Pooled effect: {pooled_effect:.3f}")
print(f"95% CI: [{ci_low:.3f}, {ci_high:.3f}]")
```

### Using Advanced Journal Methods

```python
from advanced_methods import PUniformMethods, GOSHAnalysis
from advanced_methods_part2 import BootstrapMethods

# P-uniform for publication bias
punif_result = PUniformMethods.p_uniform(effects, se)
print(f"P-uniform estimate: {punif_result['estimate']:.3f}")
print(f"Publication bias detected: {punif_result['publication_bias_detected']}")

# Bootstrap confidence intervals
boot_result = BootstrapMethods.bootstrap_ci(
    effects, se, method='bca', n_boot=10000
)
print(f"BCa 95% CI: [{boot_result['ci_low']:.3f}, {boot_result['ci_high']:.3f}]")

# GOSH analysis
study_labels = np.array([f"Study {i+1}" for i in range(len(effects))])
gosh_result = GOSHAnalysis.gosh_analysis(
    effects, se, study_labels, n_samples=5000
)
print(f"Outlier studies: {gosh_result['outlier_studies']}")
```

### Visualization

```python
from metapython.visualization import forest_plot, funnel_plot
import matplotlib.pyplot as plt

# Create forest plot
fig1 = forest_plot(
    effects, se, study_labels,
    pooled_effect=pooled_effect,
    pooled_se=pooled_se,
    title="Effect of Intervention on Outcome"
)
plt.savefig("forest_plot.png", dpi=300)

# Create funnel plot
fig2 = funnel_plot(
    effects, se,
    pooled_effect=pooled_effect,
    show_contours=True
)
plt.savefig("funnel_plot.png", dpi=300)
```

### Interactive Visualizations (requires plotly)

```python
from metapython.visualization import interactive_forest_plot

# Create interactive forest plot
fig = interactive_forest_plot(
    effects, se, study_labels,
    pooled_effect=pooled_effect,
    pooled_se=pooled_se
)
fig.show()  # Opens in browser
# fig.write_html("forest_plot.html")  # Save to file
```

### Bayesian Meta-Analysis (requires PyMC)

```python
from metapython.bayesian import BayesianMetaAnalysis

# Initialize and fit Bayesian model
bma = BayesianMetaAnalysis(effects, se, study_labels)
bma.fit(chains=4, draws=2000)

# Get results
results = bma.get_results()
print(f"Posterior mean: {results['mu_mean']:.3f}")
print(f"95% HDI: [{results['mu_hdi_low']:.3f}, {results['mu_hdi_high']:.3f}]")
print(f"Tau (heterogeneity): {results['tau_mean']:.3f}")
print(f"I²: {results['I2_mean']:.1%}")

# Plot posterior
bma.plot_posterior()
bma.plot_forest()
```

### Data Import

```python
from metapython.io import read_csv, read_excel

# Read from CSV
data_csv = read_csv(
    'meta_data.csv',
    effect_col='SMD',
    se_col='SE',
    study_col='Author'
)

# Read from Excel
data_excel = read_excel(
    'meta_data.xlsx',
    sheet_name='Sheet1',
    effect_col='effect_size',
    ci_low_col='ci_lower',
    ci_high_col='ci_upper'
)

# Extract arrays for analysis
effects = data_csv['effect'].values
se = data_csv['se'].values
studies = data_csv['study'].values
```

## Next Steps

- See `02_Advanced_Methods.md` for cutting-edge journal methods
- See `03_Bayesian_Analysis.md` for comprehensive Bayesian meta-analysis
- See `04_Network_Meta_Analysis.md` for network meta-analysis
- Check `journal_examples.py` for worked examples from top journals

## Getting Help

- Documentation: https://github.com/mahmood726-cyber/Metapython
- Issues: https://github.com/mahmood726-cyber/Metapython/issues
- Advanced Methods Guide: See `ADVANCED_METHODS_GUIDE.md`
- Improvements Summary: See `IMPROVEMENTS_SUMMARY.md`
