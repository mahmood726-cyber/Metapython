#!/usr/bin/env python
"""
Setup script for MetaPython - Unified meta-analysis suite

This setup.py provides backward compatibility for older build systems
while the primary configuration is in pyproject.toml.
"""

from setuptools import setup, find_packages
import os

# Read version from the main module
def get_version():
    """Extract version from metapython.py"""
    version_file = os.path.join(os.path.dirname(__file__), 'metapython.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                # Extract version string
                return line.split('=')[1].strip().strip('"').strip("'")
    raise RuntimeError("Unable to find version string")

# Read long description from README
def get_long_description():
    """Read README for long description"""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Unified meta-analysis suite combining PyMeta and CBAMM with production-grade extensions"

if __name__ == "__main__":
    setup(
        name="metapython",
        version=get_version(),
        description="Unified meta-analysis suite combining PyMeta and CBAMM with production-grade extensions",
        long_description=get_long_description(),
        long_description_content_type="text/markdown",
        author="PyMeta-CBAMM Development Team",
        author_email="pymeta-cbamm@example.com",
        url="https://github.com/mahmood726-cyber/Metapython",
        packages=find_packages(),
        py_modules=["metapython"],
        python_requires=">=3.8",
        install_requires=[
            "numpy>=1.20.0",
            "pandas>=1.3.0", 
            "matplotlib>=3.4.0",
            "seaborn>=0.11.0",
            "scipy>=1.7.0",
        ],
        extras_require={
            "stats": ["statsmodels>=0.13.0", "scikit-learn>=1.0.0"],
            "bayesian": ["pymc>=5.0.0", "arviz>=0.12.0"],
            "pipeline": ["PyYAML>=6.0", "Jinja2>=3.0.0", "click>=8.0.0"],
            "performance": ["numba>=0.56.0", "dask[complete]>=2022.1.0", "joblib>=1.1.0"],
            "living": ["biopython>=1.79", "requests>=2.25.0"],
            "web": ["streamlit>=1.10.0", "flask>=2.0.0", "plotly>=5.0.0"],
            "ml": ["spacy>=3.4.0", "transformers>=4.15.0", "xgboost>=1.5.0", "shap>=0.40.0"],
            "optimization": ["cvxpy>=1.2.0"],
            "dev": ["pytest>=7.0.0", "pytest-cov>=3.0.0", "hypothesis>=6.50.0", "black>=22.0.0", "isort>=5.10.0", "flake8>=4.0.0", "mypy>=0.950", "pre-commit>=2.20.0"],
            "docs": ["sphinx>=4.5.0", "sphinx-rtd-theme>=1.0.0", "nbsphinx>=0.8.8", "jupyter>=1.0.0", "myst-parser>=0.18.0"],
        },
        entry_points={
            "console_scripts": [
                "metapython=metapython:main",
                "meta=metapython:main",
            ],
        },
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Topic :: Scientific/Engineering",
            "Topic :: Scientific/Engineering :: Information Analysis",
            "Topic :: Scientific/Engineering :: Medical Science Apps.",
        ],
        keywords="meta-analysis statistics research evidence-synthesis systematic-review",
        license="MIT",
        include_package_data=True,
        zip_safe=False,
    )