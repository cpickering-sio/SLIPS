# Monitoring % cover (diver TG-6 survey images)

Biofilm **% cover** on each camera's port, measured from the diver monitoring
survey photos (Olympus TG-6, see [`../../hardware/tg6/`](../../hardware/tg6/)).
One port ROI per **camera × dive × light condition** (N = no dive light,
Y = dive light).

## Pipeline

```
raw .ORF
   │  preprocessing/slips_gray_linear.sh        (linear 16-bit grayscale TIFFs)
   ▼
MONITORING_grayscale_linear/*.tiff
   │  make_roi_crops.py                         (crop each 179x179 port ROI)
   ▼
monitoring_ROI_%cover/crops/*.png
   │  cover_macro_monitoring_FIJI.ijm           (Fiji: threshold -> measure area)
   ▼
% cover per crop
   │  cover_beta_glmm_monitoring.R              (beta GLMM, Treatment x Week)
   ▼
result
```

## Files

| File | Role |
|---|---|
| `make_roi_crops.py` | Crops each port ROI out of the grayscale-linear images. ROI origins (`ROI_x, ROI_y, ROI_w, ROI_h`) are read from **`ROI_placement.csv`** (copy in [`../../data/monitoring_ROI_placement.csv`](../../data/monitoring_ROI_placement.csv)); applies a circular mask and 1–99% contrast stretch; writes labelled PNG crops + `crops_key.csv`. |
| `cover_macro_monitoring_FIJI.ijm` | Fiji/ImageJ macro: 16-bit threshold (0–252) and `Measure` to get fouled area fraction on each crop. |
| `cover_beta_glmm_monitoring.R` | Beta GLMM (logit link, `glmmTMB`): `p ~ Treatment * Week + (1 | Camera)`. Primary test = Treatment × Week interaction. |

## Data (in [`../../data/`](../../data/))
- `monitoring_ROI_placement.csv` — per-image port ROI origins (the placement table `make_roi_crops.py` reads).
- `monitoring_crops_key.csv` — maps each crop PNG to camera / dive / date / treatment / light.
- `cover_monitoring.csv` — measured % cover feeding the GLMM.

## Notes
- The ROIs are a fixed **179 × 179 px** circle tracking the same physical port;
  the N and Y images place that port at different frame positions, so each has
  its own logged origin.
- Paths inside `make_roi_crops.py` point at the working drive
  (`/Volumes/samsung/...`); edit `LIN`, `CSV_IN`, and `OUT` for a new machine.
