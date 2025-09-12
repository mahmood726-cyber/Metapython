# RFC Process for Metapython

This document describes the RFC (Request for Comments) process for Metapython, which is used for proposing and discussing major changes to the library.

## When to Use the RFC Process

The RFC process should be used for:

- New major features or significant API changes
- Changes to core algorithms or methodologies
- Breaking changes to existing functionality
- New plugin APIs or extension points
- Significant performance optimizations
- Changes to the project governance or development process

Minor changes, bug fixes, and documentation improvements typically don't require an RFC.

## RFC Lifecycle

### 1. Pre-RFC Discussion

Before writing a formal RFC, consider:
- Discussing the idea in GitHub issues or discussions
- Checking if similar proposals already exist
- Gathering initial feedback from the community

### 2. RFC Creation

1. **Fork the repository** and create a new branch
2. **Copy the RFC template** from `docs/community/RFCs/RFC_TEMPLATE.md`
3. **Name your RFC file** as `RFC-NNNN-short-title.md` where NNNN is the next available number
4. **Fill out the template** with your proposal details
5. **Create a pull request** with your RFC

### 3. Discussion Period

- The RFC enters a **public discussion period** of at least 2 weeks
- Community members can comment on the PR
- The RFC author should be responsive to feedback and update the RFC as needed
- Core maintainers will participate in the discussion

### 4. Final Comment Period (FCP)

- When discussion has settled, a core maintainer will propose entering **Final Comment Period**
- FCP lasts for 1 week, allowing final objections or concerns
- The community has one last chance to raise blocking concerns

### 5. Decision

After FCP, the RFC will be either:
- **Accepted**: Merged into the main branch and implementation can begin
- **Rejected**: Closed with a detailed explanation
- **Postponed**: Closed but may be reconsidered in the future

### 6. Implementation

- Accepted RFCs should have associated tracking issues for implementation
- Implementation may reveal design flaws that require RFC amendments
- RFC authors are encouraged to implement their proposals but it's not required

## RFC Status Labels

RFCs use the following status labels:

- **DRAFT**: Initial proposal, still being refined by the author
- **UNDER REVIEW**: Open for community discussion
- **FCP**: In Final Comment Period
- **ACCEPTED**: Approved for implementation
- **REJECTED**: Not approved
- **POSTPONED**: Deferred to future consideration
- **IMPLEMENTED**: Implementation is complete

## Governance

### RFC Shepherds

Each RFC will be assigned a **shepherd** from the core team who will:
- Guide the RFC through the process
- Ensure discussions remain constructive
- Help determine when to enter FCP
- Make the final accept/reject decision

### Core Team Decision Making

The core team strives for consensus but may make decisions by majority vote when necessary. All core team members have equal say in RFC decisions.

## Guidelines for RFC Authors

### Writing Good RFCs

- **Be specific**: Provide concrete details and examples
- **Consider alternatives**: Explain why other approaches won't work
- **Address drawbacks**: Acknowledge potential downsides
- **Include implementation notes**: Help implementers understand the design

### Responding to Feedback

- **Be responsive**: Engage with comments and questions promptly
- **Be open-minded**: Consider suggestions for improvements
- **Update the RFC**: Incorporate good feedback into the proposal
- **Summarize changes**: Note significant updates in PR comments

### Common Pitfalls

- Proposing changes without sufficient motivation
- Not considering backward compatibility
- Ignoring performance implications
- Insufficient consideration of edge cases
- Not engaging with community feedback

## RFC Index

| RFC | Title | Status | Author | Date |
|-----|-------|--------|--------|------|
| 0001 | Plugin System Architecture | IMPLEMENTED | Core Team | 2024-01 |
| ... | ... | ... | ... | ... |

## Resources

- [RFC Template](RFC_TEMPLATE.md)
- [GitHub Discussions](https://github.com/mahmood726-cyber/Metapython/discussions)
- [Contributing Guidelines](../CONTRIBUTING.md)
- [Code of Conduct](../CODE_OF_CONDUCT.md)

## Questions?

If you have questions about the RFC process, please:
- Check existing RFCs for examples
- Ask in GitHub discussions
- Reach out to core team members
- Open an issue for process improvements