# Contributing to MetaPython

Thank you for your interest in contributing to MetaPython! 🔬

This document provides guidelines for contributing to the project, including code contributions, documentation improvements, and bug reports.

## 🚀 Getting Started

### Prerequisites

1. **Python**: Version 3.8 or higher
2. **Git**: For version control
3. **Environment Setup**: Run `meta doctor` to check your environment

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/Metapython.git
   cd Metapython
   ```

2. **Install Dependencies**
   ```bash
   pip install numpy pandas scipy matplotlib seaborn
   pip install -e .  # Install in development mode
   ```

3. **Verify Installation**
   ```bash
   python -m metapython doctor
   ```

## 📋 Contribution Types

### 🐛 Bug Reports

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.yml) and include:

- **Environment Info**: Output from `meta doctor --format json`
- **Reproduction Steps**: Clear, minimal example
- **Expected vs Actual Behavior**
- **Error Messages**: Full stack traces

### ✨ Feature Requests

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.yml) and include:

- **Problem Statement**: What problem does this solve?
- **Proposed Solution**: How should it work?
- **Use Cases**: Who would benefit?
- **Implementation Ideas**: Technical approach (optional)

### 🔒 Security Issues

For security vulnerabilities:

1. **Private Disclosure**: Email security@metapython.example.com (preferred)
2. **Public Issues**: Use [Security Issue template](.github/ISSUE_TEMPLATE/security_issue.yml) for non-critical issues

### 📚 Documentation

Documentation improvements are always welcome:

- **API Documentation**: Improve docstrings and examples
- **User Guides**: Add tutorials and how-to guides
- **Translations**: Help translate documentation (see i18n section)

## 🔄 Development Workflow

### 1. Issue First

- **Search Existing Issues**: Check if already reported
- **Create Issue**: Use appropriate template
- **Discussion**: Engage with maintainers before major changes

### 2. Development Process

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes with good commit messages
git commit -m "feat: add meta doctor GPU diagnostics"

# Run tests and linting
python -m pytest tests/
python -m flake8 metapython.py

# Push and create PR
git push origin feature/your-feature-name
```

### 3. Pull Request Guidelines

Use the [PR template](.github/PULL_REQUEST_TEMPLATE.md) and ensure:

#### ✅ Code Quality
- [ ] Follows existing code style
- [ ] Includes type hints where appropriate
- [ ] No debugging print statements
- [ ] Proper error handling

#### 🧪 Testing
- [ ] All existing tests pass
- [ ] New tests for new functionality
- [ ] Edge cases covered
- [ ] Manual testing performed

#### 📖 Documentation
- [ ] Docstrings for new functions/classes
- [ ] README updated if needed
- [ ] Migration guide updated for breaking changes

#### 🔒 Security
- [ ] No sensitive data in code
- [ ] Input validation for user data
- [ ] Dependencies scanned for vulnerabilities

## 🎯 Development Guidelines

### Code Style

1. **Python Standards**
   - Follow PEP 8
   - Use type hints
   - Maximum line length: 88 characters
   - Use meaningful variable names

2. **Documentation Style**
   ```python
   def example_function(param: str, optional: bool = False) -> Dict[str, Any]:
       """
       Brief description of what the function does.
       
       Args:
           param: Description of param
           optional: Description of optional parameter
           
       Returns:
           Description of return value
           
       Raises:
           ValueError: When param is invalid
           
       Example:
           >>> result = example_function("test")
           >>> print(result["status"])
           success
       """
   ```

### Testing Guidelines

1. **Unit Tests**
   ```python
   def test_meta_doctor_diagnostics():
       """Test environment diagnostics functionality"""
       result = MetaDoctorDiagnostics.run_environment_check()
       assert result['overall_status'] in ['healthy', 'healthy_with_warnings', 'needs_attention']
       assert 'environment' in result
       assert 'dependencies' in result
   ```

2. **Integration Tests**
   - Test CLI commands end-to-end
   - Test with real data files
   - Test error conditions

### Backward Compatibility

MetaPython maintains strict backward compatibility:

1. **API Changes**
   - No breaking changes in minor versions
   - Deprecation warnings before removal
   - Migration guides for major versions

2. **Configuration**
   - Support old config formats
   - Clear upgrade paths
   - Validation with helpful error messages

## 🌍 Internationalization (i18n)

Help translate MetaPython documentation:

### Setup for Translation

1. **Install gettext tools**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install gettext
   
   # macOS
   brew install gettext
   ```

2. **Extract translatable strings**
   ```bash
   # Generate .pot template
   xgettext --language=Python --output=docs/locale/metapython.pot metapython.py
   ```

3. **Create language-specific translations**
   ```bash
   # Example for Spanish
   mkdir -p docs/locale/es/LC_MESSAGES
   msginit --input=docs/locale/metapython.pot --locale=es --output=docs/locale/es/LC_MESSAGES/metapython.po
   ```

### Supported Languages

Current translation status:
- 🇺🇸 English (100% - source)
- 🇪🇸 Spanish (0% - volunteers needed)
- 🇫🇷 French (0% - volunteers needed)  
- 🇩🇪 German (0% - volunteers needed)
- 🇨🇳 Chinese (0% - volunteers needed)

## 👥 Community Guidelines

### Code of Conduct

We follow the [Contributor Covenant](CODE_OF_CONDUCT.md). Be respectful, inclusive, and constructive.

### Communication

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Questions, ideas, showcases
- **Email**: security@metapython.example.com for security issues

### Recognition

Contributors are recognized in:
- Release notes
- Contributors section
- Special mentions for significant contributions

## 🔄 Release Process

### Version Numbering

MetaPython follows semantic versioning:
- **Major (X.0.0)**: Breaking changes
- **Minor (0.X.0)**: New features, backward compatible
- **Patch (0.0.X)**: Bug fixes, backward compatible

### Release Cycle

- **Major**: Annual (with LTS versions)
- **Minor**: Quarterly
- **Patch**: As needed for critical fixes

### Long-Term Support (LTS)

- Support window: 2 years for LTS versions
- Security backports to N-2 minor versions
- Migration assistance for breaking changes

## 🛠️ Maintainer Guidelines

### For Core Maintainers

1. **Review Process**
   - Code review within 48 hours
   - Security review for sensitive changes
   - Performance impact assessment

2. **Release Management**
   - Feature freeze before releases
   - Changelog maintenance
   - Docker image updates

3. **Community Management**
   - Respond to issues promptly
   - Guide new contributors
   - Maintain project roadmap

## 📞 Getting Help

### For Contributors

- **Documentation**: Start with README and docs/
- **Issues**: Search existing issues first
- **Discussions**: Ask questions in GitHub Discussions
- **Direct Contact**: Email for sensitive matters

### For Users

- **Environment Issues**: Run `meta doctor` first
- **Usage Questions**: GitHub Discussions
- **Bug Reports**: Use issue templates
- **Feature Requests**: Provide detailed use cases

---

Thank you for contributing to MetaPython! Your contributions help make meta-analysis more accessible and reliable for researchers worldwide. 🔬✨