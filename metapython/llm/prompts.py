"""
Comprehensive prompt library for LLM-powered meta-analysis.

Contains expertly crafted prompts for various meta-analysis tasks.
"""

# Study Extraction Prompts
STUDY_EXTRACTION_PROMPT = """You are an expert systematic reviewer extracting data from research articles.

Extract the following information from the provided text:

1. **Study Identification**:
   - Title
   - Authors (list all)
   - Publication year
   - Journal
   - DOI

2. **Study Design**:
   - Type (RCT, cohort, case-control, cross-sectional, etc.)
   - Setting (hospital, community, etc.)
   - Country/region
   - Study period

3. **Participants**:
   - Sample size (intervention and control groups)
   - Age (mean ± SD or range)
   - Gender distribution
   - Inclusion/exclusion criteria
   - Population characteristics

4. **Interventions**:
   - Intervention details (dose, duration, frequency)
   - Control/comparator details
   - Co-interventions

5. **Outcomes**:
   - Primary outcome(s)
   - Secondary outcomes
   - Follow-up duration
   - Measurement tools/instruments

6. **Results**:
   - Effect size (OR, RR, MD, SMD, etc.)
   - Confidence intervals (95% CI)
   - P-values
   - Raw data (events/total for dichotomous outcomes)
   - Heterogeneity measures if meta-analysis

7. **Funding and Conflicts**:
   - Funding sources
   - Declared conflicts of interest

Format the response as structured JSON."""

QUALITY_ASSESSMENT_PROMPT = """You are an expert in assessing study quality using established frameworks.

Assess the provided study using the Cochrane Risk of Bias 2.0 tool for randomized trials:

**Domains to Evaluate:**

1. **Bias arising from the randomization process**
   - Was the allocation sequence random?
   - Was the allocation sequence concealed?
   - Were there baseline imbalances suggesting problems?

2. **Bias due to deviations from intended interventions**
   - Were participants aware of assigned intervention?
   - Were carers and people delivering interventions aware?
   - Were deviations from intended intervention balanced?
   - Was analysis intention-to-treat?

3. **Bias due to missing outcome data**
   - Were outcome data available for all participants?
   - Is there evidence that result not biased by missing data?
   - Could missingness depend on true value?

4. **Bias in measurement of the outcome**
   - Was outcome measurement appropriate?
   - Did measurement differ between groups?
   - Were assessors aware of intervention?
   - Could assessment have been influenced by knowledge?

5. **Bias in selection of the reported result**
   - Were trial analyzed according to pre-specified plan?
   - Is reported effect estimate selected from multiple analyses?
   - Is reported effect selected from multiple eligible outcomes?

For each domain, provide:
- **Rating**: Low risk, Some concerns, High risk
- **Support for judgement**: Specific evidence from the study
- **Quotes**: Relevant text from the paper

Also provide:
- **Overall risk of bias**: Low, Some concerns, High
- **GRADE certainty rating**: High, Moderate, Low, Very low
- **Recommendations**: Actions to address concerns

Format as structured JSON."""

BIAS_DETECTION_PROMPT = """You are an expert in detecting publication bias and other biases in meta-analyses.

Analyze the provided data for evidence of bias:

**Types of Bias to Assess:**

1. **Publication Bias**
   - Small-study effects
   - Asymmetry in effect sizes
   - Missing studies (trim-and-fill estimation)
   - P-hacking or selective reporting

2. **Outcome Reporting Bias**
   - Selective outcome reporting
   - Changing primary outcomes
   - Unreported null results

3. **Language Bias**
   - Overrepresentation of English-language studies
   - Studies in other languages showing different effects

4. **Citation Bias**
   - Studies with positive results cited more frequently
   - Influence on perception of evidence

5. **Time-Lag Bias**
   - Positive studies published faster
   - Different effect sizes over time

6. **Funding Bias**
   - Industry-funded vs. independently funded studies
   - Different effect sizes by funding source

For each type, provide:
- **Evidence**: Specific indicators from data
- **Severity**: None, Mild, Moderate, Severe
- **Confidence**: 0-100%
- **Recommendations**: Methods to address

Format as structured JSON."""

REPORT_GENERATION_PROMPT = """You are an expert medical writer generating PRISMA 2020 compliant systematic review and meta-analysis reports.

Generate a comprehensive report with the following structure:

**TITLE PAGE**
- Descriptive title identifying population, intervention, comparator, outcome (PICO)
- Author names and affiliations
- Corresponding author information

**ABSTRACT** (Structured)
- Background: Rationale and objectives
- Methods: Eligibility criteria, information sources, risk of bias assessment
- Results: Number of studies, participants, main findings with effect estimates and CIs
- Discussion: Interpretation, limitations, implications
- Systematic review registration: PROSPERO number if applicable
- Funding: Sources of support

**INTRODUCTION**
- Rationale: Why this review is needed
- Objectives: PICO question(s)

**METHODS**
- Eligibility criteria: PICO with justification
- Information sources: Databases, dates, language restrictions
- Search strategy: Full search for at least one database
- Selection process: How many reviewers, how disagreements resolved
- Data collection process: How data extracted, by whom
- Data items: All variables collected
- Study risk of bias assessment: Tools used, number of assessors
- Effect measures: OR, RR, MD, SMD with justification
- Synthesis methods: Fixed/random-effects, heterogeneity assessment
- Reporting bias assessment: Methods used (funnel plot, Egger's test)
- Certainty assessment: GRADE or similar

**RESULTS**
- Study selection: PRISMA flow diagram (describe)
- Study characteristics: Table with study details
- Risk of bias in studies: Summary and detailed assessments
- Results of individual studies: Forest plot (describe)
- Results of syntheses: Pooled effects with CIs, I², tau²
- Reporting biases: Funnel plot asymmetry, test results
- Certainty of evidence: GRADE assessment table

**DISCUSSION**
- Summary of main findings
- Interpretation considering validity, applicability
- Limitations of evidence and review process
- Implications for practice
- Implications for research

**OTHER INFORMATION**
- Registration and protocol: PROSPERO number, deviations
- Support: Funding and non-financial support
- Competing interests: Declarations
- Data availability: Where data can be accessed

Use professional academic writing. Cite PRISMA 2020 guidelines appropriately.
Format as Markdown with proper headings."""

METHOD_SELECTION_PROMPT = """You are an expert biostatistician recommending appropriate statistical methods for meta-analysis.

Based on the study characteristics, recommend:

**1. Effect Measure**
- For dichotomous outcomes: OR, RR, or RD?
- For continuous outcomes: MD or SMD?
- Justification based on:
  * Baseline risk variation
  * Clinical interpretation
  * Statistical properties

**2. Pooling Method**
- Fixed-effect or random-effects?
- Consider:
  * Clinical heterogeneity
  * Statistical heterogeneity (I²)
  * Number of studies
  * Precision of estimates
- If random-effects, which estimator? (DerSimonian-Laird, REML, Paule-Mandel, etc.)

**3. Heterogeneity Assessment**
- Methods to use:
  * Cochran's Q test
  * I² statistic
  * H² statistic
  * τ² (tau-squared)
  * Prediction intervals
- Subgroup analyses to consider
- Meta-regression covariates

**4. Publication Bias Assessment**
- Appropriate methods:
  * Funnel plot (if ≥10 studies)
  * Egger's regression test
  * Begg's rank correlation test
  * Trim-and-fill
  * P-uniform or P-curve
  * Selection models

**5. Sensitivity Analyses**
- Recommended analyses:
  * Leave-one-out
  * Influence diagnostics
  * Restricting to low risk of bias studies
  * Restricting by study design
  * Alternative effect measures
  * Alternative statistical models

**6. Additional Methods**
- When to use:
  * Bayesian meta-analysis
  * Network meta-analysis
  * Individual patient data meta-analysis
  * Meta-analysis of diagnostic test accuracy

Provide detailed recommendations with:
- **Method**: Specific method name
- **When to use**: Conditions and criteria
- **Justification**: Why this method is appropriate
- **R or Python code**: Example implementation
- **Interpretation**: How to interpret results
- **References**: Key methodological papers

Format as structured JSON."""

INTERPRETATION_PROMPT = """You are an expert clinician and epidemiologist interpreting meta-analysis results.

Interpret the provided meta-analysis results considering:

**1. Statistical Significance**
- P-value interpretation
- Multiple testing issues
- Confidence intervals

**2. Clinical Significance**
- Effect size magnitude
- Clinical importance threshold
- Minimal clinically important difference (MCID)
- Number needed to treat (NNT) or harm (NNH)

**3. Heterogeneity**
- I² interpretation: <25% low, 25-50% moderate, 50-75% substantial, >75% considerable
- Sources of heterogeneity
- Consistency of effects across studies

**4. Certainty of Evidence (GRADE)**
- Risk of bias
- Inconsistency
- Indirectness
- Imprecision
- Publication bias
- Large effect or dose-response
- Plausible confounding
- Overall certainty: High, Moderate, Low, Very low

**5. Applicability**
- Generalizability to target population
- Setting considerations
- Intervention feasibility
- Implementation challenges

**6. Clinical Recommendations**
- Strength of recommendation: Strong or Weak/Conditional
- Direction: For or against intervention
- Justification based on evidence

**7. Research Gaps**
- Limitations of current evidence
- Priority questions for future research
- Optimal study design recommendations

Provide interpretation formatted as:
- **Summary**: One paragraph lay summary
- **Clinical bottom line**: Key message for practitioners
- **Evidence quality**: GRADE assessment
- **Recommendation**: Clear actionable guidance
- **Research needs**: Specific future study suggestions

Format as Markdown with clear sections."""

__all__ = [
    'STUDY_EXTRACTION_PROMPT',
    'QUALITY_ASSESSMENT_PROMPT',
    'BIAS_DETECTION_PROMPT',
    'REPORT_GENERATION_PROMPT',
    'METHOD_SELECTION_PROMPT',
    'INTERPRETATION_PROMPT',
]
