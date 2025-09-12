"""
Metapython Package Structure v0.7.0 - Phase 10 Implementation
"""

# Import all core functionality from metapython.core
from metapython.core import *

# Import plugin system components
try:
    from metapython.plugins.api import *
    from metapython.plugins.base import *
    from metapython.plugins.examples import *
except ImportError:
    pass

# Import advanced methods  
try:
    from metapython.advanced import *
except ImportError:
    pass

# Import benchmarking
try:
    from metapython.benchmarks import *
except ImportError:
    pass

# Import data integrations
try:
    from metapython.integrations import *
except ImportError:
    pass

# Import reproducibility
try:
    from metapython.reproducibility import *
except ImportError:
    pass

# Update version to Phase 10
__version__ = "0.7.0"
__plugin_api_version__ = "1.0.0"

# Convenience functions for Phase 10 features
def get_available_features():
    """Get list of available Phase 10 features"""
    features = {}
    
    try:
        import metapython.plugins
        features['plugins'] = True
    except ImportError:
        features['plugins'] = False
    
    try:
        import metapython.advanced
        features['advanced'] = True
    except ImportError:
        features['advanced'] = False
    
    try:
        import metapython.benchmarks
        features['benchmarks'] = True
    except ImportError:
        features['benchmarks'] = False
    
    try:
        import metapython.integrations
        features['integrations'] = True
    except ImportError:
        features['integrations'] = False
    
    try:
        import metapython.reproducibility
        features['reproducibility'] = True
    except ImportError:
        features['reproducibility'] = False
    
    return features

def create_plugin_manager():
    """Create and return a plugin manager instance"""
    try:
        from metapython.plugins import PluginManager
        return PluginManager()
    except ImportError:
        raise ImportError("Plugin system not available. Install with: pip install metapython[all]")

def create_benchmark_runner():
    """Create and return a benchmark runner instance"""
    try:
        from metapython.benchmarks import BenchmarkRunner
        return BenchmarkRunner()
    except ImportError:
        raise ImportError("Benchmarking not available. Install with: pip install metapython[performance]")

def create_integration_manager():
    """Create and return an integration manager instance"""
    try:
        from metapython.integrations import IntegrationManager
        return IntegrationManager()
    except ImportError:
        raise ImportError("Data integrations not available. Install with: pip install metapython[integrations]")

def create_reproducibility_manager():
    """Create and return a reproducibility manager instance"""
    try:
        from metapython.reproducibility import ReproducibilityManager
        return ReproducibilityManager()
    except ImportError:
        raise ImportError("Reproducibility features not available. Install with: pip install metapython[reproducibility]")