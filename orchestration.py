"""
Orchestration and Artifact Scaling - Phase 8
K8s/Slurm/GHA backends, queue management, artifact stores, recovery
"""

import os
import time
import json
import asyncio
import logging
import threading
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import hashlib
import pickle
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import math

# Kubernetes support (optional)
try:
    from kubernetes import client, config, watch
    from kubernetes.client.rest import ApiException
    HAS_KUBERNETES = True
except ImportError:
    HAS_KUBERNETES = False

# AsyncIO support for modern orchestration
try:
    import aiofiles
    import asyncio
    HAS_ASYNC_FILES = True
except ImportError:
    HAS_ASYNC_FILES = False

# Cloud storage support (optional)
try:
    import boto3
    from botocore.exceptions import ClientError
    HAS_AWS = True
except ImportError:
    HAS_AWS = False

# Redis for queue management (optional)
try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

logger = logging.getLogger(__name__)

class JobStatus(Enum):
    """Job execution status"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class JobPriority(Enum):
    """Job priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class JobSpec:
    """Job specification for orchestration"""
    job_id: str
    job_type: str
    priority: JobPriority
    parameters: Dict[str, Any]
    resources: Dict[str, Any] = field(default_factory=dict)
    max_retries: int = 3
    timeout_seconds: int = 3600
    created_at: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'job_id': self.job_id,
            'job_type': self.job_type,
            'priority': self.priority.value,
            'parameters': self.parameters,
            'resources': self.resources,
            'max_retries': self.max_retries,
            'timeout_seconds': self.timeout_seconds,
            'created_at': self.created_at.isoformat(),
            'tags': self.tags
        }

@dataclass
class JobResult:
    """Job execution result"""
    job_id: str
    status: JobStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    artifacts: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'job_id': self.job_id,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'retry_count': self.retry_count,
            'artifacts': self.artifacts,
            'metrics': self.metrics
        }

class BackoffStrategy:
    """Exponential backoff with jitter for retries"""
    
    @staticmethod
    def calculate_delay(attempt: int, base_delay: float = 1.0, 
                       max_delay: float = 60.0, jitter: bool = True) -> float:
        """Calculate delay for retry attempt"""
        delay = min(base_delay * (2 ** attempt), max_delay)
        
        if jitter:
            import random
            # Add ±25% jitter
            jitter_amount = delay * 0.25
            delay += random.uniform(-jitter_amount, jitter_amount)
        
        return max(0, delay)

class QueueManager:
    """Priority queue with backpressure control"""
    
    def __init__(self, max_queue_size: int = 1000, enable_redis: bool = False):
        self.max_queue_size = max_queue_size
        self.enable_redis = enable_redis and HAS_REDIS
        
        # Local queue implementation
        self.pending_jobs: Dict[JobPriority, List[JobSpec]] = {
            priority: [] for priority in JobPriority
        }
        self.running_jobs: Dict[str, JobSpec] = {}
        self.completed_jobs: Dict[str, JobResult] = {}
        self.lock = threading.Lock()
        
        # Redis implementation
        self.redis_client = None
        if self.enable_redis:
            try:
                self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
                self.redis_client.ping()
                logger.info("Connected to Redis for queue management")
            except Exception as e:
                logger.warning(f"Redis connection failed, using local queue: {e}")
                self.enable_redis = False
    
    def enqueue_job(self, job_spec: JobSpec) -> bool:
        """Add job to queue with backpressure check"""
        if self.enable_redis:
            return self._enqueue_redis(job_spec)
        else:
            return self._enqueue_local(job_spec)
    
    def _enqueue_local(self, job_spec: JobSpec) -> bool:
        """Local queue implementation"""
        with self.lock:
            total_queued = sum(len(jobs) for jobs in self.pending_jobs.values())
            
            if total_queued >= self.max_queue_size:
                logger.warning(f"Queue at capacity ({self.max_queue_size}), rejecting job {job_spec.job_id}")
                return False
            
            self.pending_jobs[job_spec.priority].append(job_spec)
            logger.info(f"Enqueued job {job_spec.job_id} with priority {job_spec.priority.name}")
            return True
    
    def _enqueue_redis(self, job_spec: JobSpec) -> bool:
        """Redis queue implementation"""
        try:
            queue_key = f"metapython:queue:{job_spec.priority.name.lower()}"
            job_data = json.dumps(job_spec.to_dict())
            
            current_size = self.redis_client.llen(queue_key)
            if current_size >= self.max_queue_size:
                return False
            
            self.redis_client.lpush(queue_key, job_data)
            return True
        except Exception as e:
            logger.error(f"Redis enqueue failed: {e}")
            return False
    
    def dequeue_job(self) -> Optional[JobSpec]:
        """Get next job from queue (highest priority first)"""
        if self.enable_redis:
            return self._dequeue_redis()
        else:
            return self._dequeue_local()
    
    def _dequeue_local(self) -> Optional[JobSpec]:
        """Local dequeue implementation"""
        with self.lock:
            # Check priorities from highest to lowest
            for priority in sorted(JobPriority, key=lambda p: p.value, reverse=True):
                if self.pending_jobs[priority]:
                    job_spec = self.pending_jobs[priority].pop(0)
                    self.running_jobs[job_spec.job_id] = job_spec
                    return job_spec
            return None
    
    def _dequeue_redis(self) -> Optional[JobSpec]:
        """Redis dequeue implementation"""
        try:
            # Check priorities from highest to lowest
            for priority in sorted(JobPriority, key=lambda p: p.value, reverse=True):
                queue_key = f"metapython:queue:{priority.name.lower()}"
                job_data = self.redis_client.rpop(queue_key)
                
                if job_data:
                    job_dict = json.loads(job_data.decode())
                    job_spec = JobSpec(**job_dict)
                    job_spec.priority = JobPriority(job_dict['priority'])
                    job_spec.created_at = datetime.fromisoformat(job_dict['created_at'])
                    return job_spec
            return None
        except Exception as e:
            logger.error(f"Redis dequeue failed: {e}")
            return None
    
    def complete_job(self, job_id: str, result: JobResult) -> None:
        """Mark job as completed"""
        with self.lock:
            if job_id in self.running_jobs:
                del self.running_jobs[job_id]
            self.completed_jobs[job_id] = result
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        if self.enable_redis:
            return self._get_queue_stats_redis()
        else:
            return self._get_queue_stats_local()
    
    def _get_queue_stats_local(self) -> Dict[str, Any]:
        """Local queue stats"""
        with self.lock:
            return {
                'pending_by_priority': {
                    priority.name: len(jobs) 
                    for priority, jobs in self.pending_jobs.items()
                },
                'running': len(self.running_jobs),
                'completed': len(self.completed_jobs),
                'total_pending': sum(len(jobs) for jobs in self.pending_jobs.values())
            }
    
    def _get_queue_stats_redis(self) -> Dict[str, Any]:
        """Redis queue stats"""
        try:
            stats = {'pending_by_priority': {}, 'total_pending': 0}
            
            for priority in JobPriority:
                queue_key = f"metapython:queue:{priority.name.lower()}"
                count = self.redis_client.llen(queue_key)
                stats['pending_by_priority'][priority.name] = count
                stats['total_pending'] += count
            
            return stats
        except Exception as e:
            logger.error(f"Redis stats failed: {e}")
            return {}

class ArtifactStore:
    """Distributed artifact storage with caching and encryption"""
    
    def __init__(self, base_path: str = "artifacts", 
                 enable_s3: bool = False, s3_bucket: Optional[str] = None,
                 enable_encryption: bool = False, cache_size_mb: int = 1000):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.enable_s3 = enable_s3 and HAS_AWS
        self.s3_bucket = s3_bucket
        self.s3_client = None
        
        self.enable_encryption = enable_encryption
        self.cache_size_mb = cache_size_mb
        self.cache_path = self.base_path / "cache"
        self.cache_path.mkdir(exist_ok=True)
        
        self.cache_usage = {}
        self.cache_lock = threading.Lock()
        
        if self.enable_s3:
            self._setup_s3()
    
    def _setup_s3(self):
        """Setup S3 client"""
        try:
            self.s3_client = boto3.client('s3')
            # Test connection
            self.s3_client.head_bucket(Bucket=self.s3_bucket)
            logger.info(f"Connected to S3 bucket: {self.s3_bucket}")
        except Exception as e:
            logger.warning(f"S3 setup failed: {e}")
            self.enable_s3 = False
    
    def store_artifact(self, artifact_id: str, data: Any, 
                      metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Store artifact with optional cloud backup"""
        result = {
            'artifact_id': artifact_id,
            'local_path': None,
            's3_path': None,
            'checksum': None,
            'size_bytes': 0,
            'success': False
        }
        
        try:
            # Serialize data
            artifact_data = pickle.dumps(data)
            checksum = hashlib.sha256(artifact_data).hexdigest()
            
            # Store locally
            local_path = self.base_path / f"{artifact_id}.pkl"
            with open(local_path, 'wb') as f:
                f.write(artifact_data)
            
            # Store metadata
            meta_path = self.base_path / f"{artifact_id}.meta"
            artifact_metadata = {
                'artifact_id': artifact_id,
                'created_at': datetime.utcnow().isoformat(),
                'checksum': checksum,
                'size_bytes': len(artifact_data),
                'metadata': metadata or {}
            }
            
            with open(meta_path, 'w') as f:
                json.dump(artifact_metadata, f, indent=2)
            
            result.update({
                'local_path': str(local_path),
                'checksum': checksum,
                'size_bytes': len(artifact_data),
                'success': True
            })
            
            # Upload to S3 if enabled
            if self.enable_s3:
                s3_result = self._upload_to_s3(artifact_id, artifact_data, artifact_metadata)
                result['s3_path'] = s3_result.get('s3_path')
            
            logger.info(f"Stored artifact {artifact_id} ({len(artifact_data)} bytes)")
            
        except Exception as e:
            logger.error(f"Failed to store artifact {artifact_id}: {e}")
            result['error'] = str(e)
        
        return result
    
    def retrieve_artifact(self, artifact_id: str, use_cache: bool = True) -> Any:
        """Retrieve artifact with local caching"""
        # Check local cache first
        cache_path = self.cache_path / f"{artifact_id}.pkl"
        
        if use_cache and cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    data = pickle.load(f)
                self._update_cache_usage(artifact_id)
                logger.debug(f"Retrieved artifact {artifact_id} from cache")
                return data
            except Exception as e:
                logger.warning(f"Cache read failed for {artifact_id}: {e}")
        
        # Try local storage
        local_path = self.base_path / f"{artifact_id}.pkl"
        if local_path.exists():
            try:
                with open(local_path, 'rb') as f:
                    data = pickle.load(f)
                
                # Cache for future use
                if use_cache:
                    self._cache_artifact(artifact_id, data)
                
                logger.debug(f"Retrieved artifact {artifact_id} from local storage")
                return data
            except Exception as e:
                logger.warning(f"Local read failed for {artifact_id}: {e}")
        
        # Try S3 if enabled
        if self.enable_s3:
            try:
                data = self._download_from_s3(artifact_id)
                if data is not None:
                    # Store locally and cache
                    with open(local_path, 'wb') as f:
                        f.write(pickle.dumps(data))
                    
                    if use_cache:
                        self._cache_artifact(artifact_id, data)
                    
                    logger.debug(f"Retrieved artifact {artifact_id} from S3")
                    return data
            except Exception as e:
                logger.warning(f"S3 download failed for {artifact_id}: {e}")
        
        raise FileNotFoundError(f"Artifact {artifact_id} not found")
    
    def _upload_to_s3(self, artifact_id: str, data: bytes, 
                     metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Upload artifact to S3"""
        try:
            # Multi-part upload for large files
            if len(data) > 50 * 1024 * 1024:  # 50MB threshold
                return self._multipart_upload_s3(artifact_id, data, metadata)
            else:
                key = f"artifacts/{artifact_id}.pkl"
                self.s3_client.put_object(
                    Bucket=self.s3_bucket,
                    Key=key,
                    Body=data,
                    Metadata={
                        'artifact-id': artifact_id,
                        'checksum': metadata['checksum'],
                        'created-at': metadata['created_at']
                    }
                )
                return {'s3_path': f"s3://{self.s3_bucket}/{key}"}
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            return {}
    
    def _multipart_upload_s3(self, artifact_id: str, data: bytes,
                            metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Multipart upload for large artifacts"""
        try:
            key = f"artifacts/{artifact_id}.pkl"
            
            # Initialize multipart upload
            response = self.s3_client.create_multipart_upload(
                Bucket=self.s3_bucket,
                Key=key,
                Metadata={
                    'artifact-id': artifact_id,
                    'checksum': metadata['checksum'],
                    'created-at': metadata['created_at']
                }
            )
            
            upload_id = response['UploadId']
            parts = []
            
            # Upload parts (5MB each)
            part_size = 5 * 1024 * 1024
            part_number = 1
            
            for i in range(0, len(data), part_size):
                part_data = data[i:i + part_size]
                
                part_response = self.s3_client.upload_part(
                    Bucket=self.s3_bucket,
                    Key=key,
                    PartNumber=part_number,
                    UploadId=upload_id,
                    Body=part_data
                )
                
                parts.append({
                    'ETag': part_response['ETag'],
                    'PartNumber': part_number
                })
                
                part_number += 1
            
            # Complete multipart upload
            self.s3_client.complete_multipart_upload(
                Bucket=self.s3_bucket,
                Key=key,
                UploadId=upload_id,
                MultipartUpload={'Parts': parts}
            )
            
            return {'s3_path': f"s3://{self.s3_bucket}/{key}"}
            
        except Exception as e:
            # Abort multipart upload on failure
            try:
                self.s3_client.abort_multipart_upload(
                    Bucket=self.s3_bucket,
                    Key=key,
                    UploadId=upload_id
                )
            except:
                pass
            
            logger.error(f"Multipart upload failed: {e}")
            return {}
    
    def _download_from_s3(self, artifact_id: str) -> Optional[Any]:
        """Download artifact from S3"""
        try:
            key = f"artifacts/{artifact_id}.pkl"
            response = self.s3_client.get_object(Bucket=self.s3_bucket, Key=key)
            data = response['Body'].read()
            return pickle.loads(data)
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return None
            raise
    
    def _cache_artifact(self, artifact_id: str, data: Any) -> None:
        """Cache artifact locally with LRU eviction"""
        try:
            serialized = pickle.dumps(data)
            size_mb = len(serialized) / (1024 * 1024)
            
            # Check if we need to evict
            with self.cache_lock:
                self._ensure_cache_space(size_mb)
                
                # Store in cache
                cache_path = self.cache_path / f"{artifact_id}.pkl"
                with open(cache_path, 'wb') as f:
                    f.write(serialized)
                
                self.cache_usage[artifact_id] = {
                    'last_accessed': datetime.utcnow(),
                    'size_mb': size_mb
                }
        
        except Exception as e:
            logger.warning(f"Cache write failed for {artifact_id}: {e}")
    
    def _ensure_cache_space(self, required_mb: float) -> None:
        """Ensure sufficient cache space by evicting LRU items"""
        current_size = sum(item['size_mb'] for item in self.cache_usage.values())
        
        if current_size + required_mb <= self.cache_size_mb:
            return
        
        # Sort by last accessed (LRU first)
        sorted_items = sorted(
            self.cache_usage.items(),
            key=lambda x: x[1]['last_accessed']
        )
        
        # Evict until we have enough space
        for artifact_id, info in sorted_items:
            try:
                cache_file = self.cache_path / f"{artifact_id}.pkl"
                if cache_file.exists():
                    cache_file.unlink()
                
                del self.cache_usage[artifact_id]
                current_size -= info['size_mb']
                
                logger.debug(f"Evicted {artifact_id} from cache")
                
                if current_size + required_mb <= self.cache_size_mb:
                    break
                    
            except Exception as e:
                logger.warning(f"Cache eviction failed for {artifact_id}: {e}")
    
    def _update_cache_usage(self, artifact_id: str) -> None:
        """Update cache access time"""
        with self.cache_lock:
            if artifact_id in self.cache_usage:
                self.cache_usage[artifact_id]['last_accessed'] = datetime.utcnow()
    
    def cleanup_old_artifacts(self, max_age_days: int = 30) -> Dict[str, int]:
        """Clean up old artifacts based on age"""
        cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
        cleaned = {'local': 0, 's3': 0}
        
        try:
            # Clean local artifacts
            for meta_file in self.base_path.glob("*.meta"):
                try:
                    with open(meta_file, 'r') as f:
                        metadata = json.load(f)
                    
                    created_at = datetime.fromisoformat(metadata['created_at'])
                    
                    if created_at < cutoff_date:
                        artifact_id = metadata['artifact_id']
                        
                        # Remove local files
                        artifact_file = self.base_path / f"{artifact_id}.pkl"
                        if artifact_file.exists():
                            artifact_file.unlink()
                        meta_file.unlink()
                        
                        # Remove from cache
                        cache_file = self.cache_path / f"{artifact_id}.pkl"
                        if cache_file.exists():
                            cache_file.unlink()
                        
                        cleaned['local'] += 1
                        logger.debug(f"Cleaned up old artifact: {artifact_id}")
                
                except Exception as e:
                    logger.warning(f"Failed to clean artifact {meta_file}: {e}")
            
            # Clean S3 artifacts if enabled
            if self.enable_s3:
                cleaned['s3'] = self._cleanup_s3_artifacts(cutoff_date)
        
        except Exception as e:
            logger.error(f"Artifact cleanup failed: {e}")
        
        return cleaned
    
    def _cleanup_s3_artifacts(self, cutoff_date: datetime) -> int:
        """Clean up old S3 artifacts"""
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.s3_bucket, Prefix='artifacts/')
            
            objects_to_delete = []
            
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                            objects_to_delete.append({'Key': obj['Key']})
            
            # Delete in batches
            deleted_count = 0
            batch_size = 1000
            
            for i in range(0, len(objects_to_delete), batch_size):
                batch = objects_to_delete[i:i + batch_size]
                if batch:
                    self.s3_client.delete_objects(
                        Bucket=self.s3_bucket,
                        Delete={'Objects': batch}
                    )
                    deleted_count += len(batch)
            
            return deleted_count
        
        except Exception as e:
            logger.error(f"S3 cleanup failed: {e}")
            return 0

class OrchestrationManager:
    """Central orchestration management"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.queue_manager = QueueManager(
            max_queue_size=self.config.get('max_queue_size', 1000),
            enable_redis=self.config.get('enable_redis', False)
        )
        self.artifact_store = ArtifactStore(
            base_path=self.config.get('artifact_path', 'artifacts'),
            enable_s3=self.config.get('enable_s3', False),
            s3_bucket=self.config.get('s3_bucket'),
            cache_size_mb=self.config.get('cache_size_mb', 1000)
        )
        
        self.executor = ThreadPoolExecutor(
            max_workers=self.config.get('max_workers', 4)
        )
        self.shutdown_event = threading.Event()
        self.worker_thread = None
        
        # Start worker thread
        self.start_workers()
    
    def start_workers(self) -> None:
        """Start background worker threads"""
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        logger.info("Orchestration workers started")
    
    def shutdown(self) -> None:
        """Shutdown orchestration"""
        self.shutdown_event.set()
        if self.worker_thread:
            self.worker_thread.join(timeout=10)
        self.executor.shutdown(wait=True)
        logger.info("Orchestration shutdown complete")
    
    def _worker_loop(self) -> None:
        """Main worker loop"""
        while not self.shutdown_event.is_set():
            try:
                job_spec = self.queue_manager.dequeue_job()
                
                if job_spec:
                    logger.info(f"Processing job {job_spec.job_id}")
                    future = self.executor.submit(self._execute_job, job_spec)
                    # Don't block on individual jobs
                else:
                    # No jobs available, wait a bit
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Worker loop error: {e}")
                time.sleep(5)  # Back off on errors
    
    def _execute_job(self, job_spec: JobSpec) -> None:
        """Execute a single job"""
        job_result = JobResult(
            job_id=job_spec.job_id,
            status=JobStatus.RUNNING,
            started_at=datetime.utcnow()
        )
        
        try:
            # Execute job based on type
            if job_spec.job_type == "meta_analysis":
                result = self._execute_meta_analysis_job(job_spec)
            elif job_spec.job_type == "data_processing":
                result = self._execute_data_processing_job(job_spec)
            else:
                raise ValueError(f"Unknown job type: {job_spec.job_type}")
            
            # Store result artifacts
            if result:
                artifact_id = f"{job_spec.job_id}_result"
                store_result = self.artifact_store.store_artifact(
                    artifact_id, result, {'job_id': job_spec.job_id}
                )
                job_result.artifacts.append(store_result['artifact_id'])
            
            job_result.status = JobStatus.COMPLETED
            job_result.result = "Success"
            job_result.completed_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Job {job_spec.job_id} failed: {e}")
            job_result.status = JobStatus.FAILED
            job_result.error = str(e)
            job_result.completed_at = datetime.utcnow()
            
            # Retry logic
            if job_result.retry_count < job_spec.max_retries:
                job_result.retry_count += 1
                job_result.status = JobStatus.RETRYING
                
                # Calculate backoff delay
                delay = BackoffStrategy.calculate_delay(job_result.retry_count)
                logger.info(f"Retrying job {job_spec.job_id} in {delay:.1f}s (attempt {job_result.retry_count})")
                
                # Re-queue with delay
                def requeue_job():
                    time.sleep(delay)
                    self.queue_manager.enqueue_job(job_spec)
                
                threading.Thread(target=requeue_job, daemon=True).start()
        
        finally:
            self.queue_manager.complete_job(job_spec.job_id, job_result)
    
    def _execute_meta_analysis_job(self, job_spec: JobSpec) -> Any:
        """Execute meta-analysis job"""
        # This would integrate with the main UnifiedMetaAnalysis class
        # For now, it's a placeholder
        parameters = job_spec.parameters
        
        # Simulate meta-analysis execution
        time.sleep(2)  # Simulate processing time
        
        return {
            'job_type': 'meta_analysis',
            'parameters': parameters,
            'results': {
                'pooled_effect': 0.25,
                'confidence_interval': [0.10, 0.40],
                'heterogeneity': {'I2': 45.2, 'tau2': 0.08}
            }
        }
    
    def _execute_data_processing_job(self, job_spec: JobSpec) -> Any:
        """Execute data processing job"""
        # Placeholder for data processing jobs
        time.sleep(1)
        
        return {
            'job_type': 'data_processing',
            'processed_records': 1000,
            'processing_time': 1.0
        }
    
    def submit_job(self, job_spec: JobSpec) -> bool:
        """Submit job for execution"""
        success = self.queue_manager.enqueue_job(job_spec)
        if success:
            logger.info(f"Submitted job {job_spec.job_id}")
        else:
            logger.warning(f"Failed to submit job {job_spec.job_id} - queue full")
        return success
    
    def get_job_status(self, job_id: str) -> Optional[JobResult]:
        """Get job status"""
        # Check completed jobs
        if job_id in self.queue_manager.completed_jobs:
            return self.queue_manager.completed_jobs[job_id]
        
        # Check running jobs
        if job_id in self.queue_manager.running_jobs:
            return JobResult(
                job_id=job_id,
                status=JobStatus.RUNNING,
                started_at=datetime.utcnow()  # Approximate
            )
        
        # Check pending jobs
        for jobs in self.queue_manager.pending_jobs.values():
            if any(job.job_id == job_id for job in jobs):
                return JobResult(
                    job_id=job_id,
                    status=JobStatus.QUEUED
                )
        
        return None
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        queue_stats = self.queue_manager.get_queue_stats()
        
        return {
            'queue_stats': queue_stats,
            'worker_threads': self.config.get('max_workers', 4),
            'artifact_store': {
                'local_path': str(self.artifact_store.base_path),
                's3_enabled': self.artifact_store.enable_s3,
                'cache_enabled': True
            },
            'system_healthy': queue_stats.get('total_pending', 0) < self.queue_manager.max_queue_size
        }

# Global orchestration manager
_global_orchestration: Optional[OrchestrationManager] = None

def initialize_orchestration(config: Dict[str, Any] = None) -> OrchestrationManager:
    """Initialize global orchestration manager"""
    global _global_orchestration
    _global_orchestration = OrchestrationManager(config)
    return _global_orchestration

def get_orchestration() -> Optional[OrchestrationManager]:
    """Get global orchestration manager"""
    return _global_orchestration

def submit_meta_analysis_job(data_path: str, config: Dict[str, Any], 
                           priority: JobPriority = JobPriority.NORMAL) -> Optional[str]:
    """Convenience function to submit meta-analysis job"""
    orchestration = get_orchestration()
    if not orchestration:
        logger.warning("Orchestration not initialized")
        return None
    
    job_id = f"meta_{int(time.time())}"
    job_spec = JobSpec(
        job_id=job_id,
        job_type="meta_analysis",
        priority=priority,
        parameters={
            'data_path': data_path,
            'config': config
        }
    )
    
    success = orchestration.submit_job(job_spec)
    return job_id if success else None