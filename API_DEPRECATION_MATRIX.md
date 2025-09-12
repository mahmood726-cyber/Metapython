# API Deprecation Matrix

This document tracks API changes, deprecations, and stability commitments for Metapython.

## Stability Guarantee

**Effective from v0.8.0**, Metapython provides the following stability guarantees:

- **Public APIs**: Marked with `@stable_api` decorator, guaranteed stable within major version
- **Deprecation Policy**: Minimum 2 minor versions notice before removal
- **Breaking Changes**: Only in major version bumps (1.0.0, 2.0.0, etc.)
- **Backward Compatibility**: Maintained within major version series

## API Stability Matrix

| Component | Status | Since Version | Stability Level | Notes |
|-----------|--------|---------------|-----------------|-------|
| `UnifiedMetaAnalysis` | ✅ Stable | 0.8.0 | Public API | Core meta-analysis class |
| `TauSquaredEstimators` | ✅ Stable | 0.8.0 | Public API | Heterogeneity estimation |
| `quick_meta()` | ✅ Stable | 0.8.0 | Public API | Convenience function |
| `meta_from_summary_stats()` | ✅ Stable | 0.8.0 | Public API | Summary statistics input |
| `UnifiedMetaConfig` | ✅ Stable | 0.8.0 | Public API | Configuration management |
| `EnhancedDiagnosticTestAccuracy` | ✅ Stable | 0.8.0 | Public API | DTA meta-analysis |
| `NetworkMetaRankings` | ✅ Stable | 0.8.0 | Public API | Network meta-analysis |
| `SparseEventMethods` | ✅ Stable | 0.8.0 | Public API | Rare events analysis |
| `MetaCLI` | ✅ Stable | 0.8.0 | Public API | Command-line interface |
| | | | | |
| **Phase 12 Additions (v0.8.0)** | | | | |
| `StructuredLogger` | ✅ Stable | 0.8.0 | Public API | Observability framework |
| `RunHealthModel` | ✅ Stable | 0.8.0 | Public API | Health tracking |
| `PluginRegistry` | ✅ Stable | 0.8.0 | Public API | Plugin marketplace |
| `I18nManager` | ✅ Stable | 0.8.0 | Public API | Internationalization |
| `AccessibilityHelper` | ✅ Stable | 0.8.0 | Public API | Accessibility support |
| | | | | |
| **Experimental Features** | | | | |
| `DistributedExecutor` | ⚠️ Experimental | 0.8.0 | Optional Extra | May change in minor versions |
| `DaskExecutor` | ⚠️ Experimental | 0.8.0 | Optional Extra | Implementation may evolve |
| `RayExecutor` | ⚠️ Experimental | 0.8.0 | Optional Extra | Implementation may evolve |
| `JAXAccelerator` | ⚠️ Experimental | 0.8.0 | Optional Extra | GPU acceleration interface |

## Deprecation History

### v0.8.0 (Current)
- **No deprecations** - First stable API release
- All existing APIs from v0.4-v0.7 are now stable

### Future Planned Deprecations

*None currently planned. This section will be updated when deprecations are announced.*

## Deprecation Process

When an API needs to be deprecated, we follow this process:

### 1. Announcement Phase
- Deprecation announced **2 minor versions** before removal
- Warning added to documentation
- GitHub issue created for tracking

### 2. Warning Phase  
- `@deprecated` decorator added to affected APIs
- Runtime warnings issued when deprecated APIs are used
- Auto-fix suggestions provided where possible

### 3. Migration Support Phase
- Migration guide updated with examples
- Codemods provided for complex migrations
- Community support via GitHub discussions

### 4. Removal Phase
- Deprecated APIs removed in next major version
- Clear error messages for removed APIs

## Example Deprecation Workflow

```python
# Phase 1: Announcement (v0.9.0)
# Documentation updated, no code changes

# Phase 2: Warning (v1.0.0) 
@deprecated(
    deprecated_since="1.0.0",
    will_remove_in="2.0.0", 
    replacement="new_improved_function"
)
def old_function():
    """Old function - use new_improved_function instead."""
    pass

# Phase 3: Migration (v1.1.0-v1.x.x)
# Migration guide, codemods, community support

# Phase 4: Removal (v2.0.0)
# Function removed, ImportError with helpful message
```

## Version Compatibility Matrix

| Metapython Version | Python Support | Key Features | Status |
|-------------------|----------------|--------------|--------|
| 0.8.x | 3.9, 3.10, 3.11, 3.12 | API stabilization, observability, marketplace | ✅ Current |
| 0.7.x | 3.8, 3.9, 3.10, 3.11 | Network analysis, multivariate | 🔒 Maintenance only |
| 0.6.x | 3.8, 3.9, 3.10 | Enhanced diagnostics | ❌ End of life |
| 0.5.x and earlier | 3.7+ | Basic functionality | ❌ End of life |

## API Categories

### Stable Public APIs ✅
- **Guaranteed stability** within major version
- **Comprehensive documentation** 
- **Unit test coverage** >95%
- **Semantic versioning** for any changes

### Experimental APIs ⚠️
- **May change** in minor versions
- **Behind optional extras** or feature flags
- **Clearly marked** in documentation
- **Feedback welcome** for improvement

### Internal APIs 🔒
- **No stability guarantee**
- **Subject to change** without notice
- **Not covered** by deprecation policy
- **Use at your own risk**

## Breaking Change Policy

Breaking changes are **only allowed** in major version releases (1.0.0, 2.0.0, etc.):

### Allowed in Major Versions
- Remove deprecated APIs
- Change function signatures
- Modify return value formats
- Update default behaviors

### Never Allowed
- Silent behavior changes
- Data loss or corruption
- Security regressions
- Performance degradation >50%

## Feedback and Contributions

### Report API Issues
- **GitHub Issues**: For bugs in stable APIs
- **Discussions**: For design feedback
- **Security Issues**: security@metapython.example.com

### Suggest Improvements
- **Feature Requests**: Via GitHub issues
- **API Design**: Via GitHub discussions  
- **Breaking Changes**: Require RFC process

## Commitment Timeline

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| v0.8.0 | ✅ Complete | API stabilization, Phase 12 features |
| v0.9.0 | Q2 2024 | Enhanced plugin ecosystem |
| v1.0.0 | Q4 2024 | Full API stability, LTS support |
| v1.1.0+ | Ongoing | Feature additions, no breaking changes |
| v2.0.0 | 2026+ | Next major evolution (if needed) |

## Contact

For questions about API stability or deprecation policies:

- **Documentation**: https://metapython.readthedocs.io/en/latest/api-stability/
- **GitHub**: https://github.com/mahmood726-cyber/Metapython/issues
- **Email**: pymeta-cbamm@example.com