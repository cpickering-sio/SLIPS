# =============================================================================
# cover_beta_glmm.R -- monitoring percent-cover analysis (beta GLMM, logit link)
#   Model:  p ~ Treatment * Week + (1 | Camera)      [glmmTMB, beta_family]
#   PRIMARY test: Treatment x Week interaction (LRT) -> do cover trajectories
#                 differ among treatments over the deployment?
#
# Data: ../%Cover_monitoring-combined.csv  (read-only; not modified)
#   cols: Date, Week, Treatment, cam, Area, "% Area", MinThr, MaxThr, Size
#   Week 1 = baseline, uniformly 0% (clean at deployment) -> dropped in code.
#   Week 2 cam 8 = a single 0% -> handled by the (0,1) squeeze.
# =============================================================================
library(glmmTMB); library(emmeans); library(DHARMa); library(tidyverse)

ROOT <- "/Users/corinnepickering/Desktop/Thode_lab/SLIPS/SLIPS_Off_Pier_202608/Biofouling/%cover_monitoring"
setwd(file.path(ROOT, "LMM"))
csv <- file.path(ROOT, "%Cover_monitoring-combined.csv")

## ---- 1. load (CSV left untouched) ------------------------------------------
cov <- read_csv(csv, show_col_types = FALSE) %>%
  rename(pctArea = `% Area`)

## ---- 2. prep ---------------------------------------------------------------
cov <- cov %>%
  mutate(
    Treatment = str_trim(Treatment),                               # "Acrylic " -> "Acrylic"
    Treatment = factor(Treatment, levels = c("Glass","SLIPS","Acrylic")), # Glass = reference
    Camera    = factor(cam),
    p         = pctArea / 100                                      # percent -> proportion
  )

# Drop the uniformly-0% baseline (Week 1): no treatment signal, degenerate for beta.
cov <- cov %>% filter(Week != 1) %>%
  mutate(Week = droplevels(factor(Week)))                          # reference = Week 2

# Squeeze remaining 0s/1s just inside (0,1)  [Smithson & Verkuilen 2006]
# (handles the single Week-2 cam-8 zero; harmless to interior values)
n <- nrow(cov)
cov$p <- (cov$p * (n - 1) + 0.5) / n
cat(sprintf("Rows after dropping Week 1: %d  (cameras=%d, weeks=%s)\n",
            n, nlevels(cov$Camera), paste(levels(cov$Week), collapse=",")))

## ---- 3. fit beta GLMM ------------------------------------------------------
m_full  <- glmmTMB(p ~ Treatment * Week + (1 | Camera),
                   family = beta_family(link = "logit"), data = cov)
m_noint <- glmmTMB(p ~ Treatment + Week + (1 | Camera),
                   family = beta_family(link = "logit"), data = cov)

## ---- 4. results + log ------------------------------------------------------
sink("cover_results.txt", split = TRUE)
cat("Beta GLMM: p ~ Treatment * Week + (1|Camera)  [logit link]\n")
cat("Generated:", format(Sys.time()), "\n"); cat(strrep("=",70), "\n")

cat("\n-- PRIMARY test: Treatment:Week interaction (likelihood-ratio test) --\n")
print(anova(m_noint, m_full))          # significant -> trajectories differ

cat("\n-- Full model summary --\n"); print(summary(m_full))

emm <- emmeans(m_full, ~ Treatment | Week, type = "response")      # back to proportion
cat("\n-- Estimated marginal cover by Treatment x Week --\n"); print(emm)
cat("\n-- Pairwise treatment contrasts within each week (Tukey) --\n"); print(pairs(emm))
sink()

## ---- 5. diagnostics --------------------------------------------------------
png("cover_dharma.png", width = 950, height = 450, res = 110)
plot(simulateResiduals(m_full)); dev.off()

cat("\nDone. See cover_results.txt and cover_dharma.png in", getwd(), "\n")
