# Changelog

All notable changes to Metapython will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.0] - 2024-12-17

### Added

#### 🔒 API Stabilization & Deprecations
- **API Stability Framework**: Stable API guarantee for all public interfaces with `@stable_api` decorator
- **API Version 1.0.0**: Semantic versioning for public APIs with backward compatibility promise
- **Deprecation Framework**: `@deprecated` decorator with auto-fix suggestions and migration guidance
- **Deprecation Policy**: Minimum 2 minor versions notice before removal with comprehensive migration support

#### 📊 Reliability & Observability  
- **Structured Logging**: OpenTelemetry-compatible logging with semantic conventions
- **Opt-in Telemetry**: Privacy-preserving usage analytics with clear controls (`METAPYTHON_TELEMETRY`)
- **Run Health Model**: Analysis state tracking with retry mechanisms and diagnostics
- **Performance Metrics**: Throughput, latency, and memory usage monitoring

#### ⚡ Distributed & Accelerated Compute
- **Dask Executor**: Parallel meta-analysis execution with autoscaling support
- **Ray Executor**: Distributed computing for large-scale analyses  
- **JAX GPU Acceleration**: GPU-accelerated Bayesian fits with graceful CPU fallback
- **Compute Manager**: Auto-selection of optimal execution backend based on data size
- **Spark Integration**: Enhanced patterns for influence diagnostics on big datasets

#### 🛡️ Security & Supply-chain Hardening
- **SBOM Generation**: Software Bill of Materials in SPDX format via GitHub Actions
- **SLSA Provenance**: Level 3 build attestation with Sigstore signing
- **Security Scanning**: SAST/DAST with CodeQL, dependency scanning, and vulnerability reporting
- **Reproducible Builds**: Deterministic wheel generation across platforms and Python versions

#### 🌍 Accessibility & Internationalization
- **Multi-language Support**: i18n framework with EN, ES, ZH, FR, DE, JA locales
- **Right-to-left Layout**: RTL text direction support for Arabic, Hebrew, Persian
- **Screen Reader Compatibility**: Semantic output formatting for assistive technologies
- **High Contrast Mode**: Accessibility-enhanced CLI output with color alternatives
- **Keyboard Navigation**: Full keyboard shortcuts for CLI interaction

#### 🔌 Plugin Marketplace (GA)
- **Plugin Registry**: Centralized discovery with metadata and capability indexing
- **Publisher Verification**: Trust scoring system with domain and repository validation
- **Search & Discovery**: Advanced filtering by capabilities, compatibility, and quality signals
- **CLI Integration**: `metapython search/install` commands with caching and security checks
- **Abuse Reporting**: Community governance with publisher accountability

#### 🚀 Release Automation & Documentation
- **Automated Versioning**: Conventional commits with semantic release generation
- **Packaging Matrix**: Multi-platform wheels for Python 3.9-3.12 across OS variants
- **GitHub Actions**: Complete CI/CD with testing, security scanning, and deployment
- **Homebrew Integration**: Automated formula updates for macOS package manager
- **Docker Images**: Multi-architecture containers with security hardening

### Changed
- **Version**: Updated from 0.4.0 to 0.8.0 with API stability guarantees
- **Documentation**: Comprehensive rewrite with migration guides and API reference
- **Export Structure**: Organized `__all__` exports by feature category with stability annotations
- **Error Handling**: Enhanced with structured logging and health tracking integration

### Deprecated
- **None**: First stable release with no deprecated APIs (future deprecations will follow 2-version policy)

### Security
- **Supply Chain**: SLSA Level 3 attestation with reproducible builds
- **Dependencies**: Automated vulnerability scanning with safety, bandit, and pip-audit
- **Code Quality**: Enhanced SAST with security-focused CodeQL queries
- **Container Security**: Non-root user, minimal attack surface, health checks

### Performance
- **Optional Dependencies**: Modular architecture with graceful fallbacks
- **Distributed Computing**: Automatic scaling for large datasets
- **GPU Acceleration**: JAX-based Bayesian methods when hardware available
- **Memory Efficiency**: Optimized for large-scale meta-analyses

## [0.4.0] - 2024-09-12 (Previous Release)

### Added
- Network meta-analysis inconsistency analysis (DBT, node-splitting)
- Arm-based GLMMs and sparse-event methods (Peto OR, Mantel-Haenszel)
- Complete diagnostic test accuracy meta-analysis (HSROC, Fagan nomogram)
- Advanced multivariate structures (unstructured/factor-analytic covariance)
- CLI and pipeline automation (meta_cli, meta_pipeline.yaml)
- Performance optimizations (Numba hot paths, memory-efficient iterators)

## Migration Guide

For upgrading from v0.7 to v0.8, see [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md).

## API Stability

See [API_DEPRECATION_MATRIX.md](API_DEPRECATION_MATRIX.md) for detailed API stability commitments and deprecation tracking.