#!/usr/bin/env python3
# make_roi_crops.py -- crop every monitoring port ROI out of the grayscale-LINEAR
# images for the % cover analysis. One crop per camera x dive x light condition
# (N = no dive light, Y = dive light), saved full ROI resolution with a circular
# mask and a 1-99% contrast stretch, plus a key CSV.
#
# ROI origins (ROI_x, ROI_y, ROI_w, ROI_h) come from ROI_placement.csv -- the
# per-image port placements originally logged during CTF measurement and kept
# here as a dedicated placement table. N and Y use their own per-image ROI (the
# port sits at a different frame position under each light; ROIs are the same
# 179x179 size and track the same physical port).
#
# Pipeline position:
#   slips_gray_linear.sh  ->  THIS SCRIPT  ->  Fiji %cover macro  ->  cover_beta_glmm
#
# Run:  ~/slips-venv/bin/python3 make_roi_crops.py
# -----------------------------------------------------------------------------
import os, csv
import numpy as np
from PIL import Image

LIN    = "/Volumes/samsung/Corinne/SLIPS082026/MONITORING_grayscale_linear"
CSV_IN = "/Volumes/samsung/Corinne/SLIPS082026/monitoring_ROI_%cover/ROI_placement.csv"
OUT    = "/Volumes/samsung/Corinne/SLIPS082026/monitoring_ROI_%cover"
CROPS  = os.path.join(OUT, "crops")

DIVE_DATE = {"1":"08-21","2":"08-28","3":"09-04","4":"09-10","5":"09-17"}
TRT = {1:"acrylic",4:"acrylic",7:"acrylic",10:"acrylic",
       2:"glass",5:"glass",8:"glass",11:"glass",
       3:"SLIPS",6:"SLIPS",9:"SLIPS",12:"SLIPS"}

def circ(w, h):
    yy, xx = np.ogrid[0:h, 0:w]
    cx, cy = (w-1)/2.0, (h-1)/2.0
    return (xx-cx)**2 + (yy-cy)**2 <= (min(w, h)/2.0)**2

def crop_img(row):
    im = np.asarray(Image.open(os.path.join(LIN, row["Folder"], row["File_name"])),
                    dtype=np.float64)
    x, y = int(row["ROI_x"]), int(row["ROI_y"])
    w, h = int(row["ROI_w"]), int(row["ROI_h"])
    c = im[y:y+h, x:x+w]
    m = circ(c.shape[1], c.shape[0])
    v = c[m]
    lo, hi = np.percentile(v, 1), np.percentile(v, 99)
    d = np.clip((c - lo)/(hi - lo + 1e-9), 0, 1)
    d[~m] = 0.12                                   # outside circle = dark
    return Image.fromarray((d*255).astype(np.uint8))

os.makedirs(CROPS, exist_ok=True)
key, missing = [], 0
# utf-8-sig: ROI_placement.csv carries a BOM; strip it so "Camera #" keys resolve
for r in csv.DictReader(open(CSV_IN, encoding="utf-8-sig")):
    light = r["Light (Y/N)"].strip()
    cam   = r["Camera #"].strip()
    dive  = r["Monitoring Dive"].strip()
    name  = f"cam{int(cam):02d}_dive{dive}_light{light}.png"
    src   = os.path.join(LIN, r["Folder"], r["File_name"])
    if not os.path.exists(src):
        missing += 1
        continue
    crop_img(r).save(os.path.join(CROPS, name))
    key.append({"file":name, "camera":cam, "dive":dive, "date":DIVE_DATE.get(dive,""),
                "treatment":TRT.get(int(cam),""), "light":light,
                "source_folder":r["Folder"], "source_file":r["File_name"]})

with open(os.path.join(OUT, "crops_key.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["file","camera","dive","date","treatment",
                                      "light","source_folder","source_file"])
    w.writeheader()
    for k in key:
        w.writerow(k)

nN = sum(1 for k in key if k["light"] == "N")
nY = sum(1 for k in key if k["light"] == "Y")
print(f"wrote {len(key)} crops to {CROPS}  (N={nN}, Y={nY}; missing source files skipped: {missing})")
print(f"key: {os.path.join(OUT,'crops_key.csv')}")
