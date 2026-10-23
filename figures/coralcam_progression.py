#!/usr/bin/env python3
# coralcam_progression.py -- fouling progression mosaic.
# Rows = treatment (cam7 Acrylic, cam8 Glass, cam9 SLIPS); columns = date.
# Day-1 (Aug 21) is the RED-outlined reference column. Each cell is cropped to
# that camera's port-face ROI so biofouling is front-and-centre. PIL only.
import os
from PIL import Image, ImageDraw, ImageFont

BASE = "/Volumes/samsung/Corinne/SLIPS082026/coral_cams"
OUT  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coralcam_progression.png")

DATES = [("260821","Aug 21"), ("260828","Aug 28"), ("260904","Sep 4"),
         ("260910","Sep 10"), ("260918","Sep 18")]
TIME = "120013"
ROWS = [(7, "Acrylic (uncoated)",     (41, 128, 185)),
        (8, "Glass (uncoated)",       (211, 145, 20)),
        (9, "Glass + SLIPS coating",  (39, 174, 96))]
ROI = {7: (1365, 142, 674, 412), 8: (841, 133, 695, 464), 9: (525, 104, 705, 497)}  # x,y,w,h
RED = (200, 30, 30)

CELL=300; PAD=10; MARGIN=26; ROWLBL_W=60; COLHDR_H=42; TITLE_H=58; REFBAN=24
BG=(255,255,255); INK=(26,37,47); SUBTLE=(90,100,110)

def font(sz, bold=False):
    for p in (["/System/Library/Fonts/Supplemental/Arial Bold.ttf"] if bold
              else ["/System/Library/Fonts/Supplemental/Arial.ttf"]) + ["/System/Library/Fonts/Helvetica.ttc"]:
        try: return ImageFont.truetype(p, sz)
        except Exception: pass
    return ImageFont.load_default()
F_T=font(28,True); F_SUB=font(15); F_C=font(18,True); F_R=font(17,True); F_REF=font(15,True)

def crop_cover(img, w, h):
    iw, ih = img.size; tr = w/h
    if iw/ih > tr:
        nw=int(ih*tr); l=(iw-nw)//2; img=img.crop((l,0,l+nw,ih))
    else:
        nh=int(iw/tr); t=(ih-nh)//2; img=img.crop((0,t,iw,t+nh))
    return img.resize((w, h), Image.LANCZOS)

def centered(draw, box, text, fnt, fill):
    x0,y0,x1,y1=box; l,t,r,b=draw.textbbox((0,0),text,font=fnt); tw,th=r-l,b-t
    draw.text((x0+(x1-x0-tw)/2-l, y0+(y1-y0-th)/2-t), text, font=fnt, fill=fill)

def pick(cam, day):
    folder=os.path.join(BASE,str(cam)); pref="A"+day
    fr=sorted(f for f in os.listdir(folder) if f.startswith(pref) and f.lower().endswith(".jpg"))
    if not fr: return None
    ex=f"A{day}{TIME}.jpg"
    if ex in fr: return os.path.join(folder, ex)
    tgt=int(TIME); return os.path.join(folder, min(fr, key=lambda f: abs(int(f[7:13])-tgt)))

NC, NR = len(DATES), len(ROWS)
GRID_W = NC*CELL + (NC-1)*PAD
GRID_H = NR*CELL + (NR-1)*PAD
grid_left = MARGIN + ROWLBL_W
grid_top  = MARGIN + TITLE_H + REFBAN + COLHDR_H
CW = grid_left + GRID_W + MARGIN
CH = grid_top + GRID_H + MARGIN

canvas = Image.new("RGB", (CW, CH), BG); draw = ImageDraw.Draw(canvas)

centered(draw, (0, MARGIN, CW, MARGIN+TITLE_H-20),
         "Biofouling progression by port treatment", F_T, INK)
centered(draw, (0, MARGIN+TITLE_H-22, CW, MARGIN+TITLE_H+2),
         "autonomous noon port views, 2026  ·  cameras 7, 8, 9", F_SUB, SUBTLE)

# "Day 1 reference" banner over column 0
centered(draw, (grid_left, grid_top-COLHDR_H-REFBAN, grid_left+CELL, grid_top-COLHDR_H),
         "Day 1 reference", F_REF, RED)

# date column headers
for ci,(day,lbl) in enumerate(DATES):
    cx = grid_left + ci*(CELL+PAD)
    centered(draw, (cx, grid_top-COLHDR_H, cx+CELL, grid_top-6), lbl, F_C,
             RED if ci==0 else INK)

# panels + rotated row labels
for ri,(cam,lbl,acc) in enumerate(ROWS):
    rx,ry,rw,rh = ROI[cam]
    ly = grid_top + ri*(CELL+PAD)
    lab = Image.new("RGB", (CELL, ROWLBL_W), BG); ld = ImageDraw.Draw(lab)
    centered(ld, (0,0,CELL,ROWLBL_W), lbl, F_R, acc)
    canvas.paste(lab.rotate(90, expand=True), (MARGIN-6, ly))
    for ci,(day,dlbl) in enumerate(DATES):
        cx = grid_left + ci*(CELL+PAD)
        p = pick(cam, day)
        cell = Image.new("RGB", (CELL, CELL), (204,204,204))
        if p:
            try:
                im = Image.open(p).convert("RGB").crop((rx, ry, rx+rw, ry+rh))
                cell = crop_cover(im, CELL, CELL)
            except Exception:
                pass
        canvas.paste(cell, (cx, ly))
        draw.rectangle([cx, ly, cx+CELL-1, ly+CELL-1],
                       outline=(RED if ci==0 else acc), width=(4 if ci==0 else 2))

# red box around the whole reference column
draw.rectangle([grid_left-5, grid_top-COLHDR_H-REFBAN-2, grid_left+CELL+5, grid_top+GRID_H+5],
               outline=RED, width=3)

canvas.save(OUT, "PNG")
print(f"saved {OUT}  ({CW}x{CH})")
