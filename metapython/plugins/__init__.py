"""
Metapython Plugin Ecosystem v0.7
===============================

First-class plugin API for analysis methods, data readers, and report renderers
with versioned entry points and semantic capability flags.

Plugin Discovery Features:
- Local and remote plugin discovery
- Compatibility checks with semantic versioning
- Trust/sandbox levels with security policies
- Signed plugin manifests and provenance tracking

Core Plugin Types:
- AnalysisMethodPlugin: Custom effect-size transformers and meta-analysis methods
- DataReaderPlugin: Dataset readers for various formats and sources
- ReportRendererPlugin: Custom report cards and visualization templates
"""

from .api import (
    PluginAPI,
    PluginManager,
    PluginRegistry,
    PluginManifest,
    PluginCapability,
    TrustLevel,
    SandboxLevel
)

from .discovery import (
    PluginDiscovery,
    LocalPluginDiscovery,
    RemotePluginDiscovery,
    CompatibilityChecker
)

from .base import (
    BasePlugin,
    AnalysisMethodPlugin,
    DataReaderPlugin,
    ReportRendererPlugin
)

from .security import (
    PluginSecurity,
    ManifestSigner,
    PluginValidator,
    SandboxExecutor
)

from .examples import (
    ExampleEffectSizeTransformer,
    ExampleDatasetReader,
    ExampleReportRenderer
)

__all__ = [
    'PluginAPI',
    'PluginManager',
    'PluginRegistry',
    'PluginManifest',
    'PluginCapability',
    'TrustLevel',
    'SandboxLevel',
    'PluginDiscovery',
    'LocalPluginDiscovery',
    'RemotePluginDiscovery',
    'CompatibilityChecker',
    'BasePlugin',
    'AnalysisMethodPlugin',
    'DataReaderPlugin',
    'ReportRendererPlugin',
    'PluginSecurity',
    'ManifestSigner',
    'PluginValidator',
    'SandboxExecutor',
    'ExampleEffectSizeTransformer',
    'ExampleDatasetReader',
    'ExampleReportRenderer'
]

__version__ = "0.7.0"
__plugin_api_version__ = "1.0.0"