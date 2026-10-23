import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from PIL import Image
import numpy as np
import os

BASE = '/Users/corinnepickering/Desktop/Thode_lab/SLIPS/maui2026/Maui2026/SLIPs_figure_images'

# Cinderblock groups (in order as set up)
cinderblocks = [
    {'label': 'Cinderblock A\nCams 6 · 3 · 10', 'cams': [6, 3, 10]},
    {'label': 'Cinderblock B\nCams 4 · 2 · 11', 'cams': [4, 2, 11]},
    {'label': 'Cinderblock C\nCams 12 · 1 · 7',  'cams': [12, 1, 7]},
]

dates      = ['2026-03-29', '2026-04-13', '2026-04-19', '2026-04-27', '2026-05-06']
date_labels = ['Mar 29', 'Apr 13', 'Apr 19', 'Apr 27', 'May 6']
perspectives = ['inside', 'outside']
persp_labels = ['Inside\n(camera)', 'Outside\n(diver)']

# Colors for cinderblock section backgrounds
cb_colors = ['#e8f4f8', '#fef9e7', '#f0f8e8']
persp_colors = {'inside': '#d6eaf8', 'outside': '#fdebd0'}

# ── Layout ────────────────────────────────────────────────────────────────────
# 3 cinderblock sections stacked, each with 6 image rows (3 cams × 2 views)
# + 1 date header row at very top
# 5 image columns

n_cb   = 3
n_cams = 3
n_persp = 2
n_dates = 5

# Row structure (per cinderblock): 6 image rows + thin separator
# Total image rows: 18, plus top header
IMG_H = 1.5   # inches per image row
IMG_W = 2.2   # inches per image column
LABEL_W = 1.3 # inches for row labels
CB_LABEL_W = 0.5  # inches for cinderblock label column
HEADER_H = 0.55  # date header height
SEP_H = 0.25     # separator between cinderblocks

# Collect "something in frame" images before building figure
all_cams_ordered = [6, 3, 10, 4, 2, 11, 12, 1, 7]
in_water_imgs = []
in_air_imgs   = []
for _cam in all_cams_ordered:
    for _img in sorted(os.listdir(f"{BASE}/cam{_cam}/Something_in_frame_underwater") if os.path.isdir(f"{BASE}/cam{_cam}/Something_in_frame_underwater") else []):
        if _img.lower().endswith(('.jpg', '.jpeg', '.png')):
            in_water_imgs.append((_cam, f"{BASE}/cam{_cam}/Something_in_frame_underwater/{_img}"))
    for _img in sorted(os.listdir(f"{BASE}/cam{_cam}/Something_in_frame_inair") if os.path.isdir(f"{BASE}/cam{_cam}/Something_in_frame_inair") else []):
        if _img.lower().endswith(('.jpg', '.jpeg', '.png')):
            in_air_imgs.append((_cam, f"{BASE}/cam{_cam}/Something_in_frame_inair/{_img}"))
in_water_imgs = in_water_imgs[:n_dates]
in_air_imgs   = in_air_imgs[:n_dates]

NEW_SECTION_H = SEP_H + 2 * IMG_H  # separator + 2 rows

fig_w = CB_LABEL_W + LABEL_W + n_dates * IMG_W + 0.3
fig_h = HEADER_H + n_cb * (n_cams * n_persp * IMG_H + SEP_H) + NEW_SECTION_H + 0.3

fig = plt.figure(figsize=(fig_w, fig_h), dpi=150)
fig.patch.set_facecolor('white')

# ── Date headers ──────────────────────────────────────────────────────────────
header_top  = 1.0 - HEADER_H / fig_h
header_bot  = 1.0 - (HEADER_H + 0.05) / fig_h
left_start  = (CB_LABEL_W + LABEL_W) / fig_w

for di, dlabel in enumerate(date_labels):
    cx = left_start + (di + 0.5) * IMG_W / fig_w
    fig.text(cx, 1.0 - HEADER_H / 2 / fig_h,
             dlabel, ha='center', va='center',
             fontsize=11, fontweight='bold', color='#2c3e50')

# thin line under headers
line_y = 1.0 - HEADER_H / fig_h
fig.add_artist(plt.Line2D([left_start, 1.0], [line_y, line_y],
                           transform=fig.transFigure,
                           color='#95a5a6', linewidth=1.0))

# ── Images ────────────────────────────────────────────────────────────────────
running_y = HEADER_H + 0.1  # inches from top (increases downward)

for cb_idx, cb in enumerate(cinderblocks):
    cb_top_in = running_y  # inches from top of figure

    for cam_idx, cam in enumerate(cb['cams']):
        for pi, persp in enumerate(perspectives):
            row_in = running_y  # inches from top

            # Convert to axes coords (0=bottom, 1=top)
            y0 = 1.0 - (row_in + IMG_H) / fig_h
            y1 = 1.0 - row_in / fig_h
            h  = IMG_H / fig_h

            # ── Row label (perspective) ─────────────────────────────────────
            rx = (CB_LABEL_W) / fig_w
            rw = LABEL_W / fig_w
            ax_lbl = fig.add_axes([rx, y0, rw, h])
            ax_lbl.set_facecolor(persp_colors[persp])
            ax_lbl.set_xlim(0, 1); ax_lbl.set_ylim(0, 1)
            ax_lbl.axis('off')
            ax_lbl.text(0.55, 0.70, f'Cam {cam}',
                        ha='center', va='center', fontsize=9,
                        fontweight='bold', color='#2c3e50')
            ax_lbl.text(0.55, 0.32, persp_labels[pi],
                        ha='center', va='center', fontsize=7.5,
                        color='#555555')

            # ── Images ─────────────────────────────────────────────────────
            for di, date in enumerate(dates):
                x0 = (CB_LABEL_W + LABEL_W + di * IMG_W) / fig_w
                ax = fig.add_axes([x0, y0, IMG_W / fig_w, h])
                ax.set_facecolor('#cccccc')

                img_path = f"{BASE}/cam{cam}/{date}_{persp}.jpg"
                try:
                    img = Image.open(img_path)
                    # crop to 4:3 center
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
                except Exception as e:
                    ax.text(0.5, 0.5, 'N/A', ha='center', va='center',
                            fontsize=8, color='#888888')
                ax.axis('off')

                # thin border
                for spine in ax.spines.values():
                    spine.set_visible(True)
                    spine.set_linewidth(0.4)
                    spine.set_edgecolor('#aaaaaa')

            running_y += IMG_H

    # ── Cinderblock label (left column) ──────────────────────────────────────
    cb_bot_in = running_y
    cb_h_in   = cb_bot_in - cb_top_in

    cbx = 0.005
    cbw = CB_LABEL_W / fig_w - 0.005
    cby = 1.0 - cb_bot_in / fig_h
    cbh = cb_h_in / fig_h

    ax_cb = fig.add_axes([cbx, cby, cbw, cbh])
    ax_cb.set_facecolor(cb_colors[cb_idx])
    ax_cb.set_xlim(0, 1); ax_cb.set_ylim(0, 1)
    ax_cb.axis('off')
    ax_cb.text(0.5, 0.5, cb['label'],
               ha='center', va='center', fontsize=8.5,
               fontweight='bold', color='#1a252f',
               rotation=90, multialignment='center')

    # separator line between cinderblocks
    if cb_idx < n_cb - 1:
        sep_y = 1.0 - (running_y + SEP_H / 2) / fig_h
        fig.add_artist(plt.Line2D([0, 1], [sep_y, sep_y],
                                   transform=fig.transFigure,
                                   color='#7f8c8d', linewidth=1.5,
                                   linestyle='--'))
        running_y += SEP_H

# ── "Something in Frame" section ──────────────────────────────────────────────

# Separator before new section
sep_y = 1.0 - (running_y + SEP_H / 2) / fig_h
fig.add_artist(plt.Line2D([0, 1], [sep_y, sep_y],
                           transform=fig.transFigure,
                           color='#7f8c8d', linewidth=1.5,
                           linestyle='--'))
running_y += SEP_H

sif_row_colors = {'in_water': '#d5f5e3', 'in_air': '#fce4ec'}
sif_top_in = running_y

for row_key, row_title, row_sub, imgs in [
    ('in_water', 'In Water', 'something\nin frame', in_water_imgs),
    ('in_air',   'In Air',   'something\nin frame', in_air_imgs),
]:
    row_in = running_y
    y0 = 1.0 - (row_in + IMG_H) / fig_h
    h  = IMG_H / fig_h

    # Row label
    rx = CB_LABEL_W / fig_w
    rw = LABEL_W / fig_w
    ax_lbl = fig.add_axes([rx, y0, rw, h])
    ax_lbl.set_facecolor(sif_row_colors[row_key])
    ax_lbl.set_xlim(0, 1); ax_lbl.set_ylim(0, 1)
    ax_lbl.axis('off')
    ax_lbl.text(0.55, 0.70, row_title,
                ha='center', va='center', fontsize=9,
                fontweight='bold', color='#2c3e50')
    ax_lbl.text(0.55, 0.32, row_sub,
                ha='center', va='center', fontsize=7.5,
                color='#555555', multialignment='center')

    # Images
    for di in range(n_dates):
        x0 = (CB_LABEL_W + LABEL_W + di * IMG_W) / fig_w
        ax = fig.add_axes([x0, y0, IMG_W / fig_w, h])
        ax.set_facecolor('#cccccc')
        if di < len(imgs):
            cam_num, img_path = imgs[di]
            try:
                img = Image.open(img_path)
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
                ax.text(0.03, 0.05, f'Cam {cam_num}',
                        transform=ax.transAxes, fontsize=7, color='white',
                        bbox=dict(facecolor='black', alpha=0.5, pad=1, boxstyle='round'))
            except Exception:
                ax.text(0.5, 0.5, 'N/A', ha='center', va='center',
                        fontsize=8, color='#888888')
        else:
            ax.text(0.5, 0.5, '—', ha='center', va='center',
                    fontsize=12, color='#aaaaaa')
        ax.axis('off')
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(0.4)
            spine.set_edgecolor('#aaaaaa')

    running_y += IMG_H

# Section label (left column)
sif_bot_in = running_y
cbx = 0.005
cbw = CB_LABEL_W / fig_w - 0.005
cby = 1.0 - sif_bot_in / fig_h
cbh = (sif_bot_in - sif_top_in) / fig_h

ax_sif = fig.add_axes([cbx, cby, cbw, cbh])
ax_sif.set_facecolor('#f5eef8')
ax_sif.set_xlim(0, 1); ax_sif.set_ylim(0, 1)
ax_sif.axis('off')
ax_sif.text(0.5, 0.5, 'Something\nin Frame',
            ha='center', va='center', fontsize=8.5,
            fontweight='bold', color='#1a252f',
            rotation=90, multialignment='center')

# ── Title ─────────────────────────────────────────────────────────────────────
fig.text(0.5, 0.995, 'Ulua Beach SLIP Monitoring — Camera Views Over Time',
         ha='center', va='top', fontsize=13, fontweight='bold', color='#1a252f')

# ── Legend ────────────────────────────────────────────────────────────────────
inside_patch  = mpatches.Patch(color=persp_colors['inside'],  label='Inside (time-lapse camera)')
outside_patch = mpatches.Patch(color=persp_colors['outside'], label='Outside (diver photo)')
fig.legend(handles=[inside_patch, outside_patch],
           loc='lower right', bbox_to_anchor=(0.99, 0.002),
           fontsize=8, framealpha=0.9, edgecolor='#aaaaaa')

out_png = f'{BASE}/SLIPs_monitoring_figure.png'
fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor='white')
print(f"Saved:\n  {out_png}")
