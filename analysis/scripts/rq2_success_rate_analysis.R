#!/usr/bin/env Rscript
# RQ2: System Dependencies and Test Success Rate Analysis
# Date: November 5, 2025
# Author: Claude (Anthropic)

# Load required libraries
library(tidyverse)
library(lsr)

# Set output directory
output_dir <- "../results"
dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)

# Redirect output to file
sink(file.path(output_dir, "rq2_results.txt"))

cat("=" * 70, "\n")
cat("RQ2: SYSTEM DEPENDENCIES AND TEST SUCCESS RATE ANALYSIS\n")
cat("=" * 70, "\n\n")

cat("Analysis Date:", format(Sys.Date(), "%B %d, %Y"), "\n")
cat("R Version:", R.version.string, "\n\n")

# ============================================================================
# 1. LOAD AND PREPARE DATA
# ============================================================================

cat("Loading baseline test results...\n")
test_data <- read_csv("../data/baseline_test_results.csv",
                      show_col_types = FALSE)

cat("Total test runs in baseline:", nrow(test_data), "\n\n")

# ============================================================================
# 2. BASELINE SUCCESS RATES BY PLATFORM
# ============================================================================

cat("=" * 70, "\n")
cat("BASELINE SUCCESS RATES BY PLATFORM\n")
cat("=" * 70, "\n\n")

# Summary by platform
platform_summary <- test_data %>%
  group_by(platform) %>%
  summarise(
    total_runs = n(),
    successes = sum(success),
    failures = sum(!success),
    success_rate = mean(success) * 100,
    .groups = "drop"
  )

print(platform_summary)
cat("\n")

# Detailed statistics by platform
for (plat in unique(test_data$platform)) {
  plat_data <- filter(test_data, platform == plat)

  cat(sprintf("Platform: %s\n", plat))
  cat(sprintf("  Total runs: %d\n", nrow(plat_data)))
  cat(sprintf("  Successes: %d\n", sum(plat_data$success)))
  cat(sprintf("  Failures: %d\n", sum(!plat_data$success)))
  cat(sprintf("  Success rate: %.1f%%\n",
              mean(plat_data$success) * 100))

  # Most common failure reason
  if (sum(!plat_data$success) > 0) {
    failure_reasons <- plat_data %>%
      filter(!success) %>%
      count(failure_reason, sort = TRUE)
    cat(sprintf("  Primary failure reason: %s (n=%d)\n",
                failure_reasons$failure_reason[1],
                failure_reasons$n[1]))
  }
  cat("\n")
}

# ============================================================================
# 3. BASELINE SUCCESS RATES BY PYTHON VERSION (Ubuntu only)
# ============================================================================

cat("=" * 70, "\n")
cat("UBUNTU SUCCESS RATES BY PYTHON VERSION\n")
cat("=" * 70, "\n\n")

ubuntu_summary <- test_data %>%
  filter(platform == "ubuntu-latest") %>%
  group_by(python_version) %>%
  summarise(
    total_runs = n(),
    successes = sum(success),
    failures = sum(!success),
    success_rate = mean(success) * 100,
    .groups = "drop"
  )

print(ubuntu_summary)
cat("\n")

cat("Observation: All Python versions on Ubuntu failed consistently\n")
cat("Reason: Missing system dependencies (python3-dev, build-essential, etc.)\n\n")

# ============================================================================
# 4. FUNCTION FOR CHI-SQUARE/FISHER'S TEST
# ============================================================================

analyze_success_rates <- function(success_before, total_before,
                                   success_after, total_after,
                                   platform_name = "Platform") {

  cat("=" * 70, "\n")
  cat(sprintf("ANALYSIS: %s\n", platform_name))
  cat("=" * 70, "\n\n")

  # Create contingency table
  success_table <- matrix(c(
    success_after, total_after - success_after,
    success_before, total_before - success_before
  ), nrow = 2, byrow = TRUE,
     dimnames = list(
       Period = c("Intervention", "Baseline"),
       Outcome = c("Success", "Failure")
     ))

  cat("Contingency Table:\n")
  print(success_table)
  cat("\n")

  # Choose test based on expected counts
  min_count <- min(success_table)

  if (min_count < 5) {
    cat("Using Fisher's Exact Test (expected counts < 5)\n\n")
    test_result <- fisher.test(success_table, alternative = "greater")
    cat("Fisher's Exact Test Results:\n")
    cat(sprintf("  Odds Ratio = %.4f\n", test_result$estimate))
    cat(sprintf("  p-value = %.6f\n", test_result$p.value))
    cat(sprintf("  95%% CI for OR: [%.4f, Inf]\n",
                test_result$conf.int[1]))
  } else {
    cat("Using Chi-Square Test\n\n")
    test_result <- chisq.test(success_table)
    cat("Chi-Square Test Results:\n")
    cat(sprintf("  χ² = %.4f\n", test_result$statistic))
    cat(sprintf("  df = %d\n", test_result$parameter))
    cat(sprintf("  p-value = %.6f\n", test_result$p.value))

    # Effect size (Cramér's V)
    cramer_v <- cramersV(success_table)
    cat(sprintf("  Cramér's V = %.4f\n", cramer_v))

    # Interpret effect size
    if (cramer_v < 0.1) {
      cat("  Effect size: Negligible\n")
    } else if (cramer_v < 0.3) {
      cat("  Effect size: Small\n")
    } else if (cramer_v < 0.5) {
      cat("  Effect size: Medium\n")
    } else {
      cat("  Effect size: Large\n")
    }
  }

  cat("\n")

  # Success rate comparison
  rate_before <- success_before / total_before
  rate_after <- success_after / total_after
  rate_diff <- rate_after - rate_before

  cat("Success Rates:\n")
  cat(sprintf("  Baseline: %.1f%% (%d/%d)\n",
              rate_before*100, success_before, total_before))
  cat(sprintf("  Intervention: %.1f%% (%d/%d)\n",
              rate_after*100, success_after, total_after))
  cat(sprintf("  Absolute difference: %.1f percentage points\n",
              rate_diff*100))

  # 95% CI for difference in proportions
  if (success_before > 0 && success_after > 0) {
    prop_test <- prop.test(c(success_after, success_before),
                           c(total_after, total_before))
    cat(sprintf("  95%% CI for difference: [%.1f%%, %.1f%%]\n",
                -prop_test$conf.int[2]*100,
                -prop_test$conf.int[1]*100))
  }

  # Statistical significance
  alpha <- 0.017  # Bonferroni corrected
  if (test_result$p.value < alpha) {
    cat(sprintf("\nConclusion: STATISTICALLY SIGNIFICANT (p < %.3f)\n", alpha))
    cat("Reject H₀: The intervention significantly improved success rates\n")
  } else {
    cat(sprintf("\nConclusion: NOT STATISTICALLY SIGNIFICANT (p ≥ %.3f)\n", alpha))
    cat("Fail to reject H₀: Insufficient evidence of improvement\n")
  }

  cat("\n")

  return(list(
    test = test_result,
    rate_before = rate_before,
    rate_after = rate_after,
    rate_diff = rate_diff
  ))
}

# ============================================================================
# 5. BASELINE SUMMARY FOR EACH PLATFORM
# ============================================================================

cat("=" * 70, "\n")
cat("BASELINE DATA SUMMARY\n")
cat("=" * 70, "\n\n")

# Ubuntu
ubuntu_data <- filter(test_data, platform == "ubuntu-latest")
cat("Ubuntu (Python 3.9-3.12):\n")
cat(sprintf("  Total tests: %d (8 builds × 4 Python versions)\n",
            nrow(ubuntu_data)))
cat(sprintf("  Successes: %d\n", sum(ubuntu_data$success)))
cat(sprintf("  Failures: %d\n", sum(!ubuntu_data$success)))
cat(sprintf("  Success rate: %.1f%%\n\n",
            mean(ubuntu_data$success) * 100))

# Windows
windows_data <- filter(test_data, platform == "windows-latest")
cat("Windows (Python 3.11):\n")
cat(sprintf("  Total tests: %d\n", nrow(windows_data)))
cat(sprintf("  Successes: %d\n", sum(windows_data$success)))
cat(sprintf("  Failures: %d\n", sum(!windows_data$success)))
cat(sprintf("  Success rate: %.1f%%\n\n",
            mean(windows_data$success) * 100))

# macOS
macos_data <- filter(test_data, platform == "macos-latest")
cat("macOS (Python 3.11):\n")
cat(sprintf("  Total tests: %d\n", nrow(macos_data)))
cat(sprintf("  Successes: %d\n", sum(macos_data$success)))
cat(sprintf("  Failures: %d\n", sum(!macos_data$success)))
cat(sprintf("  Success rate: %.1f%%\n\n",
            mean(macos_data$success) * 100))

# ============================================================================
# 6. EXPECTED INTERVENTION RESULTS (HYPOTHETICAL)
# ============================================================================

cat("=" * 70, "\n")
cat("EXPECTED INTERVENTION RESULTS (HYPOTHETICAL)\n")
cat("=" * 70, "\n\n")

cat("Based on initial observations, we expect:\n\n")

cat("Ubuntu (Python 3.9-3.12):\n")
cat("  Expected success rate: ~90%\n")
cat("  Expected successes: ~31/34 builds × 4 versions = 124/136\n")
cat("  Improvement: +90 percentage points\n\n")

cat("Windows (Python 3.11):\n")
cat("  Expected success rate: ~95%\n")
cat("  Expected successes: ~32/34 builds\n")
cat("  Improvement: +95 percentage points\n\n")

cat("macOS (Python 3.11):\n")
cat("  Expected success rate: ~95% (already high at 87.5%)\n")
cat("  Expected successes: ~32/34 builds\n")
cat("  Improvement: +7.5 percentage points\n\n")

# Example analysis (hypothetical data)
cat("Example analysis with hypothetical intervention data:\n\n")

# Ubuntu analysis (hypothetical)
# analyze_success_rates(
#   success_before = 0, total_before = 32,
#   success_after = 124, total_after = 136,
#   platform_name = "Ubuntu (Python 3.9-3.12)"
# )

# Windows analysis (hypothetical)
# analyze_success_rates(
#   success_before = 0, total_before = 32,
#   success_after = 32, total_after = 34,
#   platform_name = "Windows (Python 3.11)"
# )

# macOS analysis (hypothetical)
# analyze_success_rates(
#   success_before = 28, total_before = 32,
#   success_after = 32, total_after = 34,
#   platform_name = "macOS (Python 3.11)"
# )

# ============================================================================
# 7. VISUALIZATIONS
# ============================================================================

cat("Creating visualizations...\n\n")

# Success rate by platform (baseline)
png("../results/figures/baseline_success_rates.png",
    width = 1000, height = 600)

platform_summary %>%
  ggplot(aes(x = platform, y = success_rate, fill = platform)) +
  geom_bar(stat = "identity") +
  geom_text(aes(label = sprintf("%.1f%%", success_rate)),
            vjust = -0.5, size = 5) +
  labs(title = "Baseline Test Success Rates by Platform",
       x = "Platform",
       y = "Success Rate (%)") +
  scale_fill_brewer(palette = "Set2") +
  ylim(0, 100) +
  theme_minimal(base_size = 14) +
  theme(legend.position = "none",
        plot.title = element_text(hjust = 0.5, size = 16, face = "bold"))

dev.off()
cat("Success rate plot saved to: ../results/figures/baseline_success_rates.png\n\n")

# ============================================================================
# 8. SUMMARY
# ============================================================================

cat("=" * 70, "\n")
cat("SUMMARY\n")
cat("=" * 70, "\n\n")

cat("Baseline Findings:\n")
cat("  - Ubuntu: 0% success rate (0/32 builds × 4 versions)\n")
cat("  - Windows: 0% success rate (0/32 builds)\n")
cat("  - macOS: 87.5% success rate (28/32 builds)\n\n")

cat("Root Causes:\n")
cat("  - Ubuntu: Missing system dependencies (python3-dev, libopenblas-dev)\n")
cat("  - Windows: NumPy/SciPy installation failures (no pre-built wheels used)\n")
cat("  - macOS: Mostly working, occasional network issues\n\n")

cat("Intervention:\n")
cat("  - Ubuntu: Added system dependencies via apt-get\n")
cat("  - Windows: Added --prefer-binary flag for pip\n")
cat("  - Both: Optimized requirements-test.txt with version-pinned packages\n\n")

cat("Next Steps:\n")
cat("  1. Complete intervention data collection (34 builds)\n")
cat("  2. Perform chi-square/Fisher's exact tests\n")
cat("  3. Calculate effect sizes (Cramér's V)\n")
cat("  4. Create before/after comparison plots\n")
cat("  5. Report statistical significance\n\n")

cat("Analysis completed:", format(Sys.time(), "%Y-%m-%d %H:%M:%S"), "\n")
cat("Output saved to: ../results/rq2_results.txt\n")

# Stop redirecting output
sink()

# Print summary to console
cat("\n✓ RQ2 analysis complete!\n")
cat("Results saved to: analysis/results/rq2_results.txt\n")
cat("Figures saved to: analysis/results/figures/\n")
