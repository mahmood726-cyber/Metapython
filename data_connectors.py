"""
Enhanced Data Connectors - Phase 8
Arrow/Parquet/Feather connectors, robust CSV handling, schema validation
"""

import os
import hashlib
import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from pathlib import Path
import pandas as pd
import numpy as np
from dataclasses import dataclass
import json
import warnings
from io import StringIO, BytesIO

# Arrow/Parquet support (optional)
try:
    import pyarrow as pa
    import pyarrow.parquet as pq
    import pyarrow.feather as feather
    HAS_ARROW = True
except ImportError:
    HAS_ARROW = False

# Enhanced CSV detection (optional)
try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False

# Schema validation (optional)
try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

logger = logging.getLogger(__name__)

@dataclass
class DataSchema:
    """Data schema definition for validation"""
    required_columns: List[str]
    optional_columns: List[str] = None
    column_types: Dict[str, str] = None
    value_constraints: Dict[str, Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.optional_columns is None:
            self.optional_columns = []
        if self.column_types is None:
            self.column_types = {}
        if self.value_constraints is None:
            self.value_constraints = {}

@dataclass
class DataLoadResult:
    """Result of data loading operation"""
    data: pd.DataFrame
    metadata: Dict[str, Any]
    warnings: List[str]
    errors: List[str]
    schema_validation: Dict[str, Any]
    checksum: Optional[str] = None

class DataChecksumValidator:
    """Data integrity validation using checksums"""
    
    @staticmethod
    def calculate_dataframe_checksum(df: pd.DataFrame) -> str:
        """Calculate checksum for DataFrame content"""
        # Convert DataFrame to consistent string representation
        df_string = df.to_csv(index=False, header=True, float_format='%.10g')
        return hashlib.sha256(df_string.encode()).hexdigest()
    
    @staticmethod
    def calculate_file_checksum(file_path: str) -> str:
        """Calculate checksum for file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def verify_data_integrity(original_checksum: str, current_checksum: str) -> bool:
        """Verify data integrity by comparing checksums"""
        return original_checksum == current_checksum

class CSVDialectDetector:
    """Enhanced CSV dialect and encoding detection"""
    
    def __init__(self):
        self.common_delimiters = [',', ';', '\t', '|', ':']
        self.common_encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
    
    def detect_encoding(self, file_path: str, sample_size: int = 10000) -> str:
        """Detect file encoding"""
        if HAS_CHARDET:
            with open(file_path, 'rb') as f:
                sample = f.read(sample_size)
                result = chardet.detect(sample)
                encoding = result.get('encoding', 'utf-8')
                confidence = result.get('confidence', 0)
                
                if confidence > 0.7:
                    return encoding
                else:
                    logger.warning(f"Low confidence ({confidence:.2f}) in encoding detection")
        
        # Fallback: try common encodings
        for encoding in self.common_encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read(1000)  # Try to read sample
                return encoding
            except UnicodeDecodeError:
                continue
        
        return 'utf-8'  # Final fallback
    
    def detect_dialect(self, file_path: str, encoding: str = 'utf-8', 
                      sample_lines: int = 10) -> Dict[str, Any]:
        """Detect CSV dialect parameters"""
        dialect_info = {
            'delimiter': ',',
            'quotechar': '"',
            'quoting': 'minimal',
            'escapechar': None,
            'skipinitialspace': False,
            'has_header': True
        }
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                sample_lines_text = []
                for i, line in enumerate(f):
                    if i >= sample_lines:
                        break
                    sample_lines_text.append(line.strip())
                
                if not sample_lines_text:
                    return dialect_info
                
                sample = '\n'.join(sample_lines_text)
                
                # Detect delimiter
                delimiter_scores = {}
                for delimiter in self.common_delimiters:
                    count = sample.count(delimiter)
                    # Check consistency across lines
                    line_counts = [line.count(delimiter) for line in sample_lines_text if line.strip()]
                    if line_counts and len(set(line_counts)) <= 2:  # Allow some variation
                        delimiter_scores[delimiter] = count
                
                if delimiter_scores:
                    best_delimiter = max(delimiter_scores, key=delimiter_scores.get)
                    dialect_info['delimiter'] = best_delimiter
                
                # Detect quote character
                quote_chars = ['"', "'"]
                for quote_char in quote_chars:
                    if quote_char in sample:
                        # Simple heuristic: if quotes appear in pairs
                        quote_count = sample.count(quote_char)
                        if quote_count % 2 == 0 and quote_count > 1:
                            dialect_info['quotechar'] = quote_char
                            break
                
                # Detect header
                if len(sample_lines_text) >= 2:
                    first_line = sample_lines_text[0].split(dialect_info['delimiter'])
                    second_line = sample_lines_text[1].split(dialect_info['delimiter'])
                    
                    # Heuristic: if first line has more text and second line has more numbers
                    first_line_numeric = sum(1 for cell in first_line if self._is_numeric(cell.strip('"\'').strip()))
                    second_line_numeric = sum(1 for cell in second_line if self._is_numeric(cell.strip('"\'').strip()))
                    
                    if first_line_numeric < second_line_numeric:
                        dialect_info['has_header'] = True
                    else:
                        dialect_info['has_header'] = False
        
        except Exception as e:
            logger.warning(f"Dialect detection failed: {e}")
        
        return dialect_info
    
    def _is_numeric(self, s: str) -> bool:
        """Check if string represents a number"""
        try:
            float(s)
            return True
        except ValueError:
            return False

class SchemaValidator:
    """Data schema validation and repair"""
    
    def __init__(self):
        self.meta_analysis_schemas = {
            'basic': DataSchema(
                required_columns=['effect', 'se', 'study'],
                optional_columns=['n', 'year', 'subgroup'],
                column_types={
                    'effect': 'float64',
                    'se': 'float64',
                    'study': 'object',
                    'n': 'int64',
                    'year': 'int64'
                },
                value_constraints={
                    'se': {'min_value': 0, 'max_value': 10},
                    'effect': {'min_value': -10, 'max_value': 10},
                    'n': {'min_value': 1}
                }
            ),
            'diagnostic_accuracy': DataSchema(
                required_columns=['tp', 'fn', 'fp', 'tn', 'study'],
                column_types={
                    'tp': 'int64', 'fn': 'int64', 'fp': 'int64', 'tn': 'int64',
                    'study': 'object'
                },
                value_constraints={
                    'tp': {'min_value': 0}, 'fn': {'min_value': 0},
                    'fp': {'min_value': 0}, 'tn': {'min_value': 0}
                }
            ),
            'network': DataSchema(
                required_columns=['treatment', 'comparator', 'effect', 'se', 'study'],
                column_types={
                    'treatment': 'object', 'comparator': 'object',
                    'effect': 'float64', 'se': 'float64', 'study': 'object'
                }
            )
        }
    
    def validate_schema(self, df: pd.DataFrame, schema_name: str = 'basic') -> Dict[str, Any]:
        """Validate DataFrame against schema"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        if schema_name not in self.meta_analysis_schemas:
            validation_result['errors'].append(f"Unknown schema: {schema_name}")
            validation_result['valid'] = False
            return validation_result
        
        schema = self.meta_analysis_schemas[schema_name]
        
        # Check required columns
        missing_columns = set(schema.required_columns) - set(df.columns)
        if missing_columns:
            validation_result['errors'].append(f"Missing required columns: {missing_columns}")
            validation_result['valid'] = False
        
        # Check column types
        for col, expected_type in schema.column_types.items():
            if col in df.columns:
                actual_type = str(df[col].dtype)
                if not self._types_compatible(actual_type, expected_type):
                    validation_result['warnings'].append(
                        f"Column '{col}' has type {actual_type}, expected {expected_type}"
                    )
        
        # Check value constraints
        for col, constraints in schema.value_constraints.items():
            if col in df.columns:
                col_validation = self._validate_column_constraints(df[col], constraints)
                if col_validation['errors']:
                    validation_result['errors'].extend([f"Column '{col}': {err}" for err in col_validation['errors']])
                    validation_result['valid'] = False
                if col_validation['warnings']:
                    validation_result['warnings'].extend([f"Column '{col}': {warn}" for warn in col_validation['warnings']])
        
        # Generate suggestions
        validation_result['suggestions'] = self._generate_repair_suggestions(df, schema, validation_result)
        
        return validation_result
    
    def _types_compatible(self, actual: str, expected: str) -> bool:
        """Check if data types are compatible"""
        type_groups = {
            'numeric': ['int64', 'int32', 'float64', 'float32'],
            'text': ['object', 'string'],
            'datetime': ['datetime64', 'datetime64[ns]']
        }
        
        for group_types in type_groups.values():
            if actual in group_types and expected in group_types:
                return True
        
        return actual == expected
    
    def _validate_column_constraints(self, column: pd.Series, constraints: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate column value constraints"""
        result = {'errors': [], 'warnings': []}
        
        # Check for missing values
        if column.isna().any():
            na_count = column.isna().sum()
            result['warnings'].append(f"{na_count} missing values found")
        
        # Check numeric constraints
        if 'min_value' in constraints:
            min_val = constraints['min_value']
            violations = column < min_val
            if violations.any():
                count = violations.sum()
                result['errors'].append(f"{count} values below minimum {min_val}")
        
        if 'max_value' in constraints:
            max_val = constraints['max_value']
            violations = column > max_val
            if violations.any():
                count = violations.sum()
                result['errors'].append(f"{count} values above maximum {max_val}")
        
        # Check for infinite values
        if pd.api.types.is_numeric_dtype(column):
            if np.isinf(column).any():
                inf_count = np.isinf(column).sum()
                result['errors'].append(f"{inf_count} infinite values found")
        
        return result
    
    def _generate_repair_suggestions(self, df: pd.DataFrame, schema: DataSchema, 
                                   validation_result: Dict[str, Any]) -> List[str]:
        """Generate suggestions for fixing validation issues"""
        suggestions = []
        
        # Missing columns
        missing_cols = set(schema.required_columns) - set(df.columns)
        if missing_cols:
            similar_cols = []
            for missing in missing_cols:
                for existing in df.columns:
                    if missing.lower() in existing.lower() or existing.lower() in missing.lower():
                        similar_cols.append(f"'{missing}' might be '{existing}'")
            if similar_cols:
                suggestions.extend(similar_cols)
        
        # Type conversion suggestions
        for col, expected_type in schema.column_types.items():
            if col in df.columns:
                actual_type = str(df[col].dtype)
                if not self._types_compatible(actual_type, expected_type):
                    suggestions.append(f"Convert '{col}' to {expected_type} using pd.to_numeric() or astype()")
        
        return suggestions
    
    def repair_data(self, df: pd.DataFrame, schema_name: str = 'basic', 
                   auto_fix: bool = True) -> Tuple[pd.DataFrame, List[str]]:
        """Attempt to repair data to match schema"""
        repairs = []
        df_repaired = df.copy()
        
        if schema_name not in self.meta_analysis_schemas:
            return df_repaired, [f"Unknown schema: {schema_name}"]
        
        schema = self.meta_analysis_schemas[schema_name]
        
        if not auto_fix:
            return df_repaired, ["Auto-repair disabled"]
        
        # Type conversions
        for col, expected_type in schema.column_types.items():
            if col in df_repaired.columns:
                try:
                    if expected_type in ['float64', 'float32']:
                        df_repaired[col] = pd.to_numeric(df_repaired[col], errors='coerce')
                        repairs.append(f"Converted '{col}' to numeric")
                    elif expected_type in ['int64', 'int32']:
                        df_repaired[col] = pd.to_numeric(df_repaired[col], errors='coerce').astype('Int64')
                        repairs.append(f"Converted '{col}' to integer")
                except Exception as e:
                    repairs.append(f"Failed to convert '{col}': {e}")
        
        # Handle outliers and invalid values
        for col, constraints in schema.value_constraints.items():
            if col in df_repaired.columns:
                if 'min_value' in constraints:
                    min_val = constraints['min_value']
                    before_count = (df_repaired[col] < min_val).sum()
                    df_repaired.loc[df_repaired[col] < min_val, col] = np.nan
                    if before_count > 0:
                        repairs.append(f"Set {before_count} values below {min_val} to NaN in '{col}'")
                
                if 'max_value' in constraints:
                    max_val = constraints['max_value']
                    before_count = (df_repaired[col] > max_val).sum()
                    df_repaired.loc[df_repaired[col] > max_val, col] = np.nan
                    if before_count > 0:
                        repairs.append(f"Set {before_count} values above {max_val} to NaN in '{col}'")
        
        return df_repaired, repairs

class ArrowDataConnector:
    """Arrow/Parquet/Feather data connector with schema hints"""
    
    def __init__(self):
        self.supported_formats = ['.parquet', '.arrow', '.feather']
    
    def read_parquet(self, file_path: str, schema_hints: Optional[Dict[str, str]] = None) -> DataLoadResult:
        """Read Parquet file with schema validation"""
        if not HAS_ARROW:
            raise ImportError("PyArrow is required for Parquet support. Install with: pip install pyarrow")
        
        try:
            # Read metadata first
            parquet_file = pq.ParquetFile(file_path)
            metadata = {
                'format': 'parquet',
                'num_rows': parquet_file.metadata.num_rows,
                'num_columns': parquet_file.metadata.num_columns,
                'file_size': os.path.getsize(file_path),
                'schema': str(parquet_file.schema_arrow)
            }
            
            # Read data
            table = pq.read_table(file_path)
            df = table.to_pandas()
            
            # Calculate checksum
            checksum = DataChecksumValidator.calculate_dataframe_checksum(df)
            
            # Validate schema if hints provided
            schema_validation = {}
            if schema_hints:
                validator = SchemaValidator()
                schema_validation = validator.validate_schema(df, schema_hints.get('schema_type', 'basic'))
            
            return DataLoadResult(
                data=df,
                metadata=metadata,
                warnings=[],
                errors=[],
                schema_validation=schema_validation,
                checksum=checksum
            )
            
        except Exception as e:
            logger.error(f"Failed to read Parquet file {file_path}: {e}")
            raise
    
    def write_parquet(self, df: pd.DataFrame, file_path: str, compression: str = 'snappy',
                     include_metadata: bool = True) -> Dict[str, Any]:
        """Write DataFrame to Parquet with metadata"""
        if not HAS_ARROW:
            raise ImportError("PyArrow is required for Parquet support")
        
        try:
            # Convert to Arrow table
            table = pa.Table.from_pandas(df)
            
            # Add custom metadata
            if include_metadata:
                custom_metadata = {
                    'created_by': 'metapython',
                    'created_at': pd.Timestamp.now().isoformat(),
                    'num_rows': str(len(df)),
                    'num_columns': str(len(df.columns)),
                    'checksum': DataChecksumValidator.calculate_dataframe_checksum(df)
                }
                
                # Add metadata to schema
                existing_metadata = table.schema.metadata or {}
                existing_metadata.update({key.encode(): value.encode() for key, value in custom_metadata.items()})
                table = table.replace_schema_metadata(existing_metadata)
            
            # Write file
            pq.write_table(table, file_path, compression=compression)
            
            return {
                'success': True,
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'compression': compression
            }
            
        except Exception as e:
            logger.error(f"Failed to write Parquet file {file_path}: {e}")
            raise
    
    def read_feather(self, file_path: str) -> DataLoadResult:
        """Read Feather file"""
        if not HAS_ARROW:
            raise ImportError("PyArrow is required for Feather support")
        
        try:
            df = feather.read_feather(file_path)
            
            metadata = {
                'format': 'feather',
                'num_rows': len(df),
                'num_columns': len(df.columns),
                'file_size': os.path.getsize(file_path)
            }
            
            checksum = DataChecksumValidator.calculate_dataframe_checksum(df)
            
            return DataLoadResult(
                data=df,
                metadata=metadata,
                warnings=[],
                errors=[],
                schema_validation={},
                checksum=checksum
            )
            
        except Exception as e:
            logger.error(f"Failed to read Feather file {file_path}: {e}")
            raise
    
    def write_feather(self, df: pd.DataFrame, file_path: str) -> Dict[str, Any]:
        """Write DataFrame to Feather format"""
        if not HAS_ARROW:
            raise ImportError("PyArrow is required for Feather support")
        
        try:
            feather.write_feather(df, file_path)
            
            return {
                'success': True,
                'file_path': file_path,
                'file_size': os.path.getsize(file_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to write Feather file {file_path}: {e}")
            raise

class EnhancedCSVConnector:
    """Enhanced CSV connector with robust parsing and validation"""
    
    def __init__(self):
        self.dialect_detector = CSVDialectDetector()
        self.schema_validator = SchemaValidator()
    
    def read_csv_robust(self, file_path: str, auto_detect: bool = True,
                       schema_name: Optional[str] = None,
                       encoding: Optional[str] = None,
                       **pandas_kwargs) -> DataLoadResult:
        """Robust CSV reading with auto-detection and validation"""
        errors = []
        warnings = []
        
        # Detect encoding
        if encoding is None and auto_detect:
            try:
                encoding = self.dialect_detector.detect_encoding(file_path)
                if encoding != 'utf-8':
                    warnings.append(f"Detected encoding: {encoding}")
            except Exception as e:
                encoding = 'utf-8'
                warnings.append(f"Encoding detection failed, using utf-8: {e}")
        else:
            encoding = encoding or 'utf-8'
        
        # Detect CSV dialect
        dialect_info = {}
        if auto_detect:
            try:
                dialect_info = self.dialect_detector.detect_dialect(file_path, encoding)
                if dialect_info['delimiter'] != ',':
                    warnings.append(f"Detected delimiter: '{dialect_info['delimiter']}'")
            except Exception as e:
                warnings.append(f"Dialect detection failed: {e}")
        
        # Merge dialect info with pandas kwargs
        read_params = {
            'encoding': encoding,
            'delimiter': dialect_info.get('delimiter', ','),
            'quotechar': dialect_info.get('quotechar', '"'),
            'header': 0 if dialect_info.get('has_header', True) else None,
            **pandas_kwargs
        }
        
        # Try reading with different strategies
        df = None
        for strategy in ['normal', 'robust', 'fallback']:
            try:
                if strategy == 'normal':
                    df = pd.read_csv(file_path, **read_params)
                elif strategy == 'robust':
                    # More forgiving parameters
                    robust_params = read_params.copy()
                    robust_params.update({
                        'error_bad_lines': False,
                        'warn_bad_lines': True,
                        'skipinitialspace': True
                    })
                    df = pd.read_csv(file_path, **robust_params)
                    warnings.append("Used robust CSV parsing")
                elif strategy == 'fallback':
                    # Minimal parameters
                    fallback_params = {
                        'encoding': encoding,
                        'header': 0,
                        'skipinitialspace': True,
                        'na_values': ['', 'NA', 'N/A', 'null', 'NULL', 'None']
                    }
                    df = pd.read_csv(file_path, **fallback_params)
                    warnings.append("Used fallback CSV parsing")
                
                break  # Success
                
            except Exception as e:
                if strategy == 'fallback':
                    errors.append(f"All CSV parsing strategies failed. Last error: {e}")
                    raise
                else:
                    warnings.append(f"CSV parsing strategy '{strategy}' failed: {e}")
        
        # Metadata
        metadata = {
            'format': 'csv',
            'encoding': encoding,
            'dialect': dialect_info,
            'num_rows': len(df),
            'num_columns': len(df.columns),
            'file_size': os.path.getsize(file_path),
            'parsing_strategy': strategy
        }
        
        # Schema validation
        schema_validation = {}
        if schema_name:
            try:
                schema_validation = self.schema_validator.validate_schema(df, schema_name)
                if not schema_validation['valid']:
                    errors.extend(schema_validation['errors'])
                warnings.extend(schema_validation['warnings'])
            except Exception as e:
                warnings.append(f"Schema validation failed: {e}")
        
        # Calculate checksum
        checksum = DataChecksumValidator.calculate_dataframe_checksum(df)
        
        return DataLoadResult(
            data=df,
            metadata=metadata,
            warnings=warnings,
            errors=errors,
            schema_validation=schema_validation,
            checksum=checksum
        )
    
    def write_csv_with_validation(self, df: pd.DataFrame, file_path: str,
                                 schema_name: Optional[str] = None,
                                 validate_before_write: bool = True,
                                 **pandas_kwargs) -> Dict[str, Any]:
        """Write CSV with optional validation"""
        result = {
            'success': False,
            'file_path': file_path,
            'validation_result': {},
            'warnings': [],
            'errors': []
        }
        
        # Pre-write validation
        if validate_before_write and schema_name:
            try:
                validation = self.schema_validator.validate_schema(df, schema_name)
                result['validation_result'] = validation
                
                if not validation['valid']:
                    result['errors'].extend(validation['errors'])
                    if not pandas_kwargs.get('force_write', False):
                        result['errors'].append("Validation failed and force_write=False")
                        return result
                
                result['warnings'].extend(validation['warnings'])
            except Exception as e:
                result['warnings'].append(f"Pre-write validation failed: {e}")
        
        # Write CSV
        try:
            write_params = {
                'index': False,
                'float_format': '%.10g',  # Consistent float formatting
                **pandas_kwargs
            }
            
            df.to_csv(file_path, **write_params)
            
            result['success'] = True
            result['file_size'] = os.path.getsize(file_path)
            result['checksum'] = DataChecksumValidator.calculate_file_checksum(file_path)
            
        except Exception as e:
            result['errors'].append(f"Failed to write CSV: {e}")
        
        return result
    
    def convert_csv_to_arrow(self, csv_path: str, output_path: str,
                           auto_detect: bool = True) -> Dict[str, Any]:
        """Convert CSV to Arrow/Parquet format"""
        result = {
            'success': False,
            'input_file': csv_path,
            'output_file': output_path,
            'conversion_info': {}
        }
        
        try:
            # Read CSV
            csv_result = self.read_csv_robust(csv_path, auto_detect=auto_detect)
            
            # Write to Arrow format
            arrow_connector = ArrowDataConnector()
            output_ext = Path(output_path).suffix.lower()
            
            if output_ext == '.parquet':
                write_result = arrow_connector.write_parquet(csv_result.data, output_path)
            elif output_ext == '.feather':
                write_result = arrow_connector.write_feather(csv_result.data, output_path)
            else:
                raise ValueError(f"Unsupported output format: {output_ext}")
            
            result['success'] = True
            result['conversion_info'] = {
                'original_size_mb': csv_result.metadata['file_size'] / (1024 * 1024),
                'converted_size_mb': write_result['file_size'] / (1024 * 1024),
                'compression_ratio': csv_result.metadata['file_size'] / write_result['file_size'],
                'rows': csv_result.metadata['num_rows'],
                'columns': csv_result.metadata['num_columns']
            }
            
        except Exception as e:
            result['errors'] = [str(e)]
        
        return result

class DataConnectorManager:
    """Central manager for all data connectors"""
    
    def __init__(self):
        self.csv_connector = EnhancedCSVConnector()
        self.arrow_connector = ArrowDataConnector() if HAS_ARROW else None
        self.checksum_validator = DataChecksumValidator()
        self.schema_validator = SchemaValidator()
    
    def read_data(self, file_path: str, format: Optional[str] = None,
                  schema_name: Optional[str] = None, **kwargs) -> DataLoadResult:
        """Universal data reader with auto-format detection"""
        file_path = Path(file_path)
        
        # Detect format if not specified
        if format is None:
            format = file_path.suffix.lower()
        
        # Route to appropriate connector
        if format in ['.csv', '.txt']:
            return self.csv_connector.read_csv_robust(
                str(file_path), schema_name=schema_name, **kwargs
            )
        elif format == '.parquet' and self.arrow_connector:
            return self.arrow_connector.read_parquet(
                str(file_path), schema_hints={'schema_type': schema_name} if schema_name else None
            )
        elif format == '.feather' and self.arrow_connector:
            return self.arrow_connector.read_feather(str(file_path))
        elif format in ['.xlsx', '.xls']:
            # Excel support
            try:
                df = pd.read_excel(file_path, **kwargs)
                metadata = {
                    'format': 'excel',
                    'num_rows': len(df),
                    'num_columns': len(df.columns),
                    'file_size': file_path.stat().st_size
                }
                checksum = self.checksum_validator.calculate_dataframe_checksum(df)
                
                schema_validation = {}
                if schema_name:
                    schema_validation = self.schema_validator.validate_schema(df, schema_name)
                
                return DataLoadResult(
                    data=df,
                    metadata=metadata,
                    warnings=[],
                    errors=[],
                    schema_validation=schema_validation,
                    checksum=checksum
                )
            except Exception as e:
                raise ValueError(f"Failed to read Excel file: {e}")
        else:
            raise ValueError(f"Unsupported file format: {format}")
    
    def get_format_capabilities(self) -> Dict[str, Any]:
        """Get supported formats and capabilities"""
        return {
            'supported_formats': {
                'csv': {
                    'read': True,
                    'write': True,
                    'auto_detection': True,
                    'schema_validation': True
                },
                'excel': {
                    'read': True,
                    'write': True,
                    'auto_detection': False,
                    'schema_validation': True
                },
                'parquet': {
                    'read': HAS_ARROW,
                    'write': HAS_ARROW,
                    'auto_detection': False,
                    'schema_validation': True,
                    'compression': HAS_ARROW
                },
                'feather': {
                    'read': HAS_ARROW,
                    'write': HAS_ARROW,
                    'auto_detection': False,
                    'schema_validation': True
                }
            },
            'features': {
                'encoding_detection': HAS_CHARDET,
                'schema_validation': True,
                'checksum_verification': True,
                'data_repair': True,
                'arrow_support': HAS_ARROW
            },
            'schemas': list(self.schema_validator.meta_analysis_schemas.keys())
        }