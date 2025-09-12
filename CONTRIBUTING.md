# Contributing to MetaPython

Thank you for your interest in contributing to MetaPython! This guide will help you get started.

## 🚀 Quick Start

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/your-username/Metapython.git
   cd Metapython
   ```
3. **Install** development dependencies:
   ```bash
   pip install -e ".[dev,all]"
   ```
4. **Create** a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🧪 Testing

Run tests before submitting:
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_phase13_features.py -v

# Check health
python -m metapython --health-check
```

## 📝 Code Standards

- **Style**: Follow PEP 8 (use Black for formatting)
- **Type Hints**: Required for all public APIs
- **Documentation**: Docstrings for all public functions
- **Tests**: Minimum 80% coverage for new code

## 🔄 Pull Request Process

1. **Update** your branch with main:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```
2. **Ensure** tests pass and code is formatted
3. **Submit** pull request with clear description
4. **Address** reviewer feedback promptly

## 💡 Types of Contributions

### 🐛 Bug Reports
- Use the bug report template
- Include minimal reproduction case
- Specify environment details

### ✨ Feature Requests  
- Use the feature request template
- Explain the use case and motivation
- Consider RFC for major features

### 📚 Documentation
- Fix typos and improve clarity
- Add examples and tutorials
- Update API documentation

### 🔧 Code Contributions
- New statistical methods
- Performance optimizations
- Enterprise integrations
- Bug fixes

## 🎯 Areas Needing Help

- **R Bridge**: Improve reticulate integration
- **Documentation**: API examples and tutorials
- **Testing**: Enterprise feature test coverage
- **Performance**: Profiling and optimization
- **Connectors**: Additional BI tool integrations

## 📋 Development Setup

### Core Dependencies
```bash
pip install numpy pandas matplotlib seaborn scipy
```

### Enterprise Dependencies (Optional)
```bash
pip install opentelemetry-api prometheus-client boto3
```

### Development Tools
```bash
pip install pytest black flake8 mypy
```

## 🏆 Recognition

Contributors are recognized in:
- **CONTRIBUTORS.md**: All contributors listed
- **Release Notes**: Major contributors featured
- **Annual Awards**: Outstanding contribution recognition

## 📞 Getting Help

- **GitHub Discussions**: General questions
- **Discord**: Real-time developer chat (invite-only)
- **Email**: dev@metapython.org

## 📜 Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

---

**Happy Contributing! 🎉**