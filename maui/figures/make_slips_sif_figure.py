import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from PIL import Image
import numpy as np
import os

BASE = '/Users/corinnepickering/Desktop/Thode_lab/SLIPS/maui2026/Maui2026/SLIPs_figure_images'

# Cameras in cinderblock order (matches main figure grouping)
cam_groups = [
    [6, 3, 10],   # Cinderblock A
    [4, 2, 11],   # Cinderblock B
    [12, 1, 7],   # Cinderblock C
]
all_cams = [c for grp in cam_groups for c in grp]  # [6,3,10,4,2,11,12,1,7]
n_cams = len(all_cams)  # 9

rows = [
    ('in_water', 'In Water',  'something\nin frame', 'Something_in_frame_underwater', '#d5f5e3'),
    ('in_air',   'In Air',    'something\nin frame', 'Something_in_frame_inair',      '#fce4ec'),
]

# ── Layout ─────────────────────────────────────────────────────────────────────
IMG_H     = 1.8   # taller since only 2 rows
IMG_W     = 2.0
LABEL_W   = 1.3
CB_LBL_W  = 0.5
GRP_HDR_H = 0.30  # cinderblock group label sub-header
CAM_HDR_H = 0.45  # camera number header
HEADER_H  = GRP_HDR_H + CAM_HDR_H
SEP_H     = 0.18  # thin gap between cinderblock column groups

fig_w = CB_LBL_W + LABEL_W + n_cams * IMG_W + 2 * SEP_H + 0.3
fig_h = HEADER_H + len(rows) * IMG_H + 0.35

fig = plt.figure(figsize=(fig_w, fig_h), dpi=150)
fig.patch.set_facecolor('white')

# ── Column header positions ───────────────────────────────────────────────────
# Build x-positions for each camera column, inserting SEP_H gaps between groups
cam_x = {}   # cam -> x_left in inches (from left edge of figure)
x_cursor = CB_LBL_W + LABEL_W
for gi, grp in enumerate(cam_groups):
    for cam in grp:
        cam_x[cam] = x_cursor
        x_cursor += IMG_W
    if gi < len(cam_groups) - 1:
        x_cursor += SEP_H  # gap between groups

total_img_width = x_cursor - CB_LBL_W - LABEL_W  # for reference

# ── Group sub-header row (top portion of header) ──────────────────────────────
group_labels = ['Cinderblock A\nCams 6 · 3 · 10',
                'Cinderblock B\nCams 4 · 2 · 11',
                'Cinderblock C\nCams 12 · 1 · 7']
cb_colors = ['#e8f4f8', '#fef9e7', '#f0f8e8']

grp_y0 = 1.0 - GRP_HDR_H / fig_h
grp_h  = GRP_HDR_H / fig_h

for gi, (grp, glabel, gcol) in enumerate(zip(cam_groups, group_labels, cb_colors)):
    gx0 = cam_x[grp[0]] / fig_w
    gx1 = (cam_x[grp[-1]] + IMG_W) / fig_w
    ax_grp = fig.add_axes([gx0, grp_y0, gx1 - gx0, grp_h])
    ax_grp.set_facecolor(gcol)
    ax_grp.set_xlim(0, 1); ax_grp.set_ylim(0, 1)
    ax_grp.axis('off')
    ax_grp.text(0.5, 0.5, glabel, ha='center', va='center',
                fontsize=7.5, color='#2c3e50', multialignment='center')

# ── Camera number header row ───────────────────────────────────────────────────
cam_hdr_top = GRP_HDR_H
for cam in all_cams:
    cx = (cam_x[cam] + IMG_W / 2) / fig_w
    fig.text(cx, 1.0 - (cam_hdr_top + CAM_HDR_H / 2) / fig_h,
             f'Cam {cam}', ha='center', va='center',
             fontsize=10, fontweight='bold', color='#2c3e50')

# Line under cam headers
line_y = 1.0 - HEADER_H / fig_h
left_start = (CB_LBL_W + LABEL_W) / fig_w
fig.add_artist(plt.Line2D([left_start, 1.0], [line_y, line_y],
                           transform=fig.transFigure,
                           color='#95a5a6', linewidth=1.0))

# Vertical dashed lines between cinderblock groups
for gi in range(len(cam_groups) - 1):
    sep_x_in = cam_x[cam_groups[gi + 1][0]] - SEP_H / 2
    sx = sep_x_in / fig_w
    fig.add_artist(plt.Line2D([sx, sx], [0.0, line_y],
                               transform=fig.transFigure,
                               color='#bdc3c7', linewidth=1.0, linestyle='--'))

# ── Images ────────────────────────────────────────────────────────────────────
running_y = HEADER_H  # inches from top

for row_key, row_title, row_sub, folder_name, row_color in rows:
    row_in = running_y
    y0 = 1.0 - (row_in + IMG_H) / fig_h
    h  = IMG_H / fig_h

    # Row label
    rx = CB_LBL_W / fig_w
    rw = LABEL_W / fig_w
    ax_lbl = fig.add_axes([rx, y0, rw, h])
    ax_lbl.set_facecolor(row_color)
    ax_lbl.set_xlim(0, 1); ax_lbl.set_ylim(0, 1)
    ax_lbl.axis('off')
    ax_lbl.text(0.55, 0.68, row_title,
                ha='center', va='center', fontsize=10,
                fontweight='bold', color='#2c3e50')
    ax_lbl.text(0.55, 0.34, row_sub,
                ha='center', va='center', fontsize=8,
                color='#555555', multialignment='center')

    # One image per camera
    for cam in all_cams:
        folder = f"{BASE}/cam{cam}/{folder_name}"
        img_file = None
        if os.path.isdir(folder):
            files = sorted(f for f in os.listdir(folder)
                           if f.lower().endswith(('.jpg', '.jpeg', '.png')))
            if files:
                img_file = os.path.join(folder, files[0])

        x0 = cam_x[cam] / fig_w
        ax = fig.add_axes([x0, y0, IMG_W / fig_w, h])
        ax.set_facecolor('#cccccc')

        if img_file:
            try:
                img = Image.open(img_file)
                iw, ih = img.size
                target_ratio = 4 / 3
                if iw / ih > target_ratio:
                    new_w = int(ih * target_ratio)
                    left = (iw - new_w) // 2
                    img = img.crop((left, 0, left + new_w, ih))
                else:
                    new_h = int(iw / target_ratio)
                    top = (ih - new_h) // 2
                    img = img.crop((0, top, iw, top + new_h))
                ax.imshow(np.array(img), aspect='auto')
            except Exception:
                ax.text(0.5, 0.5, 'N/A', ha='center', va='center',
                        fontsize=9, color='#888888')
        else:
            ax.text(0.5, 0.5, 'No image', ha='center', va='center',
                    fontsize=8, color='#aaaaaa')

        ax.axis('off')
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(0.4)
            spine.set_edgecolor('#aaaaaa')

    running_y += IMG_H

# ── Section label (left column) ───────────────────────────────────────────────
cby = 1.0 - (HEADER_H + len(rows) * IMG_H) / fig_h
cbh = len(rows) * IMG_H / fig_h

ax_lbl = fig.add_axes([0.005, cby, CB_LBL_W / fig_w - 0.005, cbh])
ax_lbl.set_facecolor('#f5eef8')
ax_lbl.set_xlim(0, 1); ax_lbl.set_ylim(0, 1)
ax_lbl.axis('off')
ax_lbl.text(0.5, 0.5, 'Something\nin Frame',
            ha='center', va='center', fontsize=9,
            fontweight='bold', color='#1a252f',
            rotation=90, multialignment='center')

# ── Title ──────────────────────────────────────────────────────────────────────
fig.text(0.5, 0.998,
         'Ulua Beach SLIP Monitoring — Something in Frame',
         ha='center', va='top', fontsize=13,
         fontweight='bold', color='#1a252f')

out_png = f'{BASE}/SLIPs_something_in_frame_figure.png'
fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor='white')
print(f"Saved:\n  {out_png}")
