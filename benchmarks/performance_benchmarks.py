"""
Performance benchmarks for MetaPython optimizations

Compares performance of optimized vs original implementations.

Run with: python benchmarks/performance_benchmarks.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import numpy as np
import pandas as pd
from metapython import UnifiedMetaAnalysis, UnifiedMetaConfig

def generate_test_data(n_studies):
    """Generate random test data"""
    np.random.seed(42)
    return pd.DataFrame({
        'study': [f'Study {i+1}' for i in range(n_studies)],
        'effect': np.random.normal(0.3, 0.2, n_studies),
        'se': np.random.uniform(0.05, 0.2, n_studies)
    })

def benchmark_leave_one_out():
    """Benchmark leave-one-out analysis performance"""
    print("\n" + "="*60)
    print("BENCHMARK: Leave-One-Out Analysis")
    print("="*60)

    for n_studies in [10, 25, 50, 100]:
        data = generate_test_data(n_studies)
        meta = UnifiedMetaAnalysis(data, 'effect', 'se', 'study')
        meta.analyze(include_bias_tests=False, include_conflicts=False)

        # Fast mode (vectorized)
        start = time.time()
        result_fast = meta.leave_one_out_analysis(fast=True)
        time_fast = time.time() - start

        # Slow mode (original)
        start = time.time()
        result_slow = meta.leave_one_out_analysis(fast=False)
        time_slow = time.time() - start

        speedup = time_slow / time_fast if time_fast > 0 else float('inf')

        print(f"\n{n_studies} studies:")
        print(f"  Fast mode:  {time_fast*1000:.2f} ms")
        print(f"  Slow mode:  {time_slow*1000:.2f} ms")
        print(f"  Speedup:    {speedup:.1f}x")

        # Verify results are similar
        diff = abs(result_fast['loo_effect'].mean() - result_slow['loo_effect'].mean())
        print(f"  Mean difference: {diff:.6f}")

def benchmark_matrix_operations():
    """Benchmark matrix operations (dense vs broadcast)"""
    print("\n" + "="*60)
    print("BENCHMARK: Matrix Operations (Dense vs Broadcast)")
    print("="*60)

    for n in [50, 100, 500, 1000]:
        weights = np.random.rand(n) + 0.1
        X = np.random.randn(n, 2)

        # Dense diagonal matrix (old method)
        start = time.time()
        W_dense = np.diag(weights)
        XWX_dense = X.T @ W_dense @ X
        time_dense = time.time() - start

        # Broadcasting (optimized)
        start = time.time()
        XWX_broadcast = X.T @ (weights[:, None] * X)
        time_broadcast = time.time() - start

        speedup = time_dense / time_broadcast if time_broadcast > 0 else float('inf')
        memory_saved_mb = (n * n * 8 - n * 8) / (1024 * 1024)  # Dense vs vector

        print(f"\n{n} observations:")
        print(f"  Dense method:     {time_dense*1000:.3f} ms")
        print(f"  Broadcast method: {time_broadcast*1000:.3f} ms")
        print(f"  Speedup:          {speedup:.1f}x")
        print(f"  Memory saved:     {memory_saved_mb:.2f} MB")

        # Verify results are identical
        diff = np.max(np.abs(XWX_dense - XWX_broadcast))
        print(f"  Max difference:   {diff:.2e}")

def benchmark_analysis_workflow():
    """Benchmark complete analysis workflow"""
    print("\n" + "="*60)
    print("BENCHMARK: Complete Analysis Workflow")
    print("="*60)

    for n_studies in [10, 25, 50, 100]:
        data = generate_test_data(n_studies)

        start = time.time()
        meta = UnifiedMetaAnalysis(data, 'effect', 'se', 'study')
        meta.analyze(include_bias_tests=True, include_conflicts=True)
        elapsed = time.time() - start

        print(f"\n{n_studies} studies:")
        print(f"  Total time: {elapsed*1000:.2f} ms")
        print(f"  Per study:  {elapsed*1000/n_studies:.2f} ms")

def benchmark_tau_squared_estimation():
    """Benchmark tau² estimation methods"""
    print("\n" + "="*60)
    print("BENCHMARK: Tau² Estimation Methods")
    print("="*60)

    from metapython import TauSquaredEstimators

    for n_studies in [10, 25, 50, 100]:
        np.random.seed(42)
        effects = np.random.normal(0.3, 0.2, n_studies)
        variances = np.random.uniform(0.01, 0.1, n_studies)

        # DerSimonian-Laird
        start = time.time()
        tau2_dl = TauSquaredEstimators.dersimonian_laird(effects, variances)
        time_dl = time.time() - start

        # REML
        start = time.time()
        tau2_reml = TauSquaredEstimators.restricted_ml(effects, variances)
        time_reml = time.time() - start

        print(f"\n{n_studies} studies:")
        print(f"  DL method:   {time_dl*1000:.3f} ms (τ²={tau2_dl:.4f})")
        print(f"  REML method: {time_reml*1000:.3f} ms (τ²={tau2_reml:.4f})")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("MetaPython Performance Benchmarks")
    print("Testing optimizations and improvements")
    print("="*60)

    try:
        benchmark_leave_one_out()
        benchmark_matrix_operations()
        benchmark_analysis_workflow()
        benchmark_tau_squared_estimation()

        print("\n" + "="*60)
        print("Benchmarks completed successfully!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n✗ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
