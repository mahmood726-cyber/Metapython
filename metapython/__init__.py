"""
MetaPython - Professional Meta-Analysis Platform
=================================================

A comprehensive, production-ready meta-analysis library implementing
cutting-edge methods from top statistics journals (2023-2024).

Key Features:
- Fixed and random effects meta-analysis
- Llama 3 integration for AI-powered analysis
- 500+ rules engine for validation
- 10,000+ scenario testing framework
- Advanced methods from top journals (2023-2024)
- Publication-quality visualizations
- Automated PRISMA-compliant reporting
- Comprehensive permutation testing (10,000+ tests)
- Publication bias assessment (P-uniform, Selection models, Limit meta-analysis)
- Network meta-analysis
- Bayesian meta-analysis with PyMC
- Interactive dashboards
- Advanced diagnostics and robust methods
- R/Shiny integration (8 pre-configured apps)
- Machine learning predictions
- FastAPI REST API with WebSocket
- React modern web interface
- Grafana real-time dashboards

Version: 0.7.0
License: MIT
"""

__version__ = '0.7.0'
__author__ = 'MetaPython Development Team'
__license__ = 'MIT'

# Core imports
from metapython.core.config import (
    DEFAULT_ALPHA,
    MIN_STUDIES_DEFAULT,
    HAS_PYMC,
    HAS_STATSMODELS,
)

from metapython.core.models import (
    FixedEffectsResults,
    RandomEffectsResults,
    HeterogeneityResults,
    PredictionIntervalResults,
    BiasTestResults,
    MetaAnalysisResults,
    UnifiedMetaConfig,
    UnifiedMetaError,
    InsufficientDataError,
    NumericalInstabilityError,
)

from metapython.core.utils import (
    calculate_pooled_estimate,
    calculate_confidence_interval,
    validate_inputs,
    safe_solve,
    safe_matrix_inverse,
)

# Import advanced methods from legacy files
try:
    from advanced_methods import PUniformMethods, SelectionModels, LimitMetaAnalysis
    from advanced_methods_part2 import GOSHAnalysis, BootstrapMethods, DoseResponseSplines
    HAS_ADVANCED_METHODS = True
except ImportError:
    HAS_ADVANCED_METHODS = False

__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__license__',

    # Configuration
    'DEFAULT_ALPHA',
    'MIN_STUDIES_DEFAULT',
    'HAS_PYMC',
    'HAS_STATSMODELS',
    'UnifiedMetaConfig',

    # Models
    'FixedEffectsResults',
    'RandomEffectsResults',
    'HeterogeneityResults',
    'PredictionIntervalResults',
    'BiasTestResults',
    'MetaAnalysisResults',

    # Exceptions
    'UnifiedMetaError',
    'InsufficientDataError',
    'NumericalInstabilityError',

    # Utilities
    'calculate_pooled_estimate',
    'calculate_confidence_interval',
    'validate_inputs',
    'safe_solve',
    'safe_matrix_inverse',
]

# Advanced methods
if HAS_ADVANCED_METHODS:
    __all__.extend([
        'PUniformMethods',
        'SelectionModels',
        'LimitMetaAnalysis',
        'GOSHAnalysis',
        'BootstrapMethods',
        'DoseResponseSplines',
    ])

# New advanced methods from 2023-2024 journals
try:
    from metapython.advanced_methods import (
        robust_variance_meta_analysis,
        prevalence_meta_analysis,
        hksj_improved,
        permutation_meta_analysis,
        empirical_bayes_meta_analysis,
        advanced_influence_diagnostics,
        robust_meta_regression,
    )
    HAS_JOURNAL_METHODS = True
except ImportError:
    HAS_JOURNAL_METHODS = False

# Enhanced visualizations
try:
    from metapython.enhanced_viz import (
        advanced_forest_plot,
        cumulative_forest_plot,
        radial_plot,
        create_meta_analysis_dashboard,
        interactive_sensitivity_dashboard,
        network_meta_3d,
    )
    HAS_ENHANCED_VIZ = True
except ImportError:
    HAS_ENHANCED_VIZ = False

# LLM integration
try:
    from metapython.llm import LlamaMetaAnalyst
    HAS_LLM_INTEGRATION = True
except ImportError:
    HAS_LLM_INTEGRATION = False

# Rules engine
try:
    from metapython.rules import RulesEngine
    HAS_RULES_ENGINE = True
except ImportError:
    HAS_RULES_ENGINE = False

# Decision support
try:
    from metapython.decision_support import MetaAnalysisAdvisor
    HAS_DECISION_SUPPORT = True
except ImportError:
    HAS_DECISION_SUPPORT = False

# Automated reporting
try:
    from metapython.reporting import (
        MethodsSectionGenerator,
        ResultsSectionGenerator,
        generate_methods_section,
        generate_results_section,
    )
    HAS_REPORTING = True
except ImportError:
    HAS_REPORTING = False

# Permutation framework
try:
    from metapython.permutations import (
        PermutationEngine,
        run_permutation_test,
        run_bootstrap_test,
    )
    HAS_PERMUTATIONS = True
except ImportError:
    HAS_PERMUTATIONS = False

# Update __all__ with new exports
if HAS_JOURNAL_METHODS:
    __all__.extend([
        'robust_variance_meta_analysis',
        'prevalence_meta_analysis',
        'hksj_improved',
        'permutation_meta_analysis',
        'empirical_bayes_meta_analysis',
        'advanced_influence_diagnostics',
        'robust_meta_regression',
    ])

if HAS_ENHANCED_VIZ:
    __all__.extend([
        'advanced_forest_plot',
        'cumulative_forest_plot',
        'radial_plot',
        'create_meta_analysis_dashboard',
        'interactive_sensitivity_dashboard',
        'network_meta_3d',
    ])

if HAS_LLM_INTEGRATION:
    __all__.extend(['LlamaMetaAnalyst'])

if HAS_RULES_ENGINE:
    __all__.extend(['RulesEngine'])

if HAS_DECISION_SUPPORT:
    __all__.extend(['MetaAnalysisAdvisor'])

if HAS_REPORTING:
    __all__.extend([
        'MethodsSectionGenerator',
        'ResultsSectionGenerator',
        'generate_methods_section',
        'generate_results_section',
    ])

if HAS_PERMUTATIONS:
    __all__.extend([
        'PermutationEngine',
        'run_permutation_test',
        'run_bootstrap_test',
    ])
