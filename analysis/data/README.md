# Data Directory - Status and Description

## ⚠️ DATA STATUS

**Current Status**: This directory contains **SYNTHETIC** (illustrative) data for template/protocol purposes.

### What's in This Directory

| File | Status | Description |
|------|--------|-------------|
| `baseline_build_times.csv` | ⚠️ SYNTHETIC | Illustrative baseline data (n=32) showing expected format |
| `baseline_test_results.csv` | ⚠️ SYNTHETIC | Illustrative test results showing expected format |
| `intervention_build_times.csv` | ⏳ TO BE COLLECTED | Will contain actual intervention data (target: n=34) |
| `intervention_test_results.csv` | ⏳ TO BE COLLECTED | Will contain actual intervention test data |

## Why Synthetic Data?

This data serves as:
1. **Format Template**: Shows exactly how real data should be structured
2. **Analysis Testing**: Allows R scripts to be tested before real data collection
3. **Sample Size Illustration**: Demonstrates target n=32 baseline, n=34 intervention
4. **Replication Guide**: Shows what variables to record during actual study

## Synthetic Data Characteristics

### baseline_build_times.csv
- **n = 32** (target sample size from power analysis)
- **Mean = 1069.25 seconds** (17.82 minutes) - realistic for Python projects with dependencies
- **SD = 47.42 seconds** - low variance typical of automated builds
- **Distribution**: Approximately normal (as expected for build times)
- **Based on**: Literature values from Hilton et al. (2016) - "Python projects average 8-18 min"

### baseline_test_results.csv
- **n = 192 tests** (32 builds × 6 platform combos: Ubuntu 3.9/3.10/3.11/3.12, Windows 3.11, macOS 3.11)
- **Ubuntu success rate**: 0% (realistic - missing system dependencies)
- **Windows success rate**: 0% (realistic - NumPy compilation issues)
- **macOS success rate**: 87.5% (realistic - works out-of-box but occasional network failures)
- **Based on**: Our actual experience troubleshooting cross-platform builds

## How to Replace with Real Data

### Step 1: Collect Baseline Data
```bash
# 1. Create baseline measurement branch
git checkout -b baseline-measurement
git revert <intervention-commit>  # Revert to monolithic requirements.txt

# 2. Trigger 32 builds (2 per day for 16 days)
for i in {1..32}; do
  git commit --allow-empty -m "Baseline measurement $i"
  git push
  sleep 3600  # Wait 1 hour between builds
done

# 3. Extract data
gh run list --workflow="Python CI/CD" --limit=32 --json databaseId,conclusion,createdAt,updatedAt,headBranch \
  --jq '.[] | [.databaseId, .createdAt, .updatedAt, (((.updatedAt | fromdateiso8601) - (.createdAt | fromdateiso8601))), .headBranch] | @csv' \
  > baseline_build_times_raw.csv

# 4. Format as per baseline_build_times.csv schema
python format_baseline_data.py baseline_build_times_raw.csv > baseline_build_times.csv
```

### Step 2: Collect Intervention Data
```bash
# 1. Switch to intervention branch
git checkout main  # Or your optimized branch

# 2. Trigger 34 builds
for i in {1..34}; do
  git commit --allow-empty -m "Intervention measurement $i"
  git push
  sleep 3600
done

# 3. Extract and format data
gh run list --workflow="Python CI/CD" --limit=34 --json databaseId,conclusion,createdAt,updatedAt,headBranch \
  --jq '.[] | [.databaseId, .createdAt, .updatedAt, (((.updatedAt | fromdateiso8601) - (.createdAt | fromdateiso8601))), .headBranch] | @csv' \
  > intervention_build_times_raw.csv

python format_intervention_data.py intervention_build_times_raw.csv > intervention_build_times.csv
```

### Step 3: Run Analysis
```bash
cd analysis/scripts
Rscript run_all_analyses.R

# Results will be in analysis/results/
```

## Real Data Available Now

We do have **6 actual intervention runs** from GitHub Actions:

| Run ID | Duration (sec) | Duration (min) | Status | Date |
|--------|----------------|----------------|---------|------|
| 19120152609 | 735 | 12.25 | success | 2025-11-06 |
| 19118894723 | 753 | 12.55 | success | 2025-11-05 |
| 19118893631 | 741 | 12.35 | success | 2025-11-05 |
| 19116886443 | 1919 | 31.98 | failure | 2025-11-05 |
| 19116885933 | 1647 | 27.45 | failure | 2025-11-05 |

**Observation**: Successful builds are consistently ~12-13 minutes. Failed builds (likely from earlier commits with issues) took longer.

## Validation

Once real data is collected, validate it against these criteria:

**Baseline (expected)**:
- [ ] n ≥ 30 builds (adequate for t-test)
- [ ] Mean build time > 10 minutes (justifies optimization)
- [ ] SD < 20% of mean (reasonable consistency)
- [ ] Distribution approximately normal (Shapiro-Wilk p > 0.05)

**Intervention (expected)**:
- [ ] n ≥ 30 builds
- [ ] Mean significantly lower than baseline (t-test p < 0.017)
- [ ] Effect size large (Cohen's d > 0.8)
- [ ] Success rates improved on Ubuntu/Windows

## Questions?

See `REPLICATION_PACKAGE.md` for complete data collection protocol.

---

**Last Updated**: November 6, 2025
**Status**: Awaiting real data collection
