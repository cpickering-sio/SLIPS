#!/usr/bin/env python3
# roi_mosaic.py -- contact sheet of every port ROI: columns = camera # (1-12),
# rows = dive date. Uses the ROIs logged in CTF_results.csv. Each cell is
# contrast-stretched so biofilm texture is visible. Camera-number headers are
# colored by treatment (acrylic/glass/coated) so treatment groups stay legible
# even though columns are in camera order. For eyeballing fouling across the
# whole experiment and/or as a base image for hand-annotation.
#
# Usage: python3 roi_mosaic.py [N|Y]     (light condition, default N)

import os, sys, csv
import numpy as np
from PIL import Image, ImageDraw

LIN = "/Volumes/samsung/Corinne/SLIPS082026/MONITORING_grayscale_linear"
CSV_IN = "/Volumes/samsung/Corinne/SLIPS082026/CTF_results.csv"
LIGHT = sys.argv[1] if len(sys.argv) > 1 else "N"

CELL = 150
LEFT = 96      # room for date labels
TOP = 26       # room for camera # labels
CAMS = [str(c) for c in range(1, 13)]
DIVES = ["1", "2", "3", "4", "5"]
DIVE_DATE = {"1": "08/21", "2": "08/28", "3": "09/04", "4": "09/10", "5": "09/17"}
TRT = {"1": "acr", "2": "gls", "3": "coat", "4": "acr", "5": "gls", "6": "coat",
       "7": "acr", "8": "gls", "9": "coat", "10": "acr", "11": "gls", "12": "coat"}
TRT_COL = {"acr": (220, 70, 60), "gls": (40, 160, 70), "coat": (60, 110, 210)}

def circ(w, h):
    yy, xx = np.ogrid[0:h, 0:w]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    return (xx - cx) ** 2 + (yy - cy) ** 2 <= (min(w, h) / 2.0) ** 2

def cell_img(row):
    im = np.asarray(Image.open(os.path.join(LIN, row["Folder"], row["File_name"])),
                    dtype=np.float64)
    x, y = int(row["ROI_x"]), int(row["ROI_y"])
    w, h = int(row["ROI_w"]), int(row["ROI_h"])
    crop = im[y:y+h, x:x+w]
    m = circ(*crop.shape[::-1]) if crop.shape[0] != crop.shape[1] else circ(crop.shape[1], crop.shape[0])
    v = crop[m]
    lo, hi = np.percentile(v, 1), np.percentile(v, 99)
    d = np.clip((crop - lo) / (hi - lo + 1e-9), 0, 1)
    d[~m] = 0.12
    g = (d * 255).astype(np.uint8)
    return np.asarray(Image.fromarray(g).resize((CELL, CELL)))

# index rows by (camera, dive) for chosen light
idx = {}
for r in csv.DictReader(open(CSV_IN)):
    if r["Light (Y/N)"] == LIGHT:
        idx[(r["Camera #"], r["Monitoring Dive"].strip())] = r

W = LEFT + len(CAMS) * CELL
H = TOP + len(DIVES) * CELL
canvas = Image.new("RGB", (W, H), (255, 255, 255))
draw = ImageDraw.Draw(canvas)

# column headers: camera # colored by treatment
for ci, cam in enumerate(CAMS):
    cx = LEFT + ci * CELL + CELL // 2 - 10
    draw.text((cx, 8), "c%s" % cam, fill=TRT_COL[TRT[cam]])
# row headers: dive date
for ri, dv in enumerate(DIVES):
    draw.text((6, TOP + ri * CELL + CELL // 2 - 8),
              "d%s\n%s" % (dv, DIVE_DATE[dv]), fill=(0, 0, 0))

missing = 0
for ri, dv in enumerate(DIVES):
    for ci, cam in enumerate(CAMS):
        r = idx.get((cam, dv))
        x0, y0 = LEFT + ci * CELL, TOP + ri * CELL
        if r is None:
            draw.rectangle([x0, y0, x0+CELL-1, y0+CELL-1], fill=(60, 60, 60))
            draw.text((x0+CELL//2-12, y0+CELL//2-6), "n/a", fill=(180, 180, 180))
            missing += 1
            continue
        canvas.paste(Image.fromarray(cell_img(r)), (x0, y0))

# grid lines
for ci in range(len(CAMS)+1):
    draw.line([(LEFT+ci*CELL, TOP), (LEFT+ci*CELL, H)], fill=(200, 200, 200))
for ri in range(len(DIVES)+1):
    draw.line([(LEFT, TOP+ri*CELL), (W, TOP+ri*CELL)], fill=(200, 200, 200))

out = "roi_mosaic_light%s.png" % LIGHT
canvas.save(out)
print("saved %s  (%d cells, %d missing)  light=%s"
      % (out, len(CAMS)*len(DIVES) - missing, missing, LIGHT))
print("columns c1-c12 colored by treatment: red=acrylic, green=glass, blue=coated")
