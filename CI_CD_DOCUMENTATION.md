# 🚀 CI/CD Documentation

## **Comprehensive GitHub Actions Workflows for MetaPython**

MetaPython uses **professional-grade CI/CD** with automated testing, code quality checks, security scanning, and release automation.

---

## 📦 Workflows Overview

### **1. Python CI/CD** (`.github/workflows/python-ci.yml`)

**Comprehensive Python testing across multiple versions and operating systems**

#### Jobs:

| Job | Description | Matrix | Run Time |
|-----|-------------|--------|----------|
| **code-quality** | Black, isort, flake8, pylint, mypy, bandit, safety | Ubuntu | ~3 min |
| **test-python** | Unit tests with pytest | Python 3.9-3.12 × Ubuntu/macOS/Windows | ~10 min |
| **test-r-integration** | R plotting integration tests | Ubuntu + R | ~5 min |
| **test-ml** | ML module tests (heavy dependencies) | Ubuntu | ~8 min |
| **test-api** | FastAPI backend tests | Ubuntu | ~3 min |
| **docs** | Sphinx documentation build | Ubuntu | ~4 min |
| **performance** | pytest-benchmark | Ubuntu | ~5 min |
| **build** | Build Python package | Ubuntu | ~2 min |
| **security** | Trivy vulnerability scanner | Ubuntu | ~3 min |

**Total: ~40 min (parallel execution)**

#### Features:
- ✅ Matrix testing across Python 3.9-3.12
- ✅ Cross-platform (Linux, macOS, Windows)
- ✅ Code coverage with Codecov
- ✅ Security scanning (Bandit, Safety, Trivy)
- ✅ Dependency caching for speed
- ✅ Parallel test execution with pytest-xdist

---

### **2. R Package CI/CD** (`.github/workflows/r-ci.yml`)

**R package testing with devtools and best practices**

#### Jobs:

| Job | Description | Matrix | Run Time |
|-----|-------------|--------|----------|
| **R-CMD-check** | R CMD check | R release/devel/oldrel × OS | ~15 min |
| **test-r-packages** | devtools testing | Ubuntu | ~5 min |
| **coverage** | R code coverage | Ubuntu | ~3 min |
| **lint** | lintr code linting | Ubuntu | ~2 min |
| **style** | styler formatting check | Ubuntu | ~2 min |
| **integration-test** | Python-R integration | Ubuntu + Python | ~5 min |
| **benchmark** | microbenchmark performance | Ubuntu | ~3 min |

**Total: ~35 min (parallel execution)**

#### Features:
- ✅ Tests metafor and meta packages
- ✅ Validates plotting functionality
- ✅ Python-R bridge (rpy2) testing
- ✅ Performance benchmarking
- ✅ Code style checks

---

### **3. Frontend CI/CD** (`.github/workflows/frontend-ci.yml`)

**React/TypeScript testing and building**

#### Jobs:

| Job | Description | Run Time |
|-----|-------------|----------|
| **setup** | ESLint, Prettier, TypeScript check | ~3 min |
| **build** | Build across Node 18/20/22 | ~5 min |
| **test** | Jest unit tests with coverage | ~4 min |
| **bundle-size** | Bundle size analysis | ~3 min |
| **security** | npm audit + Snyk | ~2 min |
| **e2e** | Playwright E2E tests | ~10 min |
| **lighthouse** | Performance audit | ~5 min |

**Total: ~30 min**

#### Features:
- ✅ TypeScript strict mode
- ✅ ESLint + Prettier enforcement
- ✅ Unit tests with Jest
- ✅ E2E tests with Playwright
- ✅ Lighthouse performance scoring
- ✅ Bundle size tracking

---

### **4. Integration Tests** (`.github/workflows/integration-tests.yml`)

**End-to-end workflow testing**

#### Jobs:

| Job | Description | Services | Run Time |
|-----|-------------|----------|----------|
| **full-stack** | Complete stack integration | PostgreSQL, Redis | ~15 min |
| **e2e-workflow** | Complete meta-analysis workflow | - | ~5 min |
| **performance** | Performance benchmarks | - | ~5 min |
| **data-pipeline** | Data import/export testing | - | ~3 min |

**Total: ~30 min**

#### Features:
- ✅ PostgreSQL + Redis integration
- ✅ Complete workflow testing
- ✅ Performance thresholds
- ✅ Data pipeline validation

---

### **5. Release Automation** (`.github/workflows/release.yml`)

**Automated releases on version tags**

#### Jobs:

| Job | Description | Run Time |
|-----|-------------|----------|
| **validate** | Version format validation | ~1 min |
| **build-python** | Build Python package | ~3 min |
| **build-frontend** | Build React frontend | ~5 min |
| **release** | Create GitHub release | ~2 min |
| **publish-pypi** | Publish to PyPI | ~3 min |
| **docker** | Build multi-arch Docker image | ~10 min |
| **docs** | Deploy documentation | ~5 min |
| **notify** | Slack notification | ~1 min |

**Total: ~30 min**

#### Triggers:
```bash
# Create release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# Workflow automatically:
# 1. Builds packages
# 2. Creates GitHub release
# 3. Publishes to PyPI
# 4. Builds Docker images
# 5. Updates documentation
# 6. Sends notifications
```

---

## 🔧 Pre-Commit Hooks

**`.pre-commit-config.yaml`**

### Installed Hooks:

**Python:**
- ✅ Black (formatting)
- ✅ isort (import sorting)
- ✅ Flake8 (linting)
- ✅ pyupgrade (syntax upgrading)
- ✅ autopep8 (PEP 8 fixes)
- ✅ MyPy (type checking)
- ✅ Bandit (security)

**Frontend:**
- ✅ Prettier (formatting)
- ✅ ESLint (linting)

**General:**
- ✅ YAML/JSON/TOML formatting
- ✅ Trailing whitespace removal
- ✅ End-of-file fixing
- ✅ Large file detection
- ✅ Secret detection
- ✅ Commit message format (Commitizen)

### Setup:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

---

## 📊 Code Coverage

**`codecov.yml`**

### Targets:
- **Project Coverage:** 80% minimum
- **Patch Coverage:** 70% minimum
- **Threshold:** 1% drop allowed

### Flags:
- `python`: Python code coverage
- `ml`: ML module coverage
- `frontend`: React frontend coverage

### Components:
1. Core Module
2. Bayesian Methods
3. Machine Learning
4. R Plotting
5. FastAPI Backend

### Integration:
```yaml
# Upload coverage in workflow
- uses: codecov/codecov-action@v4
  with:
    file: ./coverage.xml
    flags: python
    name: python-3.11
```

---

## 🧪 Test Configuration

**`pytest.ini`**

### Key Settings:

```ini
[pytest]
# Parallel execution
addopts = -n auto

# Coverage reporting
--cov=metapython
--cov-report=term-missing
--cov-report=html
--cov-report=xml

# Timeout for tests
--timeout=300

# Show slowest tests
--durations=10
```

### Test Markers:

```python
# Mark tests
@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.ml
@pytest.mark.r
@pytest.mark.api

# Run specific tests
pytest -m "not slow"  # Skip slow tests
pytest -m ml          # Only ML tests
pytest -m "integration and not slow"
```

---

## 🚦 Workflow Triggers

### Automatic Triggers:

```yaml
# Python CI
on:
  push:
    branches: [ main, develop, claude/** ]
  pull_request:
    branches: [ main, develop ]

# Release
on:
  push:
    tags: [ 'v*.*.*' ]

# Integration (scheduled)
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
```

### Manual Triggers:

```yaml
# All workflows support manual dispatch
on:
  workflow_dispatch:
```

**Run manually from GitHub:**
Actions → Select Workflow → Run workflow

---

## 📈 Performance Metrics

### Typical Run Times:

| Event | Total Time | Cost (GitHub Actions) |
|-------|------------|----------------------|
| **Push to branch** | ~40 min | $0.008/min × 40 = $0.32 |
| **Pull Request** | ~45 min | $0.36 |
| **Release** | ~30 min | $0.24 |
| **Scheduled** | ~30 min | $0.24/day |

**Monthly Estimate:** ~$15-20 (with GitHub Free tier: 2000 min/month free)

### Optimization Strategies:

1. **Dependency Caching**
   ```yaml
   - uses: actions/cache@v4
     with:
       path: ~/.cache/pip
       key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
   ```

2. **Matrix Reduction**
   ```yaml
   exclude:
     - os: macos-latest
       python-version: '3.9'  # Skip older versions on macOS
   ```

3. **Conditional Jobs**
   ```yaml
   if: github.event_name == 'push' && github.ref == 'refs/heads/main'
   ```

4. **Parallel Execution**
   ```yaml
   strategy:
     fail-fast: false  # Don't cancel other jobs on failure
   ```

---

## 🔐 Required Secrets

### GitHub Secrets:

```bash
# PyPI Publishing
PYPI_API_TOKEN=pypi-xxxxx

# Docker Hub
DOCKERHUB_USERNAME=username
DOCKERHUB_TOKEN=dckr_pat_xxxxx

# Codecov
CODECOV_TOKEN=xxxxx

# Snyk Security
SNYK_TOKEN=xxxxx

# Slack Notifications
SLACK_WEBHOOK=https://hooks.slack.com/services/xxxxx
```

### Setup:
1. Go to GitHub repo → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret

---

## 🐛 Troubleshooting

### Common Issues:

#### 1. **Tests Fail Locally But Pass in CI**
```bash
# Match CI environment
docker run -it python:3.11 bash
pip install -e .
pytest tests/
```

#### 2. **Dependency Cache Issues**
```yaml
# Clear cache by updating key
key: ${{ runner.os }}-pip-v2-${{ hashFiles('**/requirements.txt') }}
```

#### 3. **Timeout Errors**
```yaml
# Increase timeout
timeout-minutes: 30
```

#### 4. **R Package Installation Fails**
```yaml
# Install system dependencies first
- name: Install system deps
  run: |
    sudo apt-get update
    sudo apt-get install -y libcurl4-openssl-dev libssl-dev
```

---

## 📚 Best Practices

### 1. **Fast Feedback Loop**
- Unit tests run first (~5 min)
- Integration tests run later (~15 min)
- Expensive tests (ML, E2E) run in separate jobs

### 2. **Clear Failure Messages**
```yaml
- name: Run tests
  run: pytest -v --tb=short
```

### 3. **Artifact Preservation**
```yaml
- uses: actions/upload-artifact@v4
  if: always()  # Upload even on failure
  with:
    name: test-results
    path: test-output/
```

### 4. **Status Badges**

Add to README.md:
```markdown
[![Python CI](https://github.com/user/repo/workflows/Python%20CI/badge.svg)](https://github.com/user/repo/actions)
[![codecov](https://codecov.io/gh/user/repo/branch/main/graph/badge.svg)](https://codecov.io/gh/user/repo)
```

---

## 🎯 Summary

MetaPython's CI/CD pipeline provides:

✅ **Comprehensive Testing**
- Python 3.9-3.12 across Linux/macOS/Windows
- R package testing with devtools
- Frontend testing with Jest/Playwright
- Integration and E2E tests

✅ **Code Quality**
- Linting (Flake8, ESLint)
- Formatting (Black, Prettier)
- Type checking (MyPy, TypeScript)
- Security scanning (Bandit, Snyk, Trivy)

✅ **Automation**
- Pre-commit hooks
- Automated releases
- Docker image building
- Documentation deployment

✅ **Monitoring**
- Code coverage (Codecov)
- Performance benchmarks
- Bundle size tracking
- Lighthouse scores

**Total: 15+ jobs, 100+ checks per commit!** 🚀

---

## 📞 Support

**Issues?** Open a GitHub issue with the `ci/cd` label.

**Questions?** Check the [GitHub Actions docs](https://docs.github.com/en/actions).
