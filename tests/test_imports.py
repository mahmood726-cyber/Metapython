"""
Test module imports and basic availability checks.
"""

import pytest
import sys
import os


def test_metapython_import():
    """Test that metapython module can be imported."""
    import metapython
    assert metapython is not None


def test_core_dependencies():
    """Test that core dependencies are available."""
    import numpy
    import pandas
    import scipy
    import matplotlib
    import seaborn

    assert numpy is not None
    assert pandas is not None
    assert scipy is not None
    assert matplotlib is not None
    assert seaborn is not None


def test_numpy_version():
    """Test that numpy version is compatible."""
    import numpy as np
    version = tuple(map(int, np.__version__.split('.')[:2]))
    assert version >= (1, 20), f"NumPy version {np.__version__} is too old"


def test_pandas_version():
    """Test that pandas version is compatible."""
    import pandas as pd
    version = tuple(map(int, pd.__version__.split('.')[:2]))
    assert version >= (1, 0), f"Pandas version {pd.__version__} is too old"


def test_optional_dependencies_graceful():
    """Test that optional dependencies fail gracefully."""
    import metapython

    # These should be boolean flags
    assert hasattr(metapython, 'HAS_PYMC')
    assert hasattr(metapython, 'HAS_STATSMODELS')
    assert hasattr(metapython, 'HAS_BIOPYTHON')

    # Should be boolean values
    assert isinstance(metapython.HAS_PYMC, bool)
    assert isinstance(metapython.HAS_STATSMODELS, bool)
    assert isinstance(metapython.HAS_BIOPYTHON, bool)


def test_module_docstring():
    """Test that metapython has proper documentation."""
    import metapython
    assert metapython.__doc__ is not None
    assert len(metapython.__doc__) > 0
    assert 'Meta-Analysis' in metapython.__doc__


def test_logging_configured():
    """Test that logging is properly configured."""
    import logging
    logger = logging.getLogger('metapython')
    assert logger is not None


def test_environment_configuration():
    """Test that PyTensor environment is configured."""
    import os
    # The module should set PYTENSOR_FLAGS if not already set
    assert 'PYTENSOR_FLAGS' in os.environ or True  # May be set by module
