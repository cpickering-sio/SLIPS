1# =============================================================================
# Biofouling Mass Analysis: SLIPS Local Summer 2026 Deployment
# Flange Cap Mass Before & After (Section 3.5.3 / 3.7.2)
# Author: Corinne Pickering
# Description: Measured W1 (pre-deployment) and W3 (post-deployment) dry mass
#              for 4 SLIPS-coated glass, 4 uncoated glass control,0
#              and 4 factory acrylic flange caps (3 treatments x 4 replicates).
#              Units: grams. Alpha = 0.05.
# Deployment: 21 Aug 2026 - 19 Sep 2026 (~30 days, ~4 weeks)
# Note: Scale measurement error ~0.06-0.10 g (assessed with 100 g calibration weight).
# =============================================================================

library(tidyverse)
library(ggplot2)

setwd("/Users/corinnepickering/Desktop/Thode_lab/SLIPS/SLIPS_Off_Pier_202608/dry_mass")
dir.create("outputs", showWarnings = FALSE)  # ensure outputs/ exists INSIDE the project dir
set.seed(42)  # reproducibility

# =============================================================================
# 1. MEASURED DATA  (read from "Dry_Mass - Sheet1.csv" -- single source of truth)
# =============================================================================
# Camera -> treatment (3 treatments x 4 replicates = 12 units):
#   Acrylic (uncoated, factory std): cams 1, 4, 7, 10
#   Glass   (uncoated control):      cams 2, 5, 8, 11
#   SLIPS   (coated glass):          cams 3, 6, 9, 12
# Measurement protocol (from data-sheet notes):
#   Before mass: pre-deployment dry mass after cleaning w/ 70% isopropanol + Kimwipe.
#   After mass:  post-retrieval dry mass, air-dried 2 d then desiccant-dried 8 d (sealed).
# Scale measurement error: ~0.06-0.10 g (assessed with 100 g calibration weight).

raw <- readr::read_csv("Dry_Mass - Sheet1.csv", show_col_types = FALSE) |>
  select(camera  = `Camera Number`,
         trt_raw = `Treatment`,
         W1_g    = `Before Mass (g)`,   # W1: pre-deployment dry mass (g)
         W3_g    = `After Mass (g)`) |> # W3: post-deployment dry mass (g)
  filter(!is.na(camera))

flange_data <- raw |>
  mutate(
    treatment = factor(
      dplyr::recode(trt_raw,
                    "Glass"   = "Glass_Control",
                    "SLIPS"   = "Glass_SLIPS",
                    "Acrylic" = "Acrylic"),
      levels = c("Glass_Control", "Glass_SLIPS", "Acrylic")   # x-axis / colour order
    ),
    substrate = if_else(trt_raw == "Acrylic", "Acrylic", "Glass"),
    sample_id = paste0(dplyr::recode(trt_raw, "Glass" = "Control",
                                     "SLIPS" = "SLIPS", "Acrylic" = "Acrylic"),
                       "_Cam", camera)
  ) |>
  arrange(treatment, camera) |>
  select(sample_id, treatment, substrate, camera, W1_g, W3_g)

# =============================================================================
# 2. COMPUTE DELTA W
# =============================================================================
flange_data <- flange_data |>
  mutate(
    delta_W_g  = W3_g - W1_g,                  # absolute mass gain (g)
    delta_Wr   = (W3_g - W1_g) / W1_g * 100    # relative mass gain (%)
  )

print(flange_data |> select(sample_id, treatment, W1_g, W3_g, delta_W_g, delta_Wr))

# =============================================================================
# 3. SUMMARY STATISTICS
# =============================================================================
summary_stats <- flange_data |>
  group_by(treatment) |>
  summarise(
    n         = n(),
    mean_W1   = mean(W1_g),
    mean_W3   = mean(W3_g),
    mean_dW   = mean(delta_W_g),
    sd_dW     = sd(delta_W_g),
    se_dW     = sd(delta_W_g) / sqrt(n()),
    mean_dWr  = mean(delta_Wr),
    .groups   = "drop"
  )

print(summary_stats)

# =============================================================================
# 4. NORMALITY CHECK (Shapiro-Wilk) — per Section 3.7.2 decision procedure
# =============================================================================
# NOTE: With n=4, Shapiro-Wilk still has low power. Treat results as indicative.
cat("\n--- Shapiro-Wilk Normality Tests on delta_W ---\n")
by(flange_data$delta_W_g, flange_data$treatment, shapiro.test)

# =============================================================================
# 5. STATISTICAL TESTS (Glass Control vs. Glass SLIPS)  — PRIMARY, per §3.7.2
# =============================================================================
ctrl  <- flange_data |> filter(treatment == "Glass_Control") |> pull(delta_W_g)
slips <- flange_data |> filter(treatment == "Glass_SLIPS")   |> pull(delta_W_g)
acryl <- flange_data |> filter(treatment == "Acrylic")       |> pull(delta_W_g)

cat("\n--- Two-sample t-test: Glass Control vs. SLIPS ---\n")
t_test_result <- t.test(ctrl, slips, var.equal = FALSE)  # Welch's t-test
print(t_test_result)

cat("\n--- Mann-Whitney U test: Glass Control vs. SLIPS ---\n")
# NOTE: at n=4 per group the smallest possible two-sided p is 0.029, so unlike
# the n=3 Maui data this nonparametric test CAN now reach significance.
mw_result <- wilcox.test(ctrl, slips, exact = FALSE)
print(mw_result)

# Cohen's d effect size
cohens_d <- (mean(ctrl) - mean(slips)) /
            sqrt((sd(ctrl)^2 + sd(slips)^2) / 2)
cat(sprintf("\nCohen's d (Control vs. SLIPS): %.3f\n", cohens_d))

# =============================================================================
# 5b. (COMPLEMENTARY) OMNIBUS TEST ACROSS ALL THREE TREATMENTS
#     The pre-registered primary test (§3.7.2) is the pairwise Control vs SLIPS
#     above. This 3-group omnibus is ADDED (nothing removed) because the design
#     has three treatments; it mirrors the primary decision rule by reporting
#     both a parametric (ANOVA + Tukey) and nonparametric (Kruskal-Wallis +
#     BH-adjusted pairwise Wilcoxon) route, with multiple-comparison control.
# =============================================================================
cat("\n--- One-way ANOVA: delta_W ~ treatment (all 3 groups) ---\n")
aov_fit <- aov(delta_W_g ~ treatment, data = flange_data)
print(summary(aov_fit))

cat("\n--- Tukey HSD (all pairwise, family-wise error controlled) ---\n")
print(TukeyHSD(aov_fit))

cat("\n--- Kruskal-Wallis: delta_W ~ treatment (nonparametric omnibus) ---\n")
print(kruskal.test(delta_W_g ~ treatment, data = flange_data))

cat("\n--- Pairwise Wilcoxon (Benjamini-Hochberg adjusted) ---\n")
print(pairwise.wilcox.test(flange_data$delta_W_g, flange_data$treatment,
                           p.adjust.method = "BH", exact = FALSE))

# =============================================================================
# 6. VISUALISATION
# =============================================================================

# 6a. PRIMARY FIGURE — Dot plot of delta_W by treatment
#     Individual points + mean crossbar + SE error bars + significance bracket.
#     With n=4, raw points are shown (no box/violin) to honestly display the data.

# Welch's t-test p-value for the Control vs SLIPS significance bracket.
# Show "p < 0.001" below threshold (never print a misleading "p = 0.000");
# otherwise show the exact value to 3 dp.
p_cs <- t.test(ctrl, slips, var.equal = FALSE)$p.value
sig_label <- if (p_cs < 0.001) "Welch's t-test, p < 0.001" else
             sprintf("Welch's t-test, p = %.3f", p_cs)

# Bracket geometry: span treatments 1 (Control) and 2 (SLIPS); place above tallest point
y_max    <- max(flange_data$delta_W_g)
y_brkt   <- y_max + 0.10   # bracket height
y_tick   <- 0.025          # small downward ticks at bracket ends

p1 <- ggplot(flange_data, aes(x = treatment, y = delta_W_g, color = treatment)) +
  geom_jitter(size = 4, width = 0.08, alpha = 0.85) +
  stat_summary(fun.data = mean_se, geom = "errorbar", width = 0.18,
               color = "black", linewidth = 0.6) +
  stat_summary(fun = mean, geom = "crossbar", width = 0.3, fatten = 2,
               color = "black", linewidth = 0.5) +
  # significance bracket (Glass_Control[x=1] vs Glass_SLIPS[x=2])
  annotate("segment", x = 1, xend = 2, y = y_brkt, yend = y_brkt, linewidth = 0.5) +
  annotate("segment", x = 1, xend = 1, y = y_brkt, yend = y_brkt - y_tick, linewidth = 0.5) +
  annotate("segment", x = 2, xend = 2, y = y_brkt, yend = y_brkt - y_tick, linewidth = 0.5) +
  annotate("text", x = 1.5, y = y_brkt + 0.03, label = sig_label, size = 3.6) +
  labs(
    title = "Dry Biomass Accrual by Treatment (~30-day deployment)",
    subtitle = "SIO Pier, La Jolla, CA (21 Aug - 19 Sep 2026); n = 4 per treatment",
    x = "Treatment",
    y = expression(Delta * "W  (g, dry mass accrual)"),
    color = "Treatment"
  ) +
  scale_color_manual(values = c(
    "Glass_Control" = "#E07B54",
    "Glass_SLIPS"   = "#5B9BD5",
    "Acrylic"       = "#70AD47"
  )) +
  theme_bw(base_size = 13) +
  theme(legend.position = "none")

print(p1)
ggsave("outputs/delta_W_dotplot.png", p1, width = 7, height = 5, dpi = 300)

# 6a-ii. RELATIVE gain (delta_Wr, %) — complements absolute view.
#        Acrylic substrate (~18 g) is far lighter than glass (~35 g), so relative
#        gain reframes acrylic as proportionally MORE fouled per gram of substrate.
p1r <- ggplot(flange_data, aes(x = treatment, y = delta_Wr, color = treatment)) +
  geom_jitter(size = 4, width = 0.08, alpha = 0.85) +
  stat_summary(fun.data = mean_se, geom = "errorbar", width = 0.18,
               color = "black", linewidth = 0.6) +
  stat_summary(fun = mean, geom = "crossbar", width = 0.3, fatten = 2,
               color = "black", linewidth = 0.5) +
  labs(
    title = "Relative Dry Biomass Accrual by Treatment (~30-day deployment)",
    subtitle = "SIO Pier, La Jolla, CA (21 Aug - 19 Sep 2026); n = 4 per treatment",
    x = "Treatment",
    y = expression(Delta * W[r] * "  (%, gain relative to pre-deployment mass)"),
    color = "Treatment"
  ) +
  scale_color_manual(values = c(
    "Glass_Control" = "#E07B54",
    "Glass_SLIPS"   = "#5B9BD5",
    "Acrylic"       = "#70AD47"
  )) +
  theme_bw(base_size = 13) +
  theme(legend.position = "none")

print(p1r)
ggsave("outputs/delta_Wr_dotplot.png", p1r, width = 7, height = 5, dpi = 300)

# 6b. Before/After mass table plot
p2 <- flange_data |>
  pivot_longer(cols = c(W1_g, W3_g), names_to = "timepoint", values_to = "mass_g") |>
  mutate(timepoint = factor(
    recode(timepoint, W1_g = "Pre-deployment (W1)", W3_g = "Post-desiccation (W3)"),
    levels = c("Pre-deployment (W1)", "Post-desiccation (W3)")  # enforce correct order
  )) |>
  ggplot(aes(x = timepoint, y = mass_g, group = sample_id, color = treatment)) +
  geom_line(alpha = 0.6) +
  geom_point(size = 3) +
  facet_wrap(~ treatment) +  # shared y-axis across all panels
  labs(
    title = "Flange Cap Mass Before & After Deployment (21 Aug–19 Sep 2026)",
    x = NULL, y = "Mass (g)",
    color = "Treatment"
  ) +
  scale_color_manual(values = c(
    "Glass_Control" = "#E07B54",
    "Glass_SLIPS"   = "#5B9BD5",
    "Acrylic"       = "#70AD47"
  )) +
  theme_bw(base_size = 12) +
  theme(legend.position = "none",
        axis.text.x = element_text(angle = 15, hjust = 1))

print(p2)
ggsave("outputs/before_after_mass.png", p2, width = 9, height = 4, dpi = 300)

# 6c. Q-Q plots for normality assessment
par(mfrow = c(1, 3))
qqnorm(ctrl,  main = "Q-Q: Glass Control delta_W"); qqline(ctrl)
qqnorm(slips, main = "Q-Q: Glass SLIPS delta_W");   qqline(slips)
qqnorm(acryl, main = "Q-Q: Acrylic delta_W");       qqline(acryl)
dev.copy(png, "outputs/qq_plots.png", width = 900, height = 400, res = 100)
dev.off()
par(mfrow = c(1, 1))
