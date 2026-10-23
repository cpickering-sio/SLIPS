#!/usr/bin/env python3
# export_rois_for_annotation.py -- export each port ROI as a clean, BLINDED PNG
# for hand-annotation of biofilm. Reuses the ROIs in CTF_results.csv. Files get
# random IDs (roi_000.png ...) so treatment/date are hidden while scoring (keeps
# the original protocol's unbiased design). A key CSV (kept separate, don't peek)
# maps ID -> camera/dive. Paint biofilm PURE RED (255,0,0) over the growth, save
# the PNG under the same name into annotate_done/, then run ingest_annotations.py.
#
# Usage: python3 export_rois_for_annotation.py [N|Y]   (light, default N)

import os, sys, csv, random
import numpy as np
from PIL import Image, ImageDraw

LIN = "/Volumes/samsung/Corinne/SLIPS082026/MONITORING_grayscale_linear"
CSV_IN = "/Volumes/samsung/Corinne/SLIPS082026/CTF_results.csv"
OUTDIR = "/Volumes/samsung/Corinne/SLIPS082026/annotate_todo"
KEY = "/Volumes/samsung/Corinne/SLIPS082026/annotate_key.csv"
LIGHT = sys.argv[1] if len(sys.argv) > 1 else "N"
SIZE = 500          # painting canvas size
SEED = 20260918     # fixed -> reproducible blinding

def circ(w, h):
    yy, xx = np.ogrid[0:h, 0:w]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    return (xx - cx) ** 2 + (yy - cy) ** 2 <= (min(w, h) / 2.0) ** 2

def stretched(row):
    im = np.asarray(Image.open(os.path.join(LIN, row["Folder"], row["File_name"])),
                    dtype=np.float64)
    x, y = int(row["ROI_x"]), int(row["ROI_y"])
    w, h = int(row["ROI_w"]), int(row["ROI_h"])
    crop = im[y:y+h, x:x+w]
    m = circ(crop.shape[1], crop.shape[0])
    v = crop[m]
    lo, hi = np.percentile(v, 1), np.percentile(v, 99)
    d = np.clip((crop - lo) / (hi - lo + 1e-9), 0, 1)
    g = (d * 255).astype(np.uint8)
    rgb = np.dstack([g, g, g])
    rgb[~m] = (30, 30, 30)          # outside circle = dark; ignored on ingest
    return rgb

rows = [r for r in csv.DictReader(open(CSV_IN)) if r["Light (Y/N)"] == LIGHT]
random.seed(SEED)
random.shuffle(rows)

if not os.path.isdir(OUTDIR):
    os.makedirs(OUTDIR)
key = []
for i, r in enumerate(rows):
    rid = "roi_%03d" % i
    img = Image.fromarray(stretched(r)).resize((SIZE, SIZE))
    d = ImageDraw.Draw(img)
    d.ellipse([1, 1, SIZE-2, SIZE-2], outline=(0, 255, 255))   # ROI boundary
    img.save(os.path.join(OUTDIR, rid + ".png"))
    key.append({"id": rid, "camera": r["Camera #"], "dive": r["Monitoring Dive"].strip(),
                "light": r["Light (Y/N)"], "folder": r["Folder"], "file": r["File_name"]})

with open(KEY, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["id", "camera", "dive", "light", "folder", "file"])
    w.writeheader()
    for k in key:
        w.writerow(k)

print("exported %d blinded ROIs to %s" % (len(key), OUTDIR))
print("key (don't peek while scoring): %s" % KEY)
print("paint biofilm PURE RED (255,0,0), save PNGs into annotate_done/, then ingest.")
