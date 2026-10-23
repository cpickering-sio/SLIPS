# =============================================================================
# underwater_cover_stats.R
# Inner-port UNDERWATER % biofouling -- one value per camera (12 cameras, 4/trt).
# Single-endpoint, two-group procedure (mirrors the dry-mass analysis):
#   Shapiro-Wilk -> Welch's t-test (primary: Glass vs SLIPS) / Mann-Whitney U;
#   Cohen's d; omnibus one-way ANOVA + Tukey HSD, Kruskal-Wallis + BH Wilcoxon.
# Base R only (no package dependencies).
# =============================================================================
setwd("/Volumes/samsung/Corinne/SLIPS082026/coral_cams/%area_testing")
df <- read.csv("percentBiofoul_underwater.csv", check.names = FALSE)
names(df)[names(df) == "Camera #"] <- "Camera"
df$cover     <- df$Percent
df$Treatment <- factor(trimws(df$Treatment), levels = c("Glass","SLIPS","Acrylic")) # Glass = ref

sink("underwater_cover_results.txt", split = TRUE)
cat("Inner-port underwater % biofouling -- single-endpoint two-group analysis\n")
cat("Generated:", format(Sys.time()), "\n"); cat(strrep("=", 68), "\n")

cat("\n-- Descriptives (mean, SD, SE) --\n")
agg <- do.call(rbind, lapply(split(df$cover, df$Treatment), function(x)
  c(n = length(x), mean = mean(x), sd = sd(x), se = sd(x)/sqrt(length(x)))))
print(round(agg, 3))

cat("\n-- Shapiro-Wilk normality per treatment --\n")
print(by(df$cover, df$Treatment, shapiro.test))

ctrl  <- df$cover[df$Treatment == "Glass"]
slips <- df$cover[df$Treatment == "SLIPS"]
acryl <- df$cover[df$Treatment == "Acrylic"]

cat("\n-- Welch two-sample t-test: Glass vs SLIPS (PRIMARY) --\n")
print(t.test(ctrl, slips, var.equal = FALSE))
cat("\n-- Mann-Whitney U: Glass vs SLIPS --\n")
print(wilcox.test(ctrl, slips, exact = FALSE))
d <- (mean(ctrl) - mean(slips)) / sqrt((sd(ctrl)^2 + sd(slips)^2)/2)
cat(sprintf("\nCohen's d (Glass vs SLIPS): %.3f\n", d))

cat("\n-- One-way ANOVA (all three treatments) --\n")
fit <- aov(cover ~ Treatment, data = df); print(summary(fit))
cat("\n-- Tukey HSD --\n"); print(TukeyHSD(fit))
cat("\n-- Kruskal-Wallis --\n"); print(kruskal.test(cover ~ Treatment, data = df))
cat("\n-- Pairwise Wilcoxon (Benjamini-Hochberg) --\n")
print(pairwise.wilcox.test(df$cover, df$Treatment, p.adjust.method = "BH", exact = FALSE))
sink()

# dot plot (points + mean bars)
png("underwater_cover_dotplot.png", 800, 500, res = 110)
cols <- c(Glass = "#E07B54", SLIPS = "#5B9BD5", Acrylic = "#70AD47")
stripchart(cover ~ Treatment, data = df, vertical = TRUE, pch = 19, method = "jitter",
           col = cols[levels(df$Treatment)], ylim = c(0, 100),
           ylab = "Underwater biofouling cover (%)", xlab = "Treatment")
means <- tapply(df$cover, df$Treatment, mean)
for (i in seq_along(means)) segments(i - 0.2, means[i], i + 0.2, means[i], lwd = 2)
dev.off()

cat("Done. See underwater_cover_results.txt and underwater_cover_dotplot.png\n")
