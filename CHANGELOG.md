# Changelog

All notable changes to Metapython will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-01-11 - Phase 3 Release

### Added

#### Core Features
- **meta_auto_report()** - One-liner automated meta-analysis with comprehensive diagnostics and reporting
- **Enhanced dataclasses** - Structured inputs/outputs (EffectSizeInput, NetworkArm, BayesianResults, etc.)
- **Comprehensive type hints** - Full typing support across public APIs

#### Bayesian Analysis Engines (Optional)
- **Enhanced Bayesian methods** with graceful stubs when PyMC unavailable
- **bayesian_meta_regression()** - Meta-regression with moderators
- **bayesian_network_meta_analysis()** - Network meta-analysis with consistency model
- **bayesian_prediction_intervals()** - Posterior predictive intervals
- **bayesian_model_comparison()** - WAIC/LOO model comparison
- **Structured Bayesian results** with posterior summaries, credible intervals, and diagnostics

#### Interactive Visualizations (Optional)
- **create_interactive_forest_plot()** - Plotly/Altair forest plots with Matplotlib fallback
- **create_interactive_funnel_plot()** - Interactive funnel plots with bias assessment
- **create_interactive_network_plot()** - Network geometry visualization
- **create_league_table()** - Interactive league tables for NMA results
- **Graceful degradation** to static plots when interactive libraries unavailable

#### R Parity and Reproducibility
- **generate_r_script()** - Automated R script generation for validation against metafor
- **run_r_validation()** - Execute R scripts via rpy2 with side-by-side comparisons
- **create_reproducibility_report()** - Comprehensive metadata and validation results
- **Deterministic seeding** and run metadata for full reproducibility

#### Performance and Scalability (Optional)
- **enable_numba_acceleration()** - Numba-accelerated tau² solvers and diagnostics
- **enable_dask_processing()** - Dask distributed processing for large datasets
- **optimize_for_large_datasets()** - Automatic optimization detection and setup
- **Parallel bootstrap analysis** with Dask backend

#### Packaging and Distribution
- **setup.py** with proper extras definitions:
  - `[bayes]` - PyMC, ArviZ, CmdStanPy, PyStan
  - `[viz]` - Plotly, Altair, Streamlit, Bokeh  
  - `[speed]` - Numba, Cython, Joblib
  - `[rinterop]` - rpy2, tzlocal
  - `[dask]` - Dask, distributed
  - `[all]` - All optional dependencies
- **Enhanced documentation** with installation instructions and examples

### Enhanced
- **Automated diagnostics** - Comprehensive bias assessment, influence analysis, heterogeneity metrics
- **Report generation** - HTML and Markdown reports with publication-ready formatting
- **Error handling** - Robust fallbacks for missing dependencies
- **API consistency** - Standardized return types and error messages
- **Backward compatibility** - All existing APIs preserved

### Fixed
- **Conflict detection** - Graceful handling when scikit-learn unavailable
- **Forest plot rendering** - Robust cluster visualization with empty data
- **Bias test results** - Proper handling of missing bias assessment data
- **Memory management** - Improved handling of large datasets

### Technical Improvements
- **Modular architecture** - Clean separation of optional components
- **Comprehensive testing** - Validation across dependency combinations  
- **Documentation** - Extensive docstrings and usage examples
- **Performance** - Optimized algorithms with optional acceleration

## [3.0.0] - Previous Release

### Features
- Unified PyMeta-CBAMM suite combining traditional and advanced methods
- Core meta-analysis (fixed/random effects, multiple tau² estimators)
- Comprehensive publication bias assessment
- Network meta-analysis components
- Enhanced diagnostics and influence analysis
- Living meta-analysis with PubMed integration
- Educational simulation tools
- Visualization suite with multiple plot types

---

**Note**: This changelog focuses on the Phase 3 (v0.3.0) enhancements. The previous v3.0.0 represented the unified PyMeta-CBAMM platform. Version 0.3.0 adds optional dependencies, API stabilization, and production-ready features while maintaining full backward compatibility.