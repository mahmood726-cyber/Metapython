"""
R Shiny Integration Module

Seamlessly integrates MetaPython with R Shiny applications for:
- Interactive web-based meta-analysis
- Access to R's comprehensive statistical ecosystem
- Bidirectional Python ↔ R data exchange
- Embedding Shiny apps in Python workflows
"""

from metapython.r_integration.rpy2_bridge import (
    RPythonBridge,
    convert_to_r,
    convert_from_r,
    run_r_code,
)

from metapython.r_integration.shiny_wrapper import (
    ShinyAppWrapper,
    launch_shiny_app,
    embed_shiny_dashboard,
)

from metapython.r_integration.r_metaanalysis import (
    r_network_meta_analysis,
    r_dose_response,
    r_bayesian_nma,
    r_multilevel_meta,
    r_diagnostic_accuracy,
)

__all__ = [
    # Core bridge
    'RPythonBridge',
    'convert_to_r',
    'convert_from_r',
    'run_r_code',

    # Shiny integration
    'ShinyAppWrapper',
    'launch_shiny_app',
    'embed_shiny_dashboard',

    # R meta-analysis functions
    'r_network_meta_analysis',
    'r_dose_response',
    'r_bayesian_nma',
    'r_multilevel_meta',
    'r_diagnostic_accuracy',
]
