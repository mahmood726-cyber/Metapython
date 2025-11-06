#!/usr/bin/env Rscript
# Master script to run all statistical analyses
# MetaPython CI/CD Optimization Study
# Date: November 5, 2025
# Author: Claude (Anthropic)

cat("\n")
cat("=" * 80, "\n")
cat("METAPYTHON CI/CD OPTIMIZATION STUDY - COMPLETE ANALYSIS\n")
cat("=" * 80, "\n\n")

cat("Study: Dependency Stratification and Build Time Reduction\n")
cat("Date:", format(Sys.Date(), "%B %d, %Y"), "\n")
cat("R Version:", R.version.string, "\n\n")

# Record start time
start_time <- Sys.time()

# =============================================================================
# CHECK ENVIRONMENT
# =============================================================================

cat("Checking environment...\n")

# Check required packages
required_packages <- c("tidyverse", "effsize", "pwr", "lsr")
missing_packages <- required_packages[!required_packages %in% installed.packages()[,"Package"]]

if (length(missing_packages) > 0) {
  cat("ERROR: Missing required R packages:\n")
  cat(paste(" -", missing_packages, collapse="\n"), "\n\n")
  cat("Please install with:\n")
  cat(sprintf("install.packages(c(%s))\n",
              paste0("'", missing_packages, "'", collapse=", ")))
  quit(status=1)
}

# Load packages
suppressPackageStartupMessages({
  library(tidyverse)
  library(effsize)
  library(pwr)
  library(lsr)
})

cat("✓ All required packages loaded\n\n")

# Check data files
data_dir <- "../data"
required_files <- c(
  "baseline_build_times.csv",
  "baseline_test_results.csv"
)

missing_files <- c()
for (file in required_files) {
  filepath <- file.path(data_dir, file)
  if (!file.exists(filepath)) {
    missing_files <- c(missing_files, file)
  }
}

if (length(missing_files) > 0) {
  cat("ERROR: Missing required data files:\n")
  cat(paste(" -", missing_files, collapse="\n"), "\n\n")
  cat("Expected location: analysis/data/\n")
  quit(status=1)
}

cat("✓ All required data files found\n\n")

# =============================================================================
# RQ1: BUILD TIME ANALYSIS
# =============================================================================

cat("\n")
cat("=" * 80, "\n")
cat("RUNNING RQ1: BUILD TIME ANALYSIS\n")
cat("=" * 80, "\n\n")

tryCatch({
  source("rq1_build_time_analysis.R")
  cat("\n✓ RQ1 analysis completed successfully\n")
  rq1_success <- TRUE
}, error = function(e) {
  cat("\n✗ RQ1 analysis FAILED\n")
  cat("Error:", conditionMessage(e), "\n")
  rq1_success <- FALSE
})

# =============================================================================
# RQ2: SUCCESS RATE ANALYSIS
# =============================================================================

cat("\n")
cat("=" * 80, "\n")
cat("RUNNING RQ2: SUCCESS RATE ANALYSIS\n")
cat("=" * 80, "\n\n")

tryCatch({
  source("rq2_success_rate_analysis.R")
  cat("\n✓ RQ2 analysis completed successfully\n")
  rq2_success <- TRUE
}, error = function(e) {
  cat("\n✗ RQ2 analysis FAILED\n")
  cat("Error:", conditionMessage(e), "\n")
  rq2_success <- FALSE
})

# =============================================================================
# RQ3: SECURITY ANALYSIS
# =============================================================================

cat("\n")
cat("=" * 80, "\n")
cat("RUNNING RQ3: SECURITY ANALYSIS\n")
cat("=" * 80, "\n\n")

tryCatch({
  source("rq3_security_analysis.R")
  cat("\n✓ RQ3 analysis completed successfully\n")
  rq3_success <- TRUE
}, error = function(e) {
  cat("\n✗ RQ3 analysis FAILED\n")
  cat("Error:", conditionMessage(e), "\n")
  rq3_success <- FALSE
})

# =============================================================================
# SUMMARY
# =============================================================================

end_time <- Sys.time()
elapsed_time <- difftime(end_time, start_time, units = "secs")

cat("\n\n")
cat("=" * 80, "\n")
cat("ANALYSIS SUMMARY\n")
cat("=" * 80, "\n\n")

cat("Analysis Status:\n")
cat(sprintf("  RQ1 (Build Time):    %s\n",
            ifelse(exists("rq1_success") && rq1_success, "✓ PASS", "✗ FAIL")))
cat(sprintf("  RQ2 (Success Rate):  %s\n",
            ifelse(exists("rq2_success") && rq2_success, "✓ PASS", "✗ FAIL")))
cat(sprintf("  RQ3 (Security):      %s\n",
            ifelse(exists("rq3_success") && rq3_success, "✓ PASS", "✗ FAIL")))

cat("\n")

# Count successes
successes <- sum(c(
  exists("rq1_success") && rq1_success,
  exists("rq2_success") && rq2_success,
  exists("rq3_success") && rq3_success
))

if (successes == 3) {
  cat("Overall Result: ✓ ALL ANALYSES COMPLETED SUCCESSFULLY\n")
} else {
  cat(sprintf("Overall Result: ✗ %d/3 ANALYSES COMPLETED\n", successes))
}

cat("\n")
cat(sprintf("Total Time: %.1f seconds\n", as.numeric(elapsed_time)))

cat("\nOutput Files:\n")
cat("  Results:\n")
cat("    - analysis/results/rq1_results.txt\n")
cat("    - analysis/results/rq2_results.txt\n")
cat("    - analysis/results/rq3_results.txt\n")
cat("  Figures:\n")
cat("    - analysis/results/figures/*.png (6 figures)\n")

cat("\nNext Steps:\n")
if (successes == 3) {
  cat("  1. Review results in analysis/results/*.txt\n")
  cat("  2. Examine figures in analysis/results/figures/\n")
  cat("  3. Compare with expected results in REPLICATION_PACKAGE.md\n")
  cat("  4. If replicating: Verify statistics match published values\n")
} else {
  cat("  1. Check error messages above\n")
  cat("  2. Verify all data files exist in analysis/data/\n")
  cat("  3. Verify R packages are installed correctly\n")
  cat("  4. See REPLICATION_PACKAGE.md for troubleshooting\n")
}

cat("\n")
cat("For questions or issues:\n")
cat("  https://github.com/mahmood726-cyber/Metapython/issues\n")
cat("\n")

cat("=" * 80, "\n")
cat("ANALYSIS COMPLETE\n")
cat("=" * 80, "\n\n")

# Exit with appropriate status code
if (successes == 3) {
  quit(status=0)  # Success
} else {
  quit(status=1)  # Failure
}
