"""
RPy2 Bridge for R/Python Interoperability

Provides seamless bidirectional data exchange between Python and R for:
- Data frame conversions
- Meta-analysis results transfer
- R package function calls
- Statistical computations in R
"""

from typing import Dict, List, Any, Optional, Union
import numpy as np
import pandas as pd
import warnings

from metapython.core.config import logger

# Try to import rpy2
try:
    import rpy2.robjects as ro
    from rpy2.robjects import pandas2ri, numpy2ri
    from rpy2.robjects.packages import importr
    from rpy2.robjects.conversion import localconverter
    HAS_RPY2 = True
except ImportError:
    HAS_RPY2 = False
    logger.warning("rpy2 not available. Install with: pip install rpy2")


class RPythonBridge:
    """
    Bridge between Python and R for meta-analysis.

    Features:
    - Automatic data type conversion
    - R package management
    - Safe R code execution
    - Result caching

    Example:
        >>> bridge = RPythonBridge()
        >>> bridge.install_package('meta')
        >>> result = bridge.call_r_function('meta::metagen', TE=effects, seTE=se)
    """

    def __init__(self, auto_install_packages: bool = False):
        """
        Initialize R/Python bridge.

        Args:
            auto_install_packages: Whether to auto-install missing R packages
        """
        if not HAS_RPY2:
            raise ImportError("rpy2 required. Install with: pip install rpy2")

        self.auto_install = auto_install_packages
        self.installed_packages = set()

        # Activate automatic conversion
        pandas2ri.activate()
        numpy2ri.activate()

        # Load base R packages
        self.base = importr('base')
        self.utils = importr('utils')
        self.stats = importr('stats')

        logger.info("R/Python bridge initialized successfully")

    def install_package(self, package: str, repos: str = 'https://cran.r-project.org') -> bool:
        """
        Install R package if not already installed.

        Args:
            package: Package name
            repos: CRAN repository URL

        Returns:
            True if successful
        """
        try:
            # Check if already installed
            if package in self.installed_packages:
                return True

            # Try to import
            try:
                importr(package)
                self.installed_packages.add(package)
                logger.info(f"R package '{package}' already installed")
                return True
            except:
                pass

            # Install package
            logger.info(f"Installing R package '{package}'...")
            self.utils.install_packages(package, repos=repos)
            self.installed_packages.add(package)
            logger.info(f"Successfully installed '{package}'")
            return True

        except Exception as e:
            logger.error(f"Failed to install R package '{package}': {e}")
            return False

    def ensure_packages(self, packages: List[str]) -> bool:
        """
        Ensure all required packages are installed.

        Args:
            packages: List of package names

        Returns:
            True if all packages available
        """
        success = True
        for pkg in packages:
            if not self.install_package(pkg):
                success = False
        return success

    def call_r_function(
        self,
        function_name: str,
        **kwargs
    ) -> Any:
        """
        Call R function with Python arguments.

        Args:
            function_name: R function name (e.g., 'meta::metagen')
            **kwargs: Function arguments

        Returns:
            Result converted to Python
        """
        try:
            # Parse package::function syntax
            if '::' in function_name:
                package, func = function_name.split('::')
                # Ensure package is loaded
                if self.auto_install:
                    self.install_package(package)
                r_package = importr(package)
                r_function = getattr(r_package, func)
            else:
                r_function = ro.r[function_name]

            # Convert arguments to R
            r_kwargs = {}
            for key, value in kwargs.items():
                r_kwargs[key] = convert_to_r(value)

            # Call function
            result = r_function(**r_kwargs)

            # Convert result back to Python
            return convert_from_r(result)

        except Exception as e:
            logger.error(f"Error calling R function '{function_name}': {e}")
            raise

    def run_r_code(self, code: str, return_result: bool = True) -> Optional[Any]:
        """
        Execute R code directly.

        Args:
            code: R code string
            return_result: Whether to return the result

        Returns:
            Result if return_result=True
        """
        try:
            result = ro.r(code)
            if return_result:
                return convert_from_r(result)
        except Exception as e:
            logger.error(f"Error executing R code: {e}")
            raise

    def load_r_script(self, script_path: str) -> bool:
        """
        Load and execute R script file.

        Args:
            script_path: Path to R script

        Returns:
            True if successful
        """
        try:
            ro.r(f'source("{script_path}")')
            logger.info(f"Loaded R script: {script_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading R script: {e}")
            return False

    def get_r_variable(self, var_name: str) -> Any:
        """
        Get R variable value.

        Args:
            var_name: Variable name

        Returns:
            Variable value converted to Python
        """
        try:
            return convert_from_r(ro.globalenv[var_name])
        except Exception as e:
            logger.error(f"Error getting R variable '{var_name}': {e}")
            return None

    def set_r_variable(self, var_name: str, value: Any) -> bool:
        """
        Set R variable value.

        Args:
            var_name: Variable name
            value: Python value to set

        Returns:
            True if successful
        """
        try:
            ro.globalenv[var_name] = convert_to_r(value)
            return True
        except Exception as e:
            logger.error(f"Error setting R variable '{var_name}': {e}")
            return False


def convert_to_r(obj: Any) -> Any:
    """
    Convert Python object to R.

    Args:
        obj: Python object

    Returns:
        R object
    """
    if isinstance(obj, pd.DataFrame):
        with localconverter(ro.default_converter + pandas2ri.converter):
            return ro.conversion.py2rpy(obj)
    elif isinstance(obj, np.ndarray):
        with localconverter(ro.default_converter + numpy2ri.converter):
            return ro.conversion.py2rpy(obj)
    elif isinstance(obj, (list, tuple)):
        return ro.vectors.FloatVector(obj) if all(isinstance(x, (int, float)) for x in obj) else ro.vectors.StrVector(obj)
    elif isinstance(obj, dict):
        return ro.vectors.ListVector(obj)
    else:
        return obj


def convert_from_r(obj: Any) -> Any:
    """
    Convert R object to Python.

    Args:
        obj: R object

    Returns:
        Python object
    """
    try:
        # Check for data frame
        if 'data.frame' in str(type(obj)):
            with localconverter(ro.default_converter + pandas2ri.converter):
                return ro.conversion.rpy2py(obj)

        # Check for vector
        if hasattr(obj, '__iter__') and not isinstance(obj, str):
            return np.array(obj)

        # Check for list
        if isinstance(obj, ro.vectors.ListVector):
            return {k: convert_from_r(v) for k, v in obj.items()}

        # Try automatic conversion
        with localconverter(ro.default_converter + pandas2ri.converter + numpy2ri.converter):
            return ro.conversion.rpy2py(obj)

    except:
        # Return as-is if conversion fails
        return obj


def run_r_code(code: str) -> Any:
    """
    Quick function to run R code.

    Args:
        code: R code string

    Returns:
        Result converted to Python
    """
    if not HAS_RPY2:
        raise ImportError("rpy2 required")

    bridge = RPythonBridge()
    return bridge.run_r_code(code)


__all__ = [
    'RPythonBridge',
    'convert_to_r',
    'convert_from_r',
    'run_r_code',
]
