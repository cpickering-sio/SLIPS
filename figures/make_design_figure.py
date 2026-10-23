#!/usr/bin/env python3
# make_design_figure.py  (stdlib only -> emits a to-scale vector SVG)
# Orthographic experimental-design figure for the SLIPS camera array.
# Edit the DIMENSIONS block, re-run: python3 make_design_figure.py
# Output: experimental_design.svg  (vector; import to PowerPoint -> Convert to Shape)
# ---------------------------------------------------------------------------

# ===== DIMENSIONS (edit these; all in feet/inches) ==========================
SCALE   = 100.0          # px per FOOT (drawing scale)
FRAME_L_FT   = 7.0       # overall frame length
CAM_N        = 12        # number of camera housings
CAM_SPACE_IN = 7.0       # center-to-center spacing  (ASSUMED from sketch)
MESH_H_IN    = 6.0       # mesh/grid panel height    (ASSUMED - confirm)
BEAM_W_IN    = 4.0       # rail cross-section width
BEAM_H_IN    = 2.0       # rail cross-section height (side-view thickness)
LEG_H_FT     = 3.0       # leg height
BASE_W_FT    = 3.0       # base footprint width (top plan)
CAM_LEN_IN   = 5.0       # housing length (along rail)
CAM_DIA_IN   = 3.0       # housing diameter
N_CLAMPS     = 4
# ============================================================================

IN = SCALE / 12.0
def ft(v): return v * SCALE
def inch(v): return v * IN
def f(x): return f"{x:.2f}"

# ---- colours ----
C_BEAM="#9c6b3f"; C_BEAM_E="#6e4a2b"; C_CAM="#f4f4f2"; C_CAM_E="#333333"
C_LENS="#c9d6e3"; C_MESH_E="#555555"; C_CLAMP="#d1372c"; C_DIM="#222222"
C_LEG="#444444"; C_BASE="#e9eef2"; C_TXT="#111111"; C_ACC="#2f6fb0"

svg=[]
def add(s): svg.append(s)
def rect(x,y,w,h,fill="none",stroke="none",sw=1,rx=0):
    return (f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" '
            f'rx="{f(rx)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def line(x1,y1,x2,y2,stroke=C_DIM,sw=1,dash=None):
    d=f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{stroke}" stroke-width="{sw}"{d}/>'
def text(x,y,s,size=13,anchor="middle",fill=C_TXT,weight="normal",italic=False):
    st=' font-style="italic"' if italic else ''
    return (f'<text x="{f(x)}" y="{f(y)}" font-family="Helvetica,Arial,sans-serif" '
            f'font-size="{size}" text-anchor="{anchor}" fill="{fill}" font-weight="{weight}"{st}>{s}</text>')
def arrow_r(x,y): return f'<polygon points="{f(x)},{f(y)} {f(x-7)},{f(y-3.5)} {f(x-7)},{f(y+3.5)}" fill="{C_DIM}"/>'
def arrow_l(x,y): return f'<polygon points="{f(x)},{f(y)} {f(x+7)},{f(y-3.5)} {f(x+7)},{f(y+3.5)}" fill="{C_DIM}"/>'
def arrow_d(x,y): return f'<polygon points="{f(x)},{f(y)} {f(x-3.5)},{f(y-7)} {f(x+3.5)},{f(y-7)}" fill="{C_DIM}"/>'
def arrow_u(x,y): return f'<polygon points="{f(x)},{f(y)} {f(x-3.5)},{f(y+7)} {f(x+3.5)},{f(y+7)}" fill="{C_DIM}"/>'
def dimh(x1,x2,y,label,size=13):
    out=[line(x1,y,x2,y,C_DIM,1),arrow_l(x1,y),arrow_r(x2,y),
         text((x1+x2)/2,y-6,label,size,weight="bold")]
    return "".join(out)
def dimv(y1,y2,x,label,size=13,side="right"):
    out=[line(x,y1,x,y2,C_DIM,1),arrow_u(x,y1),arrow_d(x,y2)]
    tx = x+8 if side=="right" else x-8
    anc= "start" if side=="right" else "end"
    out.append(text(tx,(y1+y2)/2+4,label,size,anchor=anc,weight="bold"))
    return "".join(out)

# ===================== LAYOUT =====================
W,H = 1060, 1160
AX0 = 160                    # structure left x
beam_top = 250
beam_len = ft(FRAME_L_FT)
beam_h   = inch(BEAM_H_IN)*2.0   # exaggerate thickness x2 for visibility at this scale
mesh_h   = inch(MESH_H_IN)
cam_l    = inch(CAM_LEN_IN); cam_h = inch(CAM_DIA_IN)
sp       = inch(CAM_SPACE_IN)
row_w    = (CAM_N-1)*sp
cx0      = AX0 + (beam_len-row_w)/2.0
leg_h    = ft(LEG_H_FT)
beam_bot = beam_top+beam_h

# ---- defs ----
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
add('<defs><pattern id="mesh" width="15" height="15" patternUnits="userSpaceOnUse">'
    f'<rect width="15" height="15" fill="white"/><rect x="2.5" y="2.5" width="7" height="7" fill="{C_MESH_E}"/>'
    '</pattern></defs>')
add(rect(0,0,W,H,fill="white"))

# ---- title ----
add(text(W/2,40,"Experimental design: SLIPS anti-fouling camera array",18,weight="bold"))
add(text(W/2,60,"Orthographic views, drawn to scale",12,italic=True,fill="#555"))

# ================= PANEL A: SIDE ELEVATION =================
add(text(AX0,110,"A.  Side elevation (front view)",14,anchor="start",weight="bold"))

# mesh panel (behind cameras)
add(rect(AX0,beam_top-mesh_h,beam_len,mesh_h,fill="url(#mesh)",stroke=C_MESH_E,sw=1))
# rail / beam
add(rect(AX0,beam_top,beam_len,beam_h,fill=C_BEAM,stroke=C_BEAM_E,sw=1.2))
# legs (2 ends) + feet
for lx in (AX0+inch(BEAM_H_IN), AX0+beam_len-inch(BEAM_H_IN)):
    add(rect(lx-inch(1),beam_bot,inch(2),leg_h,fill=C_LEG,stroke="#222",sw=1))
    add(rect(lx-inch(5),beam_bot+leg_h,inch(10),inch(2.5),fill=C_LEG,stroke="#222",sw=1,rx=2))
# cameras
for k in range(CAM_N):
    cx=cx0+k*sp
    add(rect(cx-cam_l/2,beam_top-cam_h,cam_l,cam_h,fill=C_CAM,stroke=C_CAM_E,sw=1.1,rx=cam_h/2))
    add(f'<ellipse cx="{f(cx+cam_l/2-4)}" cy="{f(beam_top-cam_h/2)}" rx="3.5" ry="{f(cam_h/2-3)}" fill="{C_LENS}" stroke="{C_CAM_E}" stroke-width="0.8"/>')
# clamps (red) under beam
for i in range(N_CLAMPS):
    cxx=AX0+beam_len*(0.12+0.76*i/(N_CLAMPS-1))
    add(rect(cxx-inch(0.9),beam_bot,inch(1.8),inch(3),fill=C_CLAMP,stroke="#7f1f18",sw=0.8,rx=1))
add(text(AX0+beam_len*0.12,beam_bot+inch(3)+14,"clamp (typ.)",11,fill=C_CLAMP,anchor="middle"))

# dimensions
add(dimh(AX0,AX0+beam_len,beam_top-mesh_h-28,f"{FRAME_L_FT:g} ft"))                 # overall length
add(dimv(beam_top-mesh_h,beam_top,AX0-22,f'{MESH_H_IN:g} in',side="left"))          # mesh height
add(dimh(cx0,cx0+sp,beam_top-cam_h-14,f'{CAM_SPACE_IN:g} in',size=11))              # spacing
add(dimv(beam_bot,beam_bot+leg_h,AX0+beam_len+34,f'{LEG_H_FT:g} ft'))              # leg height
add(text(cx0+row_w/2,beam_top-cam_h-26,f"{CAM_N} camera housings",11,italic=True,fill="#555"))

# ================= PANEL B: TOP PLAN =================
BY0=760
add(text(AX0,BY0-24,"B.  Top plan (looking down)",14,anchor="start",weight="bold"))
base_w=ft(BASE_W_FT)
# base footprint
add(rect(AX0,BY0,beam_len,base_w,fill=C_BASE,stroke="#9fb3c2",sw=1.2))
# central rail
rail_d=inch(BEAM_W_IN)
add(rect(AX0,BY0+base_w/2-rail_d/2,beam_len,rail_d,fill=C_BEAM,stroke=C_BEAM_E,sw=1))
# cameras (top view)
for k in range(CAM_N):
    cx=cx0+k*sp
    add(rect(cx-cam_l/2,BY0+base_w/2-cam_h/2,cam_l,cam_h,fill=C_CAM,stroke=C_CAM_E,sw=1,rx=3))
# corner feet
for fx in (AX0,AX0+beam_len):
    for fy in (BY0,BY0+base_w):
        add(rect(fx-inch(5),fy-inch(2.5),inch(10),inch(5),fill=C_LEG,stroke="#222",sw=1,rx=2))
# dims
add(dimh(AX0,AX0+beam_len,BY0+base_w+34,f"{FRAME_L_FT:g} ft"))
add(dimv(BY0,BY0+base_w,AX0-22,f"{BASE_W_FT:g} ft",side="left"))

# ================= LEGEND + SCALE BAR =================
lx,ly=AX0+beam_len+60,250
add(text(lx,ly-16,"Legend",12,anchor="start",weight="bold"))
items=[(C_BEAM,"Rail (4x2 in)"),(C_CAM,"Camera housing (x12)"),
       ("url(#mesh)","Mesh panel"),(C_CLAMP,"Clamp"),(C_LEG,"Leg / foot")]
for i,(col,lab) in enumerate(items):
    yy=ly+i*22
    add(rect(lx,yy,16,12,fill=col,stroke="#444",sw=0.8,rx=2))
    add(text(lx+22,yy+11,lab,11,anchor="start"))
# scale bar (1 ft)
sbx,sby=lx,ly+len(items)*22+30
add(line(sbx,sby,sbx+ft(1),sby,C_TXT,2))
add(line(sbx,sby-4,sbx,sby+4,C_TXT,2)); add(line(sbx+ft(1),sby-4,sbx+ft(1),sby+4,C_TXT,2))
add(text(sbx+ft(0.5),sby+16,"1 ft",11))
add(text(sbx,sby+34,f"scale: 1 ft = {SCALE:g} px",10,anchor="start",fill="#777"))

add('</svg>')
out="experimental_design.svg"
with open(out,"w") as fh: fh.write("\n".join(svg))
print("wrote",out)
