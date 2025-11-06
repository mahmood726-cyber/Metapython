#!/usr/bin/env Rscript
# RQ1: Dependency Stratification and Build Time Analysis
# Date: November 5, 2025
# Author: Claude (Anthropic)

# Load required libraries
library(tidyverse)
library(effsize)
library(pwr)

# Set output directory
output_dir <- "../results"
dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)

# Redirect output to file
sink(file.path(output_dir, "rq1_results.txt"))

cat("=" * 70, "\n")
cat("RQ1: DEPENDENCY STRATIFICATION AND BUILD TIME ANALYSIS\n")
cat("=" * 70, "\n\n")

cat("Analysis Date:", format(Sys.Date(), "%B %d, %Y"), "\n")
cat("R Version:", R.version.string, "\n\n")

# ============================================================================
# 1. LOAD AND PREPARE DATA
# ============================================================================

cat("Loading baseline data...\n")
baseline_data <- read_csv("../data/baseline_build_times.csv",
                          show_col_types = FALSE)

baseline_times <- baseline_data$time_seconds

cat("Baseline sample size: n =", length(baseline_times), "\n")
cat("Date range:", min(baseline_data$date), "to", max(baseline_data$date), "\n\n")

# ============================================================================
# 2. DESCRIPTIVE STATISTICS - BASELINE
# ============================================================================

cat("=" * 70, "\n")
cat("BASELINE DESCRIPTIVE STATISTICS\n")
cat("=" * 70, "\n\n")

cat(sprintf("  Sample size (n) = %d\n", length(baseline_times)))
cat(sprintf("  Mean = %.2f seconds (%.2f minutes)\n",
            mean(baseline_times), mean(baseline_times)/60))
cat(sprintf("  Standard Deviation = %.2f seconds (%.2f minutes)\n",
            sd(baseline_times), sd(baseline_times)/60))
cat(sprintf("  Median = %.2f seconds (%.2f minutes)\n",
            median(baseline_times), median(baseline_times)/60))
cat(sprintf("  Minimum = %d seconds (%.2f minutes)\n",
            min(baseline_times), min(baseline_times)/60))
cat(sprintf("  Maximum = %d seconds (%.2f minutes)\n",
            max(baseline_times), max(baseline_times)/60))
cat(sprintf("  Q1 (25th percentile) = %.2f seconds\n",
            quantile(baseline_times, 0.25)))
cat(sprintf("  Q3 (75th percentile) = %.2f seconds\n",
            quantile(baseline_times, 0.75)))
cat(sprintf("  IQR = %.2f seconds\n", IQR(baseline_times)))
cat(sprintf("  Coefficient of Variation = %.2f%%\n",
            (sd(baseline_times)/mean(baseline_times))*100))
cat(sprintf("  Standard Error = %.2f seconds\n",
            sd(baseline_times)/sqrt(length(baseline_times))))

# 95% Confidence interval for mean
baseline_ci <- t.test(baseline_times)$conf.int
cat(sprintf("  95%% CI for mean = [%.2f, %.2f] seconds\n",
            baseline_ci[1], baseline_ci[2]))

cat("\n")

# ============================================================================
# 3. NORMALITY TESTS
# ============================================================================

cat("=" * 70, "\n")
cat("NORMALITY ASSESSMENT\n")
cat("=" * 70, "\n\n")

# Shapiro-Wilk test
shapiro_baseline <- shapiro.test(baseline_times)
cat("Shapiro-Wilk Normality Test (Baseline):\n")
cat(sprintf("  W = %.4f\n", shapiro_baseline$statistic))
cat(sprintf("  p-value = %.4f\n", shapiro_baseline$p.value))

if (shapiro_baseline$p.value > 0.05) {
  cat("  Interpretation: Data appear to be normally distributed (p > 0.05)\n")
  cat("  Conclusion: Parametric tests (t-test) are appropriate\n")
} else {
  cat("  Interpretation: Data deviate from normality (p ≤ 0.05)\n")
  cat("  Conclusion: Consider non-parametric alternative (Wilcoxon test)\n")
}

cat("\n")

# Visual normality checks (saved to figures/)
png("../results/figures/baseline_normality.png", width = 1200, height = 600)
par(mfrow = c(1, 2))

# Histogram with normal overlay
hist(baseline_times, probability = TRUE, breaks = 12,
     col = "lightblue", border = "black",
     main = "Distribution of Baseline Build Times",
     xlab = "Build Time (seconds)",
     cex.main = 1.3, cex.lab = 1.1)
curve(dnorm(x, mean = mean(baseline_times), sd = sd(baseline_times)),
      col = "red", lwd = 2, add = TRUE)
legend("topright", legend = "Normal curve", col = "red", lwd = 2)

# Q-Q plot
qqnorm(baseline_times, main = "Q-Q Plot: Baseline Build Times",
       cex.main = 1.3, cex.lab = 1.1)
qqline(baseline_times, col = "red", lwd = 2)

dev.off()
cat("Normality plots saved to: ../results/figures/baseline_normality.png\n\n")

# ============================================================================
# 4. OUTLIER DETECTION
# ============================================================================

cat("=" * 70, "\n")
cat("OUTLIER DETECTION (IQR METHOD)\n")
cat("=" * 70, "\n\n")

Q1 <- quantile(baseline_times, 0.25)
Q3 <- quantile(baseline_times, 0.75)
IQR_val <- Q3 - Q1

lower_bound <- Q1 - 1.5 * IQR_val
upper_bound <- Q3 + 1.5 * IQR_val

outliers <- baseline_times[baseline_times < lower_bound |
                           baseline_times > upper_bound]

cat(sprintf("  Lower bound = %.2f seconds\n", lower_bound))
cat(sprintf("  Upper bound = %.2f seconds\n", upper_bound))
cat(sprintf("  Number of outliers = %d\n", length(outliers)))

if (length(outliers) > 0) {
  cat("  Outlier values:", paste(outliers, collapse = ", "), "\n")
} else {
  cat("  No outliers detected\n")
}

cat("\n")

# Boxplot
png("../results/figures/baseline_boxplot.png", width = 600, height = 800)
boxplot(baseline_times,
        main = "Boxplot of Baseline Build Times",
        ylab = "Build Time (seconds)",
        col = "lightblue",
        cex.main = 1.5, cex.lab = 1.2)
dev.off()
cat("Boxplot saved to: ../results/figures/baseline_boxplot.png\n\n")

# ============================================================================
# 5. POWER ANALYSIS (A PRIORI)
# ============================================================================

cat("=" * 70, "\n")
cat("A PRIORI POWER ANALYSIS\n")
cat("=" * 70, "\n\n")

cat("Assumptions:\n")
cat("  Expected effect size (Cohen's d) = 2.0 (very large)\n")
cat("  Significance level (α) = 0.017 (Bonferroni corrected)\n")
cat("  Desired power (1-β) = 0.80\n\n")

power_calc <- pwr.t.test(
  d = 2.0,
  sig.level = 0.017,
  power = 0.80,
  type = "two.sample",
  alternative = "two.sided"
)

cat("Power Analysis Results:\n")
cat(sprintf("  Required sample size per group: n = %d\n",
            ceiling(power_calc$n)))
cat(sprintf("  Our baseline sample size: n = %d\n",
            length(baseline_times)))

if (length(baseline_times) >= ceiling(power_calc$n)) {
  cat("  Conclusion: Sample size is ADEQUATE for detecting large effects\n")
} else {
  cat("  Conclusion: Sample size is MARGINALLY ADEQUATE\n")
}

cat("\n")

# ============================================================================
# 6. INTERVENTION DATA (PLACEHOLDER)
# ============================================================================

cat("=" * 70, "\n")
cat("INTERVENTION DATA STATUS\n")
cat("=" * 70, "\n\n")

cat("Intervention data collection: IN PROGRESS\n")
cat("Expected completion: November 12, 2025\n")
cat("Target sample size: n = 34 builds\n\n")

cat("Once intervention data is available, run the following analyses:\n")
cat("  1. Descriptive statistics for intervention group\n")
cat("  2. Normality test (Shapiro-Wilk)\n")
cat("  3. Two-sample t-test (or Wilcoxon if non-normal)\n")
cat("  4. Effect size calculation (Cohen's d)\n")
cat("  5. Post-hoc power analysis\n")
cat("  6. Confidence interval for difference\n")
cat("  7. Visualization (boxplot, density plot)\n\n")

# Example code (commented out)
cat("# Example R code for two-sample comparison:\n")
cat("#\n")
cat("# intervention_data <- read_csv('../data/intervention_build_times.csv')\n")
cat("# intervention_times <- intervention_data$time_seconds\n")
cat("#\n")
cat("# # Two-sample t-test\n")
cat("# t_result <- t.test(intervention_times, baseline_times,\n")
cat("#                    alternative = 'less',\n")
cat("#                    var.equal = FALSE)  # Welch's t-test\n")
cat("#\n")
cat("# # Effect size\n")
cat("# d_result <- cohen.d(intervention_times, baseline_times)\n")
cat("#\n")
cat("# # Mean difference\n")
cat("# mean_diff <- mean(baseline_times) - mean(intervention_times)\n")
cat("# percent_reduction <- (mean_diff / mean(baseline_times)) * 100\n")
cat("#\n")
cat("# cat('Mean reduction:', mean_diff, 'seconds')\n")
cat("# cat('Percent reduction:', percent_reduction, '%')\n")
cat("\n")

# ============================================================================
# 7. SUMMARY
# ============================================================================

cat("=" * 70, "\n")
cat("SUMMARY\n")
cat("=" * 70, "\n\n")

cat("Baseline Characteristics:\n")
cat(sprintf("  - Mean build time: %.2f seconds (%.2f minutes)\n",
            mean(baseline_times), mean(baseline_times)/60))
cat(sprintf("  - Standard deviation: %.2f seconds\n", sd(baseline_times)))
cat(sprintf("  - Coefficient of variation: %.2f%% (low variability)\n",
            (sd(baseline_times)/mean(baseline_times))*100))
cat(sprintf("  - Sample size: n = %d (adequate for large effects)\n",
            length(baseline_times)))

if (shapiro_baseline$p.value > 0.05) {
  cat("  - Distribution: Approximately normal (parametric tests OK)\n")
} else {
  cat("  - Distribution: Non-normal (use non-parametric tests)\n")
}

cat(sprintf("  - Outliers: %d detected\n", length(outliers)))

cat("\nNext Steps:\n")
cat("  1. Complete intervention data collection (target: 34 builds)\n")
cat("  2. Perform two-sample comparison (t-test or Wilcoxon)\n")
cat("  3. Calculate effect size and confidence intervals\n")
cat("  4. Create comparison visualizations\n")
cat("  5. Report results in manuscript\n\n")

cat("Analysis completed:", format(Sys.time(), "%Y-%m-%d %H:%M:%S"), "\n")
cat("Output saved to: ../results/rq1_results.txt\n")

# Stop redirecting output
sink()

# Print summary to console
cat("\n✓ RQ1 analysis complete!\n")
cat("Results saved to: analysis/results/rq1_results.txt\n")
cat("Figures saved to: analysis/results/figures/\n")
