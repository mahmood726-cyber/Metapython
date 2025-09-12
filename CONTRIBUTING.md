# Contributing to MetaPython

Thank you for your interest in contributing to MetaPython! This document provides guidelines for contributing to the project.

## 🎯 How to Contribute

### Reporting Issues

Before reporting an issue, please:

1. **Search existing issues** to avoid duplicates
2. **Use the issue templates** when available
3. **Provide a minimal reproducible example** when reporting bugs
4. **Include your environment details** (OS, Python version, MetaPython version)

### Suggesting Features

For feature requests:

1. **Check the roadmap** in README.md to see if it's already planned
2. **Open a discussion** first for major features
3. **Describe the use case** and how it would benefit users
4. **Consider backward compatibility** implications

### Contributing Code

#### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/mahmood726-cyber/Metapython.git
cd Metapython

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[full]

# Install pre-commit hooks
pre-commit install
```

#### Development Workflow

1. **Fork the repository** and create a feature branch
2. **Make your changes** with appropriate tests
3. **Run the test suite** and ensure all tests pass
4. **Check code style** with our linting tools
5. **Submit a pull request** with a clear description

#### Code Style

We use automated code formatting and linting:

```bash
# Format code
black metapython.py
isort metapython.py

# Lint code
flake8 metapython.py
mypy metapython.py

# Run all checks
pre-commit run --all-files
```

#### Testing

Our testing strategy includes:

- **Unit tests**: Test individual functions and classes
- **Integration tests**: Test component interactions
- **Property-based tests**: Test with generated inputs (Hypothesis)
- **Golden tests**: Test against reference outputs
- **Contract tests**: Test CLI/API interfaces

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=metapython

# Run specific test types
pytest tests/unit/
pytest tests/integration/
pytest tests/property_based/
```

#### Documentation

When contributing code, please also:

1. **Update docstrings** following Google/NumPy style
2. **Add examples** to docstrings when appropriate
3. **Update relevant documentation** in `docs/`
4. **Add entries to CHANGELOG.md** for user-facing changes

### Contributing Documentation

Documentation improvements are always welcome:

- Fix typos and grammatical errors
- Improve existing explanations
- Add examples and tutorials
- Translate documentation
- Create video tutorials

#### Building Documentation

```bash
# Install documentation dependencies
pip install -e .[docs]

# Build documentation
cd docs
make html

# Serve locally
python -m http.server 8000 -d _build/html
```

## 🏗️ Development Guidelines

### Backward Compatibility

MetaPython maintains strict backward compatibility:

- **Public API**: Never break existing public interfaces
- **Default behavior**: Changes should not affect default outputs
- **Deprecation**: Use warnings before removing features
- **Migration guides**: Provide clear upgrade paths

### Performance Considerations

- **Optional dependencies**: Keep heavy dependencies optional
- **Memory efficiency**: Use generators and chunking for large datasets
- **Computational complexity**: Document algorithmic complexity
- **Benchmarking**: Include performance tests for critical paths

### Error Handling

- **Meaningful messages**: Provide actionable error messages
- **Input validation**: Validate inputs with helpful feedback
- **Graceful fallbacks**: Handle missing optional dependencies
- **Recovery**: Allow users to recover from errors when possible

### Testing Requirements

All contributions must include appropriate tests:

- **New features**: Comprehensive test coverage (>90%)
- **Bug fixes**: Tests that reproduce the bug
- **Documentation**: Doctests for code examples
- **CLI changes**: Integration tests for command-line interface

## 📋 Pull Request Process

### Before Submitting

- [ ] All tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Commit messages are descriptive

### Pull Request Template

Please use this template for pull requests:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Code coverage maintained/improved

## Documentation
- [ ] Docstrings updated
- [ ] User documentation updated
- [ ] Examples updated/added

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] No new warnings introduced
```

### Review Process

1. **Automated checks**: CI/CD pipeline runs automatically
2. **Maintainer review**: Core team reviews the code
3. **Community feedback**: Others may provide feedback
4. **Approval**: At least one maintainer approval required
5. **Merge**: Squash and merge into main branch

## 🎖️ Recognition

Contributors are recognized in several ways:

- **AUTHORS.md**: All contributors listed
- **Release notes**: Significant contributions highlighted
- **GitHub contributors**: Automatic recognition on repository
- **Citation**: Option to be included in academic citations

## 🏷️ Issue and PR Labels

We use labels to organize issues and pull requests:

### Type Labels
- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `performance`: Performance-related changes
- `testing`: Testing-related changes

### Priority Labels
- `critical`: Critical issues that need immediate attention
- `high`: High priority issues
- `medium`: Medium priority issues
- `low`: Low priority issues

### Status Labels
- `needs-review`: Waiting for review
- `needs-changes`: Changes requested
- `ready-to-merge`: Approved and ready to merge
- `blocked`: Blocked by other issues

### Area Labels
- `cli`: Command-line interface
- `api`: Public API changes
- `core`: Core meta-analysis functionality
- `visualization`: Plotting and visualization
- `docs`: Documentation
- `tests`: Testing infrastructure

## 🤝 Code of Conduct

Please note that this project is released with a [Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## 💬 Communication

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Email**: pymeta-cbamm@example.com for private matters

## 🎓 Learning Resources

For contributors new to meta-analysis:

- [Cochrane Handbook](https://handbook-5-1.cochrane.org/)
- [Meta-Analysis in Medical Research](https://doi.org/10.1002/9780470994604)
- [Introduction to Meta-Analysis](https://doi.org/10.1002/9781119558378)

For Python development:

- [Python Developer's Guide](https://devguide.python.org/)
- [Real Python Tutorials](https://realpython.com/)
- [Scientific Python Development Guide](https://learn.scientific-python.org/development/)

Thank you for contributing to MetaPython! 🎉