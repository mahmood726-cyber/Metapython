"""
Example Plugins demonstrating the Plugin API
"""

import numpy as np
import pandas as pd
import json
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
import logging

from .base import AnalysisMethodPlugin, DataReaderPlugin, ReportRendererPlugin, PluginUtils
from .api import PluginCapability

logger = logging.getLogger(__name__)

class ExampleEffectSizeTransformer(AnalysisMethodPlugin):
    """Example plugin for custom effect-size transformation"""
    
    __version__ = "1.0.0"
    __transformation_name__ = "Log Odds Ratio to Risk Ratio"
    __capabilities__ = ["log_or_to_rr", "effect_size_transformation"]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.baseline_risk = config.get('baseline_risk', 0.1) if config else 0.1
    
    def get_manifest_info(self) -> Dict[str, Any]:
        return {
            'plugin_id': 'metapython.examples.log_or_to_rr',
            'name': 'Log OR to RR Transformer',
            'version': self.__version__,
            'description': 'Transforms log odds ratios to risk ratios using baseline risk',
            'author': 'Metapython Team',
            'author_email': 'examples@metapython.org',
            'homepage': 'https://metapython.org/plugins/examples',
            'plugin_type': 'analysis_method',
            'api_version': '1.0.0',
            'capabilities': [
                PluginCapability(
                    name='log_or_to_rr',
                    version='1.0.0',
                    description='Convert log odds ratios to risk ratios',
                    required_metapython_version='0.7.0',
                    data_types=['log_odds_ratio'],
                    output_formats=['risk_ratio']
                )
            ]
        }
    
    def validate_config(self) -> Dict[str, Any]:
        issues = []
        
        if not isinstance(self.baseline_risk, (int, float)):
            issues.append("baseline_risk must be numeric")
        elif not (0 < self.baseline_risk < 1):
            issues.append("baseline_risk must be between 0 and 1")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    def transform_effect_sizes(self, 
                             effects: np.ndarray, 
                             variances: np.ndarray,
                             **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """Transform log odds ratios to risk ratios using baseline risk"""
        
        PluginUtils.validate_effect_sizes(effects, variances)
        
        # Extract baseline risk from kwargs or use default
        baseline_risk = kwargs.get('baseline_risk', self.baseline_risk)
        
        # Convert log OR to OR
        odds_ratios = np.exp(effects)
        
        # Convert OR to RR using baseline risk
        # RR = OR / (1 - p0 + p0 * OR)
        # where p0 is baseline risk
        risk_ratios = odds_ratios / (1 - baseline_risk + baseline_risk * odds_ratios)
        
        # Transform back to log scale
        log_rr = np.log(risk_ratios)
        
        # Transform variances using delta method
        # Var(log RR) ≈ Var(log OR) * (d log RR / d log OR)²
        # d log RR / d log OR = (1 - p0) / (1 - p0 + p0 * OR)
        derivative = (1 - baseline_risk) / (1 - baseline_risk + baseline_risk * odds_ratios)
        transformed_variances = variances * (derivative ** 2)
        
        self.logger.info(f"Transformed {len(effects)} log OR to log RR using baseline risk {baseline_risk}")
        
        return log_rr, transformed_variances
    
    def get_effect_size_type(self) -> str:
        return "log_odds_ratio"

class ExampleDatasetReader(DataReaderPlugin):
    """Example plugin for reading custom dataset format"""
    
    __version__ = "1.0.0"
    __capabilities__ = ["json_meta_reader", "custom_format_reader"]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.required_fields = config.get('required_fields', ['study_id', 'effect', 'se']) if config else ['study_id', 'effect', 'se']
    
    def get_manifest_info(self) -> Dict[str, Any]:
        return {
            'plugin_id': 'metapython.examples.json_meta_reader',
            'name': 'JSON Meta-Analysis Reader',
            'version': self.__version__,
            'description': 'Reads meta-analysis data from custom JSON format',
            'author': 'Metapython Team',
            'author_email': 'examples@metapython.org',
            'homepage': 'https://metapython.org/plugins/examples',
            'plugin_type': 'data_reader',
            'api_version': '1.0.0',
            'capabilities': [
                PluginCapability(
                    name='json_meta_reader',
                    version='1.0.0',
                    description='Read meta-analysis data from JSON files',
                    required_metapython_version='0.7.0',
                    data_types=['json', 'meta_analysis'],
                    output_formats=['pandas_dataframe']
                )
            ]
        }
    
    def validate_config(self) -> Dict[str, Any]:
        issues = []
        
        if not isinstance(self.required_fields, list):
            issues.append("required_fields must be a list")
        elif len(self.required_fields) == 0:
            issues.append("required_fields cannot be empty")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    def read_data(self, source: Union[str, Any], **kwargs) -> pd.DataFrame:
        """Read meta-analysis data from JSON source"""
        
        try:
            # Handle different source types
            if isinstance(source, (str, Path)):
                source_path = Path(source)
                if not source_path.exists():
                    raise ValueError(f"Source file does not exist: {source}")
                
                with open(source_path, 'r') as f:
                    data = json.load(f)
            elif isinstance(source, dict):
                data = source
            elif isinstance(source, str) and source.startswith('{'):
                # JSON string
                data = json.loads(source)
            else:
                raise ValueError(f"Unsupported source type: {type(source)}")
            
            # Expected JSON format:
            # {
            #   "studies": [
            #     {
            #       "study_id": "Study1",
            #       "effect": 0.5,
            #       "se": 0.1,
            #       "sample_size": 100,
            #       "year": 2020,
            #       ...
            #     }
            #   ],
            #   "metadata": {
            #     "effect_type": "log_odds_ratio",
            #     "source": "systematic_review"
            #   }
            # }
            
            if 'studies' not in data:
                raise ValueError("JSON must contain 'studies' key")
            
            studies = data['studies']
            metadata = data.get('metadata', {})
            
            # Convert to DataFrame
            df = pd.DataFrame(studies)
            
            # Validate required fields
            missing_fields = [field for field in self.required_fields if field not in df.columns]
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")
            
            # Add metadata as attributes
            for key, value in metadata.items():
                setattr(df, f'meta_{key}', value)
            
            self.logger.info(f"Successfully read {len(df)} studies from JSON source")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to read data from source: {e}")
            raise
    
    def get_supported_formats(self) -> List[str]:
        return ['json', 'json_meta', '.json']
    
    def validate_source(self, source: Union[str, Any]) -> bool:
        """Validate if source is supported by this reader"""
        try:
            if isinstance(source, (str, Path)):
                source_path = Path(source)
                return source_path.suffix.lower() == '.json' and source_path.exists()
            elif isinstance(source, dict):
                return 'studies' in source
            elif isinstance(source, str) and source.startswith('{'):
                # Try parsing as JSON
                json.loads(source)
                return True
            return False
        except:
            return False
    
    def get_schema_info(self) -> Optional[Dict[str, Any]]:
        return {
            'required_fields': self.required_fields,
            'optional_fields': ['sample_size', 'year', 'author', 'journal', 'country'],
            'format': 'JSON with studies array and optional metadata',
            'example': {
                'studies': [
                    {
                        'study_id': 'Study1',
                        'effect': 0.5,
                        'se': 0.1,
                        'sample_size': 100
                    }
                ],
                'metadata': {
                    'effect_type': 'log_odds_ratio'
                }
            }
        }

class ExampleReportRenderer(ReportRendererPlugin):
    """Example plugin for custom report rendering"""
    
    __version__ = "1.0.0"
    __capabilities__ = ["markdown_report", "custom_template"]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.include_plots = config.get('include_plots', True) if config else True
        self.include_diagnostics = config.get('include_diagnostics', True) if config else True
    
    def get_manifest_info(self) -> Dict[str, Any]:
        return {
            'plugin_id': 'metapython.examples.markdown_renderer',
            'name': 'Markdown Report Renderer',
            'version': self.__version__,
            'description': 'Renders meta-analysis results as Markdown reports',
            'author': 'Metapython Team',
            'author_email': 'examples@metapython.org',
            'homepage': 'https://metapython.org/plugins/examples',
            'plugin_type': 'report_renderer',
            'api_version': '1.0.0',
            'capabilities': [
                PluginCapability(
                    name='markdown_report',
                    version='1.0.0',
                    description='Generate Markdown reports from meta-analysis results',
                    required_metapython_version='0.7.0',
                    data_types=['meta_analysis_results'],
                    output_formats=['markdown', 'md']
                )
            ]
        }
    
    def validate_config(self) -> Dict[str, Any]:
        issues = []
        
        if not isinstance(self.include_plots, bool):
            issues.append("include_plots must be boolean")
        
        if not isinstance(self.include_diagnostics, bool):
            issues.append("include_diagnostics must be boolean")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    def render_report(self, 
                     results: Any,
                     template: Optional[str] = None,
                     **kwargs) -> str:
        """Render meta-analysis results as Markdown report"""
        
        template = template or 'standard'
        
        if template == 'standard':
            return self._render_standard_template(results, **kwargs)
        elif template == 'brief':
            return self._render_brief_template(results, **kwargs)
        elif template == 'detailed':
            return self._render_detailed_template(results, **kwargs)
        else:
            raise ValueError(f"Unknown template: {template}")
    
    def get_output_format(self) -> str:
        return 'markdown'
    
    def get_template_names(self) -> List[str]:
        return ['standard', 'brief', 'detailed']
    
    def _render_standard_template(self, results: Any, **kwargs) -> str:
        """Render standard Markdown report"""
        
        title = kwargs.get('title', 'Meta-Analysis Results')
        author = kwargs.get('author', 'Unknown')
        
        md_content = f"""# {title}

**Author:** {author}
**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

"""
        
        # Add results summary
        try:
            if hasattr(results, 'fixed_effects'):
                fe = results.fixed_effects
                md_content += f"""### Fixed Effects Model
- **Effect Size:** {fe.effect:.3f} (95% CI: {fe.ci_low:.3f} to {fe.ci_high:.3f})
- **p-value:** {fe.p_value:.3f}
- **Significance:** {'Yes' if fe.is_significant() else 'No'}

"""
            
            if hasattr(results, 'random_effects'):
                re = results.random_effects
                md_content += f"""### Random Effects Model
- **Effect Size:** {re.effect:.3f} (95% CI: {re.ci_low:.3f} to {re.ci_high:.3f})
- **p-value:** {re.p_value:.3f}
- **Tau²:** {re.tau2:.3f}
- **Significance:** {'Yes' if re.is_significant() else 'No'}

"""
            
            if hasattr(results, 'heterogeneity'):
                het = results.heterogeneity
                md_content += f"""### Heterogeneity Assessment
- **Q-statistic:** {het.Q:.3f} (df = {het.df})
- **p-value:** {het.p_value:.3f}
- **I²:** {het.I2:.1f}%
- **Significant heterogeneity:** {'Yes' if het.is_significant() else 'No'}

"""
        except Exception as e:
            md_content += f"Error rendering results: {e}\n\n"
        
        # Add diagnostics if requested
        if self.include_diagnostics and hasattr(results, 'bias_assessment'):
            md_content += """## Publication Bias Assessment

"""
            try:
                bias = results.bias_assessment
                if hasattr(bias, 'egger'):
                    egger = bias.egger
                    md_content += f"- **Egger's test:** p = {egger.get('p_value', 'N/A')}\n"
                
                if hasattr(bias, 'begg'):
                    begg = bias.begg
                    md_content += f"- **Begg's test:** p = {begg.get('p_value', 'N/A')}\n"
                
                md_content += "\n"
            except:
                md_content += "Bias assessment information not available.\n\n"
        
        # Add plots section if requested
        if self.include_plots:
            md_content += """## Visualizations

*Note: Plot generation would be handled by the main analysis system.*

- Forest plot
- Funnel plot
- Diagnostic plots

"""
        
        md_content += """## Interpretation

"""
        
        # Add basic interpretation
        try:
            if hasattr(results, 'random_effects'):
                re = results.random_effects
                if re.p_value < 0.05:
                    if re.effect > 0:
                        md_content += "The meta-analysis shows a statistically significant positive effect.\n\n"
                    else:
                        md_content += "The meta-analysis shows a statistically significant negative effect.\n\n"
                else:
                    md_content += "The meta-analysis does not show a statistically significant effect.\n\n"
                
                if hasattr(results, 'heterogeneity') and results.heterogeneity.I2 > 50:
                    md_content += "There is substantial heterogeneity between studies, suggesting caution in interpretation.\n\n"
        except:
            md_content += "Interpretation could not be generated automatically.\n\n"
        
        md_content += """---
*Report generated by Metapython Example Report Renderer*
"""
        
        self.logger.info("Generated standard Markdown report")
        return md_content
    
    def _render_brief_template(self, results: Any, **kwargs) -> str:
        """Render brief Markdown report"""
        
        title = kwargs.get('title', 'Meta-Analysis Brief')
        
        md_content = f"""# {title}

"""
        try:
            if hasattr(results, 'random_effects'):
                re = results.random_effects
                md_content += f"**Effect:** {re.effect:.3f} (95% CI: {re.ci_low:.3f} to {re.ci_high:.3f}), p = {re.p_value:.3f}\n\n"
            
            if hasattr(results, 'heterogeneity'):
                het = results.heterogeneity
                md_content += f"**Heterogeneity:** I² = {het.I2:.1f}%, p = {het.p_value:.3f}\n\n"
        except:
            md_content += "Results not available.\n\n"
        
        return md_content
    
    def _render_detailed_template(self, results: Any, **kwargs) -> str:
        """Render detailed Markdown report"""
        
        # Start with standard template and add more details
        md_content = self._render_standard_template(results, **kwargs)
        
        md_content += """
## Detailed Statistics

"""
        
        # Add more detailed information
        try:
            if hasattr(results, 'prediction_interval') and results.prediction_interval:
                pi = results.prediction_interval
                md_content += f"""### Prediction Interval
- **Range:** {pi.low:.3f} to {pi.high:.3f}
- **Standard Error:** {pi.se:.3f}

"""
            
            if hasattr(results, 'conflict_detection') and results.conflict_detection:
                conflict = results.conflict_detection
                md_content += f"""### Conflict Detection
- **Number of clusters:** {conflict.k}
- **Silhouette score:** {conflict.silhouette:.3f}
- **Effect range:** {conflict.delta:.3f}
- **Conflicting results:** {'Yes' if conflict.conflicting else 'No'}

"""
        except:
            md_content += "Additional statistics not available.\n\n"
        
        return md_content

# Plugin manifest information for registration
__plugin_manifest__ = {
    'plugin_id': 'metapython.examples.all',
    'name': 'Metapython Example Plugins',
    'version': '1.0.0',
    'description': 'Collection of example plugins demonstrating the Plugin API',
    'author': 'Metapython Team',
    'author_email': 'examples@metapython.org',
    'homepage': 'https://metapython.org/plugins/examples',
    'plugin_type': 'collection',
    'api_version': '1.0.0',
    'capabilities': [
        {
            'name': 'example_collection',
            'version': '1.0.0',
            'description': 'Collection of example plugins for demonstration',
            'required_metapython_version': '0.7.0',
            'data_types': ['various'],
            'output_formats': ['various']
        }
    ],
    'required_dependencies': ['numpy', 'pandas'],
    'optional_dependencies': []
}