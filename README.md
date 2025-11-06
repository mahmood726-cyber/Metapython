# MetaPython: Pre-Registered CI/CD Optimization Study

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Pre-Registration](https://img.shields.io/badge/Status-Pre--Registered-blue.svg)]()
[![Data: Partial](https://img.shields.io/badge/Data-Partial%20(6%2F66%20builds)-orange.svg)]()

> **Note**: This repository contains a **pre-registered methodology template** for rigorous CI/CD optimization studies. While analysis infrastructure is complete, baseline data collection is pending. See [METHODOLOGY_STATUS.md](METHODOLOGY_STATUS.md) for details.

## What Is This?

This project demonstrates **how to conduct publication-quality empirical software engineering research** on CI/CD optimization, using pre-registration to prevent p-hacking and selective reporting.

**What we provide:**
- ✅ Complete research protocol with pre-registered hypotheses
- ✅ Statistical analysis infrastructure (R scripts, Docker, data formats)
- ✅ Comprehensive literature review (35+ citations)
- ✅ Practitioner implementation guide
- ✅ Comparative analysis of 7 dependency management approaches
- ⏳ Partial empirical data (6/66 builds collected)

**What makes this unique:**
- 🎯 **Pre-registered**: Hypotheses and analysis plan documented *before* full data collection
- 📊 **Rigorous**: Power analysis, Bonferroni correction, threats to validity
- 🔬 **Replicable**: Complete protocol + Docker environment + synthetic data showing format
- 📚 **Well-positioned**: 35+ literature citations, gap analysis, comparative evaluation
- 🎓 **Educational**: Shows what "good" empirical SE research looks like

## Quick Links

### Core Methodology Documents
- 📋 **[METHODOLOGY_STATUS.md](METHODOLOGY_STATUS.md)** - **START HERE**: Explains what we have, what we don't, and why this is valuable
- 🔬 **[RESEARCH_METHODOLOGY.md](RESEARCH_METHODOLOGY.md)** - Pre-registered experimental design, hypotheses, and protocol
- 📊 **[STATISTICAL_ANALYSIS.md](STATISTICAL_ANALYSIS.md)** - Pre-specified statistical tests and analysis plan
- 📦 **[REPLICATION_PACKAGE.md](REPLICATION_PACKAGE.md)** - Complete replication instructions with Docker

### Context and Comparisons
- 📚 **[RELATED_WORK.md](RELATED_WORK.md)** - Literature review (35+ papers), gap analysis, positioning
- ⚖️ **[COMPARATIVE_ANALYSIS.md](COMPARATIVE_ANALYSIS.md)** - Systematic comparison of 7 dependency management approaches
- 👷 **[PRACTITIONER_GUIDE.md](PRACTITIONER_GUIDE.md)** - Step-by-step implementation guide, cost-benefit analysis, decision matrix

### Analysis Infrastructure
- 📂 **[analysis/](analysis/)** - R scripts, data formats, Docker environment
  - `scripts/` - RQ1/RQ2/RQ3 analysis + master script
  - `data/` - Synthetic baseline + partial real intervention data
  - `results/` - Output directory for statistical tests and plots

## Research Questions

Our study investigates three pre-registered research questions:

### RQ1: Dependency Stratification and Build Time
**Hypothesis**: Separating dependencies into production/testing/development tiers reduces CI/CD build times.
- **Baseline target**: n=32 builds (to be collected)
- **Intervention target**: n=34 builds (6/34 collected)
- **Expected effect**: ~60-75% reduction (12-13 min vs. 18 min)

### RQ2: System Dependencies and Test Success
**Hypothesis**: Adding system dependencies (python3-dev, libopenblas-dev) improves test success rates on Ubuntu/Windows.
- **Baseline**: 0% success on Ubuntu/Windows (from troubleshooting experience)
- **Expected improvement**: ~90-95% success rate

### RQ3: Security Improvements
**Hypothesis**: Replacing bare `except:` with specific `except Exception as e:` reduces static analysis vulnerabilities.
- ✅ **Status**: COMPLETE with real data
- **Result**: 4 vulnerabilities → 0 (100% reduction)
- **Statistical test**: McNemar's test (p=0.046), Sign test (p=0.0625)

## Current Status

| Component | Status | Details |
|-----------|--------|---------|
| Research protocol | ✅ Complete | Pre-registered RQs, hypotheses, α levels |
| Analysis scripts | ✅ Complete | 4 R scripts (600+ lines), tested on synthetic data |
| Literature review | ✅ Complete | 35+ citations, gap analysis |
| Baseline data | ⚠️ Pending | n=0/32 (synthetic data available as template) |
| Intervention data | 🟡 Partial | n=6/34 (12-13 min for successful builds) |
| Security data | ✅ Complete | 4→0 vulnerabilities (actual code changes) |

**Why no baseline?**
CI/CD workflows were first added November 5, 2025 (already optimized). To collect baseline, we must:
1. Revert to monolithic `requirements.txt`
2. Trigger 32 builds over 2-3 weeks
3. Then re-apply optimization

## How to Use This Repository

### As a Researcher

**Option 1: Replicate our methodology on your project**
```bash
# 1. Clone and adapt the protocol
git clone https://github.com/mahmood726-cyber/Metapython.git
cd Metapython
# Edit RESEARCH_METHODOLOGY.md for your context

# 2. Collect your baseline data (following our protocol)
# See REPLICATION_PACKAGE.md for detailed steps

# 3. Apply optimization to your project
# See PRACTITIONER_GUIDE.md for implementation

# 4. Collect intervention data

# 5. Run our R scripts on your data
cd analysis/scripts
Rscript run_all_analyses.R
```

**Option 2: Meta-analysis**
If 5-10 groups follow this protocol on different projects, we can conduct a meta-analysis to assess generalizability.

### As a Practitioner

**Want to optimize your CI/CD?**
1. Read [PRACTITIONER_GUIDE.md](PRACTITIONER_GUIDE.md) (step-by-step implementation)
2. Check [COMPARATIVE_ANALYSIS.md](COMPARATIVE_ANALYSIS.md) (is 3-tier pip right for you?)
3. Use decision matrix to assess if approach fits your context
4. Follow implementation guide
5. Optionally: Collect data following our protocol and contribute to meta-analysis

### As an Educator

**Teaching empirical software engineering?**
- Use RESEARCH_METHODOLOGY.md as example of pre-registration
- Show STATISTICAL_ANALYSIS.md for proper statistical reporting
- Compare RELATED_WORK.md to typical "related work" sections
- Demonstrate value of replication packages with our REPLICATION_PACKAGE.md

## Quick Start: Run Analysis on Synthetic Data

Even without real baseline data, you can test the analysis pipeline:

```bash
# Clone repository
git clone https://github.com/mahmood726-cyber/Metapython.git
cd Metapython

# Option 1: Docker (recommended)
docker build -t metapython-analysis -f Dockerfile.analysis .
docker run -v $(pwd)/analysis:/analysis metapython-analysis

# Option 2: Native R
cd analysis/scripts
Rscript run_all_analyses.R

# View results
cat analysis/results/rq1_results.txt
cat analysis/results/rq2_results.txt
cat analysis/results/rq3_results.txt
ls analysis/results/figures/
```

**Note**: Results use synthetic baseline data (realistic but illustrative). Output demonstrates the analysis pipeline works and shows expected format.

## Citation

If you use this methodology, analysis infrastructure, or approach in your research:

### APA Format
```
Claude (Anthropic) & mahmood726-cyber. (2025). MetaPython: Pre-registered
methodology for rigorous CI/CD optimization studies. GitHub repository.
https://github.com/mahmood726-cyber/Metapython
```

### BibTeX
```bibtex
@misc{metapython2025,
  title = {MetaPython: Pre-Registered Methodology for Rigorous CI/CD Optimization Studies},
  author = {Claude (Anthropic) and mahmood726-cyber},
  year = {2025},
  publisher = {GitHub},
  howpublished = {\url{https://github.com/mahmood726-cyber/Metapython}},
  note = {Pre-registered protocol with analysis infrastructure}
}
```

## Contributing

We welcome contributions:
- 🐛 **Bug reports**: Issues in R scripts or Docker environment
- 📊 **Data**: Share your results following our protocol
- 📝 **Improvements**: Suggest methodology enhancements
- 🔄 **Replications**: Adapt protocol to your project

See [REPLICATION_PACKAGE.md](REPLICATION_PACKAGE.md) for how to collect data following our protocol.

## License

- **Code** (R scripts, Docker): MIT License
- **Documentation**: CC BY 4.0
- **Data** (once collected): CC BY 4.0

See LICENSE file for details.

## Acknowledgments

- **GitHub Actions**: Free CI/CD infrastructure for open source
- **R Community**: tidyverse, ggplot2, effsize, pwr packages
- **Reviewers**: Critical feedback that pushed us toward pre-registration
- **Open Science Movement**: Inspiration for transparency and rigor

## FAQ

### Q: Why publish before collecting all data?

**A**: Demonstrates pre-registration best practices. Protocol and analysis plan documented *before* seeing results prevents p-hacking and selective reporting. This is standard in medicine (clinical trials) and psychology (registered reports) but rare in software engineering.

### Q: Can I use this if I'm not a researcher?

**A**: Yes! See [PRACTITIONER_GUIDE.md](PRACTITIONER_GUIDE.md) for step-by-step implementation without the research methodology.

### Q: What if I want to compare Docker vs. Conda instead?

**A**: Adapt the protocol! Our comparative analysis ([COMPARATIVE_ANALYSIS.md](COMPARATIVE_ANALYSIS.md)) covers 7 approaches. Choose the comparison relevant to your context.

### Q: How do I know if this approach fits my project?

**A**: See decision matrix in [PRACTITIONER_GUIDE.md](PRACTITIONER_GUIDE.md) - "When This Guide Applies" section. Not a universal solution!

### Q: What if your final results contradict your hypotheses?

**A**: We'll publish anyway. That's the commitment of pre-registration. Negative results are valuable for preventing publication bias.

## Contact

- **Issues**: https://github.com/mahmood726-cyber/Metapython/issues
- **Discussions**: https://github.com/mahmood726-cyber/Metapython/discussions
- **Email**: mahmood726-cyber@github.com (use "MetaPython:" prefix)

---

**Last Updated**: November 6, 2025
**Version**: 1.0 (Pre-registration)
**Status**: Data collection in progress (6/66 builds)
