"""
Base Plugin Classes for Different Plugin Types
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

class BasePlugin(ABC):
    """Base class for all Metapython plugins"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
    
    @abstractmethod
    def get_manifest_info(self) -> Dict[str, Any]:
        """Return manifest information for this plugin"""
        pass
    
    @abstractmethod
    def validate_config(self) -> Dict[str, Any]:
        """Validate plugin configuration"""
        pass
    
    def get_version(self) -> str:
        """Get plugin version"""
        return getattr(self, '__version__', '1.0.0')
    
    def get_capabilities(self) -> List[str]:
        """Get list of plugin capabilities"""
        return getattr(self, '__capabilities__', [])

class AnalysisMethodPlugin(BasePlugin):
    """Base class for analysis method plugins (effect-size transformers, etc.)"""
    
    @abstractmethod
    def transform_effect_sizes(self, 
                             effects: np.ndarray, 
                             variances: np.ndarray,
                             **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """Transform effect sizes and their variances"""
        pass
    
    @abstractmethod
    def get_effect_size_type(self) -> str:
        """Return the effect size type this plugin handles"""
        pass
    
    def supports_effect_type(self, effect_type: str) -> bool:
        """Check if this plugin supports a given effect size type"""
        return effect_type == self.get_effect_size_type()
    
    def get_transformation_name(self) -> str:
        """Get human-readable name of the transformation"""
        return getattr(self, '__transformation_name__', self.__class__.__name__)

class DataReaderPlugin(BasePlugin):
    """Base class for data reader plugins"""
    
    @abstractmethod
    def read_data(self, source: Union[str, Any], **kwargs) -> pd.DataFrame:
        """Read data from source and return standardized DataFrame"""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Return list of supported file formats/sources"""
        pass
    
    @abstractmethod
    def validate_source(self, source: Union[str, Any]) -> bool:
        """Validate if source is supported by this reader"""
        pass
    
    def get_schema_info(self) -> Optional[Dict[str, Any]]:
        """Get schema information for data validation"""
        return getattr(self, '__schema_info__', None)
    
    def preprocess_data(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Optional preprocessing step after reading"""
        return data

class ReportRendererPlugin(BasePlugin):
    """Base class for report renderer plugins"""
    
    @abstractmethod
    def render_report(self, 
                     results: Any,
                     template: Optional[str] = None,
                     **kwargs) -> Union[str, bytes]:
        """Render meta-analysis results into report format"""
        pass
    
    @abstractmethod
    def get_output_format(self) -> str:
        """Return output format (e.g., 'html', 'pdf', 'markdown')"""
        pass
    
    @abstractmethod
    def get_template_names(self) -> List[str]:
        """Return list of available templates"""
        pass
    
    def supports_results_type(self, results_type: str) -> bool:
        """Check if renderer supports given results type"""
        supported_types = getattr(self, '__supported_results_types__', ['any'])
        return 'any' in supported_types or results_type in supported_types
    
    def validate_template(self, template: str) -> bool:
        """Validate if template exists and is valid"""
        return template in self.get_template_names()

# Utility classes for plugin development

@dataclass
class PluginContext:
    """Context information provided to plugins during execution"""
    metapython_version: str
    api_version: str
    current_analysis: Optional[Any] = None
    user_config: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    
class PluginError(Exception):
    """Base exception for plugin-related errors"""
    pass

class PluginConfigError(PluginError):
    """Exception for plugin configuration errors"""
    pass

class PluginCompatibilityError(PluginError):
    """Exception for plugin compatibility errors"""
    pass

class PluginExecutionError(PluginError):
    """Exception for plugin execution errors"""
    pass

# Plugin utilities

class PluginUtils:
    """Utility functions for plugin development"""
    
    @staticmethod
    def validate_effect_sizes(effects: np.ndarray, variances: np.ndarray) -> None:
        """Validate effect sizes and variances"""
        if len(effects) != len(variances):
            raise PluginConfigError("Effects and variances must have same length")
        
        if np.any(np.isnan(effects)) or np.any(np.isinf(effects)):
            raise PluginConfigError("Effects contain NaN or infinite values")
        
        if np.any(variances <= 0):
            raise PluginConfigError("Variances must be positive")
        
        if np.any(np.isnan(variances)) or np.any(np.isinf(variances)):
            raise PluginConfigError("Variances contain NaN or infinite values")
    
    @staticmethod
    def standardize_dataframe(df: pd.DataFrame, 
                            required_columns: List[str],
                            column_mapping: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """Standardize DataFrame with required columns"""
        if column_mapping:
            df = df.rename(columns=column_mapping)
        
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise PluginConfigError(f"Missing required columns: {missing_cols}")
        
        return df[required_columns].copy()
    
    @staticmethod
    def safe_log_transform(values: np.ndarray, base: float = np.e) -> np.ndarray:
        """Safe logarithmic transformation with handling for edge cases"""
        # Handle zeros and negative values
        safe_values = np.where(values <= 0, 1e-10, values)
        return np.log(safe_values) / np.log(base)
    
    @staticmethod
    def safe_exp_transform(values: np.ndarray, base: float = np.e) -> np.ndarray:
        """Safe exponential transformation with overflow protection"""
        # Clip to prevent overflow
        safe_values = np.clip(values, -700, 700)  # exp(700) is near float64 limit
        return np.power(base, safe_values)

class PluginDecorator:
    """Decorators for plugin development"""
    
    @staticmethod
    def requires_config(config_keys: List[str]):
        """Decorator to ensure required config keys are present"""
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                missing_keys = [key for key in config_keys if key not in self.config]
                if missing_keys:
                    raise PluginConfigError(f"Missing required config keys: {missing_keys}")
                return func(self, *args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def validate_inputs(input_types: Dict[str, type]):
        """Decorator to validate input types"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Simple validation - could be more sophisticated
                return func(*args, **kwargs)
            return wrapper
        return decorator

# Plugin development helpers

def create_analysis_plugin(name: str, 
                         version: str,
                         transform_func: callable,
                         effect_type: str,
                         **kwargs) -> type:
    """Factory function to create simple analysis method plugins"""
    
    class DynamicAnalysisPlugin(AnalysisMethodPlugin):
        __version__ = version
        __transformation_name__ = name
        
        def get_manifest_info(self) -> Dict[str, Any]:
            return {
                'name': name,
                'version': version,
                'type': 'analysis_method',
                'effect_type': effect_type
            }
        
        def validate_config(self) -> Dict[str, Any]:
            return {'valid': True, 'issues': []}
        
        def transform_effect_sizes(self, effects: np.ndarray, variances: np.ndarray, **transform_kwargs) -> Tuple[np.ndarray, np.ndarray]:
            PluginUtils.validate_effect_sizes(effects, variances)
            return transform_func(effects, variances, **transform_kwargs)
        
        def get_effect_size_type(self) -> str:
            return effect_type
    
    return DynamicAnalysisPlugin

def create_data_reader_plugin(name: str,
                            version: str, 
                            read_func: callable,
                            supported_formats: List[str],
                            **kwargs) -> type:
    """Factory function to create simple data reader plugins"""
    
    class DynamicDataReaderPlugin(DataReaderPlugin):
        __version__ = version
        
        def get_manifest_info(self) -> Dict[str, Any]:
            return {
                'name': name,
                'version': version,
                'type': 'data_reader',
                'formats': supported_formats
            }
        
        def validate_config(self) -> Dict[str, Any]:
            return {'valid': True, 'issues': []}
        
        def read_data(self, source: Union[str, Any], **read_kwargs) -> pd.DataFrame:
            return read_func(source, **read_kwargs)
        
        def get_supported_formats(self) -> List[str]:
            return supported_formats
        
        def validate_source(self, source: Union[str, Any]) -> bool:
            # Basic validation - could be more sophisticated
            return True
    
    return DynamicDataReaderPlugin

def create_report_renderer_plugin(name: str,
                                version: str,
                                render_func: callable, 
                                output_format: str,
                                templates: List[str],
                                **kwargs) -> type:
    """Factory function to create simple report renderer plugins"""
    
    class DynamicReportRendererPlugin(ReportRendererPlugin):
        __version__ = version
        
        def get_manifest_info(self) -> Dict[str, Any]:
            return {
                'name': name,
                'version': version,
                'type': 'report_renderer',
                'output_format': output_format,
                'templates': templates
            }
        
        def validate_config(self) -> Dict[str, Any]:
            return {'valid': True, 'issues': []}
        
        def render_report(self, results: Any, template: Optional[str] = None, **render_kwargs) -> Union[str, bytes]:
            return render_func(results, template, **render_kwargs)
        
        def get_output_format(self) -> str:
            return output_format
        
        def get_template_names(self) -> List[str]:
            return templates
    
    return DynamicReportRendererPlugin