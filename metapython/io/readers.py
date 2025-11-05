"""
Data readers and exporters for various file formats.

Provides convenient functions to import meta-analysis data from
common research data formats and export results.
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
import pandas as pd
import numpy as np

from metapython.core.utils import validate_file_path
from metapython.core.config import logger


def read_csv(
    file_path: str,
    effect_col: str = 'effect',
    se_col: Optional[str] = None,
    ci_low_col: Optional[str] = None,
    ci_high_col: Optional[str] = None,
    study_col: str = 'study',
    **kwargs
) -> pd.DataFrame:
    """
    Read meta-analysis data from CSV file.

    Args:
        file_path: Path to CSV file
        effect_col: Column name for effect sizes
        se_col: Column name for standard errors (optional if CIs provided)
        ci_low_col: Column name for lower CI bound
        ci_high_col: Column name for upper CI bound
        study_col: Column name for study identifiers
        **kwargs: Additional arguments passed to pd.read_csv()

    Returns:
        DataFrame with standardized column names

    Example:
        >>> data = read_csv('meta_data.csv', effect_col='SMD', se_col='SE')
    """
    validated_path = validate_file_path(
        file_path,
        allowed_extensions=['.csv', '.txt']
    )

    df = pd.read_csv(validated_path, **kwargs)

    # Validate required columns
    if effect_col not in df.columns:
        raise ValueError(f"Effect column '{effect_col}' not found in file")

    # Calculate SE from CIs if not provided
    if se_col is None and ci_low_col is not None and ci_high_col is not None:
        if ci_low_col not in df.columns or ci_high_col not in df.columns:
            raise ValueError(f"CI columns '{ci_low_col}' or '{ci_high_col}' not found")

        # SE = (CI_high - CI_low) / (2 * 1.96)
        df['se'] = (df[ci_high_col] - df[ci_low_col]) / 3.92
        logger.info("Standard errors calculated from confidence intervals")
    elif se_col not in df.columns:
        raise ValueError(
            f"Either SE column '{se_col}' or CI columns must be provided"
        )
    else:
        df['se'] = df[se_col]

    # Standardize column names
    df['effect'] = df[effect_col]

    if study_col in df.columns:
        df['study'] = df[study_col]
    else:
        df['study'] = [f"Study {i+1}" for i in range(len(df))]

    logger.info(f"Loaded {len(df)} studies from {file_path}")

    return df[['study', 'effect', 'se']]


def read_excel(
    file_path: str,
    sheet_name: str = 0,
    effect_col: str = 'effect',
    se_col: Optional[str] = None,
    ci_low_col: Optional[str] = None,
    ci_high_col: Optional[str] = None,
    study_col: str = 'study',
    **kwargs
) -> pd.DataFrame:
    """
    Read meta-analysis data from Excel file.

    Args:
        file_path: Path to Excel file (.xlsx or .xls)
        sheet_name: Sheet name or index (default: first sheet)
        effect_col: Column name for effect sizes
        se_col: Column name for standard errors
        ci_low_col: Column name for lower CI bound
        ci_high_col: Column name for upper CI bound
        study_col: Column name for study identifiers
        **kwargs: Additional arguments passed to pd.read_excel()

    Returns:
        DataFrame with standardized column names
    """
    validated_path = validate_file_path(
        file_path,
        allowed_extensions=['.xlsx', '.xls']
    )

    try:
        df = pd.read_excel(validated_path, sheet_name=sheet_name, **kwargs)
    except ImportError:
        raise ImportError(
            "openpyxl required for Excel files. "
            "Install with: pip install openpyxl"
        )

    # Use same logic as read_csv
    if effect_col not in df.columns:
        raise ValueError(f"Effect column '{effect_col}' not found")

    if se_col is None and ci_low_col is not None and ci_high_col is not None:
        df['se'] = (df[ci_high_col] - df[ci_low_col]) / 3.92
    elif se_col in df.columns:
        df['se'] = df[se_col]
    else:
        raise ValueError("Either SE or CI columns must be provided")

    df['effect'] = df[effect_col]
    df['study'] = df[study_col] if study_col in df.columns else [
        f"Study {i+1}" for i in range(len(df))
    ]

    logger.info(f"Loaded {len(df)} studies from {file_path}")

    return df[['study', 'effect', 'se']]


def read_spss(
    file_path: str,
    effect_col: str = 'effect',
    se_col: str = 'se',
    study_col: str = 'study',
) -> pd.DataFrame:
    """
    Read meta-analysis data from SPSS file (.sav).

    Args:
        file_path: Path to SPSS .sav file
        effect_col: Column name for effect sizes
        se_col: Column name for standard errors
        study_col: Column name for study identifiers

    Returns:
        DataFrame with standardized column names
    """
    validated_path = validate_file_path(
        file_path,
        allowed_extensions=['.sav']
    )

    try:
        import pyreadstat
    except ImportError:
        raise ImportError(
            "pyreadstat required for SPSS files. "
            "Install with: pip install pyreadstat"
        )

    df, meta = pyreadstat.read_sav(validated_path)

    if effect_col not in df.columns:
        raise ValueError(f"Effect column '{effect_col}' not found")

    if se_col not in df.columns:
        raise ValueError(f"SE column '{se_col}' not found")

    df['effect'] = df[effect_col]
    df['se'] = df[se_col]
    df['study'] = df[study_col] if study_col in df.columns else [
        f"Study {i+1}" for i in range(len(df))
    ]

    logger.info(f"Loaded {len(df)} studies from SPSS file")

    return df[['study', 'effect', 'se']]


def read_stata(
    file_path: str,
    effect_col: str = 'effect',
    se_col: str = 'se',
    study_col: str = 'study',
) -> pd.DataFrame:
    """
    Read meta-analysis data from Stata file (.dta).

    Args:
        file_path: Path to Stata .dta file
        effect_col: Column name for effect sizes
        se_col: Column name for standard errors
        study_col: Column name for study identifiers

    Returns:
        DataFrame with standardized column names
    """
    validated_path = validate_file_path(
        file_path,
        allowed_extensions=['.dta']
    )

    try:
        import pyreadstat
    except ImportError:
        raise ImportError(
            "pyreadstat required for Stata files. "
            "Install with: pip install pyreadstat"
        )

    df, meta = pyreadstat.read_dta(validated_path)

    if effect_col not in df.columns:
        raise ValueError(f"Effect column '{effect_col}' not found")

    if se_col not in df.columns:
        raise ValueError(f"SE column '{se_col}' not found")

    df['effect'] = df[effect_col]
    df['se'] = df[se_col]
    df['study'] = df[study_col] if study_col in df.columns else [
        f"Study {i+1}" for i in range(len(df))
    ]

    logger.info(f"Loaded {len(df)} studies from Stata file")

    return df[['study', 'effect', 'se']]


def export_results(
    results: Dict[str, Any],
    output_path: str,
    format: str = 'auto',
) -> None:
    """
    Export meta-analysis results to file.

    Args:
        results: Dictionary with meta-analysis results
        output_path: Path for output file
        format: Output format ('csv', 'excel', 'json', or 'auto' to detect from extension)

    Example:
        >>> export_results(results, 'meta_analysis_results.xlsx')
    """
    output_path_obj = Path(output_path)

    # Auto-detect format
    if format == 'auto':
        suffix = output_path_obj.suffix.lower()
        if suffix == '.csv':
            format = 'csv'
        elif suffix in ['.xlsx', '.xls']:
            format = 'excel'
        elif suffix == '.json':
            format = 'json'
        else:
            format = 'csv'
            output_path_obj = output_path_obj.with_suffix('.csv')

    # Convert results to DataFrame
    results_flat = {}
    for key, value in results.items():
        if isinstance(value, (int, float, str, bool)):
            results_flat[key] = value
        elif isinstance(value, np.ndarray):
            results_flat[key] = value.tolist()
        elif hasattr(value, '__dict__'):
            # Handle dataclass objects
            for k, v in value.__dict__.items():
                results_flat[f"{key}_{k}"] = v

    df = pd.DataFrame([results_flat])

    # Export
    if format == 'csv':
        df.to_csv(output_path_obj, index=False)
    elif format == 'excel':
        df.to_excel(output_path_obj, index=False)
    elif format == 'json':
        df.to_json(output_path_obj, orient='records', indent=2)

    logger.info(f"Results exported to {output_path_obj}")


__all__ = [
    'read_csv',
    'read_excel',
    'read_spss',
    'read_stata',
    'export_results',
]
