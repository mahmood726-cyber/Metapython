# MetaPython Governance and Community Guidelines

## Project Governance

### Vision
MetaPython aims to be the leading enterprise-grade meta-analysis platform, providing researchers with comprehensive statistical methods, enterprise integrations, and production-ready tools for evidence synthesis.

### Leadership Structure

#### Steering Committee
- **Lead Maintainer**: Responsible for strategic direction and final decisions
- **Technical Lead**: Oversees architecture and API design
- **Community Manager**: Manages community engagement and outreach

#### Core Team
- **Maintainers**: Have merge rights, guide project direction
- **Reviewers**: Review pull requests, mentor contributors
- **Contributors**: Submit code, documentation, and feedback

### RFC (Request for Comments) Process

#### When to Submit an RFC
- New major features or enterprise integrations
- Breaking API changes
- Significant architectural decisions
- New dependency additions

#### RFC Workflow
1. **Draft**: Create RFC using template in `/rfcs/template.md`
2. **Discussion**: 2-week community review period
3. **Decision**: Steering committee makes final decision
4. **Implementation**: Begin development after approval

#### RFC Template
```markdown
# RFC: [Feature Name]

## Summary
Brief description of the proposed feature.

## Motivation
Why is this change needed? What problems does it solve?

## Detailed Design
Technical specification and implementation details.

## Drawbacks
What are the potential downsides?

## Alternatives
What other approaches were considered?

## Adoption Strategy
How will users migrate to this feature?
```

### Contributor Ladder

#### 1. Contributor
**Requirements:**
- Signed CLA (Contributor License Agreement)
- Follows code of conduct

**Responsibilities:**
- Submit bug reports and feature requests
- Contribute code via pull requests
- Participate in community discussions

**Benefits:**
- Listed in contributors section
- Access to contributor Discord/Slack

#### 2. Reviewer
**Requirements:**
- 5+ meaningful contributions
- Demonstrated technical expertise
- Community endorsement

**Responsibilities:**
- Review pull requests in expertise area
- Mentor new contributors
- Participate in technical discussions

**Benefits:**
- Review assignment notifications
- Input on technical decisions
- Invitation to maintainer meetings (observer)

#### 3. Maintainer
**Requirements:**
- 20+ contributions across different areas
- Led major feature implementation
- Community trust and collaboration

**Responsibilities:**
- Merge pull requests
- Guide project direction
- Mentor reviewers and contributors
- Participate in governance decisions

**Benefits:**
- Merge permissions
- Voting rights on technical decisions
- Access to private maintainer channels

### Decision Making

#### Technical Decisions
- **Minor changes**: Any maintainer can approve
- **Major changes**: Requires RFC and majority maintainer approval
- **Breaking changes**: Requires RFC and 2/3 maintainer approval

#### Governance Decisions
- **Process changes**: Majority steering committee approval
- **Leadership changes**: Unanimous steering committee approval
- **Code of conduct updates**: Community input + steering committee approval

## Community Guidelines

### Code of Conduct

#### Our Pledge
We pledge to make participation in MetaPython a harassment-free experience for everyone, regardless of:
- Age, body size, disability, ethnicity
- Gender identity and expression
- Level of experience, education, socio-economic status
- Nationality, personal appearance, race, religion
- Sexual identity and orientation

#### Expected Behavior
- **Be respectful**: Treat all community members with dignity
- **Be collaborative**: Work together constructively
- **Be inclusive**: Welcome newcomers and diverse perspectives
- **Be patient**: Help others learn and grow
- **Be professional**: Maintain appropriate communication

#### Unacceptable Behavior
- Harassment, discrimination, or intimidation
- Offensive comments or personal attacks
- Public or private harassment
- Publishing private information without consent
- Trolling, spamming, or disruptive behavior

#### Enforcement

**Reporting:**
- Email: conduct@metapython.org
- Anonymous form: [reporting-form-link]
- Direct message to any steering committee member

**Response Timeline:**
- Initial response: Within 24 hours
- Investigation: Within 7 days
- Resolution: Within 14 days

**Consequences:**
1. **Warning**: Private warning with explanation
2. **Temporary Suspension**: 1-30 day ban from community spaces
3. **Permanent Ban**: Permanent exclusion from all community spaces

### Communication Channels

#### Primary Channels
- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Questions, announcements, general discussion
- **Discord/Slack**: Real-time chat (invite-only for contributors)

#### Meetings
- **Weekly Maintainer Sync**: Technical coordination (Tuesdays 2pm UTC)
- **Monthly Community Call**: Public updates and Q&A (First Friday 3pm UTC)
- **Quarterly Planning**: Roadmap and strategic planning

### Release Management

#### Release Schedule
- **Major Releases**: Every 6 months (January, July)
- **Minor Releases**: Monthly for new features
- **Patch Releases**: As needed for bug fixes

#### LTS (Long Term Support)
- **Duration**: 18 months
- **Scope**: Security patches and critical bug fixes only
- **Branches**: `v0.8.x`, `v1.0.x`, etc.

#### Release Process
1. **Feature Freeze**: 2 weeks before release
2. **Release Candidate**: 1 week testing period
3. **GA Release**: Tag, package, and announce
4. **Post-Release**: Monitor for critical issues

### Contribution Guidelines

#### Getting Started
1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Create** a feature branch
4. **Make** your changes with tests
5. **Submit** a pull request

#### Code Standards
- **Style**: Follow PEP 8 (enforced by Black)
- **Type Hints**: Required for all public APIs
- **Documentation**: Docstrings for all public functions
- **Tests**: Minimum 80% coverage for new code

#### Pull Request Process
1. **Description**: Clear explanation of changes
2. **Tests**: Include tests for new functionality
3. **Documentation**: Update docs if needed
4. **Review**: Address reviewer feedback
5. **Merge**: Maintainer merges after approval

#### Recognition
- **Contributors**: Listed in CONTRIBUTORS.md
- **Major Contributors**: Featured in release notes
- **Hall of Fame**: Annual recognition for outstanding contributions

## Enterprise Support

### Professional Services
- **Consulting**: Implementation guidance and best practices
- **Training**: Workshops and certification programs
- **Custom Development**: Tailored features for enterprise needs
- **Support**: Dedicated support channels for enterprise customers

### Partnership Program
- **Academic**: Free licenses for educational institutions
- **Research**: Collaboration on methodology development
- **Commercial**: Integration partnerships with BI/analytics vendors

### Sustainability
- **Funding**: Combination of corporate sponsorship and consulting revenue
- **Transparency**: Annual financial reports to community
- **Independence**: No single entity controls project direction

## Contact Information

### Leadership
- **Project Lead**: lead@metapython.org
- **Technical Lead**: tech@metapython.org
- **Community Manager**: community@metapython.org

### General
- **General Inquiries**: hello@metapython.org
- **Security Issues**: security@metapython.org
- **Code of Conduct**: conduct@metapython.org

### Social Media
- **Twitter**: @MetaPythonLib
- **LinkedIn**: MetaPython Project
- **YouTube**: MetaPython Tutorials

---

*Last Updated: December 2024*
*Next Review: June 2025*