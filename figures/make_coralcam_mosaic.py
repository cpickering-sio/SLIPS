#!/usr/bin/env python3
"""
SLIPS local (off-pier) summer 2026 — autonomous "coral cam" photo mosaic.

One representative frame per camera (cameras 1-12, in order) from a single day,
laid out 4 rows x 3 columns. Because camera ID -> treatment cycles 1,2,3, filling
1-12 in row-major order makes each COLUMN a treatment (no cinderblocks):

    col 1 = Acrylic  (cams 1, 4, 7, 10)
    col 2 = Glass    (cams 2, 5, 8, 11)
    col 3 = SLIPS    (cams 3, 6, 9, 12)

Source frames: /Volumes/samsung/Corinne/SLIPS082026/coral_cams/<cam>/A<YYMMDD><HHMMSS>.jpg
Built with PIL only (matplotlib is arch-broken on this machine).
"""

import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# ── Config ──────────────────────────────────────────────────────────────────
CORAL_BASE = "/Volumes/samsung/Corinne/SLIPS082026/coral_cams"
OUT_DIR    = os.path.dirname(os.path.abspath(__file__))
OUT_PNG    = os.path.join(OUT_DIR, "SLIPs_coralcam_mosaic.png")

DAY   = "260918"    # A<YYMMDD> — 2026-09-18
TIME  = "120013"    # preferred HHMMSS (nearest noon); falls back to closest frame
DATE_NOTE = "autonomous camera"   # appended after the actual date in the subtitle

# Cameras in plain 1..12 order. Row-major into 3 columns => columns are treatments.
CAM_ORDER = list(range(1, 13))
N_COLS = 3
N_ROWS = 4

# Treatment per column (camera id mod 3): 1=Acrylic, 2=Glass, 0=SLIPS
TREATMENTS = ["Acrylic (uncoated)", "Glass (uncoated)", "Glass + SLIPS coating"]
COL_COLORS = [(214, 234, 248), (253, 235, 208), (213, 245, 227)]  # blue / tan / green
COL_ACCENT = [(41, 128, 185),  (211, 145, 20),  (39, 174, 96)]

# ── Panel / canvas geometry (pixels) ────────────────────────────────────────
CELL_W, CELL_H = 620, 349          # image cell (16:9 -> 620x349)
PAD            = 14                 # gap between cells
MARGIN         = 28                 # outer margin
COLHDR_H       = 60                 # treatment column header
CAMLBL_H       = 30                 # per-panel camera label strip
TITLE_H        = 70
SUBTITLE_H     = 34

GRID_W = N_COLS * CELL_W + (N_COLS - 1) * PAD
GRID_H = N_ROWS * (CELL_H + CAMLBL_H) + (N_ROWS - 1) * PAD

CANVAS_W = GRID_W + 2 * MARGIN
CANVAS_H = TITLE_H + SUBTITLE_H + COLHDR_H + GRID_H + 2 * MARGIN

BG      = (255, 255, 255)
INK     = (26, 37, 47)
SUBTLE  = (90, 100, 110)


def load_font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold
        else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


F_TITLE = load_font(34, bold=True)
F_SUB   = load_font(18)
F_COL   = load_font(20, bold=True)
F_CAM   = load_font(17, bold=True)


def frame_dt(fname):
    """Parse A<YYMMDD><HHMMSS>.jpg -> datetime."""
    return datetime.strptime(os.path.basename(fname)[1:13], "%y%m%d%H%M%S")


def pick_frame(cam):
    """Return (path, datetime) of the chosen frame for a camera, or (None, None)."""
    folder = os.path.join(CORAL_BASE, str(cam))
    if not os.path.isdir(folder):
        return None, None
    prefix = "A" + DAY
    frames = sorted(f for f in os.listdir(folder)
                    if f.startswith(prefix) and f.lower().endswith(".jpg"))
    if not frames:
        return None, None
    exact = f"A{DAY}{TIME}.jpg"
    if exact in frames:
        return os.path.join(folder, exact), frame_dt(exact)
    # else closest by time-of-day
    target = int(TIME)
    best = min(frames, key=lambda f: abs(int(f[7:13]) - target))
    return os.path.join(folder, best), frame_dt(best)


def crop_cover(img, w, h):
    """Center-crop img to the w:h aspect, then resize to (w, h)."""
    iw, ih = img.size
    tr = w / h
    if iw / ih > tr:
        nw = int(ih * tr)
        left = (iw - nw) // 2
        img = img.crop((left, 0, left + nw, ih))
    else:
        nh = int(iw / tr)
        top = (ih - nh) // 2
        img = img.crop((0, top, iw, top + nh))
    return img.resize((w, h), Image.LANCZOS)


def centered(draw, box, text, font, fill):
    x0, y0, x1, y1 = box
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    tw, th = r - l, b - t
    draw.text((x0 + (x1 - x0 - tw) / 2 - l,
               y0 + (y1 - y0 - th) / 2 - t), text, font=font, fill=fill)


def main():
    # Resolve chosen frame + timestamp for every camera up front
    picks = {cam: pick_frame(cam) for cam in CAM_ORDER}

    # Subtitle date = actual date of the frames (they share one capture day)
    dts = [dt for _, dt in picks.values() if dt is not None]
    if dts:
        date_label = dts[0].strftime("%b %-d, %Y") + f" — {DATE_NOTE}"
    else:
        date_label = DATE_NOTE

    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG)
    draw = ImageDraw.Draw(canvas)

    # Title + subtitle
    centered(draw, (0, MARGIN, CANVAS_W, MARGIN + TITLE_H - 20),
             "SLIP Off-Pier Monitoring — Port Views by Treatment", F_TITLE, INK)
    centered(draw, (0, MARGIN + TITLE_H - 24, CANVAS_W, MARGIN + TITLE_H + SUBTITLE_H - 24),
             date_label, F_SUB, SUBTLE)

    grid_top = MARGIN + TITLE_H + SUBTITLE_H + COLHDR_H
    grid_left = MARGIN

    # Column (treatment) headers
    for c in range(N_COLS):
        cx0 = grid_left + c * (CELL_W + PAD)
        hy0 = grid_top - COLHDR_H + 4
        draw.rounded_rectangle([cx0, hy0, cx0 + CELL_W, grid_top - 8],
                               radius=8, fill=COL_COLORS[c])
        draw.rounded_rectangle([cx0, hy0, cx0 + CELL_W, grid_top - 8],
                               radius=8, outline=COL_ACCENT[c], width=2)
        centered(draw, (cx0, hy0, cx0 + CELL_W, grid_top - 8),
                 TREATMENTS[c], F_COL, INK)

    # Panels
    for idx, cam in enumerate(CAM_ORDER):
        r, c = divmod(idx, N_COLS)
        x0 = grid_left + c * (CELL_W + PAD)
        y0 = grid_top + r * (CELL_H + CAMLBL_H + PAD)

        # image
        path, dt = picks[cam]
        cell = Image.new("RGB", (CELL_W, CELL_H), (204, 204, 204))
        if path:
            try:
                cell = crop_cover(Image.open(path).convert("RGB"), CELL_W, CELL_H)
            except Exception:
                pass
        canvas.paste(cell, (x0, y0))
        draw.rectangle([x0, y0, x0 + CELL_W - 1, y0 + CELL_H - 1],
                       outline=COL_ACCENT[c], width=3)

        # camera label strip beneath image: cam number + actual capture date/time
        ly0 = y0 + CELL_H
        draw.rectangle([x0, ly0, x0 + CELL_W, ly0 + CAMLBL_H], fill=COL_COLORS[c])
        stamp = dt.strftime("%Y-%m-%d %H:%M:%S") if dt else "no frame"
        centered(draw, (x0, ly0, x0 + CELL_W, ly0 + CAMLBL_H),
                 f"Camera {cam}  ·  {stamp}", F_CAM, INK)

    canvas.save(OUT_PNG, "PNG")
    print(f"Saved:\n  {OUT_PNG}\n  ({CANVAS_W}x{CANVAS_H})")


if __name__ == "__main__":
    main()
