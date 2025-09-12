"""
Performance Profiling and Optimization Module - Phase 8
Enhanced performance monitoring, profiling, and optimization capabilities
"""

import time
import psutil
import threading
from typing import Dict, Any, List, Optional, Callable, Tuple
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from functools import wraps
import logging
import json
from pathlib import Path

# GPU monitoring (optional)
try:
    import GPUtil
    HAS_GPU_UTILS = True
except ImportError:
    HAS_GPU_UTILS = False

# Memory profiling (optional)
try:
    from memory_profiler import profile as memory_profile
    HAS_MEMORY_PROFILER = True
except ImportError:
    HAS_MEMORY_PROFILER = False

# Line profiling (optional)
try:
    import line_profiler
    HAS_LINE_PROFILER = True
except ImportError:
    HAS_LINE_PROFILER = False

# Numba for JIT compilation
try:
    from numba import jit, njit, prange
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics collection"""
    execution_time: float = 0.0
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    peak_memory_mb: float = 0.0
    gpu_utilization: float = 0.0
    gpu_memory_mb: float = 0.0
    function_name: str = ""
    timestamp: str = ""
    thread_id: int = 0
    process_id: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'execution_time': self.execution_time,
            'cpu_percent': self.cpu_percent,
            'memory_mb': self.memory_mb,
            'peak_memory_mb': self.peak_memory_mb,
            'gpu_utilization': self.gpu_utilization,
            'gpu_memory_mb': self.gpu_memory_mb,
            'function_name': self.function_name,
            'timestamp': self.timestamp,
            'thread_id': self.thread_id,
            'process_id': self.process_id
        }

class PerformanceProfiler:
    """Comprehensive performance profiler for meta-analysis operations"""
    
    def __init__(self, enabled: bool = True, sample_interval: float = 0.1):
        self.enabled = enabled
        self.sample_interval = sample_interval
        self.metrics_history: List[PerformanceMetrics] = []
        self.monitoring_thread: Optional[threading.Thread] = None
        self.stop_monitoring = threading.Event()
        self.current_metrics = PerformanceMetrics()
        
    def start_monitoring(self) -> None:
        """Start background performance monitoring"""
        if not self.enabled:
            return
            
        self.stop_monitoring.clear()
        self.monitoring_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitoring_thread.start()
        
    def stop_monitoring(self) -> None:
        """Stop background performance monitoring"""
        if self.monitoring_thread:
            self.stop_monitoring.set()
            self.monitoring_thread.join()
            
    def _monitor_loop(self) -> None:
        """Background monitoring loop"""
        process = psutil.Process()
        
        while not self.stop_monitoring.is_set():
            try:
                # CPU and memory monitoring
                cpu_percent = process.cpu_percent()
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                
                # GPU monitoring if available
                gpu_util = 0.0
                gpu_memory = 0.0
                if HAS_GPU_UTILS:
                    try:
                        gpus = GPUtil.getGPUs()
                        if gpus:
                            gpu = gpus[0]  # Use first GPU
                            gpu_util = gpu.load * 100
                            gpu_memory = gpu.memoryUsed
                    except Exception:
                        pass
                
                # Update current metrics
                self.current_metrics.cpu_percent = cpu_percent
                self.current_metrics.memory_mb = memory_mb
                self.current_metrics.gpu_utilization = gpu_util
                self.current_metrics.gpu_memory_mb = gpu_memory
                self.current_metrics.peak_memory_mb = max(
                    self.current_metrics.peak_memory_mb, memory_mb
                )
                
                time.sleep(self.sample_interval)
                
            except Exception as e:
                logger.warning(f"Performance monitoring error: {e}")
                time.sleep(self.sample_interval)
    
    def profile_function(self, func: Callable) -> Callable:
        """Decorator to profile function performance"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.enabled:
                return func(*args, **kwargs)
            
            # Start monitoring
            self.start_monitoring()
            
            # Reset metrics
            self.current_metrics = PerformanceMetrics()
            self.current_metrics.function_name = func.__name__
            self.current_metrics.timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            self.current_metrics.thread_id = threading.get_ident()
            self.current_metrics.process_id = psutil.Process().pid
            
            start_time = time.perf_counter()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                self.current_metrics.execution_time = end_time - start_time
                
                # Stop monitoring and save metrics
                self.stop_monitoring()
                self.metrics_history.append(self.current_metrics)
                
                # Log performance summary
                logger.info(
                    f"Performance: {func.__name__} took {self.current_metrics.execution_time:.3f}s, "
                    f"peak memory: {self.current_metrics.peak_memory_mb:.1f}MB"
                )
        
        return wrapper
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics"""
        if not self.metrics_history:
            return {"message": "No performance data available"}
        
        execution_times = [m.execution_time for m in self.metrics_history]
        memory_usage = [m.peak_memory_mb for m in self.metrics_history]
        cpu_usage = [m.cpu_percent for m in self.metrics_history]
        
        return {
            "total_functions_profiled": len(self.metrics_history),
            "execution_time": {
                "mean": np.mean(execution_times),
                "median": np.median(execution_times),
                "min": np.min(execution_times),
                "max": np.max(execution_times),
                "std": np.std(execution_times)
            },
            "memory_usage_mb": {
                "mean": np.mean(memory_usage),
                "median": np.median(memory_usage),
                "min": np.min(memory_usage),
                "max": np.max(memory_usage),
                "std": np.std(memory_usage)
            },
            "cpu_usage_percent": {
                "mean": np.mean(cpu_usage),
                "median": np.median(cpu_usage),
                "min": np.min(cpu_usage),
                "max": np.max(cpu_usage),
                "std": np.std(cpu_usage)
            },
            "functions": [m.function_name for m in self.metrics_history]
        }
    
    def save_metrics(self, filepath: str) -> None:
        """Save performance metrics to file"""
        metrics_data = {
            "summary": self.get_performance_summary(),
            "detailed_metrics": [m.to_dict() for m in self.metrics_history]
        }
        
        with open(filepath, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        logger.info(f"Performance metrics saved to {filepath}")

class PerformanceOptimizer:
    """Performance optimization utilities and strategies"""
    
    @staticmethod
    def optimize_matrix_operations():
        """Configure optimal matrix operation settings"""
        try:
            import os
            # Set optimal BLAS threads
            n_cores = psutil.cpu_count(logical=False)
            os.environ['OMP_NUM_THREADS'] = str(n_cores)
            os.environ['MKL_NUM_THREADS'] = str(n_cores)
            os.environ['NUMEXPR_MAX_THREADS'] = str(n_cores)
            
            logger.info(f"Configured matrix operations for {n_cores} cores")
        except Exception as e:
            logger.warning(f"Matrix optimization setup failed: {e}")
    
    @staticmethod
    def create_chunked_iterator(data: pd.DataFrame, chunk_size: int = 1000):
        """Create chunked iterator for large datasets"""
        for i in range(0, len(data), chunk_size):
            yield data.iloc[i:i + chunk_size]
    
    @staticmethod
    def estimate_memory_requirements(n_studies: int, n_outcomes: int = 1) -> Dict[str, float]:
        """Estimate memory requirements for meta-analysis"""
        # Basic estimates in MB
        base_memory = 50  # Base overhead
        
        # Effect sizes and variances
        data_memory = (n_studies * n_outcomes * 8 * 2) / (1024 * 1024)  # 8 bytes per float64
        
        # Covariance matrices (worst case: unstructured)
        if n_outcomes > 1:
            cov_memory = (n_outcomes ** 2 * 8) / (1024 * 1024)
        else:
            cov_memory = 0
        
        # Additional computations (bias tests, diagnostics)
        computation_memory = data_memory * 3  # Conservative estimate
        
        total_memory = base_memory + data_memory + cov_memory + computation_memory
        
        return {
            "base_mb": base_memory,
            "data_mb": data_memory,
            "covariance_mb": cov_memory,
            "computation_mb": computation_memory,
            "total_estimated_mb": total_memory,
            "recommended_chunk_size": max(100, min(1000, int(500000 / n_studies)))
        }
    
    @staticmethod
    def get_resource_recommendations(n_studies: int, 
                                   analysis_type: str = "standard") -> Dict[str, Any]:
        """Get resource allocation recommendations"""
        memory_est = PerformanceOptimizer.estimate_memory_requirements(n_studies)
        
        # CPU recommendations
        n_cores = psutil.cpu_count(logical=False)
        if analysis_type == "bayesian":
            recommended_cores = min(4, n_cores)  # Limit for MCMC
        elif analysis_type == "simulation":
            recommended_cores = n_cores  # Use all cores
        else:
            recommended_cores = min(2, n_cores)  # Conservative for standard
        
        # Memory recommendations
        available_memory = psutil.virtual_memory().available / (1024 * 1024)
        memory_buffer = 0.8  # Use 80% of available memory
        max_safe_memory = available_memory * memory_buffer
        
        chunking_needed = memory_est["total_estimated_mb"] > max_safe_memory
        
        return {
            "cpu_cores": {
                "available": n_cores,
                "recommended": recommended_cores
            },
            "memory": {
                "available_mb": available_memory,
                "estimated_usage_mb": memory_est["total_estimated_mb"],
                "chunking_needed": chunking_needed,
                "recommended_chunk_size": memory_est["recommended_chunk_size"]
            },
            "optimization_suggestions": [
                "Enable Numba JIT compilation" if HAS_NUMBA else "Install Numba for performance boost",
                "Use BLAS-optimized NumPy" if "blas" in np.__config__.show() else "Consider BLAS-optimized NumPy",
                "Enable memory profiling" if HAS_MEMORY_PROFILER else "Install memory_profiler for monitoring",
                f"Consider chunking with size {memory_est['recommended_chunk_size']}" if chunking_needed else "No chunking needed"
            ]
        }

# Optimized algorithms with Numba JIT (if available)

def pooled_effect_optimized(effects: np.ndarray, variances: np.ndarray) -> Tuple[float, float]:
    """Optimized pooled effect calculation"""
    if HAS_NUMBA:
        return _pooled_effect_numba(effects, variances)
    else:
        return _pooled_effect_numpy(effects, variances)

@njit if HAS_NUMBA else lambda f: f
def _pooled_effect_numba(effects, variances):
    """Numba-optimized pooled effect calculation"""
    weights = 1.0 / variances
    sum_weights = 0.0
    sum_weighted_effects = 0.0
    
    for i in range(len(effects)):
        sum_weights += weights[i]
        sum_weighted_effects += weights[i] * effects[i]
    
    pooled_effect = sum_weighted_effects / sum_weights
    pooled_se = (1.0 / sum_weights) ** 0.5
    
    return pooled_effect, pooled_se

def _pooled_effect_numpy(effects: np.ndarray, variances: np.ndarray) -> Tuple[float, float]:
    """NumPy fallback for pooled effect calculation"""
    weights = 1 / variances
    pooled_effect = np.sum(weights * effects) / np.sum(weights)
    pooled_se = np.sqrt(1 / np.sum(weights))
    return pooled_effect, pooled_se

@njit if HAS_NUMBA else lambda f: f
def tau2_dersimonian_laird_optimized(effects, variances):
    """Optimized DerSimonian-Laird tau² estimation"""
    if len(effects) < 2:
        return 0.0
    
    weights = 1.0 / variances
    sum_weights = 0.0
    sum_weighted_effects = 0.0
    
    # Calculate weighted mean
    for i in range(len(effects)):
        sum_weights += weights[i]
        sum_weighted_effects += weights[i] * effects[i]
    
    weighted_mean = sum_weighted_effects / sum_weights
    
    # Calculate Q statistic
    Q = 0.0
    sum_weights_squared = 0.0
    for i in range(len(effects)):
        Q += weights[i] * (effects[i] - weighted_mean) ** 2
        sum_weights_squared += weights[i] ** 2
    
    # Calculate tau²
    denominator = sum_weights - sum_weights_squared / sum_weights
    if denominator <= 0:
        return 0.0
    
    tau2 = max(0.0, (Q - (len(effects) - 1)) / denominator)
    return tau2

def tau2_dersimonian_laird_fallback(effects: np.ndarray, variances: np.ndarray) -> float:
    """NumPy fallback for DerSimonian-Laird tau² estimation"""
    if len(effects) < 2:
        return 0.0
    
    weights = 1 / variances
    sum_weights = np.sum(weights)
    weighted_mean = np.sum(weights * effects) / sum_weights
    Q = np.sum(weights * (effects - weighted_mean) ** 2)
    
    sum_weights_squared = np.sum(weights ** 2)
    denominator = sum_weights - sum_weights_squared / sum_weights
    
    if denominator <= 0:
        return 0.0
    
    tau2 = max(0, (Q - (len(effects) - 1)) / denominator)
    return float(tau2)

class StreamingMetaAnalysis:
    """Streaming meta-analysis for large datasets"""
    
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size
        self.accumulated_stats = {
            'n_studies': 0,
            'sum_weights': 0.0,
            'sum_weighted_effects': 0.0,
            'sum_weighted_squared_effects': 0.0,
            'sum_weights_squared': 0.0
        }
    
    def process_chunk(self, effects: np.ndarray, variances: np.ndarray) -> None:
        """Process a chunk of data and update accumulated statistics"""
        weights = 1 / variances
        
        self.accumulated_stats['n_studies'] += len(effects)
        self.accumulated_stats['sum_weights'] += np.sum(weights)
        self.accumulated_stats['sum_weighted_effects'] += np.sum(weights * effects)
        self.accumulated_stats['sum_weighted_squared_effects'] += np.sum(weights * effects**2)
        self.accumulated_stats['sum_weights_squared'] += np.sum(weights**2)
    
    def get_fixed_effect_estimate(self) -> Tuple[float, float]:
        """Get current fixed-effect estimate"""
        if self.accumulated_stats['sum_weights'] == 0:
            return 0.0, float('inf')
        
        pooled_effect = (self.accumulated_stats['sum_weighted_effects'] / 
                        self.accumulated_stats['sum_weights'])
        pooled_se = np.sqrt(1 / self.accumulated_stats['sum_weights'])
        
        return pooled_effect, pooled_se
    
    def get_heterogeneity_estimate(self) -> Dict[str, float]:
        """Get current heterogeneity estimate"""
        stats = self.accumulated_stats
        
        if stats['n_studies'] < 2 or stats['sum_weights'] == 0:
            return {'Q': 0.0, 'tau2': 0.0, 'I2': 0.0}
        
        # Fixed-effect estimate
        pooled_effect = stats['sum_weighted_effects'] / stats['sum_weights']
        
        # Q statistic (approximation from accumulated stats)
        Q = (stats['sum_weighted_squared_effects'] - 
             2 * pooled_effect * stats['sum_weighted_effects'] + 
             pooled_effect**2 * stats['sum_weights'])
        
        # DerSimonian-Laird tau²
        df = stats['n_studies'] - 1
        denominator = stats['sum_weights'] - stats['sum_weights_squared'] / stats['sum_weights']
        
        if denominator > 0:
            tau2 = max(0, (Q - df) / denominator)
        else:
            tau2 = 0.0
        
        # I² statistic
        I2 = max(0, ((Q - df) / Q) * 100) if Q > 0 else 0
        
        return {
            'Q': Q,
            'tau2': tau2,
            'I2': I2,
            'df': df
        }
    
    def process_dataframe_streaming(self, data: pd.DataFrame, 
                                  effect_col: str, se_col: str) -> Dict[str, Any]:
        """Process large dataframe in streaming fashion"""
        results = []
        
        for chunk in PerformanceOptimizer.create_chunked_iterator(data, self.chunk_size):
            effects = chunk[effect_col].values
            variances = (chunk[se_col] ** 2).values
            
            # Filter out invalid values
            valid_mask = ~(np.isnan(effects) | np.isnan(variances) | (variances <= 0))
            effects = effects[valid_mask]
            variances = variances[valid_mask]
            
            if len(effects) > 0:
                self.process_chunk(effects, variances)
                
                # Get current estimates
                fe_estimate, fe_se = self.get_fixed_effect_estimate()
                het_stats = self.get_heterogeneity_estimate()
                
                results.append({
                    'chunk_studies': len(effects),
                    'total_studies': self.accumulated_stats['n_studies'],
                    'fixed_effect': fe_estimate,
                    'fixed_effect_se': fe_se,
                    'tau2': het_stats['tau2'],
                    'I2': het_stats['I2'],
                    'Q': het_stats['Q']
                })
        
        return {
            'streaming_results': results,
            'final_estimates': {
                'fixed_effect': self.get_fixed_effect_estimate(),
                'heterogeneity': self.get_heterogeneity_estimate(),
                'total_studies': self.accumulated_stats['n_studies']
            }
        }

# Global profiler instance
global_profiler = PerformanceProfiler()

# Decorator for easy profiling
def profile_performance(func: Callable) -> Callable:
    """Convenience decorator for performance profiling"""
    return global_profiler.profile_function(func)

# Performance monitoring context manager
class PerformanceContext:
    """Context manager for performance monitoring"""
    
    def __init__(self, operation_name: str, profiler: Optional[PerformanceProfiler] = None):
        self.operation_name = operation_name
        self.profiler = profiler or global_profiler
        self.metrics = PerformanceMetrics()
        
    def __enter__(self):
        self.metrics.function_name = self.operation_name
        self.metrics.timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        self.start_time = time.perf_counter()
        self.profiler.start_monitoring()
        return self.metrics
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.metrics.execution_time = time.perf_counter() - self.start_time
        self.profiler.stop_monitoring()
        
        # Copy current metrics
        self.metrics.cpu_percent = self.profiler.current_metrics.cpu_percent
        self.metrics.memory_mb = self.profiler.current_metrics.memory_mb
        self.metrics.peak_memory_mb = self.profiler.current_metrics.peak_memory_mb
        self.metrics.gpu_utilization = self.profiler.current_metrics.gpu_utilization
        self.metrics.gpu_memory_mb = self.profiler.current_metrics.gpu_memory_mb
        
        self.profiler.metrics_history.append(self.metrics)
        
        logger.info(f"Performance: {self.operation_name} completed in {self.metrics.execution_time:.3f}s")