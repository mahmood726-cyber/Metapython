# MetaPython v0.4.0 - Phase 6 Implementation

## What's New in Phase 6: Cloud-Ready Orchestration and Rich Reporting

### 1. Cloud and Distributed Runners ✨ NEW

#### Execution Backends
- **LocalBackend**: Default backend for immediate local execution
- **KubernetesBackend**: Submit meta-analysis jobs to Kubernetes clusters
- **SlurmBackend**: Execute on HPC systems with SLURM workload manager
- **GitHubActionsBackend**: Leverage GitHub Actions self-hosted runners

#### Artifact Stores
- **LocalArtifactStore**: File-based storage with local file system
- **S3ArtifactStore**: AWS S3 integration with signed URLs
- **GCSArtifactStore**: Google Cloud Storage support
- **AzureArtifactStore**: Azure Blob Storage integration

#### Cloud Orchestrator
- **Idempotent Run IDs**: Deterministic job identification prevents duplicates
- **Retry Logic**: Automatic retry for failed jobs with configurable limits
- **Queueing System**: Job submission and status tracking across backends
- **Structured Logging**: Comprehensive progress events and status tracking

### 2. Reporting and Templating System ✨ NEW

#### Template Engine
- **Jinja2 Templates**: Flexible HTML/Markdown report generation
- **Built-in Templates**: 4 ready-to-use templates for common analyses
- **Custom Templates**: Easy addition of organization-specific templates

#### Built-in Report Templates
1. **Basic Template**: Standard meta-analysis with effect sizes and heterogeneity
2. **Network Template**: Network meta-analysis with inconsistency testing and rankings
3. **Diagnostic Template**: Diagnostic test accuracy with HSROC and Fagan nomogram
4. **Sparse Events Template**: Rare events analysis with Peto OR and Mantel-Haenszel

#### PDF Export
- **WeasyPrint Support**: High-quality PDF generation from HTML
- **wkhtmltopdf Support**: Alternative PDF export option
- **Graceful Fallbacks**: HTML-only when PDF libraries unavailable

### 3. Enhanced Command Line Interface ✨ NEW

#### New CLI Commands
```bash
# Backend management
meta backends                    # List available execution backends
meta run --backend k8s config.yaml  # Run with specific backend

# Report generation  
meta templates                   # List available report templates
meta report --template basic --data results.yaml --output report.html --pdf

# Job management
meta status RUN_ID              # Check job status
meta cancel RUN_ID              # Cancel running job
```

#### Cloud Execution Examples
```bash
# Local execution (default)
meta run --config analysis.yaml

# Kubernetes execution
meta run --backend k8s --config analysis.yaml

# SLURM execution
meta run --backend slurm --config analysis.yaml

# Asynchronous submission
meta run --backend k8s --config analysis.yaml --no-wait
```

### 4. Configuration and Profiles

#### Artifact Store Configuration
- **Programmatic Setup**: Configure stores via Python API
- **Environment Variables**: Support for AWS/GCS/Azure credentials
- **Profile Management**: Multiple configurations for different environments

#### Backend Configuration
- **Kubernetes**: Namespace, resource limits, custom images
- **SLURM**: Partition, time limits, module loading
- **GitHub Actions**: Repository, workflow file, input parameters

### 5. Backward Compatibility ✅

#### Graceful Dependency Handling
- **Optional Dependencies**: All cloud features behind dependency checks
- **Fallback Behaviors**: Local backend always available
- **Zero Breaking Changes**: All existing code continues to work

#### Import Compatibility
```python
# All existing imports work unchanged
from metapython import UnifiedMetaAnalysis, MetaCLI

# New Phase 6 imports available
from metapython import CloudOrchestrator, ReportGenerator
```

## Usage Examples

### Cloud Execution
```python
import metapython

# Create CLI instance
cli = metapython.MetaCLI()

# Configure S3 artifact store
cli.configure_artifact_store(
    's3',
    bucket_name='my-meta-bucket',
    aws_access_key_id='AKIA...',
    aws_secret_access_key='xxx'
)

# Run analysis on Kubernetes
job_config = {
    'type': 'meta_analysis',
    'data_file': 's3://my-bucket/data.csv',
    'effect_col': 'effect',
    'se_col': 'se'
}

result = cli.run_with_backend(job_config, backend='k8s', store='s3')
print(f"Job submitted: {result['run_id']}")
```

### Report Generation
```python
import metapython

# Generate report from analysis results
report_gen = metapython.ReportGenerator()

data = {
    'n_studies': 15,
    'pooled_effect': {'effect': 0.45, 'ci_lower': 0.25, 'ci_upper': 0.65},
    'heterogeneity': {'I2': 32.1, 'tau2': 0.08}
}

result = report_gen.generate_report('basic', data)
print(result['content'])  # HTML report content

# Save with PDF export
report_gen.save_report(result['content'], 'report.html')
pdf_exporter = metapython.PDFExporter()
pdf_exporter.export_to_pdf(result['content'], 'report.pdf')
```

### Advanced Orchestration
```python
import metapython

# Direct orchestrator usage
orchestrator = metapython.CloudOrchestrator()

# Register custom backends
k8s_backend = metapython.KubernetesBackend(namespace='meta-analysis')
orchestrator.register_backend('k8s', k8s_backend)

# Submit with automatic retry
job_config = {'type': 'pipeline', 'pipeline_file': 'workflow.yaml'}
result = orchestrator.submit_job(job_config, backend='k8s', retry_limit=5)

# Monitor progress
status = orchestrator.check_job_status(result['run_id'])
print(f"Status: {status['status']}")
```

## Dependencies

### Core Requirements (unchanged)
- numpy >= 1.19.0
- pandas >= 1.3.0
- matplotlib >= 3.3.0
- seaborn >= 0.11.0
- scipy >= 1.7.0

### Phase 6 Optional Dependencies
```bash
# Cloud backends
pip install kubernetes boto3 google-cloud-storage azure-storage-blob

# Reporting
pip install jinja2 weasyprint pdfkit

# Complete installation
pip install metapython[cloud,reporting]
```

## Migration Guide

Phase 6 is fully backward compatible. No changes needed for existing code.

### To Enable Cloud Features
1. Install optional dependencies: `pip install kubernetes boto3`
2. Configure backends: `cli.configure_artifact_store('s3', ...)`
3. Use new CLI commands: `meta run --backend k8s`

### To Enable Rich Reporting
1. Install template engine: `pip install jinja2`
2. Install PDF export: `pip install weasyprint`
3. Generate reports: `meta report --template basic --data results.yaml`

## Version History

- **v0.4.0 Phase 6**: Cloud orchestration, rich reporting, service-oriented interface
- **v0.4.0 Phase 4**: Network inconsistency, sparse events, enhanced DTA, multivariate structures, CLI automation
- **v3.0.0**: Unified PyMeta-CBAMM suite with comprehensive meta-analysis capabilities

## License

MIT License - see LICENSE file for details.