# SLIPS

Analysis, processing, and figure code for the **SLIPS** (Slippery Liquid-Infused
Porous Surface) anti-biofouling camera-housing experiment. Three surface
treatments (× 4 replicate camera housings each = 12 cameras) were deployed and
surveyed over repeated dives; this repository holds the full pipeline from raw
images to published figures and statistics.

> **Code only.** Raw imagery, video, and large binaries are intentionally
> excluded (see `.gitignore`). Derived, small data tables needed to reproduce
> the analyses are included under [`data/`](data/).

## Repository layout

| Folder | Contents |
|---|---|
| [`preprocessing/`](preprocessing/) | Raw Olympus `.ORF` → half-resolution 16-bit grayscale TIFF (LibRaw + ImageMagick), plus the conversion tutorial. `slips_gray_linear.sh` is the **linear-output** pipeline used for **both** the optical-clarity metrics **and** the % cover monitoring images. |
| [`optical_clarity/`](optical_clarity/) | Optical-clarity statistics — the linear mixed model (`analyze_multimetric.R`). Image processing (ROI cropping + metric measurement) was done with the **Biofouling Analyzer** tool (see below); the MATLAB time-series / environment plots live in [`figures/`](figures/). |
| [`biofouling_cover/`](biofouling_cover/) | Biofilm **% cover** — two analyses: `monitoring/` (diver TG-6 survey: `make_roi_crops.py` crops each port ROI from the grayscale-linear images using `ROI_placement.csv`, then a Fiji threshold macro + beta GLMM) and `inner_cam/` (autonomous underwater camera footage: mixed model, `underwater_cover_stats.R`). See [`biofouling_cover/monitoring/README.md`](biofouling_cover/monitoring/README.md) for the monitoring pipeline. |
| [`dry_mass/`](dry_mass/) | Dry-mass biofouling statistics. |
| [`figures/`](figures/) | Figure-generation scripts (design, experimental layout, coral-cam mosaics/progression) and the MATLAB optical-clarity time-series / environment plots. |
| [`rois/`](rois/) | `camera_crops/` — rotated per-camera crop ROIs (`RoiSet`) used for optics/inner-cam; `percent_cover_fiji/` — the ROIs used in Fiji for the monitoring % cover. |
| [`data/`](data/) | Small derived CSVs used as analysis inputs (metrics master, monitoring % cover, underwater % cover, wave aggregate, dry mass). |
| [`hardware/`](hardware/) | Camera documentation: `tg6/` (specs, spec sheet PDF, one sample RAW) for the monitoring-capture camera, and `wayne_cameras/` for the autonomous time-lapse units. |
| [`maui/`](maui/) | Preliminary Maui trial — randomization, figures, dry-mass stats, and data (not pursued in depth; see its README). |

## Image processing — Biofouling Analyzer

Optical-clarity image processing (per-camera ROI cropping and metric measurement
on the grayscale frames) was performed with the **Biofouling Analyzer** tool:

- **https://oceaneboulais.github.io/biofouling-analyzer/**

The per-camera crop regions it used are provided in
[`rois/camera_crops/`](rois/camera_crops/); the Fiji % cover monitoring ROIs are
in [`rois/percent_cover_fiji/`](rois/percent_cover_fiji/).

## Requirements

- **LibRaw** (`dcraw_emu`) and **ImageMagick** (`magick`): `brew install libraw imagemagick`
- **Python 3** with `numpy`, `pillow` (plus `matplotlib` / `scipy` for the figure scripts)
- **R** with `lme4`, `glmmTMB`, `emmeans`, `tidyverse`
- **MATLAB** for the `figures/*.m` time-series plots
- **Fiji / ImageJ** for ROI measurement

## Pipeline overview

1. **Preprocess** — `preprocessing/slips_gray_linear.sh` converts raw `.ORF` to
   linear 16-bit grayscale TIFFs (identical radiometric treatment across dates).
   Used for both optics and the monitoring % cover images.
2. **Extract metrics** — optical-clarity metrics measured within the per-camera
   crop ROIs (`rois/camera_crops/`) via the Biofouling Analyzer.
3. **Model** — `optical_clarity/analyze_multimetric.R` fits the linear mixed
   model (Treatment × Day, camera random intercept).
4. **% cover** — monitoring: `make_roi_crops.py` crops each port ROI from the
   grayscale-linear images using `data/monitoring_ROI_placement.csv`, then a Fiji
   threshold macro measures fouled area → `cover_beta_glmm_monitoring.R`.
   Inner-cam (`biofouling_cover/inner_cam/`) quantifies cover from the autonomous
   camera footage; `dry_mass/` covers dry-mass biofouling.
5. **Figures** — `figures/` regenerate the manuscript figures.

## License

MIT — see [`LICENSE`](LICENSE).

## Citation

See [`CITATION.cff`](CITATION.cff). Please cite the archived release (Zenodo DOI,
added on first release) when using this code.
