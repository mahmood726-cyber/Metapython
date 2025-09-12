"""
Continuous Benchmarking System for Metapython
"""

import time
import gc
import json
import numpy as np
import pandas as pd
import sys
import platform
from typing import Dict, List, Optional, Any, Callable, Union
from pathlib import Path
from datetime import datetime
import logging
import warnings
from dataclasses import dataclass, asdict
from functools import wraps

# Optional dependency
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

logger = logging.getLogger(__name__)

@dataclass
class BenchmarkResult:
    """Single benchmark result"""
    name: str
    duration: float
    memory_peak: float
    memory_start: float
    memory_end: float
    iterations: int
    timestamp: str
    system_info: Dict[str, Any]
    parameters: Dict[str, Any]
    success: bool
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class BenchmarkSuite:
    """Collection of benchmark results"""
    suite_name: str
    results: List[BenchmarkResult]
    total_duration: float
    timestamp: str
    git_commit: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'suite_name': self.suite_name,
            'results': [r.to_dict() for r in self.results],
            'total_duration': self.total_duration,
            'timestamp': self.timestamp,
            'git_commit': self.git_commit
        }

class SystemProfiler:
    """System resource profiling utilities"""
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get system information"""
        try:
            info = {
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'platform': sys.platform,
                'architecture': platform.architecture()[0],
                'processor': platform.processor(),
                'hostname': platform.node()
            }
            
            if HAS_PSUTIL:
                info.update({
                    'cpu_count': psutil.cpu_count(logical=False),
                    'cpu_count_logical': psutil.cpu_count(logical=True),
                    'memory_total': psutil.virtual_memory().total
                })
            
            return info
        except Exception as e:
            logger.warning(f"Failed to get system info: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def get_memory_usage() -> float:
        """Get current memory usage in MB"""
        if not HAS_PSUTIL:
            return 0.0
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except Exception:
            return 0.0
    
    @staticmethod
    def get_cpu_usage() -> float:
        """Get current CPU usage percentage"""
        if not HAS_PSUTIL:
            return 0.0
        try:
            return psutil.cpu_percent(interval=0.1)
        except Exception:
            return 0.0

class BenchmarkRunner:
    """Core benchmark execution engine"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path.cwd() / 'benchmark_results'
        self.output_dir.mkdir(exist_ok=True)
        self.profiler = SystemProfiler()
        
    def benchmark(self, 
                 func: Callable,
                 name: str,
                 iterations: int = 1,
                 warmup_iterations: int = 0,
                 parameters: Optional[Dict[str, Any]] = None) -> BenchmarkResult:
        """Run a single benchmark"""
        
        parameters = parameters or {}
        
        # Warmup
        if warmup_iterations > 0:
            for _ in range(warmup_iterations):
                try:
                    func()
                except Exception:
                    pass
        
        # Clear memory
        gc.collect()
        
        # Measure initial state
        memory_start = self.profiler.get_memory_usage()
        system_info = self.profiler.get_system_info()
        
        success = True
        error = None
        memory_peak = memory_start
        
        # Run benchmark
        start_time = time.perf_counter()
        
        try:
            for i in range(iterations):
                func()
                
                # Track peak memory
                current_memory = self.profiler.get_memory_usage()
                memory_peak = max(memory_peak, current_memory)
                
        except Exception as e:
            success = False
            error = str(e)
            logger.error(f"Benchmark {name} failed: {e}")
        
        end_time = time.perf_counter()
        memory_end = self.profiler.get_memory_usage()
        
        # Calculate metrics
        duration = (end_time - start_time) / iterations if iterations > 0 else 0
        
        return BenchmarkResult(
            name=name,
            duration=duration,
            memory_peak=memory_peak,
            memory_start=memory_start,
            memory_end=memory_end,
            iterations=iterations,
            timestamp=datetime.now().isoformat(),
            system_info=system_info,
            parameters=parameters,
            success=success,
            error=error
        )
    
    def run_suite(self, 
                  benchmarks: List[Dict[str, Any]],
                  suite_name: str = "default") -> BenchmarkSuite:
        """Run a suite of benchmarks"""
        
        results = []
        suite_start = time.perf_counter()
        
        logger.info(f"Starting benchmark suite: {suite_name}")
        
        for bench_config in benchmarks:
            name = bench_config['name']
            func = bench_config['func']
            iterations = bench_config.get('iterations', 1)
            warmup = bench_config.get('warmup_iterations', 0)
            parameters = bench_config.get('parameters', {})
            
            logger.info(f"Running benchmark: {name}")
            
            result = self.benchmark(
                func=func,
                name=name,
                iterations=iterations,
                warmup_iterations=warmup,
                parameters=parameters
            )
            
            results.append(result)
            
            if result.success:
                logger.info(f"  Completed in {result.duration:.4f}s (peak memory: {result.memory_peak:.1f}MB)")
            else:
                logger.error(f"  Failed: {result.error}")
        
        suite_end = time.perf_counter()
        total_duration = suite_end - suite_start
        
        return BenchmarkSuite(
            suite_name=suite_name,
            results=results,
            total_duration=total_duration,
            timestamp=datetime.now().isoformat(),
            git_commit=self._get_git_commit()
        )
    
    def save_results(self, suite: BenchmarkSuite, filename: Optional[str] = None) -> Path:
        """Save benchmark results to JSON file"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_{suite.suite_name}_{timestamp}.json"
        
        output_path = self.output_dir / filename
        
        with open(output_path, 'w') as f:
            json.dump(suite.to_dict(), f, indent=2)
        
        logger.info(f"Benchmark results saved to: {output_path}")
        return output_path
    
    def _get_git_commit(self) -> Optional[str]:
        """Get current git commit hash"""
        try:
            import subprocess
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

class MetapythonBenchmarks:
    """Metapython-specific benchmark collection"""
    
    def __init__(self):
        self.runner = BenchmarkRunner()
        
    def create_test_data(self, n_studies: int, seed: int = 42) -> pd.DataFrame:
        """Create test data for benchmarking"""
        np.random.seed(seed)
        
        # Generate realistic meta-analysis data
        true_effect = 0.3
        between_study_sd = 0.2
        
        studies = []
        for i in range(n_studies):
            # Study-specific effect
            study_effect = np.random.normal(true_effect, between_study_sd)
            
            # Sample sizes
            n1 = np.random.randint(20, 200)
            n2 = np.random.randint(20, 200)
            
            # Within-study variance
            within_var = 1/n1 + 1/n2
            se = np.sqrt(within_var)
            
            # Observed effect with sampling error
            observed_effect = np.random.normal(study_effect, se)
            
            studies.append({
                'study_id': f'Study_{i+1:03d}',
                'effect': observed_effect,
                'se': se,
                'n1': n1,
                'n2': n2,
                'year': 2000 + np.random.randint(0, 24),
                'country': np.random.choice(['US', 'UK', 'DE', 'CA', 'AU'])
            })
        
        return pd.DataFrame(studies)
    
    def benchmark_core_meta_analysis(self, n_studies_list: List[int] = None) -> BenchmarkSuite:
        """Benchmark core meta-analysis methods"""
        
        if n_studies_list is None:
            n_studies_list = [10, 50, 100, 500, 1000]
        
        benchmarks = []
        
        for n_studies in n_studies_list:
            test_data = self.create_test_data(n_studies)
            
            # Import here to avoid circular dependencies
            def run_basic_meta():
                from metapython import quick_meta
                return quick_meta(
                    effects=test_data['effect'].tolist(),
                    se=test_data['se'].tolist(),
                    labels=test_data['study_id'].tolist()
                )
            
            benchmarks.append({
                'name': f'basic_meta_analysis_n{n_studies}',
                'func': run_basic_meta,
                'iterations': 10 if n_studies <= 100 else 3,
                'warmup_iterations': 2,
                'parameters': {'n_studies': n_studies}
            })
        
        return self.runner.run_suite(benchmarks, "core_meta_analysis")
    
    def benchmark_network_meta_analysis(self) -> BenchmarkSuite:
        """Benchmark network meta-analysis methods"""
        
        benchmarks = []
        
        # Create network data
        network_data = pd.DataFrame({
            'treatment': ['A', 'B', 'A', 'C', 'B', 'C'],
            'control': ['C', 'C', 'B', 'D', 'D', 'D'],
            'effect': [0.2, 0.3, -0.1, 0.4, 0.1, 0.3],
            'se': [0.1, 0.15, 0.12, 0.2, 0.14, 0.18],
            'study': ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
        })
        
        def run_network_inconsistency():
            try:
                from metapython.advanced import NetworkMetaAnalysisExtended
                nma = NetworkMetaAnalysisExtended()
                return nma.inconsistency_model(network_data)
            except ImportError:
                logger.warning("Advanced methods not available")
                return None
        
        def run_multi_arm_correction():
            try:
                from metapython.advanced import NetworkMetaAnalysisExtended
                nma = NetworkMetaAnalysisExtended()
                return nma.multi_arm_correction(network_data)
            except ImportError:
                logger.warning("Advanced methods not available") 
                return None
        
        benchmarks.extend([
            {
                'name': 'network_inconsistency_test',
                'func': run_network_inconsistency,
                'iterations': 5,
                'parameters': {'n_comparisons': len(network_data)}
            },
            {
                'name': 'multi_arm_correction',
                'func': run_multi_arm_correction,
                'iterations': 10,
                'parameters': {'n_comparisons': len(network_data)}
            }
        ])
        
        return self.runner.run_suite(benchmarks, "network_meta_analysis")
    
    def benchmark_io_operations(self) -> BenchmarkSuite:
        """Benchmark I/O operations"""
        
        benchmarks = []
        
        # Create test data files
        small_data = self.create_test_data(100)
        large_data = self.create_test_data(10000)
        
        # CSV I/O
        small_csv = self.runner.output_dir / 'test_small.csv'
        large_csv = self.runner.output_dir / 'test_large.csv'
        
        small_data.to_csv(small_csv, index=False)
        large_data.to_csv(large_csv, index=False)
        
        def read_small_csv():
            return pd.read_csv(small_csv)
        
        def read_large_csv():
            return pd.read_csv(large_csv)
        
        # Parquet I/O (if available)
        def write_parquet():
            try:
                large_data.to_parquet(self.runner.output_dir / 'test_large.parquet')
                return True
            except Exception:
                return False
        
        def read_parquet():
            try:
                return pd.read_parquet(self.runner.output_dir / 'test_large.parquet')
            except Exception:
                return None
        
        benchmarks.extend([
            {
                'name': 'csv_read_small',
                'func': read_small_csv,
                'iterations': 50,
                'parameters': {'size': '100 rows'}
            },
            {
                'name': 'csv_read_large', 
                'func': read_large_csv,
                'iterations': 10,
                'parameters': {'size': '10000 rows'}
            },
            {
                'name': 'parquet_write',
                'func': write_parquet,
                'iterations': 5,
                'parameters': {'size': '10000 rows'}
            },
            {
                'name': 'parquet_read',
                'func': read_parquet,
                'iterations': 10,
                'parameters': {'size': '10000 rows'}
            }
        ])
        
        return self.runner.run_suite(benchmarks, "io_operations")
    
    def benchmark_plugin_system(self) -> BenchmarkSuite:
        """Benchmark plugin system operations"""
        
        benchmarks = []
        
        def plugin_discovery():
            try:
                from metapython.plugins import PluginDiscovery
                discovery = PluginDiscovery()
                return discovery.discover_local()
            except ImportError:
                return []
        
        def plugin_registry_operations():
            try:
                from metapython.plugins import PluginRegistry, PluginManifest, TrustLevel
                registry = PluginRegistry()
                
                # Create test manifest
                manifest = PluginManifest(
                    plugin_id='test.benchmark',
                    name='Benchmark Test Plugin',
                    version='1.0.0',
                    description='Test plugin for benchmarking',
                    author='Test',
                    author_email='test@example.com',
                    homepage='',
                    plugin_type='analysis_method',
                    api_version='1.0.0',
                    capabilities=[],
                    trust_level=TrustLevel.BASIC
                )
                
                # Register and unregister
                registry.register_plugin(manifest)
                registry.list_plugins()
                registry.unregister_plugin(manifest.plugin_id)
                
                return True
            except ImportError:
                return False
        
        benchmarks.extend([
            {
                'name': 'plugin_discovery',
                'func': plugin_discovery,
                'iterations': 10,
                'parameters': {}
            },
            {
                'name': 'plugin_registry_ops',
                'func': plugin_registry_operations,
                'iterations': 20,
                'parameters': {}
            }
        ])
        
        return self.runner.run_suite(benchmarks, "plugin_system")

class PerformanceRegression:
    """Performance regression detection"""
    
    def __init__(self, baseline_path: Optional[Path] = None):
        self.baseline_path = baseline_path
        self.thresholds = {
            'duration_increase': 0.20,  # 20% slowdown threshold
            'memory_increase': 0.30,    # 30% memory increase threshold
        }
    
    def load_baseline(self) -> Optional[BenchmarkSuite]:
        """Load baseline benchmark results"""
        if not self.baseline_path or not self.baseline_path.exists():
            return None
        
        try:
            with open(self.baseline_path) as f:
                data = json.load(f)
            
            results = [BenchmarkResult(**r) for r in data['results']]
            return BenchmarkSuite(
                suite_name=data['suite_name'],
                results=results,
                total_duration=data['total_duration'],
                timestamp=data['timestamp'],
                git_commit=data.get('git_commit')
            )
        except Exception as e:
            logger.error(f"Failed to load baseline: {e}")
            return None
    
    def compare_performance(self, current: BenchmarkSuite, 
                          baseline: BenchmarkSuite) -> Dict[str, Any]:
        """Compare current results against baseline"""
        
        regressions = []
        improvements = []
        comparison_results = {}
        
        # Create lookup for baseline results
        baseline_lookup = {r.name: r for r in baseline.results if r.success}
        
        for current_result in current.results:
            if not current_result.success:
                continue
                
            name = current_result.name
            if name not in baseline_lookup:
                continue
                
            baseline_result = baseline_lookup[name]
            
            # Compare duration
            duration_ratio = current_result.duration / baseline_result.duration
            duration_change = (duration_ratio - 1) * 100
            
            # Compare memory
            memory_ratio = current_result.memory_peak / baseline_result.memory_peak
            memory_change = (memory_ratio - 1) * 100
            
            comparison = {
                'name': name,
                'duration_change_pct': duration_change,
                'memory_change_pct': memory_change,
                'duration_ratio': duration_ratio,
                'memory_ratio': memory_ratio,
                'current_duration': current_result.duration,
                'baseline_duration': baseline_result.duration,
                'current_memory': current_result.memory_peak,
                'baseline_memory': baseline_result.memory_peak
            }
            
            comparison_results[name] = comparison
            
            # Check for regressions
            if (duration_ratio > (1 + self.thresholds['duration_increase']) or 
                memory_ratio > (1 + self.thresholds['memory_increase'])):
                regressions.append(comparison)
            
            # Check for improvements  
            if duration_ratio < 0.95 or memory_ratio < 0.95:  # 5% improvement threshold
                improvements.append(comparison)
        
        return {
            'regressions': regressions,
            'improvements': improvements,
            'all_comparisons': comparison_results,
            'regression_count': len(regressions),
            'improvement_count': len(improvements),
            'total_comparisons': len(comparison_results)
        }
    
    def generate_regression_report(self, comparison: Dict[str, Any]) -> str:
        """Generate human-readable regression report"""
        
        report = ["# Performance Regression Report\n"]
        
        if comparison['regression_count'] > 0:
            report.append("## ⚠️ Performance Regressions Detected\n")
            
            for reg in comparison['regressions']:
                report.append(f"**{reg['name']}**")
                if reg['duration_change_pct'] > self.thresholds['duration_increase'] * 100:
                    report.append(f"- Duration: {reg['duration_change_pct']:+.1f}% ({reg['current_duration']:.4f}s vs {reg['baseline_duration']:.4f}s)")
                if reg['memory_change_pct'] > self.thresholds['memory_increase'] * 100:
                    report.append(f"- Memory: {reg['memory_change_pct']:+.1f}% ({reg['current_memory']:.1f}MB vs {reg['baseline_memory']:.1f}MB)")
                report.append("")
        
        if comparison['improvement_count'] > 0:
            report.append("## ✅ Performance Improvements\n")
            
            for imp in comparison['improvements']:
                report.append(f"**{imp['name']}**")
                if imp['duration_change_pct'] < -5:
                    report.append(f"- Duration: {imp['duration_change_pct']:+.1f}% faster")
                if imp['memory_change_pct'] < -5:
                    report.append(f"- Memory: {imp['memory_change_pct']:+.1f}% less")
                report.append("")
        
        if comparison['regression_count'] == 0 and comparison['improvement_count'] == 0:
            report.append("## ✅ No Significant Performance Changes\n")
            report.append("All benchmarks are within acceptable performance thresholds.\n")
        
        return "\n".join(report)

# Benchmark decorator for easy function benchmarking
def benchmark_function(name: str, iterations: int = 1):
    """Decorator to benchmark a function"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            runner = BenchmarkRunner()
            
            def run_func():
                return func(*args, **kwargs)
            
            result = runner.benchmark(run_func, name, iterations)
            
            if result.success:
                logger.info(f"Benchmark {name}: {result.duration:.4f}s")
            else:
                logger.error(f"Benchmark {name} failed: {result.error}")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

# Export main classes
__all__ = [
    'BenchmarkRunner',
    'BenchmarkResult', 
    'BenchmarkSuite',
    'MetapythonBenchmarks',
    'PerformanceRegression',
    'SystemProfiler',
    'benchmark_function'
]