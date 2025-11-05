"""
Comprehensive Permutation Framework

Permutation-based inference with 10,000+ tests for all meta-analysis methods:
- Standard permutation tests
- Bootstrap resampling
- Monte Carlo simulations
- Randomization tests
- Exact permutation distributions
"""

from metapython.permutations.permutation_engine import (
    PermutationEngine,
    run_permutation_test,
    run_bootstrap_test,
)

from metapython.permutations.permutation_tests import (
    permutation_meta_analysis,
    permutation_heterogeneity_test,
    permutation_publication_bias_test,
    permutation_subgroup_test,
    permutation_meta_regression,
)

__all__ = [
    # Engine
    'PermutationEngine',
    'run_permutation_test',
    'run_bootstrap_test',

    # Tests
    'permutation_meta_analysis',
    'permutation_heterogeneity_test',
    'permutation_publication_bias_test',
    'permutation_subgroup_test',
    'permutation_meta_regression',
]
