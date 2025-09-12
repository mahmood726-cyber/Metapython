# MetaPython Documentation

Welcome to MetaPython v0.6.0 - the comprehensive meta-analysis platform with Phase 9 enhancements!

## 🚀 Quick Start

### Installation

```bash
pip install metapython
```

### Environment Check

Run the built-in diagnostics to check your environment:

```bash
python -m metapython doctor
```

### Basic Usage

```python
import metapython

# Quick meta-analysis
result = metapython.quick_meta(
    effects=[0.1, 0.2, 0.15, 0.3],
    ses=[0.05, 0.06, 0.04, 0.08]
)
print(f"Pooled effect: {result.summary_effect:.3f}")
```

## 📋 Phase 9 Features

### Enhanced CLI

MetaPython now includes a comprehensive command-line interface:

```bash
# Environment diagnostics
meta doctor

# Run analysis from configuration
meta run config.yaml

# Execute pipeline workflow  
meta pipeline workflow.yaml

# Federated analysis (prototype)
meta federated coordinator --port 8080
meta federated client --coordinator localhost:8080 --site-id hospital1

# Generate reports
meta report generate output/
```

### Configuration Schema v1.0

MetaPython now supports structured configuration with validation:

```yaml
version: "1.0"
data_file: "studies.csv"
analysis_type: "standard"
effect_col: "log_or"
se_col: "se_log_or"

analysis_options:
  tau2_method: "REML"
  use_hksj: true
  confidence_level: 0.95

output_options:
  save_plots: true
  save_html: true
  output_dir: "meta_results"
```

### Healthcare Data Integration (Optional)

Phase 9 includes prototype support for healthcare data sources:

```python
# FHIR integration (requires extra: pip install 'metapython[healthcare]')
fhir_reader = metapython.HealthcareDataIntegration.create_fhir_reader(
    server_url="https://fhir.server.com"
)

# OMOP CDM integration
omop_reader = metapython.HealthcareDataIntegration.create_omop_reader(
    connection_string="postgresql://user:pass@host/omop"
)
```

### Federated Meta-Analysis (Prototype)

```python
# Coordinator setup
coordinator = metapython.FederatedMetaAnalysis.create_coordinator(
    port=8080,
    privacy_budget=1.0
)

# Client participation
client = metapython.FederatedMetaAnalysis.create_client(
    coordinator_url="http://coordinator:8080",
    site_id="hospital_1"
)
```

## 🔧 Language Clients

MetaPython can generate clients for multiple languages:

```python
# Generate OpenAPI clients
clients = metapython.LanguageClientGeneration.generate_openapi_clients()

# R client examples
r_examples = metapython.LanguageClientGeneration.create_r_client_examples()

# JavaScript dashboard snippets
js_snippets = metapython.LanguageClientGeneration.create_js_dashboard_snippets()
```

## 📊 Data Interoperability

Enhanced support for various data formats:

```python
# Arrow/Parquet connector
arrow_connector = metapython.DataInteropEnhancements.create_arrow_connector()

# Large CSV streaming
csv_parser = metapython.DataInteropEnhancements.create_csv_streaming_parser(
    chunk_size=10000
)
```

## 🔒 Privacy and Security

Phase 9 includes privacy-preserving features:

```python
# Privacy budget management
budget_manager = metapython.PrivacyBudgetManager(total_budget=1.0)
budget_manager.allocate_budget("aggregation", 0.3)
```

## 📖 Documentation

- [Installation Guide](docs/installation.md)
- [Configuration Schema](docs/config-schema.md)
- [CLI Reference](docs/cli-reference.md)
- [API Documentation](docs/api.md)
- [Healthcare Integration](docs/healthcare.md)
- [Federated Analysis](docs/federated.md)
- [Migration Guide](docs/migration/)
- [Troubleshooting](docs/troubleshooting.md)

## 🌍 Internationalization

MetaPython documentation is being translated into multiple languages:

- 🇺🇸 [English](README.md) (primary)
- 🇪🇸 [Español](README.es.md) (coming soon)
- 🇫🇷 [Français](README.fr.md) (coming soon)
- 🇩🇪 [Deutsch](README.de.md) (coming soon)
- 🇨🇳 [中文](README.zh.md) (coming soon)

## 🎯 Migration from Previous Versions

If you're upgrading from v0.4.0 or earlier:

1. **CLI Changes**: The CLI now uses grouped commands. Update scripts from `python metapython.py` to `meta <command>`.

2. **Configuration**: Consider migrating to the new v1.0 schema for better validation.

3. **Deprecations**: Run deprecation audit to check for deprecated features:
   ```python
   audit = metapython.DeprecationManager.audit_features(config)
   ```

See the [Migration Guide](docs/migration/) for detailed instructions.

## 🤝 Contributing

Please see our [Contributing Guide](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md).

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📚 [Documentation](https://metapython.readthedocs.io/)
- 🐛 [Issue Tracker](https://github.com/mahmood726-cyber/Metapython/issues)
- 💬 [Discussions](https://github.com/mahmood726-cyber/Metapython/discussions)
- 📧 Email: pymeta-cbamm@example.com

---

MetaPython v0.6.0 (Phase 9) - Post-GA enhancements with ecosystem integrations 🔬