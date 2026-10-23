#!/usr/bin/env python3
# coralcam_progression_svg.py -- hybrid VECTOR version of the progression figure.
# Photos are embedded (base64 PNG) as placed <image> objects; all text, borders,
# and the red reference box are editable vector elements. -> edit parts in
# PowerPoint ("Convert to Shape") or Illustrator. Output: coralcam_progression.svg
import os, io, base64
from PIL import Image

BASE = "/Volumes/samsung/Corinne/SLIPS082026/coral_cams"
OUT  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coralcam_progression.svg")

DATES = [("260821","Aug 21"), ("260828","Aug 28"), ("260904","Sep 4"),
         ("260910","Sep 10"), ("260918","Sep 18")]
TIME = "120013"
ROWS = [(7, "Acrylic (uncoated)",     (41, 128, 185)),
        (8, "Glass (uncoated)",       (211, 145, 20)),
        (9, "Glass + SLIPS coating",  (39, 174, 96))]
ROI = {7: (1365,142,674,412), 8: (841,133,695,464), 9: (525,104,705,497)}
RED=(200,30,30); INK=(26,37,47); SUBTLE=(90,100,110)

CELL=300; PAD=10; MARGIN=26; ROWLBL_W=60; COLHDR_H=42; TITLE_H=58; REFBAN=24

def crop_cover(img, w, h):
    iw,ih=img.size; tr=w/h
    if iw/ih>tr:
        nw=int(ih*tr); l=(iw-nw)//2; img=img.crop((l,0,l+nw,ih))
    else:
        nh=int(iw/tr); t=(ih-nh)//2; img=img.crop((0,t,iw,t+nh))
    return img.resize((w,h), Image.LANCZOS)

def pick(cam, day):
    folder=os.path.join(BASE,str(cam)); pref="A"+day
    fr=sorted(f for f in os.listdir(folder) if f.startswith(pref) and f.lower().endswith(".jpg"))
    if not fr: return None
    ex=f"A{day}{TIME}.jpg"
    return os.path.join(folder, ex if ex in fr else min(fr, key=lambda f: abs(int(f[7:13])-int(TIME))))

def cell_b64(cam, day, gray=False):
    rx,ry,rw,rh=ROI[cam]
    im=Image.open(pick(cam,day)).convert("RGB").crop((rx,ry,rx+rw,ry+rh))
    im=crop_cover(im, CELL, CELL)
    if gray: im=im.convert("L").convert("RGB")
    buf=io.BytesIO(); im.save(buf,"PNG")
    return base64.b64encode(buf.getvalue()).decode()

def rgb(t): return f"rgb({t[0]},{t[1]},{t[2]})"
def txt(x,y,s,sz,anc="middle",wt="normal",fill=INK,rot=None):
    tr=f' transform="rotate({rot} {x} {y})"' if rot is not None else ''
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial,Helvetica,sans-serif" '
            f'font-size="{sz}" font-weight="{wt}" fill="{rgb(fill)}" '
            f'text-anchor="{anc}"{tr}>{s}</text>')

NC,NR=len(DATES),len(ROWS)
GRID_W=NC*CELL+(NC-1)*PAD; GRID_H=NR*CELL+(NR-1)*PAD
grid_left=MARGIN+ROWLBL_W; grid_top=MARGIN+TITLE_H+REFBAN+COLHDR_H
CW=grid_left+GRID_W+MARGIN; CH=grid_top+GRID_H+MARGIN
HERE=os.path.dirname(os.path.abspath(__file__))

def build(gray, suffix):
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
       f'width="{CW}" height="{CH}" viewBox="0 0 {CW} {CH}">']
    s.append(f'<rect width="{CW}" height="{CH}" fill="white"/>')
    s.append(txt(CW/2, MARGIN+30, "Biofouling progression by port treatment", 28, "middle", "bold", INK))
    s.append(txt(CW/2, MARGIN+50, "autonomous noon port views, 2026 · cameras 7, 8, 9", 15, "middle", "normal", SUBTLE))
    s.append(txt(grid_left+CELL/2, grid_top-COLHDR_H-REFBAN/2+2, "Day 1 reference", 15, "middle", "bold", RED))
    for ci,(day,lbl) in enumerate(DATES):
        cx=grid_left+ci*(CELL+PAD)
        s.append(txt(cx+CELL/2, grid_top-12, lbl, 18, "middle", "bold", RED if ci==0 else INK))
    for ri,(cam,lbl,acc) in enumerate(ROWS):
        ly=grid_top+ri*(CELL+PAD); lx=MARGIN+ROWLBL_W/2; cy=ly+CELL/2
        s.append(txt(lx, cy, lbl, 17, "middle", "bold", acc, rot=-90))
        for ci,(day,dlbl) in enumerate(DATES):
            cx=grid_left+ci*(CELL+PAD)
            s.append(f'<image x="{cx}" y="{ly}" width="{CELL}" height="{CELL}" '
                     f'preserveAspectRatio="none" xlink:href="data:image/png;base64,{cell_b64(cam,day,gray)}"/>')
            col=RED if ci==0 else acc; w=4 if ci==0 else 2
            s.append(f'<rect x="{cx}" y="{ly}" width="{CELL}" height="{CELL}" fill="none" '
                     f'stroke="{rgb(col)}" stroke-width="{w}"/>')
    s.append(f'<rect x="{grid_left-5}" y="{grid_top-COLHDR_H-REFBAN-2}" width="{CELL+10}" '
             f'height="{COLHDR_H+REFBAN+GRID_H+7}" fill="none" stroke="{rgb(RED)}" stroke-width="3"/>')
    s.append('</svg>')
    out=os.path.join(HERE, f"coralcam_progression_{suffix}.svg")
    with open(out,"w") as f: f.write("\n".join(s))
    print("saved", out, f"({CW}x{CH})")

build(False, "color")
build(True,  "gray")
