"""
Test NumPy operations used in meta-analysis.
"""

import pytest
import numpy as np


def test_array_creation():
    """Test NumPy array creation."""
    arr = np.array([1, 2, 3, 4, 5])
    assert len(arr) == 5
    assert arr.dtype in [np.int64, np.int32]


def test_array_operations():
    """Test basic array operations."""
    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])

    # Addition
    c = a + b
    assert np.array_equal(c, np.array([5, 7, 9]))

    # Multiplication
    d = a * b
    assert np.array_equal(d, np.array([4, 10, 18]))

    # Element-wise square
    e = a ** 2
    assert np.array_equal(e, np.array([1, 4, 9]))


def test_array_statistics():
    """Test statistical operations on arrays."""
    arr = np.array([1, 2, 3, 4, 5])

    assert np.mean(arr) == 3.0
    assert np.median(arr) == 3.0
    assert np.std(arr) > 0
    assert np.var(arr) > 0
    assert np.min(arr) == 1
    assert np.max(arr) == 5


def test_array_filtering():
    """Test array filtering operations."""
    arr = np.array([1, 2, 3, 4, 5])

    # Filter values greater than 3
    filtered = arr[arr > 3]
    assert len(filtered) == 2
    assert np.array_equal(filtered, np.array([4, 5]))


def test_random_number_generation(random_seed):
    """Test random number generation with seed."""
    np.random.seed(random_seed)
    rand1 = np.random.rand(5)

    np.random.seed(random_seed)
    rand2 = np.random.rand(5)

    # Should be identical with same seed
    assert np.array_equal(rand1, rand2)


def test_matrix_operations():
    """Test matrix operations."""
    A = np.array([[1, 2], [3, 4]])
    B = np.array([[5, 6], [7, 8]])

    # Matrix multiplication
    C = np.dot(A, B)
    assert C.shape == (2, 2)

    # Transpose
    At = A.T
    assert At[0, 1] == A[1, 0]


def test_array_reshaping():
    """Test array reshaping."""
    arr = np.array([1, 2, 3, 4, 5, 6])

    # Reshape to 2x3
    reshaped = arr.reshape(2, 3)
    assert reshaped.shape == (2, 3)
    assert reshaped[0, 0] == 1
    assert reshaped[1, 2] == 6


def test_boolean_indexing():
    """Test boolean indexing."""
    arr = np.array([1, 2, 3, 4, 5])
    mask = arr > 2

    result = arr[mask]
    assert np.array_equal(result, np.array([3, 4, 5]))


def test_nan_handling():
    """Test NaN handling."""
    arr = np.array([1.0, 2.0, np.nan, 4.0, 5.0])

    # Check for NaN
    has_nan = np.isnan(arr).any()
    assert has_nan

    # Remove NaN
    clean = arr[~np.isnan(arr)]
    assert len(clean) == 4
    assert not np.isnan(clean).any()


def test_array_concatenation():
    """Test array concatenation."""
    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])

    c = np.concatenate([a, b])
    assert len(c) == 6
    assert np.array_equal(c, np.array([1, 2, 3, 4, 5, 6]))


def test_linspace():
    """Test linspace for creating evenly spaced arrays."""
    arr = np.linspace(0, 1, 11)

    assert len(arr) == 11
    assert arr[0] == 0.0
    assert arr[-1] == 1.0
    assert arr[5] == pytest.approx(0.5)


def test_where_function():
    """Test np.where for conditional operations."""
    arr = np.array([1, 2, 3, 4, 5])

    # Replace values > 3 with 0
    result = np.where(arr > 3, 0, arr)
    assert np.array_equal(result, np.array([1, 2, 3, 0, 0]))


def test_array_sorting():
    """Test array sorting."""
    arr = np.array([3, 1, 4, 1, 5, 9, 2, 6])

    sorted_arr = np.sort(arr)
    assert sorted_arr[0] == 1
    assert sorted_arr[-1] == 9

    # Argsort returns indices
    indices = np.argsort(arr)
    assert arr[indices[0]] == 1


def test_array_unique():
    """Test finding unique values."""
    arr = np.array([1, 2, 2, 3, 3, 3, 4])

    unique = np.unique(arr)
    assert len(unique) == 4
    assert np.array_equal(unique, np.array([1, 2, 3, 4]))


def test_mathematical_functions():
    """Test mathematical functions."""
    arr = np.array([1, 2, 3, 4])

    # Exponential
    exp_arr = np.exp(arr)
    assert all(exp_arr > 0)
    assert exp_arr[0] == pytest.approx(np.e)

    # Logarithm
    log_arr = np.log(arr)
    assert log_arr[0] == 0.0

    # Square root
    sqrt_arr = np.sqrt(arr)
    assert sqrt_arr[0] == 1.0
    assert sqrt_arr[3] == 2.0
