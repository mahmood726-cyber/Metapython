# Migration Guide: Metapython v0.7 → v0.8

This guide helps you migrate from Metapython v0.7 to v0.8, which introduces API stabilization, new observability features, distributed computing capabilities, and the plugin marketplace.

## Table of Contents

- [Breaking Changes](#breaking-changes)
- [New Features](#new-features)
- [API Stability](#api-stability)
- [Deprecations](#deprecations)
- [Installation Changes](#installation-changes)
- [Migration Examples](#migration-examples)
- [Troubleshooting](#troubleshooting)

## Breaking Changes

### None! 

Metapython v0.8 maintains **100% backward compatibility** with v0.7. All existing code should continue to work without modification.

## New Features

### 1. API Stability Framework

```python
import metapython

# Check API stability
print(metapython.__api_version__)  # "1.0.0"
print(metapython.API_STABILITY_GUARANTEE)

# All public APIs are now marked as stable
@metapython.stable_api(since_version="0.8.0")
def my_analysis_function():
    pass
```

### 2. Structured Logging and Telemetry

```python
# Enable structured logging (opt-in)
import os
os.environ["METAPYTHON_TELEMETRY"] = "true"

# Get logger instance
logger = metapython.get_logger()

# Track analysis health
health = metapython.get_run_health()
health.start_run()
# ... perform analysis ...
health.complete_run(success=True)
```

### 3. Distributed Computing

```python
# Check available executors
compute_manager = metapython.get_compute_manager()
available = compute_manager.get_available_executors()
print(f"Available: {available}")  # ['dask', 'ray', 'jax']

# Use JAX acceleration (if available)
jax_accel = metapython.JAXAccelerator()
if jax_accel.is_available():
    result = jax_accel.accelerated_bayesian_fit(data)
```

### 4. Plugin Marketplace

```python
# Search plugins
registry = metapython.get_marketplace_registry()
plugins = registry.search_plugins(query="bayesian", min_trust_score=0.7)

# CLI interface
cli = metapython.get_marketplace_cli()
cli.search("meta-analysis")
cli.install("advanced-plots")
```

### 5. Internationalization

```python
# Set locale
metapython.set_locale("es")  # Spanish

# Get translated text
message = metapython._("analysis.starting")
print(message)  # "Iniciando meta-análisis..."

# Check text direction
i18n = metapython.get_i18n_manager()
is_rtl = i18n.is_rtl("ar")  # True for Arabic
```

### 6. Accessibility

```python
# Enable accessibility features
a11y = metapython.get_accessibility_helper()
a11y.enable_high_contrast()
a11y.enable_screen_reader_mode()

# Format output for accessibility
formatted = a11y.format_cli_output("Analysis complete", level="success")
print(formatted)  # "[SUCCESS] Analysis complete"
```

## API Stability

### Stable APIs (Guaranteed)

The following APIs are now **stable** and covered by our compatibility guarantee:

- Core meta-analysis classes: `UnifiedMetaAnalysis`, `TauSquaredEstimators`
- Analysis functions: `quick_meta()`, `meta_from_summary_stats()`
- Configuration: `UnifiedMetaConfig`
- Main utilities and helpers

### Experimental APIs (May Change)

- Distributed computing interfaces (marked as optional extras)
- Plugin marketplace internal APIs
- Telemetry collection mechanisms

## Deprecations

### None in v0.8

No APIs are deprecated in v0.8. Future deprecations will follow this process:

1. **Minimum 2 minor versions notice** before removal
2. **Deprecation warnings** with auto-fix suggestions
3. **Migration codemods** for complex changes
4. **Comprehensive documentation** of alternatives

Example of future deprecation (not applicable to v0.8):

```python
# If something were deprecated:
@metapython.deprecated(
    deprecated_since="0.9.0", 
    will_remove_in="1.0.0", 
    replacement="new_function"
)
def old_function():
    pass
```

## Installation Changes

### New Optional Extras

```bash
# Distributed computing
pip install metapython[distributed]  # Dask + Ray
pip install metapython[gpu]          # JAX GPU acceleration
pip install metapython[spark]        # Spark integration

# Web interfaces
pip install metapython[web]          # Streamlit + Flask
pip install metapython[cli]          # Enhanced CLI tools

# All features
pip install metapython[all]
```

### Environment Variables

New optional configuration:

```bash
# Telemetry (off by default)
export METAPYTHON_TELEMETRY=true
export METAPYTHON_PRIVACY_MODE=strict

# Accessibility
export METAPYTHON_HIGH_CONTRAST=true
export METAPYTHON_LOCALE=es
```

## Migration Examples

### Basic Analysis (No Changes Required)

```python
# v0.7 code - works unchanged in v0.8
import metapython
import numpy as np

effects = np.array([0.5, 0.3, 0.7])
variances = np.array([0.1, 0.2, 0.15])

result = metapython.quick_meta(effects, variances)
print(f"Pooled effect: {result['pooled_effect']}")
```

### Enhanced with v0.8 Features

```python
# Same analysis with v0.8 enhancements
import metapython
import numpy as np

# Enable logging
logger = metapython.get_logger()
health = metapython.get_run_health()

# Set locale for international users
metapython.set_locale("es")

# Start tracking
health.start_run()
logger.log_analysis_start("fixed-effects", study_count=3)

try:
    effects = np.array([0.5, 0.3, 0.7])
    variances = np.array([0.1, 0.2, 0.15])
    
    # Use distributed computing if available
    compute_manager = metapython.get_compute_manager()
    if "jax" in compute_manager.get_available_executors():
        print("Using JAX acceleration")
    
    result = metapython.quick_meta(effects, variances)
    
    # Log success
    logger.log_analysis_complete("fixed-effects", duration_ms=150, success=True)
    health.complete_run(success=True)
    
    print(f"Pooled effect: {result['pooled_effect']}")
    
except Exception as e:
    logger.log_analysis_complete("fixed-effects", duration_ms=150, success=False)
    health.complete_run(success=False)
    raise
```

### Plugin Development

```python
# Create a plugin for the marketplace
from metapython import PluginMetadata
import datetime

plugin_meta = PluginMetadata(
    name="my-custom-plots",
    version="1.0.0",
    author="Your Name",
    email="you@example.com",
    description="Custom visualization plots for meta-analysis",
    keywords=["visualization", "plots", "meta-analysis"],
    capabilities=["plotting", "export"],
    compatibility={"metapython": ">=0.8.0"},
    license="MIT",
    repository_url="https://github.com/yourusername/my-custom-plots",
    documentation_url="https://my-custom-plots.readthedocs.io"
)

# Register with marketplace
registry = metapython.get_marketplace_registry()
result = registry.register_plugin(plugin_meta)
print(f"Plugin registered: {result}")
```

## Troubleshooting

### Common Issues

#### 1. Optional dependencies not available

```
INFO:metapython:Dask not available - big data processing disabled
```

**Solution**: Install optional extras:
```bash
pip install metapython[distributed]
```

#### 2. Telemetry privacy concerns

**Solution**: Telemetry is **opt-in only** and respects privacy:
```python
# Check telemetry status
logger = metapython.get_logger()
print(f"Telemetry enabled: {logger.telemetry_enabled}")
print(f"Privacy mode: {logger.privacy_mode}")
```

#### 3. Locale not supported

```
WARNING:metapython:Locale 'xyz' not supported. Using default 'en'.
```

**Solution**: Use supported locales:
```python
i18n = metapython.get_i18n_manager()
print(f"Supported: {i18n.supported_locales}")
```

### Performance Considerations

- **JAX acceleration**: Requires CUDA/GPU for significant speedup
- **Distributed computing**: Overhead only beneficial for large datasets (>1000 studies)
- **Telemetry**: Minimal performance impact when enabled

### Getting Help

- **Documentation**: https://metapython.readthedocs.io
- **GitHub Issues**: https://github.com/mahmood726-cyber/Metapython/issues
- **Plugin Marketplace**: Browse verified plugins for extended functionality

## Summary

Metapython v0.8 provides:

✅ **100% backward compatibility** - no code changes required  
✅ **Stable API guarantee** - predictable evolution  
✅ **Rich observability** - structured logging and telemetry  
✅ **Distributed computing** - scale to large datasets  
✅ **Plugin ecosystem** - extend functionality safely  
✅ **Global accessibility** - i18n and a11y support  

Your existing v0.7 code will work unchanged, and you can gradually adopt new features as needed.