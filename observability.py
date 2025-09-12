"""
Observability Module - Phase 8
OpenTelemetry integration, Prometheus metrics, structured logging, and health monitoring
"""

import os
import time
import logging
import threading
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from functools import wraps
import json
from pathlib import Path
import socket
from contextlib import contextmanager

# OpenTelemetry imports (optional)
try:
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.logging import LoggingInstrumentor
    from opentelemetry.trace import Status, StatusCode
    HAS_OTEL = True
except ImportError:
    HAS_OTEL = False

# Prometheus metrics (optional)
try:
    from prometheus_client import (
        Counter, Histogram, Gauge, Summary, CollectorRegistry,
        generate_latest, CONTENT_TYPE_LATEST, start_http_server
    )
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

# Structured logging (optional)
try:
    import structlog
    HAS_STRUCTLOG = True
except ImportError:
    HAS_STRUCTLOG = False

# FastAPI health endpoints (optional)
try:
    from fastapi import FastAPI, Response
    from fastapi.responses import JSONResponse
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

logger = logging.getLogger(__name__)

@dataclass
class ObservabilityConfig:
    """Configuration for observability features"""
    # Tracing
    enable_tracing: bool = False
    trace_endpoint: Optional[str] = None
    service_name: str = "metapython"
    service_version: str = "0.6.0"
    
    # Metrics
    enable_metrics: bool = False
    metrics_port: int = 8080
    metrics_endpoint: str = "/metrics"
    
    # Logging
    enable_structured_logging: bool = False
    log_level: str = "INFO"
    log_format: str = "json"  # json, text
    
    # Health monitoring
    enable_health_endpoints: bool = False
    health_port: int = 8081
    
    # Privacy and compliance
    anonymize_data: bool = True
    enable_telemetry: bool = False  # Disabled by default
    telemetry_endpoint: Optional[str] = None

class TelemetryManager:
    """Manages telemetry collection and anonymization"""
    
    def __init__(self, config: ObservabilityConfig):
        self.config = config
        self.telemetry_data: Dict[str, Any] = {}
        self.session_id = self._generate_session_id()
        
    def _generate_session_id(self) -> str:
        """Generate anonymous session ID"""
        import hashlib
        import uuid
        
        # Create anonymous session ID
        random_uuid = str(uuid.uuid4())
        return hashlib.sha256(random_uuid.encode()).hexdigest()[:16]
    
    def record_usage(self, event_type: str, metadata: Dict[str, Any] = None) -> None:
        """Record usage event with privacy safeguards"""
        if not self.config.enable_telemetry:
            return
        
        # Anonymize metadata
        safe_metadata = self._anonymize_metadata(metadata or {})
        
        event = {
            'session_id': self.session_id,
            'event_type': event_type,
            'timestamp': time.time(),
            'metadata': safe_metadata
        }
        
        if event_type not in self.telemetry_data:
            self.telemetry_data[event_type] = []
        
        self.telemetry_data[event_type].append(event)
        
        # Optionally send to endpoint
        if self.config.telemetry_endpoint:
            self._send_telemetry_async(event)
    
    def _anonymize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Remove PII and sensitive data from metadata"""
        safe_metadata = {}
        
        # Allowed fields (non-sensitive)
        allowed_fields = {
            'n_studies', 'analysis_type', 'method', 'has_subgroups',
            'python_version', 'platform', 'performance_tier'
        }
        
        for key, value in metadata.items():
            if key in allowed_fields:
                # Further sanitize values
                if isinstance(value, (int, float)) and value > 0:
                    # Bin large numbers for privacy
                    if key == 'n_studies':
                        if value < 10:
                            safe_metadata[key] = '<10'
                        elif value < 50:
                            safe_metadata[key] = '10-50'
                        elif value < 100:
                            safe_metadata[key] = '50-100'
                        else:
                            safe_metadata[key] = '100+'
                    else:
                        safe_metadata[key] = value
                elif isinstance(value, str) and len(value) < 50:
                    safe_metadata[key] = value
        
        return safe_metadata
    
    def _send_telemetry_async(self, event: Dict[str, Any]) -> None:
        """Send telemetry data asynchronously"""
        def send_data():
            try:
                import requests
                response = requests.post(
                    self.config.telemetry_endpoint,
                    json=event,
                    timeout=5,
                    headers={'Content-Type': 'application/json'}
                )
                response.raise_for_status()
            except Exception as e:
                logger.debug(f"Telemetry upload failed: {e}")
        
        threading.Thread(target=send_data, daemon=True).start()
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get anonymized usage summary"""
        summary = {
            'session_id': self.session_id,
            'events_recorded': sum(len(events) for events in self.telemetry_data.values()),
            'event_types': list(self.telemetry_data.keys()),
            'first_event': None,
            'last_event': None
        }
        
        # Find first and last events
        all_events = []
        for events in self.telemetry_data.values():
            all_events.extend(events)
        
        if all_events:
            all_events.sort(key=lambda x: x['timestamp'])
            summary['first_event'] = all_events[0]['timestamp']
            summary['last_event'] = all_events[-1]['timestamp']
        
        return summary

class TracingManager:
    """OpenTelemetry tracing management"""
    
    def __init__(self, config: ObservabilityConfig):
        self.config = config
        self.tracer = None
        
        if HAS_OTEL and config.enable_tracing:
            self._setup_tracing()
    
    def _setup_tracing(self) -> None:
        """Setup OpenTelemetry tracing"""
        try:
            # Configure tracer provider
            trace.set_tracer_provider(TracerProvider())
            
            # Configure span processor and exporter
            if self.config.trace_endpoint:
                if "jaeger" in self.config.trace_endpoint.lower():
                    exporter = JaegerExporter(
                        agent_host_name="localhost",
                        agent_port=14268,
                    )
                else:
                    exporter = OTLPSpanExporter(endpoint=self.config.trace_endpoint)
                
                span_processor = BatchSpanProcessor(exporter)
                trace.get_tracer_provider().add_span_processor(span_processor)
            
            # Get tracer
            self.tracer = trace.get_tracer(
                self.config.service_name,
                self.config.service_version
            )
            
            # Enable logging instrumentation
            LoggingInstrumentor().instrument(set_logging_format=True)
            
            logger.info("OpenTelemetry tracing initialized")
            
        except Exception as e:
            logger.warning(f"Failed to setup tracing: {e}")
            self.tracer = None
    
    @contextmanager
    def trace_operation(self, operation_name: str, attributes: Dict[str, Any] = None):
        """Context manager for tracing operations"""
        if not self.tracer:
            yield None
            return
        
        with self.tracer.start_as_current_span(operation_name) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
            
            try:
                yield span
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
    
    def trace_function(self, operation_name: Optional[str] = None):
        """Decorator for tracing functions"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                name = operation_name or f"{func.__module__}.{func.__name__}"
                
                with self.trace_operation(name) as span:
                    if span:
                        span.set_attribute("function.name", func.__name__)
                        span.set_attribute("function.module", func.__module__)
                    
                    return func(*args, **kwargs)
            
            return wrapper
        return decorator

class MetricsManager:
    """Prometheus metrics management"""
    
    def __init__(self, config: ObservabilityConfig):
        self.config = config
        self.registry = None
        self.metrics: Dict[str, Any] = {}
        
        if HAS_PROMETHEUS and config.enable_metrics:
            self._setup_metrics()
    
    def _setup_metrics(self) -> None:
        """Setup Prometheus metrics"""
        try:
            self.registry = CollectorRegistry()
            
            # Core meta-analysis metrics
            self.metrics['analysis_total'] = Counter(
                'metapython_analysis_total',
                'Total number of meta-analyses performed',
                ['analysis_type', 'method'],
                registry=self.registry
            )
            
            self.metrics['analysis_duration'] = Histogram(
                'metapython_analysis_duration_seconds',
                'Duration of meta-analysis operations',
                ['analysis_type', 'method'],
                buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 300.0],
                registry=self.registry
            )
            
            self.metrics['studies_processed'] = Histogram(
                'metapython_studies_processed',
                'Number of studies in meta-analyses',
                ['analysis_type'],
                buckets=[5, 10, 25, 50, 100, 250, 500, 1000, 2500],
                registry=self.registry
            )
            
            self.metrics['active_analyses'] = Gauge(
                'metapython_active_analyses',
                'Number of currently running analyses',
                registry=self.registry
            )
            
            self.metrics['queue_length'] = Gauge(
                'metapython_queue_length',
                'Number of analyses in queue',
                ['priority'],
                registry=self.registry
            )
            
            self.metrics['memory_usage'] = Gauge(
                'metapython_memory_usage_bytes',
                'Current memory usage',
                registry=self.registry
            )
            
            self.metrics['errors_total'] = Counter(
                'metapython_errors_total',
                'Total number of errors',
                ['error_type', 'component'],
                registry=self.registry
            )
            
            # Start metrics server
            if self.config.metrics_port:
                start_http_server(self.config.metrics_port, registry=self.registry)
                logger.info(f"Prometheus metrics server started on port {self.config.metrics_port}")
            
        except Exception as e:
            logger.warning(f"Failed to setup metrics: {e}")
            self.metrics = {}
    
    def increment_counter(self, metric_name: str, labels: Dict[str, str] = None) -> None:
        """Increment a counter metric"""
        if metric_name in self.metrics:
            if labels:
                self.metrics[metric_name].labels(**labels).inc()
            else:
                self.metrics[metric_name].inc()
    
    def observe_histogram(self, metric_name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Record a histogram observation"""
        if metric_name in self.metrics:
            if labels:
                self.metrics[metric_name].labels(**labels).observe(value)
            else:
                self.metrics[metric_name].observe(value)
    
    def set_gauge(self, metric_name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Set a gauge value"""
        if metric_name in self.metrics:
            if labels:
                self.metrics[metric_name].labels(**labels).set(value)
            else:
                self.metrics[metric_name].set(value)
    
    def get_metrics(self) -> str:
        """Get current metrics in Prometheus format"""
        if self.registry:
            return generate_latest(self.registry).decode('utf-8')
        return ""

class StructuredLogger:
    """Structured logging management"""
    
    def __init__(self, config: ObservabilityConfig):
        self.config = config
        self.logger = None
        
        if config.enable_structured_logging:
            self._setup_structured_logging()
    
    def _setup_structured_logging(self) -> None:
        """Setup structured logging"""
        if HAS_STRUCTLOG:
            # Configure processors based on format
            if self.config.log_format == "json":
                processors = [
                    structlog.stdlib.filter_by_level,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.processors.UnicodeDecoder(),
                    structlog.processors.JSONRenderer()
                ]
            else:
                processors = [
                    structlog.stdlib.filter_by_level,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.processors.UnicodeDecoder(),
                    structlog.dev.ConsoleRenderer()
                ]
            
            structlog.configure(
                processors=processors,
                context_class=dict,
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )
            
            self.logger = structlog.get_logger("metapython")
            
            # Set logging level
            logging.basicConfig(level=getattr(logging, self.config.log_level.upper()))
            
            logger.info("Structured logging initialized")
        else:
            # Fallback to standard logging
            logging.basicConfig(
                level=getattr(logging, self.config.log_level.upper()),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            self.logger = logging.getLogger("metapython")

class HealthMonitor:
    """Health and readiness monitoring"""
    
    def __init__(self, config: ObservabilityConfig):
        self.config = config
        self.health_checks: Dict[str, Callable] = {}
        self.app = None
        
        if HAS_FASTAPI and config.enable_health_endpoints:
            self._setup_health_endpoints()
    
    def _setup_health_endpoints(self) -> None:
        """Setup health endpoints using FastAPI"""
        self.app = FastAPI(title="MetaPython Health API")
        
        @self.app.get("/health")
        async def health_check():
            """Basic health check"""
            return {"status": "healthy", "timestamp": time.time()}
        
        @self.app.get("/health/ready")
        async def readiness_check():
            """Readiness check with dependency validation"""
            checks = {}
            overall_status = "ready"
            
            for name, check_func in self.health_checks.items():
                try:
                    result = check_func()
                    checks[name] = {"status": "pass", "result": result}
                except Exception as e:
                    checks[name] = {"status": "fail", "error": str(e)}
                    overall_status = "not_ready"
            
            status_code = 200 if overall_status == "ready" else 503
            
            return JSONResponse(
                content={
                    "status": overall_status,
                    "timestamp": time.time(),
                    "checks": checks
                },
                status_code=status_code
            )
        
        @self.app.get("/health/live")
        async def liveness_check():
            """Liveness check"""
            return {"status": "alive", "timestamp": time.time()}
        
        logger.info(f"Health endpoints configured")
    
    def register_health_check(self, name: str, check_func: Callable) -> None:
        """Register a health check function"""
        self.health_checks[name] = check_func
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check core dependency status"""
        deps = {}
        
        # Core dependencies
        try:
            import numpy
            deps['numpy'] = {"status": "available", "version": numpy.__version__}
        except ImportError:
            deps['numpy'] = {"status": "missing"}
        
        try:
            import pandas
            deps['pandas'] = {"status": "available", "version": pandas.__version__}
        except ImportError:
            deps['pandas'] = {"status": "missing"}
        
        try:
            import scipy
            deps['scipy'] = {"status": "available", "version": scipy.__version__}
        except ImportError:
            deps['scipy'] = {"status": "missing"}
        
        return deps
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource availability"""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            cpu_percent = psutil.cpu_percent(interval=1)
            
            return {
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "percent_used": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "percent_used": round((disk.used / disk.total) * 100, 1)
                },
                "cpu_percent": cpu_percent
            }
        except ImportError:
            return {"error": "psutil not available"}

class ObservabilityManager:
    """Central observability management"""
    
    def __init__(self, config: Optional[ObservabilityConfig] = None):
        self.config = config or ObservabilityConfig()
        
        # Initialize components
        self.telemetry = TelemetryManager(self.config)
        self.tracing = TracingManager(self.config)
        self.metrics = MetricsManager(self.config)
        self.logging = StructuredLogger(self.config)
        self.health = HealthMonitor(self.config)
        
        # Register default health checks
        self.health.register_health_check("dependencies", self.health.check_dependencies)
        self.health.register_health_check("resources", self.health.check_system_resources)
        
        # Update system metrics periodically
        if self.config.enable_metrics:
            self._start_system_metrics_collection()
    
    def _start_system_metrics_collection(self) -> None:
        """Start background system metrics collection"""
        def collect_metrics():
            while True:
                try:
                    import psutil
                    
                    # Memory usage
                    memory = psutil.virtual_memory()
                    self.metrics.set_gauge('memory_usage', memory.used)
                    
                    # CPU usage could be added here
                    
                    time.sleep(30)  # Collect every 30 seconds
                    
                except Exception as e:
                    logger.warning(f"System metrics collection failed: {e}")
                    time.sleep(60)  # Retry after 1 minute
        
        thread = threading.Thread(target=collect_metrics, daemon=True)
        thread.start()
    
    def record_analysis(self, analysis_type: str, method: str, duration: float, 
                       n_studies: int, success: bool = True) -> None:
        """Record meta-analysis metrics"""
        labels = {"analysis_type": analysis_type, "method": method}
        
        # Metrics
        self.metrics.increment_counter('analysis_total', labels)
        self.metrics.observe_histogram('analysis_duration', duration, labels)
        self.metrics.observe_histogram('studies_processed', n_studies, {"analysis_type": analysis_type})
        
        if not success:
            self.metrics.increment_counter('errors_total', {
                "error_type": "analysis_failure",
                "component": "meta_analysis"
            })
        
        # Telemetry
        self.telemetry.record_usage('meta_analysis', {
            'analysis_type': analysis_type,
            'method': method,
            'n_studies': n_studies,
            'success': success
        })
    
    def get_observability_status(self) -> Dict[str, Any]:
        """Get overall observability status"""
        return {
            "tracing": {
                "enabled": self.config.enable_tracing,
                "available": HAS_OTEL,
                "endpoint": self.config.trace_endpoint
            },
            "metrics": {
                "enabled": self.config.enable_metrics,
                "available": HAS_PROMETHEUS,
                "port": self.config.metrics_port
            },
            "logging": {
                "structured": self.config.enable_structured_logging,
                "available": HAS_STRUCTLOG,
                "level": self.config.log_level
            },
            "health": {
                "enabled": self.config.enable_health_endpoints,
                "available": HAS_FASTAPI,
                "port": self.config.health_port
            },
            "telemetry": {
                "enabled": self.config.enable_telemetry,
                "anonymized": self.config.anonymize_data
            }
        }

# Global observability manager instance
_global_observability: Optional[ObservabilityManager] = None

def initialize_observability(config: Optional[ObservabilityConfig] = None) -> ObservabilityManager:
    """Initialize global observability"""
    global _global_observability
    _global_observability = ObservabilityManager(config)
    return _global_observability

def get_observability() -> Optional[ObservabilityManager]:
    """Get global observability manager"""
    return _global_observability

# Convenience decorators
def trace_operation(operation_name: Optional[str] = None):
    """Decorator for tracing operations"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            obs = get_observability()
            if obs and obs.tracing.tracer:
                name = operation_name or f"{func.__module__}.{func.__name__}"
                with obs.tracing.trace_operation(name):
                    return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator

def monitor_performance(analysis_type: str = "unknown", method: str = "unknown"):
    """Decorator for monitoring analysis performance"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            obs = get_observability()
            start_time = time.time()
            success = True
            n_studies = 0
            
            # Try to extract n_studies from arguments
            try:
                if args and hasattr(args[0], 'df'):
                    n_studies = len(args[0].df)
                elif 'data' in kwargs:
                    n_studies = len(kwargs['data'])
            except:
                pass
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                if obs:
                    obs.record_analysis(analysis_type, method, duration, n_studies, success)
        
        return wrapper
    return decorator