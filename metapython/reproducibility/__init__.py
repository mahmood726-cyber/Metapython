"""
Reproducibility Hardening for Metapython
"""

import hashlib
import json
import time
import uuid
import os
import sys
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass, asdict
import logging
import pickle
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class DatasetSnapshot:
    """Content-addressed dataset snapshot"""
    dataset_id: str
    content_hash: str
    metadata: Dict[str, Any]
    timestamp: str
    size_bytes: int
    row_count: int
    column_count: int
    checksum_algorithm: str = "sha256"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatasetSnapshot':
        return cls(**data)

@dataclass
class EnvironmentLockfile:
    """Environment specification for reproducible runs"""
    lockfile_id: str
    python_version: str
    packages: Dict[str, str]  # package_name -> version
    system_info: Dict[str, Any]
    created_at: str
    metapython_version: str
    git_commit: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnvironmentLockfile':
        return cls(**data)

@dataclass
class ProvenanceRecord:
    """Comprehensive provenance tracking"""
    run_id: str
    dataset_snapshots: List[str]  # Dataset IDs
    environment_lockfile: str     # Lockfile ID
    analysis_config: Dict[str, Any]
    execution_info: Dict[str, Any]
    results_hash: str
    created_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProvenanceRecord':
        return cls(**data)

class DatasetSnapshotManager:
    """Manage dataset snapshots with content-addressed storage"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / '.metapython' / 'snapshots'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.metadata_file = self.storage_path / 'snapshots.json'
        self.snapshots: Dict[str, DatasetSnapshot] = {}
        self._load_snapshots()
    
    def _load_snapshots(self):
        """Load existing snapshots from metadata file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                
                for snapshot_data in data.values():
                    snapshot = DatasetSnapshot.from_dict(snapshot_data)
                    self.snapshots[snapshot.dataset_id] = snapshot
                    
            except Exception as e:
                logger.warning(f"Failed to load snapshots metadata: {e}")
    
    def _save_snapshots(self):
        """Save snapshots metadata to file"""
        try:
            metadata = {sid: snapshot.to_dict() for sid, snapshot in self.snapshots.items()}
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save snapshots metadata: {e}")
    
    def create_snapshot(self, data: pd.DataFrame, 
                       name: str, 
                       metadata: Optional[Dict[str, Any]] = None) -> DatasetSnapshot:
        """Create content-addressed snapshot of dataset"""
        
        # Generate content hash
        content_hash = self._compute_dataframe_hash(data)
        dataset_id = f"{name}_{content_hash[:12]}"
        
        # Check if snapshot already exists
        if dataset_id in self.snapshots:
            logger.info(f"Snapshot {dataset_id} already exists")
            return self.snapshots[dataset_id]
        
        # Save data file
        data_file = self.storage_path / f"{dataset_id}.parquet"
        try:
            data.to_parquet(data_file, index=False)
        except Exception:
            # Fallback to pickle if parquet fails
            data_file = self.storage_path / f"{dataset_id}.pkl"
            with open(data_file, 'wb') as f:
                pickle.dump(data, f)
        
        # Create snapshot metadata
        snapshot = DatasetSnapshot(
            dataset_id=dataset_id,
            content_hash=content_hash,
            metadata=metadata or {},
            timestamp=datetime.now().isoformat(),
            size_bytes=int(data_file.stat().st_size),
            row_count=len(data),
            column_count=len(data.columns)
        )
        
        # Store snapshot
        self.snapshots[dataset_id] = snapshot
        self._save_snapshots()
        
        logger.info(f"Created dataset snapshot: {dataset_id}")
        return snapshot
    
    def load_snapshot(self, dataset_id: str) -> Optional[pd.DataFrame]:
        """Load dataset from snapshot"""
        if dataset_id not in self.snapshots:
            logger.error(f"Snapshot not found: {dataset_id}")
            return None
        
        # Try parquet first, then pickle
        parquet_file = self.storage_path / f"{dataset_id}.parquet"
        pickle_file = self.storage_path / f"{dataset_id}.pkl"
        
        try:
            if parquet_file.exists():
                return pd.read_parquet(parquet_file)
            elif pickle_file.exists():
                with open(pickle_file, 'rb') as f:
                    return pickle.load(f)
            else:
                logger.error(f"Data file not found for snapshot: {dataset_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to load snapshot {dataset_id}: {e}")
            return None
    
    def verify_snapshot(self, dataset_id: str, data: pd.DataFrame) -> bool:
        """Verify dataset matches snapshot"""
        if dataset_id not in self.snapshots:
            return False
        
        snapshot = self.snapshots[dataset_id]
        current_hash = self._compute_dataframe_hash(data)
        
        return current_hash == snapshot.content_hash
    
    def list_snapshots(self) -> List[DatasetSnapshot]:
        """List all available snapshots"""
        return list(self.snapshots.values())
    
    def delete_snapshot(self, dataset_id: str) -> bool:
        """Delete a snapshot"""
        if dataset_id not in self.snapshots:
            return False
        
        try:
            # Remove data files
            for ext in ['.parquet', '.pkl']:
                data_file = self.storage_path / f"{dataset_id}{ext}"
                if data_file.exists():
                    data_file.unlink()
            
            # Remove from metadata
            del self.snapshots[dataset_id]
            self._save_snapshots()
            
            logger.info(f"Deleted snapshot: {dataset_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete snapshot {dataset_id}: {e}")
            return False
    
    def _compute_dataframe_hash(self, data: pd.DataFrame) -> str:
        """Compute deterministic hash of DataFrame"""
        # Sort by all columns to ensure deterministic order
        try:
            sorted_data = data.sort_values(by=list(data.columns))
        except:
            # If sorting fails, use original order
            sorted_data = data
        
        # Convert to CSV string for hashing
        csv_string = sorted_data.to_csv(index=False, float_format='%.10g')
        
        # Compute hash
        return hashlib.sha256(csv_string.encode()).hexdigest()

class EnvironmentManager:
    """Manage environment lockfiles for reproducible execution"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / '.metapython' / 'environments'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.lockfiles: Dict[str, EnvironmentLockfile] = {}
        self._load_lockfiles()
    
    def _load_lockfiles(self):
        """Load existing lockfiles"""
        lockfile_pattern = self.storage_path / '*.json'
        
        for lockfile_path in self.storage_path.glob('*.json'):
            try:
                with open(lockfile_path, 'r') as f:
                    data = json.load(f)
                
                lockfile = EnvironmentLockfile.from_dict(data)
                self.lockfiles[lockfile.lockfile_id] = lockfile
                
            except Exception as e:
                logger.warning(f"Failed to load lockfile {lockfile_path}: {e}")
    
    def create_lockfile(self, name: str = None) -> EnvironmentLockfile:
        """Create lockfile for current environment"""
        
        # Generate lockfile ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        lockfile_id = name or f"env_{timestamp}"
        
        # Get Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        # Get installed packages
        packages = self._get_installed_packages()
        
        # Get system info
        system_info = self._get_system_info()
        
        # Get git commit if available
        git_commit = self._get_git_commit()
        
        # Get Metapython version
        try:
            import metapython
            metapython_version = metapython.__version__
        except:
            metapython_version = "unknown"
        
        # Create lockfile
        lockfile = EnvironmentLockfile(
            lockfile_id=lockfile_id,
            python_version=python_version,
            packages=packages,
            system_info=system_info,
            created_at=datetime.now().isoformat(),
            metapython_version=metapython_version,
            git_commit=git_commit
        )
        
        # Save lockfile
        self.lockfiles[lockfile_id] = lockfile
        self._save_lockfile(lockfile)
        
        logger.info(f"Created environment lockfile: {lockfile_id}")
        return lockfile
    
    def _save_lockfile(self, lockfile: EnvironmentLockfile):
        """Save lockfile to disk"""
        lockfile_path = self.storage_path / f"{lockfile.lockfile_id}.json"
        
        try:
            with open(lockfile_path, 'w') as f:
                json.dump(lockfile.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save lockfile {lockfile.lockfile_id}: {e}")
    
    def compare_environments(self, lockfile_id1: str, lockfile_id2: str) -> Dict[str, Any]:
        """Compare two environment lockfiles"""
        
        if lockfile_id1 not in self.lockfiles or lockfile_id2 not in self.lockfiles:
            return {'error': 'One or both lockfiles not found'}
        
        env1 = self.lockfiles[lockfile_id1]
        env2 = self.lockfiles[lockfile_id2]
        
        # Compare Python versions
        python_diff = env1.python_version != env2.python_version
        
        # Compare packages
        packages1 = set(env1.packages.items())
        packages2 = set(env2.packages.items())
        
        added_packages = packages2 - packages1
        removed_packages = packages1 - packages2
        
        # Find version changes
        common_packages = set(env1.packages.keys()) & set(env2.packages.keys())
        version_changes = {}
        
        for pkg in common_packages:
            if env1.packages[pkg] != env2.packages[pkg]:
                version_changes[pkg] = {
                    'old_version': env1.packages[pkg],
                    'new_version': env2.packages[pkg]
                }
        
        return {
            'python_version_changed': python_diff,
            'python_versions': (env1.python_version, env2.python_version),
            'added_packages': dict(added_packages),
            'removed_packages': dict(removed_packages),
            'version_changes': version_changes,
            'identical': not (python_diff or added_packages or removed_packages or version_changes)
        }
    
    def validate_current_environment(self, lockfile_id: str) -> Dict[str, Any]:
        """Validate current environment against lockfile"""
        
        if lockfile_id not in self.lockfiles:
            return {'valid': False, 'error': 'Lockfile not found'}
        
        lockfile = self.lockfiles[lockfile_id]
        current_packages = self._get_installed_packages()
        
        # Check Python version
        current_python = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        python_match = current_python == lockfile.python_version
        
        # Check packages
        missing_packages = []
        version_mismatches = []
        
        for pkg, version in lockfile.packages.items():
            if pkg not in current_packages:
                missing_packages.append(pkg)
            elif current_packages[pkg] != version:
                version_mismatches.append({
                    'package': pkg,
                    'expected': version,
                    'actual': current_packages[pkg]
                })
        
        # Check for extra packages
        extra_packages = set(current_packages.keys()) - set(lockfile.packages.keys())
        
        valid = python_match and not missing_packages and not version_mismatches
        
        return {
            'valid': valid,
            'python_version_match': python_match,
            'missing_packages': missing_packages,
            'version_mismatches': version_mismatches,
            'extra_packages': list(extra_packages),
            'expected_python': lockfile.python_version,
            'actual_python': current_python
        }
    
    def _get_installed_packages(self) -> Dict[str, str]:
        """Get installed packages and versions"""
        packages = {}
        
        try:
            import pkg_resources
            
            for dist in pkg_resources.working_set:
                packages[dist.project_name] = dist.version
                
        except ImportError:
            # Fallback: use pip list
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'list', '--format=json'],
                    capture_output=True, text=True, timeout=30
                )
                
                if result.returncode == 0:
                    pip_list = json.loads(result.stdout)
                    packages = {pkg['name']: pkg['version'] for pkg in pip_list}
                    
            except Exception as e:
                logger.warning(f"Failed to get package list: {e}")
        
        return packages
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'hostname': platform.node(),
            'python_implementation': platform.python_implementation()
        }
    
    def _get_git_commit(self) -> Optional[str]:
        """Get current git commit"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
                
        except Exception:
            pass
        
        return None

class SeedManager:
    """Seed management for reproducible random number generation"""
    
    def __init__(self):
        self.seeds: Dict[str, Any] = {}
        self.global_seed: Optional[int] = None
    
    def set_global_seed(self, seed: int):
        """Set global seed for all random number generators"""
        self.global_seed = seed
        
        # Set seeds for different libraries
        np.random.seed(seed)
        
        try:
            import random
            random.seed(seed)
        except ImportError:
            pass
        
        try:
            import torch
            torch.manual_seed(seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(seed)
        except ImportError:
            pass
        
        logger.info(f"Set global seed: {seed}")
    
    def generate_seed(self, name: str) -> int:
        """Generate and store a named seed"""
        if self.global_seed is not None:
            # Derive deterministic seed from global seed and name
            seed_string = f"{self.global_seed}_{name}"
            seed = int(hashlib.md5(seed_string.encode()).hexdigest()[:8], 16)
        else:
            # Generate random seed
            seed = np.random.randint(0, 2**31 - 1)
        
        self.seeds[name] = seed
        logger.debug(f"Generated seed for '{name}': {seed}")
        return seed
    
    def get_seed(self, name: str) -> Optional[int]:
        """Get stored seed by name"""
        return self.seeds.get(name)
    
    def get_all_seeds(self) -> Dict[str, Any]:
        """Get all stored seeds"""
        return self.seeds.copy()

class ProvenanceTracker:
    """Comprehensive provenance tracking for analyses"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / '.metapython' / 'provenance'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.records: Dict[str, ProvenanceRecord] = {}
        self._load_records()
    
    def _load_records(self):
        """Load existing provenance records"""
        records_file = self.storage_path / 'provenance.json'
        
        if records_file.exists():
            try:
                with open(records_file, 'r') as f:
                    data = json.load(f)
                
                for record_data in data.values():
                    record = ProvenanceRecord.from_dict(record_data)
                    self.records[record.run_id] = record
                    
            except Exception as e:
                logger.warning(f"Failed to load provenance records: {e}")
    
    def _save_records(self):
        """Save provenance records"""
        records_file = self.storage_path / 'provenance.json'
        
        try:
            data = {rid: record.to_dict() for rid, record in self.records.items()}
            with open(records_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save provenance records: {e}")
    
    def create_record(self,
                     dataset_snapshots: List[str],
                     environment_lockfile: str,
                     analysis_config: Dict[str, Any],
                     results: Any,
                     run_id: str = None) -> ProvenanceRecord:
        """Create comprehensive provenance record"""
        
        # Generate run ID if not provided
        if run_id is None:
            run_id = f"run_{uuid.uuid4().hex[:12]}"
        
        # Get execution info
        execution_info = {
            'python_executable': sys.executable,
            'command_line': sys.argv,
            'working_directory': str(Path.cwd()),
            'user': os.getenv('USER', 'unknown'),
            'hostname': platform.node(),
            'start_time': datetime.now().isoformat()
        }
        
        # Compute results hash
        results_hash = self._compute_results_hash(results)
        
        # Create record
        record = ProvenanceRecord(
            run_id=run_id,
            dataset_snapshots=dataset_snapshots,
            environment_lockfile=environment_lockfile,
            analysis_config=analysis_config,
            execution_info=execution_info,
            results_hash=results_hash,
            created_at=datetime.now().isoformat()
        )
        
        # Store record
        self.records[run_id] = record
        self._save_records()
        
        logger.info(f"Created provenance record: {run_id}")
        return record
    
    def get_record(self, run_id: str) -> Optional[ProvenanceRecord]:
        """Get provenance record by ID"""
        return self.records.get(run_id)
    
    def list_records(self) -> List[ProvenanceRecord]:
        """List all provenance records"""
        return list(self.records.values())
    
    def find_similar_runs(self, 
                         dataset_snapshots: List[str] = None,
                         environment_lockfile: str = None) -> List[ProvenanceRecord]:
        """Find runs with similar datasets or environment"""
        
        similar_runs = []
        
        for record in self.records.values():
            if dataset_snapshots and set(dataset_snapshots) == set(record.dataset_snapshots):
                similar_runs.append(record)
            elif environment_lockfile and environment_lockfile == record.environment_lockfile:
                similar_runs.append(record)
        
        return similar_runs
    
    def _compute_results_hash(self, results: Any) -> str:
        """Compute hash of analysis results"""
        try:
            # Convert results to JSON string for hashing
            if hasattr(results, 'to_dict'):
                results_str = json.dumps(results.to_dict(), sort_keys=True)
            elif isinstance(results, dict):
                results_str = json.dumps(results, sort_keys=True, default=str)
            else:
                results_str = str(results)
            
            return hashlib.sha256(results_str.encode()).hexdigest()
            
        except Exception as e:
            logger.warning(f"Failed to compute results hash: {e}")
            return "unknown"

class ReproducibilityManager:
    """Central manager for all reproducibility features"""
    
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path.home() / '.metapython'
        self.base_path.mkdir(exist_ok=True)
        
        self.snapshot_manager = DatasetSnapshotManager(self.base_path / 'snapshots')
        self.environment_manager = EnvironmentManager(self.base_path / 'environments')
        self.seed_manager = SeedManager()
        self.provenance_tracker = ProvenanceTracker(self.base_path / 'provenance')
    
    def create_reproducible_run(self,
                               data: pd.DataFrame,
                               analysis_config: Dict[str, Any],
                               dataset_name: str = "analysis_data",
                               environment_name: str = None,
                               global_seed: int = None) -> Dict[str, str]:
        """Create all necessary components for a reproducible run"""
        
        # Set global seed if provided
        if global_seed is not None:
            self.seed_manager.set_global_seed(global_seed)
        
        # Create dataset snapshot
        snapshot = self.snapshot_manager.create_snapshot(data, dataset_name)
        
        # Create environment lockfile
        lockfile = self.environment_manager.create_lockfile(environment_name)
        
        # Record provenance (results will be added later)
        record = self.provenance_tracker.create_record(
            dataset_snapshots=[snapshot.dataset_id],
            environment_lockfile=lockfile.lockfile_id,
            analysis_config=analysis_config,
            results={}  # Placeholder
        )
        
        return {
            'dataset_id': snapshot.dataset_id,
            'environment_id': lockfile.lockfile_id,
            'run_id': record.run_id
        }
    
    def recreate_run(self, run_id: str) -> Dict[str, Any]:
        """Recreate analysis environment and data from run ID"""
        
        # Get provenance record
        record = self.provenance_tracker.get_record(run_id)
        if not record:
            return {'error': f'Run {run_id} not found'}
        
        # Validate environment
        env_validation = self.environment_manager.validate_current_environment(
            record.environment_lockfile
        )
        
        # Load datasets
        datasets = {}
        for dataset_id in record.dataset_snapshots:
            data = self.snapshot_manager.load_snapshot(dataset_id)
            if data is not None:
                datasets[dataset_id] = data
        
        return {
            'run_id': run_id,
            'record': record,
            'environment_valid': env_validation['valid'],
            'environment_issues': env_validation if not env_validation['valid'] else None,
            'datasets': datasets,
            'analysis_config': record.analysis_config
        }
    
    def generate_reproducibility_report(self, run_id: str) -> str:
        """Generate comprehensive reproducibility report"""
        
        record = self.provenance_tracker.get_record(run_id)
        if not record:
            return f"Run {run_id} not found"
        
        report = [f"# Reproducibility Report for Run: {run_id}\n"]
        report.append(f"**Created:** {record.created_at}\n")
        
        # Environment information
        env_lockfile = self.environment_manager.lockfiles.get(record.environment_lockfile)
        if env_lockfile:
            report.append("## Environment")
            report.append(f"- **Python Version:** {env_lockfile.python_version}")
            report.append(f"- **Metapython Version:** {env_lockfile.metapython_version}")
            report.append(f"- **Git Commit:** {env_lockfile.git_commit or 'Unknown'}")
            report.append(f"- **Packages:** {len(env_lockfile.packages)} installed\n")
        
        # Dataset information
        report.append("## Datasets")
        for dataset_id in record.dataset_snapshots:
            snapshot = self.snapshot_manager.snapshots.get(dataset_id)
            if snapshot:
                report.append(f"- **{dataset_id}**")
                report.append(f"  - Content Hash: {snapshot.content_hash}")
                report.append(f"  - Rows: {snapshot.row_count}, Columns: {snapshot.column_count}")
                report.append(f"  - Size: {snapshot.size_bytes / 1024:.1f} KB")
        report.append("")
        
        # Analysis configuration
        report.append("## Analysis Configuration")
        report.append("```json")
        report.append(json.dumps(record.analysis_config, indent=2))
        report.append("```\n")
        
        # Execution information
        report.append("## Execution Information")
        for key, value in record.execution_info.items():
            report.append(f"- **{key.replace('_', ' ').title()}:** {value}")
        report.append("")
        
        # Results hash
        report.append(f"## Results Hash\n{record.results_hash}\n")
        
        return "\n".join(report)

# Export main classes
__all__ = [
    'DatasetSnapshot',
    'EnvironmentLockfile', 
    'ProvenanceRecord',
    'DatasetSnapshotManager',
    'EnvironmentManager',
    'SeedManager',
    'ProvenanceTracker',
    'ReproducibilityManager'
]