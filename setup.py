#!/usr/bin/env python3
"""
MetaPython v0.8.0 GA - Setup Configuration
==========================================

Enterprise-grade meta-analysis platform with comprehensive features.
"""

from setuptools import setup, find_packages
import os

# Read long description from README
def read_long_description():
    with open("PHASE4_CHANGELOG.md", "r", encoding="utf-8") as f:
        return f.read()

# Read version from package
def read_version():
    version = {}
    with open("metapython.py", "r", encoding="utf-8") as f:
        content = f.read()
        # Extract version from docstring
        if "Version: 0.8.0" in content:
            return "0.8.0"
    return "0.8.0"

# Core dependencies
CORE_DEPS = [
    "numpy>=1.21.0",
    "pandas>=1.3.0", 
    "matplotlib>=3.5.0",
    "seaborn>=0.11.0",
    "scipy>=1.7.0"
]

# Optional enterprise features (behind extras)
ENTERPRISE_EXTRAS = [
    "pymc>=5.0.0",  # Bayesian methods
    "arviz>=0.12.0",  # Bayesian diagnostics
    "statsmodels>=0.13.0",  # Advanced regression
    "scikit-learn>=1.0.0",  # ML clustering
    "numba>=0.56.0",  # Performance optimization
]

# Observability and monitoring
OBSERVABILITY_EXTRAS = [
    "opentelemetry-api>=1.15.0",
    "opentelemetry-sdk>=1.15.0", 
    "opentelemetry-exporter-otlp>=1.15.0",
    "prometheus-client>=0.15.0",
]

# Data lineage and catalog
LINEAGE_EXTRAS = [
    "openlineage-python>=0.20.0",
    "apache-airflow>=2.5.0",  # For DataHub integration
]

# BI and productivity
BI_EXTRAS = [
    "openpyxl>=3.0.0",  # Excel support
    "tableauhyperapi>=0.0.15106",  # Tableau integration
    "pyarrow>=10.0.0",  # Arrow interchange
]

# Enterprise security
SECURITY_EXTRAS = [
    "cryptography>=3.4.0",
    "boto3>=1.20.0",  # AWS KMS
    "google-cloud-kms>=2.11.0",  # GCP KMS
    "azure-keyvault>=4.0.0",  # Azure Key Vault
    "python-saml>=1.14.0",  # SAML SSO
]

# Development and testing
DEV_EXTRAS = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=0.991",
]

setup(
    name="metapython",
    version=read_version(),
    description="Enterprise-grade meta-analysis platform with comprehensive statistical methods",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    author="PyMeta-CBAMM Development Team", 
    author_email="metapython-dev@example.com",
    url="https://github.com/mahmood726-cyber/Metapython",
    py_modules=["metapython"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
    ],
    python_requires=">=3.8",
    install_requires=CORE_DEPS,
    extras_require={
        "enterprise": ENTERPRISE_EXTRAS,
        "observability": OBSERVABILITY_EXTRAS,
        "lineage": LINEAGE_EXTRAS,
        "bi": BI_EXTRAS,
        "security": SECURITY_EXTRAS,
        "dev": DEV_EXTRAS,
        "all": (ENTERPRISE_EXTRAS + OBSERVABILITY_EXTRAS + 
                LINEAGE_EXTRAS + BI_EXTRAS + SECURITY_EXTRAS),
    },
    entry_points={
        "console_scripts": [
            "metapython=metapython:main",
            "meta-cli=metapython:run_cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="meta-analysis statistics research enterprise bayesian",
)