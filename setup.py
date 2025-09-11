#!/usr/bin/env python3
"""Setup script for Metapython v0.3.0 - Phase 3 Release"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), 'r', encoding='utf-8') if os.path.exists(
    os.path.join(here, 'README.md')) else open(os.path.join(here, 'README.txt'), 'w+') as f:
    if f.mode == 'w+':
        f.write("Metapython - Unified Meta-Analysis Suite")
        f.seek(0)
    long_description = f.read()

# Read version from metapython.py
version = "0.3.0"

# Core dependencies (always required)
install_requires = [
    "numpy>=1.20.0",
    "pandas>=1.3.0",
    "scipy>=1.7.0",
    "matplotlib>=3.3.0",
    "seaborn>=0.11.0",
]

# Optional extras
extras_require = {
    # Bayesian analysis engines
    "bayes": [
        "pymc>=5.0.0",
        "arviz>=0.15.0",
        "cmdstanpy>=1.1.0",  # CmdStanPy fallback
        "pystan>=3.5.0",      # PyStan fallback
    ],
    
    # Interactive visualizations
    "viz": [
        "plotly>=5.0.0",
        "altair>=4.2.0",
        "streamlit>=1.20.0",
        "bokeh>=2.4.0",
    ],
    
    # Performance optimizations
    "speed": [
        "numba>=0.56.0",
        "cython>=0.29.0",
        "joblib>=1.1.0",
    ],
    
    # R interoperability
    "rinterop": [
        "rpy2>=3.5.0",
        "tzlocal>=4.0",  # Required for rpy2
    ],
    
    # Big data processing
    "dask": [
        "dask[dataframe]>=2022.0.0",
        "distributed>=2022.0.0",
    ],
    
    # Additional ML and NLP features
    "ml": [
        "scikit-learn>=1.0.0",
        "xgboost>=1.6.0",
        "shap>=0.41.0",
        "spacy>=3.4.0",
    ],
    
    # Development and testing
    "dev": [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "black>=22.0.0",
        "flake8>=5.0.0",
        "mypy>=0.991",
        "pre-commit>=2.20.0",
    ],
    
    # Documentation
    "docs": [
        "mkdocs>=1.4.0",
        "mkdocs-material>=8.5.0",
        "mkdocstrings[python]>=0.19.0",
        "jinja2>=3.1.0",
    ],
    
    # Full installation (all extras except dev)
    "all": [
        "pymc>=5.0.0", "arviz>=0.15.0", "cmdstanpy>=1.1.0", "pystan>=3.5.0",
        "plotly>=5.0.0", "altair>=4.2.0", "streamlit>=1.20.0", "bokeh>=2.4.0",
        "numba>=0.56.0", "cython>=0.29.0", "joblib>=1.1.0",
        "rpy2>=3.5.0", "tzlocal>=4.0",
        "dask[dataframe]>=2022.0.0", "distributed>=2022.0.0",
        "scikit-learn>=1.0.0", "xgboost>=1.6.0", "shap>=0.41.0", "spacy>=3.4.0",
        "jinja2>=3.1.0",
    ],
}

setup(
    name="metapython",
    version=version,
    author="PyMeta-CBAMM Development Team",
    author_email="pymeta-cbamm@example.com",
    description="Unified meta-analysis suite with Bayesian engines, automated diagnostics, and interactive visualizations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mahmood726-cyber/Metapython",
    py_modules=["metapython"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require=extras_require,
    include_package_data=True,
    zip_safe=False,
    keywords="meta-analysis bayesian statistics research evidence synthesis",
    project_urls={
        "Bug Reports": "https://github.com/mahmood726-cyber/Metapython/issues",
        "Source": "https://github.com/mahmood726-cyber/Metapython",
        "Documentation": "https://mahmood726-cyber.github.io/Metapython/",
    },
)