"""
MetaPython - Professional Meta-Analysis Platform
=================================================

A comprehensive, production-ready meta-analysis library implementing
cutting-edge methods from top statistics journals.
"""

from setuptools import setup, find_packages
import os

# Read version from __init__.py
def get_version():
    init_file = os.path.join('metapython', '__init__.py')
    if os.path.exists(init_file):
        with open(init_file) as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"').strip("'")
    return '0.5.0'

# Read long description from README
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='metapython',
    version=get_version(),
    author='MetaPython Development Team',
    author_email='mahmood726.cyber@gmail.com',
    description='Professional meta-analysis platform with cutting-edge methods',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mahmood726-cyber/Metapython',
    packages=find_packages(exclude=['tests', 'benchmarks', 'docs']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Healthcare Industry',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=[
        'numpy>=1.20.0',
        'pandas>=1.3.0',
        'scipy>=1.7.0',
        'matplotlib>=3.3.0',
        'seaborn>=0.11.0',
        'scikit-learn>=0.24.0',
    ],
    extras_require={
        'full': [
            'pymc>=5.0.0',
            'arviz>=0.12.0',
            'plotly>=5.0.0',
            'statsmodels>=0.13.0',
            'networkx>=2.6.0',
        ],
        'nlp': [
            'spacy>=3.0.0',
            'transformers>=4.0.0',
        ],
        'dev': [
            'pytest>=6.0.0',
            'pytest-cov>=2.12.0',
            'black>=21.0',
            'mypy>=0.910',
            'flake8>=3.9.0',
            'sphinx>=4.0.0',
            'sphinx-rtd-theme>=0.5.0',
        ],
        'all': [
            'pymc>=5.0.0',
            'arviz>=0.12.0',
            'plotly>=5.0.0',
            'statsmodels>=0.13.0',
            'networkx>=2.6.0',
            'spacy>=3.0.0',
            'transformers>=4.0.0',
            'pytest>=6.0.0',
            'pytest-cov>=2.12.0',
            'black>=21.0',
            'mypy>=0.910',
            'flake8>=3.9.0',
            'sphinx>=4.0.0',
            'sphinx-rtd-theme>=0.5.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'metapython=metapython.cli.commands:main',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/mahmood726-cyber/Metapython/issues',
        'Source': 'https://github.com/mahmood726-cyber/Metapython',
        'Documentation': 'https://github.com/mahmood726-cyber/Metapython/blob/main/README.md',
    },
    keywords='meta-analysis statistics medicine research publication-bias bayesian',
    include_package_data=True,
    zip_safe=False,
)
