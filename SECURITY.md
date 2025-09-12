# Security Policy

## Supported Versions

MetaPython follows a Long-Term Support (LTS) model for security updates:

| Version | Supported          | Support Type | End of Support |
| ------- | ------------------ | ------------ | -------------- |
| 0.6.x   | ✅ Current        | Full Support | TBD            |
| 0.5.x   | ✅ LTS            | Security Only| Dec 2025       |
| 0.4.x   | ⚠️ Limited       | Critical Only| Jun 2025       |
| < 0.4   | ❌ Not Supported  | None         | N/A            |

### Support Types

- **Full Support**: New features, bug fixes, security patches
- **Security Only**: Security patches and critical bug fixes
- **Critical Only**: Only critical security vulnerabilities
- **Not Supported**: No updates provided

## Reporting a Vulnerability

### 🔒 Private Disclosure (Recommended)

For security vulnerabilities, please contact us privately:

**Email**: security@metapython.example.com

**Response Time**: Within 48 hours

**What to Include**:
- Description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Suggested mitigation (if any)

### 📋 Public Disclosure

For non-critical security issues, you can use our [Security Issue Template](.github/ISSUE_TEMPLATE/security_issue.yml).

## Security Considerations by Component

### Core Meta-Analysis Engine

**Risk Level**: Low
- Statistical computations with validated inputs
- No network access or file system modifications
- Defensive programming against malformed data

**Security Measures**:
- Input validation for all user data
- Bounds checking for numerical computations
- Exception handling for edge cases

### CLI Interface

**Risk Level**: Medium
- File system access for data loading
- Command execution capabilities
- Configuration file parsing

**Security Measures**:
- Path validation and sandboxing
- Safe YAML/JSON parsing
- Input sanitization
- No arbitrary code execution

### Healthcare Data Integration

**Risk Level**: High (when enabled)
- External API access (FHIR)
- Database connections (OMOP)
- Potential PHI/PII handling

**Security Measures**:
- Optional via extras (`pip install 'metapython[healthcare]'`)
- TLS/SSL required for external connections
- No credential storage in code
- Data anonymization recommendations
- Audit logging for data access

### Federated Analysis (Prototype)

**Risk Level**: High (experimental)
- Network communication between sites
- Cryptographic operations
- Multi-party computation

**Security Measures**:
- Prototype status clearly marked
- Differential privacy implementation
- Secure aggregation protocols
- No production deployment recommended

## Threat Model

### Assets Protected

1. **User Data**: Meta-analysis datasets, study information
2. **Research Results**: Statistical outputs, publication-ready analyses
3. **System Resources**: Computational resources, file system
4. **Healthcare Data**: PHI/PII in healthcare integrations (when enabled)

### Threat Actors

1. **Malicious Users**: Attempting to exploit CLI or API
2. **Compromised Dependencies**: Supply chain attacks
3. **Network Attackers**: Intercepting federated communications
4. **Insider Threats**: Misuse of healthcare data access

### Attack Vectors

1. **Malicious Input Files**: Crafted CSV/Excel files
2. **Configuration Injection**: Malicious YAML/JSON configs
3. **Dependency Vulnerabilities**: Compromised packages
4. **Network Attacks**: Man-in-the-middle on federated analysis
5. **Data Exfiltration**: Unauthorized access to sensitive data

## Security Best Practices

### For Users

1. **Environment Security**
   ```bash
   # Run security diagnostics
   meta doctor --include-security-check
   
   # Verify installation integrity
   pip check metapython
   ```

2. **Data Protection**
   - Use anonymized datasets when possible
   - Validate data sources before analysis
   - Secure file permissions on analysis results
   - Regular backups with encryption

3. **Configuration Security**
   - Use configuration validation: `meta config validate`
   - Avoid hardcoded credentials
   - Use environment variables for sensitive settings
   - Regular security audits of configurations

### For Developers

1. **Secure Coding**
   ```python
   # Input validation example
   def validate_effect_sizes(effects: List[float]) -> List[float]:
       """Validate and sanitize effect size inputs"""
       if not effects:
           raise ValueError("Effect sizes cannot be empty")
       
       validated = []
       for i, effect in enumerate(effects):
           if not isinstance(effect, (int, float)):
               raise TypeError(f"Effect size {i} must be numeric")
           if abs(effect) > 100:  # Reasonable bound
               raise ValueError(f"Effect size {i} outside reasonable bounds")
           validated.append(float(effect))
       
       return validated
   ```

2. **Dependency Management**
   - Pin dependency versions
   - Regular security scanning with `pip-audit`
   - Monitor security advisories
   - Use minimal required permissions

3. **Testing Security**
   ```python
   def test_input_validation():
       """Test that malicious inputs are rejected"""
       with pytest.raises(ValueError):
           validate_effect_sizes([1e10, -1e10])  # Extreme values
       
       with pytest.raises(TypeError):
           validate_effect_sizes(["malicious_string"])  # Wrong type
   ```

## Vulnerability Response Process

### 1. Initial Response (0-48 hours)

- Acknowledge receipt of report
- Assign severity level (Critical, High, Medium, Low)
- Create internal tracking issue
- Assemble response team

### 2. Investigation (2-7 days)

- Reproduce the vulnerability
- Assess impact and scope
- Develop mitigation strategies
- Estimate fix timeline

### 3. Resolution (1-4 weeks)

- Develop and test fix
- Create security advisory
- Coordinate disclosure timeline
- Prepare release with fix

### 4. Disclosure (After fix)

- Public security advisory
- CVE assignment (if applicable)
- Update documentation
- Notify users of security update

## Security Advisory Process

### Advisory Format

```
METAPYTHON-YYYY-NNN: [Title]

Severity: [Critical|High|Medium|Low]
CVSS Score: [If applicable]
Affected Versions: [Version range]
Fixed In: [Version number]

Description:
[Detailed description of vulnerability]

Impact:
[What attackers could achieve]

Mitigation:
[Temporary workarounds if available]

Resolution:
[How to update and fix]
```

### Distribution

- GitHub Security Advisories
- Mailing list notifications
- Documentation updates
- Social media announcements (for critical issues)

## Compliance and Standards

### Healthcare Compliance (Optional Features)

When using healthcare integrations:

- **HIPAA**: Guidelines for PHI handling
- **GDPR**: Data protection and privacy
- **FDA**: Guidance for medical device software
- **ISO 27001**: Information security management

### Security Standards

- **OWASP**: Web application security (for web interfaces)
- **NIST**: Cybersecurity framework
- **CIS**: Security benchmarks
- **SANS**: Security awareness and training

## Security Tools and Automation

### Automated Security Scanning

```yaml
# .github/workflows/security.yml
name: Security Scan
on: [push, pull_request]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: github/super-linter@v4
        env:
          DEFAULT_BRANCH: main
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Run safety check
        run: |
          pip install safety
          safety check
```

### Dependency Monitoring

- **Dependabot**: Automated dependency updates
- **pip-audit**: Python package vulnerability scanning
- **GitHub Security Advisories**: Automated notifications

## Contact Information

### Security Team

- **Primary Contact**: security@metapython.example.com
- **Backup Contact**: mahmood726-cyber@github.com
- **PGP Key**: [Available on request]

### Responsible Disclosure

We appreciate responsible disclosure and will:
- Acknowledge your contribution publicly (with permission)
- Provide updates on fix progress
- Credit you in security advisories
- Consider bounty programs for significant vulnerabilities

---

**Last Updated**: Phase 9 Implementation
**Next Review**: Quarterly security review scheduled