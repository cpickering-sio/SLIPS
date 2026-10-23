# analyze_multimetric.R -- which metric separates treatments over time?
# Reads ctf_metrics.csv (from extract_metrics.py), fits the mixed model
#   value ~ treatment * days + (1|camera)
# for every metric x light condition, and reports the treatment:days
# interaction p-value (the key "do treatments diverge?" test) plus the
# acrylic-vs-coating slope difference. Saves a summary table + figure.

pkgs <- c("tidyverse", "lme4", "lmerTest", "emmeans")
new <- pkgs[!pkgs %in% rownames(installed.packages())]
if (length(new)) install.packages(new, repos = "https://cloud.r-project.org")
invisible(lapply(pkgs, library, character.only = TRUE))

# optional args: 1 = metrics CSV, 2 = output summary CSV
args <- commandArgs(trailingOnly = TRUE)
in_csv  <- if (length(args) >= 1) args[1] else
  "/Volumes/samsung/Corinne/SLIPS082026/ctf_metrics.csv"
out_csv <- if (length(args) >= 2) args[2] else
  "/Volumes/samsung/Corinne/SLIPS082026/multimetric_summary.csv"
cat("Reading:", in_csv, "\n")
m <- read_csv(in_csv, show_col_types = FALSE)

treatment_map <- c(
  "1"="Acrylic (uncoated)","2"="Glass (uncoated)","3"="Glass + coating",
  "4"="Acrylic (uncoated)","5"="Glass (uncoated)","6"="Glass + coating",
  "7"="Acrylic (uncoated)","8"="Glass (uncoated)","9"="Glass + coating",
 "10"="Acrylic (uncoated)","11"="Glass (uncoated)","12"="Glass + coating")
trt_levels <- c("Acrylic (uncoated)","Glass (uncoated)","Glass + coating")
parse_date <- function(fldr) as.Date(sub("^[0-9]+_", "", fldr), format = "%m%d%Y")

metric_cols <- c("michelson","rms_contrast","sd","variance","entropy","lapvar_norm")

dat <- m %>%
  mutate(treatment = factor(treatment_map[as.character(camera)], levels = trt_levels),
         light = factor(light, levels = c("N","Y"),
                        labels = c("No dive light","Dive light")),
         camera = factor(camera),
         days = as.numeric(parse_date(folder) - min(parse_date(folder)))) %>%
  group_by(camera, treatment, dive, days, light) %>%
  summarise(across(all_of(metric_cols), mean), .groups = "drop")

## ---- fit model for each metric x light; collect key p-values ----
summ <- list()
for (mc in metric_cols) {
  for (lc in levels(dat$light)) {
    sub <- dat %>% filter(light == lc) %>% rename(value = all_of(mc))
    fit <- suppressMessages(suppressWarnings(
      lmerTest::lmer(value ~ treatment * days + (1 | camera), data = sub)))
    a <- anova(fit)
    p_int <- a["treatment:days", "Pr(>F)"]
    et <- suppressMessages(emmeans::emtrends(fit, ~ treatment, var = "days"))
    pr <- as.data.frame(pairs(et))
    p_ac <- pr$p.value[pr$contrast == "Acrylic (uncoated) - (Glass + coating)"]
    summ[[paste(mc, lc)]] <- tibble(metric = mc, light = lc,
                                    p_interaction = p_int,
                                    p_acrylic_vs_coating_slope = ifelse(length(p_ac), p_ac, NA))
  }
}
summ <- bind_rows(summ) %>% arrange(p_interaction)
cat("\n===== treatment x time interaction (smaller p = treatments diverge) =====\n")
print(as.data.frame(summ), digits = 3)
write_csv(summ, out_csv)

## ---- figure: trajectories for every metric (rows) x light (cols) ----
long <- dat %>%
  pivot_longer(all_of(metric_cols), names_to = "metric", values_to = "value") %>%
  group_by(metric, light, treatment, days) %>%
  summarise(mean = mean(value), se = sd(value)/sqrt(n()), .groups = "drop")

p <- ggplot(long, aes(days, mean, colour = treatment, group = treatment)) +
  geom_line(linewidth = 0.6) + geom_point(size = 1.8) +
  geom_errorbar(aes(ymin = mean - se, ymax = mean + se), width = 0.6) +
  facet_grid(metric ~ light, scales = "free_y") +
  labs(x = "Days since first dive", y = "metric value (mean ± SE)",
       title = "Which metric separates treatments over time?", colour = NULL) +
  theme_bw(base_size = 11) + theme(legend.position = "top")

ggsave("multimetric_trajectories.png", p, width = 10, height = 12, dpi = 200)
cat("\nSaved figure: multimetric_trajectories.png\n")
