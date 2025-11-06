"""
Test Pandas operations used in meta-analysis.
"""

import pytest
import pandas as pd
import numpy as np


def test_dataframe_creation():
    """Test DataFrame creation."""
    df = pd.DataFrame({
        'study': ['A', 'B', 'C'],
        'effect': [0.5, 0.3, 0.7],
        'se': [0.1, 0.12, 0.09]
    })

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert len(df.columns) == 3


def test_dataframe_indexing(sample_meta_data):
    """Test DataFrame indexing."""
    df = sample_meta_data

    # Column access
    effects = df['effect_size']
    assert isinstance(effects, pd.Series)
    assert len(effects) == len(df)

    # Row access
    first_row = df.iloc[0]
    assert isinstance(first_row, pd.Series)


def test_dataframe_filtering(sample_meta_data):
    """Test DataFrame filtering."""
    df = sample_meta_data

    # Filter by condition
    large_effects = df[df['effect_size'] > 0.5]
    assert len(large_effects) <= len(df)
    assert all(large_effects['effect_size'] > 0.5)


def test_dataframe_statistics(sample_meta_data):
    """Test DataFrame statistical operations."""
    df = sample_meta_data

    mean_effect = df['effect_size'].mean()
    std_effect = df['effect_size'].std()
    min_effect = df['effect_size'].min()
    max_effect = df['effect_size'].max()

    assert isinstance(mean_effect, (float, np.floating))
    assert std_effect >= 0
    assert min_effect <= mean_effect <= max_effect


def test_dataframe_sorting(sample_meta_data):
    """Test DataFrame sorting."""
    df = sample_meta_data

    # Sort by effect size
    sorted_df = df.sort_values('effect_size')

    first_effect = sorted_df.iloc[0]['effect_size']
    last_effect = sorted_df.iloc[-1]['effect_size']

    assert first_effect <= last_effect


def test_dataframe_groupby(sample_binary_data):
    """Test DataFrame groupby operations."""
    df = sample_binary_data.copy()

    # Add a category column
    df['category'] = ['A', 'A', 'B']

    grouped = df.groupby('category')['ai'].sum()

    assert isinstance(grouped, pd.Series)
    assert len(grouped) == 2


def test_dataframe_merge():
    """Test DataFrame merging."""
    df1 = pd.DataFrame({
        'study': ['A', 'B', 'C'],
        'effect': [0.5, 0.3, 0.7]
    })

    df2 = pd.DataFrame({
        'study': ['A', 'B', 'C'],
        'year': [2020, 2021, 2022]
    })

    merged = pd.merge(df1, df2, on='study')

    assert len(merged) == 3
    assert 'effect' in merged.columns
    assert 'year' in merged.columns


def test_dataframe_apply(sample_meta_data):
    """Test DataFrame apply function."""
    df = sample_meta_data

    # Calculate variance from SE
    df['variance'] = df['se'].apply(lambda x: x ** 2)

    assert 'variance' in df.columns
    assert all(df['variance'] > 0)


def test_dataframe_null_handling():
    """Test handling of null values."""
    df = pd.DataFrame({
        'study': ['A', 'B', 'C', 'D'],
        'effect': [0.5, np.nan, 0.7, 0.3]
    })

    # Check for nulls
    has_null = df['effect'].isnull().any()
    assert has_null

    # Drop nulls
    clean_df = df.dropna()
    assert len(clean_df) == 3

    # Fill nulls
    filled_df = df.fillna(0)
    assert not filled_df['effect'].isnull().any()


def test_dataframe_describe(sample_meta_data):
    """Test DataFrame describe method."""
    df = sample_meta_data

    desc = df['effect_size'].describe()

    assert 'mean' in desc
    assert 'std' in desc
    assert 'min' in desc
    assert 'max' in desc
    assert desc['count'] == len(df)


def test_dataframe_value_counts():
    """Test value_counts method."""
    df = pd.DataFrame({
        'category': ['A', 'B', 'A', 'C', 'B', 'A']
    })

    counts = df['category'].value_counts()

    assert counts['A'] == 3
    assert counts['B'] == 2
    assert counts['C'] == 1


def test_dataframe_concatenation():
    """Test DataFrame concatenation."""
    df1 = pd.DataFrame({'study': ['A', 'B'], 'effect': [0.5, 0.3]})
    df2 = pd.DataFrame({'study': ['C', 'D'], 'effect': [0.7, 0.4]})

    combined = pd.concat([df1, df2], ignore_index=True)

    assert len(combined) == 4
    assert list(combined['study']) == ['A', 'B', 'C', 'D']


def test_dataframe_rename():
    """Test DataFrame column renaming."""
    df = pd.DataFrame({'old_name': [1, 2, 3]})

    df_renamed = df.rename(columns={'old_name': 'new_name'})

    assert 'new_name' in df_renamed.columns
    assert 'old_name' not in df_renamed.columns


def test_dataframe_to_numpy(sample_meta_data):
    """Test converting DataFrame to NumPy array."""
    df = sample_meta_data

    arr = df['effect_size'].to_numpy()

    assert isinstance(arr, np.ndarray)
    assert len(arr) == len(df)


def test_series_operations():
    """Test Pandas Series operations."""
    s = pd.Series([1, 2, 3, 4, 5])

    # Basic operations
    assert s.sum() == 15
    assert s.mean() == 3.0
    assert s.max() == 5
    assert s.min() == 1

    # Indexing
    assert s[0] == 1
    assert s.iloc[-1] == 5
