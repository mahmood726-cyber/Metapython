"""
Automated module splitter for metapython.py
Splits the monolithic file into logical modules
"""

import re
import os

def read_file(filepath):
    with open(filepath, 'r') as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, 'w') as f:
        f.write(content)

def extract_section(content, start_marker, end_marker=None):
    """Extract section between markers"""
    start_idx = content.find(start_marker)
    if start_idx == -1:
        return ""

    if end_marker:
        end_idx = content.find(end_marker, start_idx)
        if end_idx == -1:
            return content[start_idx:]
        return content[start_idx:end_idx]
    return content[start_idx:]

def extract_class(content, class_name):
    """Extract a class and its methods"""
    pattern = rf'^class {class_name}.*?(?=^class |\Z)'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(0)
    return ""

def create_header(description):
    """Create standard module header"""
    return f'''"""
{description}

Part of the MetaPython meta-analysis library.
"""

import datetime
import logging
import re
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any, Union

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import norm, chi2, t
from scipy.optimize import minimize

logger = logging.getLogger(__name__)

'''

def split_metapython():
    """Main splitting logic"""
    print("Reading metapython.py...")
    content = read_file('/home/user/Metapython/metapython.py')

    # Ensure meta_core directory exists
    os.makedirs('/home/user/Metapython/meta_core', exist_ok=True)

    print("Creating config.py...")
    # Extract config module content (lines 1-518)
    config_lines = content.split('\n')[68:518]  # Constants through utility functions
    config_content = create_header("Core configuration, constants, dataclasses, and utility functions")
    config_content += '\n'.join(config_lines)
    write_file('/home/user/Metapython/meta_core/config.py', config_content)

    print("Module splitting complete!")
    print("\nCreated files:")
    print("  - meta_core/__init__.py")
    print("  - meta_core/config.py")

if __name__ == "__main__":
    split_metapython()
