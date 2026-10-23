#!/usr/bin/env python3
# make_experimental_layout.py  (stdlib only -> to-scale vector SVG, METRIC)
# Orthographic experimental-design figure: SLIPS camera array + checkerboard target.
# Edit DIMENSIONS, re-run: python3 make_experimental_layout.py
# Output: experimental_layout.svg  (import to PowerPoint -> Convert to Shape)
# ---------------------------------------------------------------------------

# ===== DIMENSIONS (metres) ==================================================
SCALE        = 320.0      # px per METRE
TARGET_L     = 2.28       # checkerboard target length (= array length)
TARGET_H     = 0.20       # checkerboard target height
TARGET_W     = 0.30       # checkerboard target width (depth, seen in plan)
CAM_N        = 12
EDGE_INSET   = 0.1778     # end cameras set in from each edge
PORT_TARGET  = 0.30       # optical port -> target distance
CAM_ELEV     = 0.040      # cameras raised off mounting board
STRUCT_H     = 0.9144     # structure height
CAM_LEN      = 0.09       # housing length (schematic; not given)
CAM_DIA      = 0.06       # housing diameter (schematic; not given)
N_CLAMPS     = 4
# NOTE: text said "0.08 m apart", but target length 2.28 m + 0.1778 m edge insets
# imply ~0.175 m spacing for 12 cameras. Pitch is derived below from L + insets.
# ============================================================================

def m(v): return v*SCALE
def f(x): return f"{x:.2f}"

PITCH = (TARGET_L - 2*EDGE_INSET)/(CAM_N-1)   # ~0.175 m

C_BOARD="#9c6b3f"; C_BOARD_E="#6e4a2b"; C_CAM="#f4f4f2"; C_CAM_E="#333"
C_LENS="#c9d6e3"; C_CLAMP="#d1372c"; C_DIM="#222"; C_LEG="#444"
C_TGT_E="#333"; C_TXT="#111"

svg=[]
def add(s): svg.append(s)
def rect(x,y,w,h,fill="none",stroke="none",sw=1,rx=0):
    return (f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(rx)}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def line(x1,y1,x2,y2,stroke=C_DIM,sw=1,dash=None):
    d=f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{stroke}" stroke-width="{sw}"{d}/>'
def text(x,y,s,size=13,anchor="middle",fill=C_TXT,weight="normal",italic=False):
    st=' font-style="italic"' if italic else ''
    return (f'<text x="{f(x)}" y="{f(y)}" font-family="Helvetica,Arial,sans-serif" '
            f'font-size="{size}" text-anchor="{anchor}" fill="{fill}" font-weight="{weight}"{st}>{s}</text>')
def aR(x,y): return f'<polygon points="{f(x)},{f(y)} {f(x-7)},{f(y-3.5)} {f(x-7)},{f(y+3.5)}" fill="{C_DIM}"/>'
def aL(x,y): return f'<polygon points="{f(x)},{f(y)} {f(x+7)},{f(y-3.5)} {f(x+7)},{f(y+3.5)}" fill="{C_DIM}"/>'
def aD(x,y): return f'<polygon points="{f(x)},{f(y)} {f(x-3.5)},{f(y-7)} {f(x+3.5)},{f(y-7)}" fill="{C_DIM}"/>'
def aU(x,y): return f'<polygon points="{f(x)},{f(y)} {f(x-3.5)},{f(y+7)} {f(x+3.5)},{f(y+7)}" fill="{C_DIM}"/>'
def dimh(x1,x2,y,label,size=13):
    return "".join([line(x1,y,x2,y),aL(x1,y),aR(x2,y),text((x1+x2)/2,y-6,label,size,weight="bold")])
def dimv(y1,y2,x,label,size=13,side="right"):
    tx=x+8 if side=="right" else x-8; anc="start" if side=="right" else "end"
    return "".join([line(x,y1,x,y2),aU(x,y1),aD(x,y2),text(tx,(y1+y2)/2+4,label,size,anchor=anc,weight="bold")])

# ===== layout =====
W,H=1180,1010
AX0=175
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
add('<defs><pattern id="check" width="34" height="34" patternUnits="userSpaceOnUse">'
    '<rect width="34" height="34" fill="white"/><rect width="17" height="17" fill="#1a1a1a"/>'
    '<rect x="17" y="17" width="17" height="17" fill="#1a1a1a"/></pattern></defs>')
add(rect(0,0,W,H,fill="white"))
add(text(W/2,38,"Experimental design: SLIPS anti-fouling camera array",18,weight="bold"))
add(text(W/2,58,"Orthographic views, drawn to scale  -  W of SIO Pier, ~9.19 m depth, heading ~280 deg",11,italic=True,fill="#555"))

# ---------- PANEL A: FRONT ELEVATION (facing the target) ----------
add(text(AX0,100,"A.  Front elevation (camera view toward target)",14,anchor="start",weight="bold"))
tgt_l=m(TARGET_L); tgt_h=m(TARGET_H)
tgt_top=200
# checkerboard target (behind cameras)
add(rect(AX0,tgt_top,tgt_l,tgt_h,fill="url(#check)",stroke=C_TGT_E,sw=1.2))
# mounting board (rail) just below target centre line
board_y=tgt_top+tgt_h-m(0.02); board_h=m(CAM_ELEV)
add(rect(AX0,board_y,tgt_l,board_h,fill=C_BOARD,stroke=C_BOARD_E,sw=1.2))
# cameras on board
cam_l=m(CAM_LEN); cam_d=m(CAM_DIA); pitch=m(PITCH); inset=m(EDGE_INSET)
for k in range(CAM_N):
    cx=AX0+inset+k*pitch
    add(rect(cx-cam_l/2,board_y-cam_d,cam_l,cam_d,fill=C_CAM,stroke=C_CAM_E,sw=1.1,rx=cam_d/2))
    add(f'<ellipse cx="{f(cx)}" cy="{f(board_y-cam_d/2)}" rx="{f(cam_l/2-3)}" ry="2.6" fill="{C_LENS}" stroke="{C_CAM_E}" stroke-width="0.7"/>')
# legs + feet
leg_h=m(STRUCT_H)
for lx in (AX0+inset, AX0+tgt_l-inset):
    add(rect(lx-m(0.015),board_y+board_h,m(0.03),leg_h,fill=C_LEG,stroke="#222",sw=1))
    add(rect(lx-m(0.07),board_y+board_h+leg_h,m(0.14),m(0.035),fill=C_LEG,stroke="#222",sw=1,rx=2))
# clamps (red) under board
for i in range(N_CLAMPS):
    cxx=AX0+tgt_l*(0.12+0.76*i/(N_CLAMPS-1))
    add(rect(cxx-m(0.012),board_y+board_h,m(0.024),m(0.05),fill=C_CLAMP,stroke="#7f1f18",sw=0.8,rx=1))
# dims
add(dimh(AX0,AX0+tgt_l,tgt_top-26,f"{TARGET_L:g} m"))
add(dimv(tgt_top,tgt_top+tgt_h,AX0-24,f"{TARGET_H:.2f} m",side="left"))
add(dimh(AX0+inset,AX0+inset+pitch,board_y-cam_d-12,f"{PITCH:.3f} m",size=11))
add(dimh(AX0,AX0+inset,tgt_top+tgt_h+22,f"{EDGE_INSET:.4f} m",size=11))
add(dimv(board_y+board_h,board_y+board_h+leg_h,AX0+tgt_l+34,f"{STRUCT_H:.4f} m"))
add(text(AX0+tgt_l/2,board_y-cam_d-24,f"{CAM_N} camera housings",11,italic=True,fill="#555"))
add(text(AX0+tgt_l/2,board_y+board_h+m(0.05)+16,f"cameras raised {CAM_ELEV:.3f} m off board; clamps (red)",10,italic=True,fill="#555"))

# ---------- PANEL B: PLAN VIEW (looking down) ----------
BY0=690
add(text(AX0,BY0-22,"B.  Plan view (looking down)",14,anchor="start",weight="bold"))
tgt_w=m(TARGET_W); gap=m(PORT_TARGET)
# target bar (depth = width)
add(rect(AX0,BY0,tgt_l,tgt_w,fill="url(#check)",stroke=C_TGT_E,sw=1.2))
# camera row, gap below target
cam_row_y=BY0+tgt_w+gap
for k in range(CAM_N):
    cx=AX0+inset+k*pitch
    add(rect(cx-cam_l/2,cam_row_y,cam_l,cam_d,fill=C_CAM,stroke=C_CAM_E,sw=1,rx=3))
# port->target distance dim
add(dimv(BY0+tgt_w,cam_row_y,AX0-24,f"{PORT_TARGET:.2f} m",side="left"))
add(text(AX0-70,(BY0+tgt_w+cam_row_y)/2+16,"port-target",10,anchor="middle",fill="#555",italic=True))
# target width dim (right)
add(dimv(BY0,BY0+tgt_w,AX0+tgt_l+34,f"{TARGET_W:.2f} m"))
add(text(AX0+tgt_l+42,BY0+tgt_w/2-6,"target width",10,anchor="start",fill="#555",italic=True))
# length dim
add(dimh(AX0,AX0+tgt_l,cam_row_y+cam_d+28,f"{TARGET_L:g} m"))
add(text(AX0+tgt_l/2,BY0+tgt_w/2+4,"checkerboard resolution target",11,weight="bold",fill="#fff"))

# ---------- legend + scale bar ----------
lx,ly=AX0+tgt_l+70,210
add(text(lx,ly-16,"Legend",12,anchor="start",weight="bold"))
items=[(C_BOARD,"Mounting board"),(C_CAM,"Camera housing (x12)"),
       ("url(#check)","Checkerboard target"),(C_CLAMP,"Hose clamp"),(C_LEG,"Leg / foot")]
for i,(col,lab) in enumerate(items):
    yy=ly+i*22
    add(rect(lx,yy,16,12,fill=col,stroke="#444",sw=0.8,rx=2))
    add(text(lx+22,yy+11,lab,11,anchor="start"))
sbx,sby=lx,ly+len(items)*22+26
add(line(sbx,sby,sbx+m(0.5),sby,C_TXT,2))
add(line(sbx,sby-4,sbx,sby+4,C_TXT,2)); add(line(sbx+m(0.5),sby-4,sbx+m(0.5),sby+4,C_TXT,2))
add(text(sbx+m(0.25),sby+15,"0.5 m",11))
add(text(sbx,sby+32,f"scale: 1 m = {SCALE:g} px",10,anchor="start",fill="#777"))

add('</svg>')
with open("experimental_layout.svg","w") as fh: fh.write("\n".join(svg))
print(f"wrote experimental_layout.svg  (derived camera pitch = {PITCH:.4f} m)")
