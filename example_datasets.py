"""
Example datasets for parity testing with R packages
===================================================

Classic meta-analysis datasets for validation against R implementations
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

def bcg_vaccine_data() -> Dict[str, Any]:
    """
    BCG vaccine data - classic meta-analysis dataset
    From metafor package
    """
    data = {
        'study': [
            'Aronson', 'Ferguson & Simes', 'Rosenthal et al', 'Hart & Sutherland',
            'Frimodt-Moller et al', 'Stein & Aronson', 'Vandiviere et al',
            'TPT Madras', 'Coetzee & Berjak', 'Rosenthal et al',
            'Comstock et al', 'Comstock & Webster', 'Comstock et al'
        ],
        'tpos': [4, 6, 3, 62, 33, 180, 8, 505, 29, 17, 186, 5, 27],
        'tneg': [119, 300, 228, 13536, 5036, 1361, 2537, 87886, 7470, 1699, 50448, 9821, 7499],
        'cpos': [11, 29, 11, 248, 47, 372, 10, 499, 45, 65, 141, 3, 29],
        'cneg': [128, 274, 209, 12619, 5761, 1079, 619, 87892, 7232, 1600, 27197, 7827, 7277],
        'ablat': [44, 55, 42, 52, 13, 44, 19, 13, 27, 42, 18, 33, 33],
        'alloc': ['random', 'random', 'random', 'random', 'random', 'random', 
                 'alternate', 'alternate', 'alternate', 'alternate', 'alternate', 
                 'systematic', 'systematic']
    }
    
    df = pd.DataFrame(data)
    
    # Calculate log risk ratio and variance
    rr = (df['tpos'] / (df['tpos'] + df['tneg'])) / (df['cpos'] / (df['cpos'] + df['cneg']))
    df['yi'] = np.log(rr)
    df['vi'] = (1/df['tpos'] - 1/(df['tpos']+df['tneg']) + 1/df['cpos'] - 1/(df['cpos']+df['cneg']))
    df['sei'] = np.sqrt(df['vi'])
    
    return {
        'data': df,
        'description': 'BCG vaccine efficacy against tuberculosis',
        'measure': 'log risk ratio',
        'reference': 'Colditz et al. (1994)'
    }

def smoking_cessation_network() -> Dict[str, Any]:
    """
    Smoking cessation network meta-analysis data
    Adapted for network structure
    """
    data = {
        'study': ['Study1', 'Study1', 'Study1', 'Study2', 'Study2', 
                 'Study3', 'Study3', 'Study4', 'Study4', 'Study5', 'Study5'],
        'treatment': ['Placebo', 'NRT', 'Bupropion', 'Placebo', 'NRT',
                     'Placebo', 'Varenicline', 'NRT', 'Bupropion', 'NRT', 'Varenicline'],
        'yi': [0.0, 0.51, 0.83, 0.0, 0.48, 0.0, 1.12, 0.52, 0.79, 0.49, 1.08],
        'sei': [0.0, 0.12, 0.15, 0.0, 0.14, 0.0, 0.18, 0.13, 0.16, 0.11, 0.17],
        'n': [100, 98, 102, 150, 148, 120, 125, 180, 175, 200, 195],
        'events': [15, 35, 42, 22, 45, 18, 58, 52, 67, 58, 98]
    }
    
    df = pd.DataFrame(data)
    df['vi'] = df['sei']**2
    
    return {
        'data': df,
        'description': 'Smoking cessation interventions network',
        'measure': 'log odds ratio',
        'reference': 'Hypothetical network data'
    }

def antidepressant_network() -> Dict[str, Any]:
    """
    Antidepressant network meta-analysis data
    Simplified version for testing
    """
    data = {
        'study': ['Cipriani1', 'Cipriani1', 'Cipriani2', 'Cipriani2', 'Cipriani2',
                 'Cipriani3', 'Cipriani3', 'Cipriani4', 'Cipriani4', 'Cipriani5', 'Cipriani5'],
        'treatment': ['Placebo', 'Fluoxetine', 'Placebo', 'Sertraline', 'Paroxetine',
                     'Fluoxetine', 'Sertraline', 'Paroxetine', 'Venlafaxine', 'Fluoxetine', 'Venlafaxine'],
        'yi': [0.0, 0.32, 0.0, 0.28, 0.35, 0.31, 0.29, 0.34, 0.41, 0.33, 0.39],
        'sei': [0.0, 0.08, 0.0, 0.09, 0.10, 0.08, 0.09, 0.11, 0.12, 0.07, 0.11],
        'n': [80, 85, 120, 115, 110, 90, 95, 75, 78, 100, 105],
        'events': [25, 42, 35, 48, 52, 38, 44, 34, 41, 45, 53]
    }
    
    df = pd.DataFrame(data)
    df['vi'] = df['sei']**2
    
    return {
        'data': df,
        'description': 'Antidepressant efficacy network',
        'measure': 'log odds ratio', 
        'reference': 'Based on Cipriani et al. (2018)'
    }

def multilevel_example() -> Dict[str, Any]:
    """
    Example multilevel data with multiple outcomes per study
    """
    data = {
        'study': ['Study1', 'Study1', 'Study1', 'Study2', 'Study2', 'Study2',
                 'Study3', 'Study3', 'Study4', 'Study4', 'Study5', 'Study5'],
        'outcome': ['Depression', 'Anxiety', 'Quality of Life', 'Depression', 'Anxiety', 'Quality of Life',
                   'Depression', 'Anxiety', 'Depression', 'Anxiety', 'Depression', 'Quality of Life'],
        'yi': [0.45, 0.32, 0.28, 0.52, 0.38, 0.31, 0.41, 0.29, 0.48, 0.35, 0.39, 0.26],
        'vi': [0.025, 0.030, 0.035, 0.028, 0.032, 0.038, 0.026, 0.031, 0.027, 0.033, 0.024, 0.036],
        'n1': [50, 50, 50, 60, 60, 60, 45, 45, 55, 55, 48, 48],
        'n2': [52, 52, 52, 58, 58, 58, 47, 47, 53, 53, 50, 50]
    }
    
    df = pd.DataFrame(data)
    df['sei'] = np.sqrt(df['vi'])
    
    return {
        'data': df,
        'description': 'Multilevel meta-analysis with multiple outcomes',
        'measure': 'standardized mean difference',
        'reference': 'Hypothetical multilevel data'
    }

def correlated_effects_example() -> Dict[str, Any]:
    """
    Example data for correlated effects analysis
    """
    data = {
        'study': ['A', 'A', 'A', 'B', 'B', 'C', 'C', 'C', 'D', 'D', 'E'],
        'effect_id': [1, 2, 3, 1, 2, 1, 2, 3, 1, 2, 1],
        'yi': [0.25, 0.32, 0.18, 0.41, 0.38, 0.29, 0.35, 0.22, 0.46, 0.42, 0.31],
        'vi': [0.020, 0.025, 0.022, 0.028, 0.026, 0.024, 0.027, 0.023, 0.030, 0.029, 0.021],
        'n': [80, 80, 80, 95, 95, 70, 70, 70, 110, 110, 65]
    }
    
    df = pd.DataFrame(data)
    df['sei'] = np.sqrt(df['vi'])
    
    return {
        'data': df,
        'description': 'Correlated effects from studies with multiple effect sizes',
        'measure': 'correlation coefficient (Fisher z)',
        'reference': 'Hypothetical correlated data'
    }

# Dataset registry
DATASETS = {
    'bcg': bcg_vaccine_data,
    'smoking_network': smoking_cessation_network,
    'antidepressant_network': antidepressant_network,
    'multilevel': multilevel_example,
    'correlated': correlated_effects_example
}

def get_example_dataset(name: str) -> Dict[str, Any]:
    """Get example dataset by name"""
    if name not in DATASETS:
        available = list(DATASETS.keys())
        raise ValueError(f"Dataset '{name}' not found. Available: {available}")
    
    return DATASETS[name]()

def list_datasets() -> Dict[str, str]:
    """List available example datasets"""
    descriptions = {}
    for name, func in DATASETS.items():
        dataset = func()
        descriptions[name] = dataset['description']
    
    return descriptions