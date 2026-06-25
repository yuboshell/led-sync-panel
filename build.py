#!/usr/bin/env python3
"""Build the illustrated LED-sync-panel design doc (single self-contained HTML
with inline SVG diagrams + downloaded product photos)."""
import xml.etree.ElementTree as ET

OUT = "/Users/yubo/github/led-sync-panel/index.html"

# palette (clean / monochrome + one functional accent for "lit" LEDs)
AMBER = "#b45309"   # lit LED / highlight (matches the site copper)
OFF   = "#dcdcdc"   # unlit LED
INK   = "#1f2937"
MUTE  = "#6b7280"
LINE  = "#9ca3af"
PANEL = "#111827"
# functional part-tag colours (BOM <-> diagram projection)
C_MCU="#0d9488"; C_SHIFT="#2563eb"; C_LED="#dc2626"; C_RES="#b45309"
C_PSU="#16a34a"; C_BOARD="#7c3aed"; C_BB="#475569"

def wrap(inner, w, h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="100%" style="max-width:{w}px;height:auto" '
            f'font-family="Helvetica Neue, Helvetica, Arial, sans-serif">{inner}</svg>')

def txt(x, y, s, size=13, fill=INK, anchor="start", weight="normal"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}">{s}</text>')

# ---------- Diagram 1: geometry (Option C) ----------
def svg_geometry():
    px, py = 285, 165
    s  = [txt(165, 70, "Large flat LED time-code panel", 13, INK, "middle", "bold")]
    # panel body
    s.append(f'<rect x="40" y="82" width="250" height="160" rx="8" fill="{PANEL}"/>')
    # 16-bit gray bar (schematic), a few lit
    lit_bar = {1, 2, 5, 8, 11, 14}
    for i in range(16):
        c = AMBER if i in lit_bar else "#3b4252"
        s.append(f'<rect x="{55+i*14}" y="120" width="9" height="22" rx="2" fill="{c}"/>')
    s.append(txt(60, 113, "16-bit Gray bar", 9, "#cbd5e1"))
    # coarse spatial row
    for i in range(10):
        c = AMBER if i == 3 else "#3b4252"
        s.append(f'<circle cx="{66+i*20}" cy="200" r="6" fill="{c}"/>')
    s.append(txt(60, 224, "coarse row", 9, "#cbd5e1"))
    # cameras facing the panel
    cams = [(385,82),(475,66),(565,78),(652,106),
            (375,152),(478,144),(582,142),(676,154),
            (408,224),(516,244),(628,226)]
    for (x, y) in cams:
        s.append(f'<line x1="{x-16}" y1="{y}" x2="{px}" y2="{py}" stroke="{LINE}" stroke-width="1" opacity="0.4"/>')
    for (x, y) in cams:
        s.append(f'<rect x="{x-16}" y="{y-11}" width="32" height="22" rx="4" fill="{INK}"/>')
        s.append(f'<circle cx="{x-16}" cy="{y}" r="5" fill="{AMBER}"/>')
    s.append(txt(534, 300, "11 Pixel 7 cameras, placed to face the panel", 12, MUTE, "middle"))
    return wrap("".join(s), 720, 320)

# ---------- Diagram 2: encoding layout ----------
def svg_encoding():
    s = [txt(20, 28, "Readout layout (one flat panel)", 14, INK, "start", "bold")]
    bits = [0,1,1,0,1,0,0,1,1,1,0,0,1,0,1,1]   # sample
    for i in range(16):
        x = 40 + i*36
        c = AMBER if bits[i] else OFF
        s.append(f'<rect x="{x}" y="56" width="28" height="28" rx="3" fill="{c}" stroke="{LINE}"/>')
    # bracket + labels fine->coarse
    s.append(f'<line x1="40" y1="98" x2="616" y2="98" stroke="{MUTE}" stroke-width="1"/>')
    s.append(f'<polygon points="616,98 608,94 608,102" fill="{MUTE}"/>')
    s.append(txt(40, 114, "LSB  ·  fine = τ", 11, MUTE))
    s.append(txt(616, 114, "MSB  ·  coarse = τ·2¹⁵", 11, MUTE, "end"))
    # parity LED set apart
    s.append(f'<rect x="664" y="56" width="28" height="28" rx="3" fill="{OFF}" stroke="{LINE}" stroke-dasharray="3 2"/>')
    s.append(txt(678, 114, "parity", 11, MUTE, "middle"))
    # optional coarse spatial row
    s.append(txt(20, 150, "coarse spatial row (×W slower — redundant, human-readable cross-check)", 12, INK))
    for i in range(10):
        c = AMBER if i == 6 else OFF
        s.append(f'<circle cx="{56+i*36}" cy="178" r="11" fill="{c}" stroke="{LINE}"/>')
    s.append(txt(20, 214, "decode (in software): threshold LEDs → Gray→binary → count → t = count × τ", 12, INK))
    return wrap("".join(s), 720, 232)

# ---------- Diagram 3: vernier disambiguation ----------
def svg_vernier():
    s = [txt(20, 26, "Why a coarse scale is mandatory (the vernier)", 14, INK, "start", "bold")]
    def minipanel(x0, label, fine_lit, coarse_lit, note):
        g = [f'<rect x="{x0}" y="44" width="300" height="118" rx="6" fill="#f8fafc" stroke="{LINE}"/>']
        g.append(txt(x0+12, 64, label, 12, INK, "start", "bold"))
        g.append(txt(x0+12, 84, "fine", 10, MUTE))
        for i in range(10):
            c = AMBER if i == fine_lit else OFF
            g.append(f'<circle cx="{x0+60+i*22}" cy="80" r="7" fill="{c}" stroke="{LINE}"/>')
        g.append(txt(x0+12, 124, "coarse", 10, MUTE))
        for i in range(10):
            c = AMBER if i == coarse_lit else OFF
            g.append(f'<circle cx="{x0+60+i*22}" cy="120" r="7" fill="{c}" stroke="{LINE}"/>')
        g.append(txt(x0+12, 150, note, 10, MUTE))
        return "".join(g)
    s.append(minipanel(20,  "Camera A frame", 5, 2, "fine=5  coarse=2"))
    s.append(minipanel(400, "Camera B frame", 5, 7, "fine=5  coarse=7"))
    s.append(txt(20, 196, "Same fine reading (5) on both, yet they are far apart: true offset = (7−2) × fine-range.", 12.5, INK))
    s.append(txt(20, 216, "Without the coarse scale an offset of one fine-wrap period reads as ZERO. Make the", 12.5, INK))
    s.append(txt(20, 234, "unambiguous range exceed the largest possible offset. In binary, the high bits ARE the coarse scale.", 12.5, INK))
    return wrap("".join(s), 720, 250)

# ---------- Diagram 6: physical build (breadboard driver + LED panel) ----------
def svg_layout():
    s = [txt(20, 24, "Physical build: the driver sits on the breadboard, the 10 mm LEDs live on the panel", 13.5, INK, "start", "bold")]
    # 5 V supply
    s.append(f'<rect x="40" y="92" width="78" height="26" rx="4" fill="#fff" stroke="{C_PSU}"/>')
    s.append(txt(79, 109, "5 V (USB)", 9.5, C_PSU, "middle"))
    # breadboard body
    bx, by, bw, bh = 40, 150, 300, 150
    s.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="9" fill="#f5f5f3" stroke="{C_BB}"/>')
    s.append(txt(bx + bw/2, by + bh + 16, "breadboard — driver only", 10, C_BB, "middle"))
    hx = bx + 20
    def hrow(y, n=20):
        return "".join(f'<circle cx="{hx+i*13}" cy="{y}" r="1.7" fill="#cfcfcf"/>' for i in range(n))
    s.append(f'<line x1="{hx}" y1="{by+13}" x2="{hx+19*13}" y2="{by+13}" stroke="{C_BB}" stroke-width="1.1"/>')
    s.append(hrow(by+24)); s.append(hrow(by+bh-24))
    s.append(f'<line x1="{hx}" y1="{by+bh-13}" x2="{hx+19*13}" y2="{by+bh-13}" stroke="{C_BB}" stroke-width="1.1"/>')
    # 74HC595 DIP
    dipx, dipy, dipw = hx+14, by+66, 11*13
    s.append(f'<rect x="{dipx}" y="{dipy}" width="{dipw}" height="30" rx="3" fill="{C_SHIFT}"/>')
    s.append(f'<circle cx="{dipx+8}" cy="{dipy+15}" r="3" fill="none" stroke="#666"/>')
    s.append(txt(dipx+dipw/2, dipy+13, "shift register", 8.5, "#e5e7eb", "middle", "bold"))
    s.append(txt(dipx+dipw/2, dipy+24, "74HC595", 7, "#dbeafe", "middle"))
    # resistors row
    for i in range(8):
        rx = dipx + 10 + i*16
        s.append(f'<rect x="{rx}" y="{dipy-20}" width="6" height="13" rx="2" fill="#d6b06a" stroke="#a07d3a" stroke-width="0.5"/>')
    s.append(txt(dipx+dipw/2, dipy-26, "8 × current-limit resistors", 8.5, C_RES, "middle"))
    # Teensy
    s.append(f'<rect x="{bx+8}" y="{by+bh-44}" width="66" height="28" rx="4" fill="{C_MCU}"/>')
    s.append(txt(bx+41, by+bh-26, "microcontroller", 7.5, "#e6fffb", "middle", "bold"))
    s.append(f'<path d="M{bx+74},{by+bh-34} L{dipx+10},{dipy+30}" fill="none" stroke="{INK}" stroke-width="1"/>')
    s.append(txt(bx+78, by+bh-36, "SER·SRCLK·RCLK", 8, MUTE, "start"))
    s.append(f'<path d="M79,118 L79,{by+13} L{hx},{by+13}" fill="none" stroke="{C_PSU}" stroke-width="1.1"/>')
    # ribbon to panel
    for i in range(8):
        s.append(f'<path d="M{dipx+13+i*16},{dipy-20} C360,{160+i*6} 430,{110+i*20} 470,{120+i*20}" fill="none" stroke="{C_BB}" stroke-width="1"/>')
    s.append(txt(405, 138, "jumper wires", 9, C_BB, "middle"))
    # LED panel
    px, py, pw, ph = 470, 84, 408, 250
    s.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10" fill="{PANEL}" stroke="{C_BOARD}" stroke-width="2"/>')
    s.append(txt(px+pw/2, py-8, "LED display panel — every camera films this", 10.5, C_BOARD, "middle"))
    lit = {1,2,5,8,11,14}
    dx, dp, ry = px+30, 21, py+74
    s.append(txt(dx, ry-20, "16-bit Gray bar", 9, "#cbd5e1", "start"))
    for i in range(16):
        cx = dx+i*dp
        c = C_LED if i in lit else "#7f1d1d"
        s.append(f'<circle cx="{cx}" cy="{ry}" r="8" fill="{c}"/>')
        s.append(f'<circle cx="{cx-2.4}" cy="{ry-2.4}" r="2" fill="#fff" opacity="0.45"/>')
    pcx = dx+16*dp+8
    s.append(f'<circle cx="{pcx}" cy="{ry}" r="8" fill="#7f1d1d" stroke="#cbd5e1" stroke-dasharray="2 2"/>')
    s.append(txt(pcx, ry+22, "parity", 8.5, "#cbd5e1", "middle"))
    cry = py+158
    s.append(txt(dx, cry-22, "coarse row", 9, "#cbd5e1", "start"))
    for i in range(10):
        cx = dx+i*36
        c = C_LED if i==6 else "#7f1d1d"
        s.append(f'<circle cx="{cx}" cy="{cry}" r="8" fill="{c}"/>')
        s.append(f'<circle cx="{cx-2.4}" cy="{cry-2.4}" r="2" fill="#fff" opacity="0.45"/>')
    scx = dx+9*36
    s.append(f'<line x1="{scx-8}" y1="{cry+24}" x2="{scx+8}" y2="{cry+24}" stroke="#cbd5e1" stroke-width="1"/>')
    s.append(f'<line x1="{scx-8}" y1="{cry+21}" x2="{scx-8}" y2="{cry+27}" stroke="#cbd5e1" stroke-width="1"/>')
    s.append(f'<line x1="{scx+8}" y1="{cry+21}" x2="{scx+8}" y2="{cry+27}" stroke="#cbd5e1" stroke-width="1"/>')
    s.append(txt(scx, cry+38, "10 mm", 8.5, "#cbd5e1", "middle"))
    # callout
    return wrap("".join(s), 900, 350)

# ---------- Diagram: bring-up wiring (breadboard, hole-level control wiring) ----------
def svg_wiring():
    # Bring-up across BOTH MB-104 strips: Pico + 595 on the LEFT strip, 8-LED comb on the RIGHT. Exact holes.
    P=17.0; HOLE=6.0; R0=1; RN=33; LX=120; TY=92
    RED="#dc2626"; BLUE="#2563eb"; HOLEC="#39393c"; GRN="#22c55e"; ORA="#ea580c"; PUR="#7c3aed"; CYN="#0891b2"; TAN="#d6b06a"
    seq=[("LEFT+","rail"),("LEFT-","rail"),
         ("La","s"),("Lb","s"),("Lc","s"),("Ld","s"),("Le","s"),("|L","gap"),("Lf","s"),("Lg","s"),("Lh","s"),("Li","s"),("Lj","s"),
         ("MIDa+","rail"),("MIDa-","rail"),("MIDb+","rail"),("MIDb-","rail"),
         ("Ra","s"),("Rb","s"),("Rc","s"),("Rd","s"),("Re","s"),("|R","gap"),("Rf","s"),("Rg","s"),("Rh","s"),("Ri","s"),("Rj","s"),
         ("RIGHT+","rail"),("RIGHT-","rail")]
    X={}; x=LX
    for nm,k in seq:
        if k=="gap": x+=P*0.85; continue
        X[nm]=x; x+=P
        if nm in ("LEFT-","Lj","MIDb-","Rj"): x+=P*0.55
    GR=x; W=int(GR+30); H=int(TY+(RN-R0)*P+56)
    def cx(c): return X[c]
    def cy(r): return TY+(r-R0)*P
    s=[]
    def rect(x,y,w,h,r,fill,ex=""): s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" fill="{fill}" {ex}/>')
    def txt(x,y,t,sz,fill,a="middle",w="normal"): s.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{sz}" fill="{fill}" text-anchor="{a}" font-weight="{w}">{t}</text>')
    def line(x1,y1,x2,y2,c,w=2.2): s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="{w}" stroke-linecap="round"/>')
    def J(c1,r1,c2,r2,clr,w=2.0):
        x1,y1,x2,y2=cx(c1),cy(r1),cx(c2),cy(r2); mx=(x1+x2)/2
        s.append(f'<path d="M{x1:.1f},{y1:.1f} C{mx:.1f},{y1:.1f} {mx:.1f},{y2:.1f} {x2:.1f},{y2:.1f}" fill="none" stroke="{clr}" stroke-width="{w}" stroke-linecap="round"/>')
    def hole(c,r,fill=HOLEC): s.append(f'<rect x="{cx(c)-HOLE/2:.1f}" y="{cy(r)-HOLE/2:.1f}" width="{HOLE}" height="{HOLE}" rx="1.3" fill="{fill}"/>')
    gtop=cy(R0)-9; gbot=cy(RN)+9
    rect(5,5,W-10,H-10,15,"#1d1d1d")
    for grp in [("La","Lj"),("Ra","Rj")]:
        rect(cx(grp[0])-8,gtop,(cx(grp[1])-cx(grp[0]))+16,gbot-gtop,5,"#f3f1ea")
    railtint={"LEFT+":"#f7dede","LEFT-":"#dee5f7","MIDa+":"#f7dede","MIDa-":"#dee5f7","MIDb+":"#f7dede","MIDb-":"#dee5f7","RIGHT+":"#f7dede","RIGHT-":"#dee5f7"}
    for rl,t in railtint.items():
        rect(cx(rl)-6,gtop,12,gbot-gtop,4,t)   # light polarity tint, NO line — the rail is an inherent bus, not a wire you add
    for gcx in [(cx("Le")+cx("Lf"))/2,(cx("Re")+cx("Rf"))/2]:
        rect(gcx-6,gtop+2,12,(gbot-2)-(gtop+2),2,"#d9d6cc")
    allcols=[c for c,k in seq if k in ("s","rail")]
    for c in allcols:
        for r in range(R0,RN+1): hole(c,r)
    for c in allcols:
        lab=c[-1] if (c[0] in "LR" and len(c)==2) else ("+" if c.endswith("+") else "–")
        cl=RED if c.endswith("+") else (BLUE if c.endswith("-") else "#d6dde5")
        txt(cx(c),gtop-5,lab,8.5,cl,"middle","bold")
    txt(cx("MIDa+"),gtop-18,"3V3",7,RED,"middle","bold"); txt(cx("MIDa-"),gtop-18,"GND",7,BLUE,"middle","bold")
    txt(cx("RIGHT-"),gtop-18,"GND",7,BLUE,"middle","bold")
    for r in range(R0,RN+1):
        if r==1 or r%5==0: txt(LX-26,cy(r)+3,str(r),8,"#cbd5e1","middle")
    px1,px2=cx("Lc"),cx("Lh"); py1,py2=cy(1),cy(20)
    rect(px1-8,py1-8,(px2-px1)+16,(py2-py1)+16,6,"#0b6b5e",'opacity="0.92"')
    txt((px1+px2)/2,py1-8+13,"Pico (USB ↑)",8,"#dffaf4","middle","bold")
    txt((px1+px2)/2,(py1+py2)/2,"PICO",13,"#0d4a41","middle","bold")
    for nm,c,r,cl in [("3V3","Lh",5,RED),("GP19","Lh",16,PUR),("GP18","Lh",17,CYN),("GND","Lh",18,BLUE),("GP17","Lh",19,ORA)]:
        hole(c,r,cl); txt(cx(c)+8,cy(r)+3,nm,6,cl,"start","bold")
    qx1,qx2=cx("Le"),cx("Lf"); qy1,qy2=cy(24),cy(31)
    rect(qx1-7,qy1-7,(qx2-qx1)+14,(qy2-qy1)+14,3,"#23252b")
    txt((qx1+qx2)/2,(qy1+qy2)/2,"595",9,"#9fb0c0","middle","bold")
    # orientation: notch DOWN (row-31 end); pin 1 (QB) at bottom-right (Lf31)
    s.append(f'<circle cx="{(qx1+qx2)/2:.1f}" cy="{qy2+7:.1f}" r="5" fill="#f3f1ea"/>')
    s.append(f'<circle cx="{cx("Lf")-3:.1f}" cy="{cy(31)-3:.1f}" r="1.7" fill="#ffd27f"/>')
    txt((qx1+qx2)/2,qy2+16,"notch ↓  (pin 1 = QB)",5,"#e0a0a0","middle","bold")
    p595={"GNDp":("Lf",24),"QH":("Lf",25),"QG":("Lf",26),"QF":("Lf",27),"QE":("Lf",28),"QD":("Lf",29),"QC":("Lf",30),"QB":("Lf",31),
          "QHp":("Le",24),"MR":("Le",25),"SRCLK":("Le",26),"RCLK":("Le",27),"OE":("Le",28),"SER":("Le",29),"QA":("Le",30),"VCC":("Le",31)}
    for nm,(c,r) in p595.items():
        hole(c,r,"#c9a36a")
        if c=="Le":
            lab={"VCC":"VCC","QA":"QA","SER":"SER","OE":"OE","RCLK":"RCK","SRCLK":"SCK","MR":"MR","QHp":"QH'"}.get(nm,nm)
            txt(cx(c)-7,cy(r)+2.5,lab,5,"#9aa3ad","end")
    # power & signal jumpers — each plugs into a FREE hole of the pin's 5-hole group (never the pin hole), shortest path
    J("Lj",5,"MIDa+",5,RED); J("Lj",18,"MIDa-",18,BLUE)             # Pico 3V3 / GND -> central rails (free f-j edge hole)
    J("La",31,"LEFT+",31,RED); J("La",25,"LEFT+",25,RED)           # 595 VCC(Le31), MR(Le25) -> + (left rail, free a-e edge hole)
    J("La",28,"LEFT-",28,BLUE)                                      # 595 OE(Le28) -> - (left rail)
    J("Lj",24,"MIDa-",24,BLUE)                                      # 595 GND(8)(Lf24) -> - (central rail)
    line(cx("LEFT+"),cy(32),cx("MIDa+"),cy(32),RED,1.8)            # tie + bus -> left rail, BELOW the chip (clear)
    line(cx("LEFT-"),cy(33),cx("MIDa-"),cy(33),BLUE,1.8)          # tie - bus -> left rail
    line(cx("MIDa-"),cy(33),cx("RIGHT-"),cy(33),BLUE,1.8)         # tie - bus -> right rail for the cathodes
    def sig(tap,r0,arow,dcol,r1,clr):   # route a signal AROUND the chips: down beside the Pico, across the clear gap (rows 21-23), down to the control tap
        x0=cx(tap); xa=cx(dcol); ya=cy(arow)
        line(x0,cy(r0),x0,ya,clr,1.8); line(x0,ya,xa,ya,clr,1.8); line(xa,ya,xa,cy(r1),clr,1.8)
    sig("Li",16,21,"Ld",29,PUR)   # GP19 -> SER (Le29)
    sig("Lj",17,22,"Lc",26,CYN)   # GP18 -> SRCLK (Le26)
    sig("Li",19,23,"Lb",27,ORA)   # GP17 -> RCLK (Le27)
    leds=[("QB","Lf",31,31),("QC","Lf",30,30),("QD","Lf",29,29),("QE","Lf",28,28),
          ("QF","Lf",27,27),("QG","Lf",26,26),("QH","Lf",25,25),("QA","Le",30,24)]
    for nm,oc,orow,lr in leds:
        ay=cy(lr)
        src="Lj" if oc=="Lf" else "Ld"          # plug the ribbon into a FREE edge hole of the output's group, not the pin
        J(src,orow,"Ra",lr,TAN,1.7)
        line(cx("Rc"),ay,cx("Rg"),ay,"#9a8050",1.1)
        rect((cx("Rc")+cx("Rg"))/2-7,ay-2.5,14,5,2,TAN,'stroke="#a07d3a" stroke-width="0.5"')
        ah=cx("Rh"); rk=cx("RIGHT-"); dm=ah+0.6*(rk-ah)
        line(ah,ay,dm-4,ay,"#9aa0a6",1.5)
        line(dm+4,ay,rk,ay,"#9aa0a6",1.5)
        s.append(f'<circle cx="{dm:.1f}" cy="{ay:.1f}" r="4.6" fill="{GRN}" stroke="#15803d" stroke-width="0.7"/>')
        hole("Rh",lr,"#2a2a2a"); txt(ah,ay-7,"+",6.5,"#15803d","middle","bold")
        txt(rk,ay-7,"–",6.5,BLUE,"middle","bold")
        txt(dm,ay+10,nm,5,"#9aa0a6","middle")
    txt((cx("Rc")+cx("RIGHT-"))/2,cy(24)-12,"LEDs: long lead (+) → hole Rh,  short lead (–) → GND rail",6,GRN,"middle","bold")
    txt(W/2,24,"Bring-up across both strips — Pico + 595 (left), 8-LED comb (right)",12,"#ffffff","middle","bold")
    txt(W/2,40,"595 outputs face right, so each LED sits across from its output (rows 24–31)",8.5,"#aab2bd","middle")
    leg=[("3V3",RED),("GND",BLUE),("SER",PUR),("SRCLK",CYN),("RCLK",ORA),("output→LED",TAN)]
    lx=40; ly=H-14
    for lab,col in leg:
        line(lx,ly,lx+18,ly,col,3); txt(lx+22,ly+3.2,lab,8.5,"#d6dde5","start"); lx+=34+6.2*len(lab)
    return wrap("".join(s), W, H)

def svg_blink():
    # Simplest possible circuit: Pico GP15 -> 240Ω -> LED -> one jumper -> GND. One strip, no rails.
    P=18.0; HOLE=6.5; R0=1; RN=27; LX=78; TY=66
    ORA="#ea580c"; BLUE="#2563eb"; GRN="#22c55e"; TAN="#d6b06a"; HOLEC="#39393c"
    cols=list("abcde")+["|"]+list("fghij")
    X={}; x=LX
    for c in cols:
        if c=="|": x+=P*0.9; continue
        X[c]=x; x+=P
    GR=x; W=int(GR+70); H=int(TY+(RN-R0)*P+44)
    def cx(c): return X[c]
    def cy(r): return TY+(r-R0)*P
    s=[]
    def rect(x,y,w,h,r,fill,ex=""): s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" fill="{fill}" {ex}/>')
    def txt(x,y,t,sz,fill,a="middle",w="normal"): s.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{sz}" fill="{fill}" text-anchor="{a}" font-weight="{w}">{t}</text>')
    def line(x1,y1,x2,y2,c,w=2.4): s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="{w}" stroke-linecap="round"/>')
    def hole(c,r,fill=HOLEC): s.append(f'<rect x="{cx(c)-HOLE/2:.1f}" y="{cy(r)-HOLE/2:.1f}" width="{HOLE}" height="{HOLE}" rx="1.4" fill="{fill}"/>')
    gtop=cy(R0)-9; gbot=cy(RN)+9
    rect(5,5,W-10,H-10,14,"#1d1d1d")
    rect(cx("a")-9,gtop,(cx("j")-cx("a"))+18,gbot-gtop,5,"#f3f1ea")
    gxc=(cx("e")+cx("f"))/2; rect(gxc-6,gtop+2,12,(gbot-2)-(gtop+2),2,"#d9d6cc")
    for c in "abcdefghij":
        for r in range(R0,RN+1): hole(c,r)
    for c in "abcdefghij": txt(cx(c),gtop-5,c,9,"#d6dde5","middle","bold")
    for r in range(R0,RN+1):
        if r==1 or r%5==0: txt(LX-24,cy(r)+3,str(r),8.5,"#cbd5e1","middle")
    # Pico (cols c-h, rows 1-20, USB up)
    px1,px2=cx("c"),cx("h"); py1,py2=cy(1),cy(20)
    rect(px1-8,py1-8,(px2-px1)+16,(py2-py1)+16,6,"#0b6b5e",'opacity="0.92"')
    txt((px1+px2)/2,py1-8+14,"Pico (USB ↑)",9,"#dffaf4","middle","bold")
    txt((px1+px2)/2,(py1+py2)/2,"PICO",15,"#0d4a41","middle","bold")
    hole("c",18,BLUE); txt(cx("c")-10,cy(18)+3,"GND",7,BLUE,"end","bold")
    hole("c",20,ORA); txt(cx("c")-10,cy(20)+3,"GP15",7,ORA,"end","bold")
    # 240Ω resistor: Lb20 (GP15 group) -> Lb23
    line(cx("b"),cy(20),cx("b"),cy(23),"#9a8050",1.4)
    rect(cx("b")-3.2,(cy(20)+cy(23))/2-8,6.4,16,2,TAN,'stroke="#a07d3a" stroke-width="0.6"')
    txt(cx("b")+10,(cy(20)+cy(23))/2+2,"240Ω",6.5,TAN,"start","bold")
    # LED: anode (long,+) Lc23 -> cathode (short,-) Lc25
    ax,ay=cx("c"),cy(23); ky=cy(25); dm=ay+0.62*(ky-ay)
    line(ax,ay,ax,dm-4,"#9aa0a6",1.5)            # long anode lead (Lc23 -> dome)
    line(ax,dm+4,ax,ky,"#9aa0a6",1.5)            # short cathode lead
    s.append(f'<circle cx="{ax:.1f}" cy="{dm:.1f}" r="5.6" fill="{GRN}" stroke="#15803d" stroke-width="0.7"/>')
    txt(ax+10,ay+3,"+ long leg",6.5,GRN,"start","bold")
    txt(ax+10,ky+3,"– short leg",6.5,BLUE,"start","bold")
    # the ONE jumper: cathode group (La25) -> GND group (La18)
    x0=cx("a")
    s.append(f'<path d="M{x0:.1f},{cy(25):.1f} C{x0-16:.1f},{cy(25):.1f} {x0-16:.1f},{cy(18):.1f} {x0:.1f},{cy(18):.1f}" fill="none" stroke="{BLUE}" stroke-width="2.6" stroke-linecap="round"/>')
    txt(x0-20,(cy(18)+cy(25))/2,"1 jumper",6.2,"#bcd",a="middle",w="bold")
    txt(x0-20,(cy(18)+cy(25))/2+9,"→ GND",6.2,"#bcd","middle")
    # title + flow
    txt(W/2,24,"Step 0 — the simplest blink (Pico + resistor + LED + 1 jumper)",11,"#ffffff","middle","bold")
    txt(W/2,40,"GP15 → 240Ω → LED → GND   (toggle GP15 to blink)",9,"#aab2bd","middle")
    return wrap("".join(s), W, H)

def svg_wiring_b():
    # OPTION B (revised): Pico LEFT; 595 on the RIGHT strip RAISED to sit beside the Pico's GP17-19,
    # so the 3 control wires are short near-horizontal hops. Comb spread out below. No two leads share a hole.
    P=17.0; HOLE=6.0; R0=1; RN=40; LX=120; TY=92
    RED="#dc2626"; BLUE="#2563eb"; HOLEC="#39393c"; GRN="#22c55e"; ORA="#ea580c"; PUR="#7c3aed"; CYN="#0891b2"; TAN="#d6b06a"
    seq=[("LEFT+","rail"),("LEFT-","rail"),
         ("La","s"),("Lb","s"),("Lc","s"),("Ld","s"),("Le","s"),("|L","gap"),("Lf","s"),("Lg","s"),("Lh","s"),("Li","s"),("Lj","s"),
         ("MIDa+","rail"),("MIDa-","rail"),("MIDb+","rail"),("MIDb-","rail"),
         ("Ra","s"),("Rb","s"),("Rc","s"),("Rd","s"),("Re","s"),("|R","gap"),("Rf","s"),("Rg","s"),("Rh","s"),("Ri","s"),("Rj","s"),
         ("RIGHT+","rail"),("RIGHT-","rail")]
    X={}; x=LX
    for nm,k in seq:
        if k=="gap": x+=P*0.85; continue
        X[nm]=x; x+=P
        if nm in ("LEFT-","Lj","MIDb-","Rj"): x+=P*0.55
    GR=x; W=int(GR+30); H=int(TY+(RN-R0)*P+56)
    def cx(c): return X[c]
    def cy(r): return TY+(r-R0)*P
    s=[]
    def rect(x,y,w,h,r,fill,ex=""): s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" fill="{fill}" {ex}/>')
    def txt(x,y,t,sz,fill,a="middle",w="normal"): s.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{sz}" fill="{fill}" text-anchor="{a}" font-weight="{w}">{t}</text>')
    def line(x1,y1,x2,y2,c,w=2.2): s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="{w}" stroke-linecap="round"/>')
    def J(c1,r1,c2,r2,clr,w=2.0):
        x1,y1,x2,y2=cx(c1),cy(r1),cx(c2),cy(r2); mx=(x1+x2)/2
        s.append(f'<path d="M{x1:.1f},{y1:.1f} C{mx:.1f},{y1:.1f} {mx:.1f},{y2:.1f} {x2:.1f},{y2:.1f}" fill="none" stroke="{clr}" stroke-width="{w}" stroke-linecap="round"/>')
    def hole(c,r,fill=HOLEC): s.append(f'<rect x="{cx(c)-HOLE/2:.1f}" y="{cy(r)-HOLE/2:.1f}" width="{HOLE}" height="{HOLE}" rx="1.3" fill="{fill}"/>')
    gtop=cy(R0)-9; gbot=cy(RN)+9
    rect(5,5,W-10,H-10,15,"#1d1d1d")
    for grp in [("La","Lj"),("Ra","Rj")]:
        rect(cx(grp[0])-8,gtop,(cx(grp[1])-cx(grp[0]))+16,gbot-gtop,5,"#f3f1ea")
    railtint={"LEFT+":"#f7dede","LEFT-":"#dee5f7","MIDa+":"#f7dede","MIDa-":"#dee5f7","MIDb+":"#f7dede","MIDb-":"#dee5f7","RIGHT+":"#f7dede","RIGHT-":"#dee5f7"}
    for rl,t in railtint.items():
        rect(cx(rl)-6,gtop,12,gbot-gtop,4,t)
    for gcx in [(cx("Le")+cx("Lf"))/2,(cx("Re")+cx("Rf"))/2]:
        rect(gcx-6,gtop+2,12,(gbot-2)-(gtop+2),2,"#d9d6cc")
    allcols=[c for c,k in seq if k in ("s","rail")]
    for c in allcols:
        for r in range(R0,RN+1): hole(c,r)
    for c in allcols:
        lab=c[-1] if (c[0] in "LR" and len(c)==2) else ("+" if c.endswith("+") else "–")
        cl=RED if c.endswith("+") else (BLUE if c.endswith("-") else "#d6dde5")
        txt(cx(c),gtop-5,lab,8.5,cl,"middle","bold")
    txt(cx("MIDa+"),gtop-18,"3V3",7,RED,"middle","bold"); txt(cx("MIDa-"),gtop-18,"GND",7,BLUE,"middle","bold")
    txt(cx("MIDb+"),gtop-18,"3V3",7,RED,"middle","bold"); txt(cx("MIDb-"),gtop-18,"GND",7,BLUE,"middle","bold")
    for r in range(R0,RN+1):
        if r==1 or r%5==0: txt(LX-26,cy(r)+3,str(r),8,"#cbd5e1","middle")
    # Pico — left strip (unchanged)
    px1,px2=cx("Lc"),cx("Lh"); py1,py2=cy(1),cy(20)
    rect(px1-8,py1-8,(px2-px1)+16,(py2-py1)+16,6,"#0b6b5e",'opacity="0.92"')
    txt((px1+px2)/2,py1-8+13,"Pico (USB ↑)",8,"#dffaf4","middle","bold")
    txt((px1+px2)/2,(py1+py2)/2,"PICO",13,"#0d4a41","middle","bold")
    for nm,c,r,cl in [("3V3","Lh",5,RED),("GP19","Lh",16,PUR),("GP18","Lh",17,CYN),("GND","Lh",18,BLUE),("GP17","Lh",19,ORA)]:
        hole(c,r,cl); txt(cx(c)+8,cy(r)+3,nm,6,cl,"start","bold")
    # 595 — RIGHT strip, rows 14-21 (control SER@16 lines up with GP19@16). notch-up: control on Re, outputs QB-QH on Rf.
    qx1,qx2=cx("Re"),cx("Rf"); qy1,qy2=cy(14),cy(21)
    rect(qx1-7,qy1-7,(qx2-qx1)+14,(qy2-qy1)+14,3,"#23252b")
    txt((qx1+qx2)/2,(qy1+qy2)/2,"595",9,"#9fb0c0","middle","bold")
    s.append(f'<circle cx="{(qx1+qx2)/2:.1f}" cy="{qy1-7:.1f}" r="5" fill="#f3f1ea"/>')   # notch UP (row-14 end)
    p595={"QB":("Rf",14),"QC":("Rf",15),"QD":("Rf",16),"QE":("Rf",17),"QF":("Rf",18),"QG":("Rf",19),"QH":("Rf",20),"GNDp":("Rf",21),
          "VCC":("Re",14),"QA":("Re",15),"SER":("Re",16),"OE":("Re",17),"RCLK":("Re",18),"SRCLK":("Re",19),"MR":("Re",20),"QHp":("Re",21)}
    for nm,(c,r) in p595.items():
        hole(c,r,"#c9a36a")
        if c=="Re":
            lab={"VCC":"VCC","QA":"QA","SER":"SER","OE":"OE","RCLK":"RCK","SRCLK":"SCK","MR":"MR","QHp":"QH'"}.get(nm,nm)
            txt(cx(c)-7,cy(r)+2.5,lab,5,"#9aa3ad","end")
    # ---- power ----
    J("Lj",5,"MIDa+",5,RED); J("Lj",18,"MIDa-",18,BLUE)
    line(cx("MIDa+"),cy(3),cx("MIDb+"),cy(3),RED,1.8)
    line(cx("MIDa-"),cy(2),cx("MIDb-"),cy(2),BLUE,1.8)
    J("Ra",14,"MIDb+",14,RED); J("Ra",20,"MIDb+",20,RED)     # VCC(Re14), MR(Re20) -> + rail
    J("Ra",17,"MIDb-",17,BLUE)                                # OE(Re17) -> - rail
    J("Rg",21,"RIGHT-",21,BLUE); line(cx("RIGHT-"),cy(23),cx("MIDb-"),cy(23),BLUE,1.6)  # GND(8)(Rf21) -> right rail, tied to - bus
    # ---- 3 control wires: Pico (GP) -> 595 control (Re). Short, near-horizontal. ----
    J("Li",16,"Rd",16,PUR)   # GP19 -> SER (Re16)   aligned
    J("Li",17,"Rd",19,CYN)   # GP18 -> SRCLK (Re19)
    J("Lj",19,"Rd",18,ORA)   # GP17 -> RCLK (Re18)
    # ---- outputs -> comb (spread, rows 24-39). output jumper lands at Rh; resistor sits at Rg (different hole). ----
    leds=[("QB","Rf",14,24),("QC","Rf",15,26),("QD","Rf",16,28),("QE","Rf",17,30),
          ("QF","Rf",18,32),("QG","Rf",19,34),("QH","Rf",20,36),("QA","Re",15,38)]
    for nm,oc,orow,lr in leds:
        ay=cy(lr)
        tap="Ri" if oc=="Rf" else "Rd"             # free hole in the output's group
        J(tap,orow,"Rh",lr,TAN,1.7)                # output -> comb input at Rh
        line(cx("Rc"),ay,cx("Rg"),ay,"#9a8050",1.1)   # 240Ω bridges the channel (Rg<->Rc) — separate hole from Rh
        rect((cx("Rc")+cx("Rg"))/2-7,ay-2.5,14,5,2,TAN,'stroke="#a07d3a" stroke-width="0.5"')
        an=cx("Rb"); ka=cx("MIDb-"); dm=an+0.5*(ka-an)
        line(an,ay,dm-4,ay,"#9aa0a6",1.5); line(dm+4,ay,ka,ay,"#9aa0a6",1.5)
        s.append(f'<circle cx="{dm:.1f}" cy="{ay:.1f}" r="4.6" fill="{GRN}" stroke="#15803d" stroke-width="0.7"/>')
        txt(an,ay-7,"+",6.5,"#15803d","middle","bold"); txt(ka,ay-7,"–",6.5,BLUE,"middle","bold")
        txt(dm,ay+10,nm,5,"#9aa0a6","middle")
    txt(W/2,24,"OPTION B (revised) — 595 raised beside GP17–19; comb spread below; no shared holes",11.5,"#ffffff","middle","bold")
    txt(W/2,40,"3 control wires are short horizontal hops; the 8 outputs run down the right side to the comb",8.5,"#aab2bd","middle")
    leg=[("3V3",RED),("GND",BLUE),("SER",PUR),("SRCLK",CYN),("RCLK",ORA),("output→LED",TAN)]
    lx=40; ly=H-14
    for lab,col in leg:
        line(lx,ly,lx+18,ly,col,3); txt(lx+22,ly+3.2,lab,8.5,"#d6dde5","start"); lx+=34+6.2*len(lab)
    return wrap("".join(s), W, H)

def svg_schematic():
    # Academic circuit schematic: Pico -> 74HC595 -> 8x (R + LED) -> GND. Logical, not physical.
    W,H=820,560
    INK="#1f2937"; RED="#c0392b"; BLU="#1f5fb4"; GRN="#1f9d55"; MUT="#6b7280"
    s=[]
    def rect(x,y,w,h,fill="none",stroke=INK,sw=1.4,rx=2): s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    def ln(x1,y1,x2,y2,c=INK,w=1.4): s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="{w}" stroke-linecap="round"/>')
    def txt(x,y,t,sz=11,fill=INK,a="middle",w="normal",fam="sans-serif"): s.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{sz}" fill="{fill}" text-anchor="{a}" font-weight="{w}" font-family="{fam}">{t}</text>')
    def dot(x,y,c=INK,r=2.6): s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{c}"/>')
    def res(x,y,w=26,lab=""):   # horizontal resistor (IEC box) centred at (x,y)
        rect(x-w/2,y-5,w,10,"#fff",INK,1.3,1);
        if lab: txt(x,y-9,lab,8.5,MUT)
    def led(x,y,sz=9):          # LED pointing DOWN (anode top -> cathode bar bottom)
        s.append(f'<path d="M{x-sz:.1f},{y-sz:.1f} L{x+sz:.1f},{y-sz:.1f} L{x:.1f},{y+sz*0.4:.1f} Z" fill="#fde8e8" stroke="{INK}" stroke-width="1.3"/>')
        ln(x-sz,y+sz*0.4,x+sz,y+sz*0.4,INK,1.6)
        for dx in (4,9):
            ln(x+sz*0.6+dx,y-sz*0.7,x+sz*0.6+dx+4,y-sz*0.7-4,GRN,1.1); ln(x+sz*0.6+dx+4,y-sz*0.7-4,x+sz*0.6+dx+1.5,y-sz*0.7-3.2,GRN,1.1)
    def gndsym(x,y):            # ground symbol
        ln(x,y,x,y+7); ln(x-8,y+7,x+8,y+7,INK,1.6); ln(x-5,y+11,x+5,y+11,INK,1.4); ln(x-2.5,y+14.5,x+2.5,y+14.5,INK,1.2)
    rect(6,6,W-12,H-12,"#ffffff","#d0d4da",1.2,10)
    txt(W/2,28,"Circuit schematic — Raspberry Pi Pico → 74HC595 shift register → 8 LEDs",13,INK,"middle","bold")
    txt(W/2,44,"3.3 V logic · serial in (SER), shift clock (SRCLK), latch (RCLK) · outputs Qₐ–Qₕ each through 240 Ω to an LED",9.5,MUT)
    # power rails
    yV=70; yG=H-40
    ln(70,yV,W-30,yV,RED,1.8); txt(70,yV-6,"+3.3 V",10,RED,"start","bold")
    ln(70,yG,W-30,yG,INK,1.8); txt(70,yG+16,"GND",10,INK,"start","bold"); gndsym(70,yG)
    # ---- Pico ----
    px,py,pw,ph=70,120,120,300
    rect(px,py,pw,ph,"#eef6f4"); txt(px+pw/2,py+18,"Raspberry",10,INK,"middle","bold"); txt(px+pw/2,py+31,"Pi Pico",10,INK,"middle","bold")
    txt(px+pw/2,py+ph-10,"(USB-powered)",8,MUT)
    pico={"3V3":150,"GP19":210,"GP18":250,"GP17":290,"GND":360}
    for nm,y in pico.items():
        ln(px+pw,y,px+pw+16,y); txt(px+pw-5,y-4,nm,8.5,INK,"end","bold")
    # ---- 595 ----
    qx,qy,qw,qh=320,120,120,300
    rect(qx,qy,qw,qh,"#eef2fb"); txt(qx+qw/2,qy+16,"74HC595",10,INK,"middle","bold"); txt(qx+qw/2,qy+28,"shift register",8,MUT)
    Lpin={"VCC":150,"SER":210,"SRCLK":250,"RCLK":290,"OE":330,"SRCLR":360,"GND":395}
    for nm,y in Lpin.items():
        ln(qx-16,y,qx,y); txt(qx+5,y-4,nm,8,INK,"start","bold")
    Rpin={}
    for i,nm in enumerate(["QA","QB","QC","QD","QE","QF","QG","QH"]):
        y=150+i*30; Rpin[nm]=y; ln(qx+qw,y,qx+qw+16,y); txt(qx+qw-5,y-4,nm,8,INK,"end","bold")
    # ---- power wiring ----
    # 3V3 -> Pico 3V3, 595 VCC, 595 SRCLR(MR active-low: tie high = never reset)
    ln(px+pw+16,150,px+pw+16,yV); dot(px+pw+16,yV,RED)
    ln(qx-16,150,qx-40,150); ln(qx-40,150,qx-40,yV); dot(qx-40,yV,RED); ln(qx-16,150,qx-40,150)   # VCC up to 3V3
    ln(qx-16,360,qx-52,360); ln(qx-52,360,qx-52,yV); dot(qx-52,yV,RED)                              # SRCLR(MR) -> 3V3
    txt(qx-52,355,"MR",7,MUT,"middle")
    # GND -> Pico GND, 595 GND, 595 OE (active-low: tie low = outputs enabled)
    ln(px+pw+16,360,px+pw+16,yG); dot(px+pw+16,yG,INK)
    ln(qx-16,395,qx-30,395); ln(qx-30,395,qx-30,yG); dot(qx-30,yG,INK)                               # 595 GND -> GND
    ln(qx-16,330,qx-64,330); ln(qx-64,330,qx-64,yG); dot(qx-64,yG,INK); txt(qx-64,325,"OE",7,MUT,"middle")  # OE -> GND
    # decoupling cap across VCC-GND (near the chip)
    cx0=qx-78
    ln(cx0,158,cx0,yV); dot(cx0,yV,RED) if False else ln(cx0,yV,cx0,yV)
    ln(cx0,yV,cx0,170); ln(cx0-7,170,cx0+7,170,INK,1.6); ln(cx0-7,176,cx0+7,176,INK,1.6); ln(cx0,176,cx0,yG); dot(cx0,yG,INK)
    txt(cx0-10,173,"0.1µF",7,MUT,"end")
    # ---- control wiring: GP -> SER/SRCLK/RCLK ----
    for g,sgnl,clr in [("GP19","SER",RED),("GP18","SRCLK",BLU),("GP17","RCLK",GRN)]:
        ya=pico[g]; yb=Lpin[sgnl]; xa=px+pw+16; xb=qx-16
        midx=(xa+xb)/2 + (6 if sgnl=="SRCLK" else (-6 if sgnl=="RCLK" else 0))
        ln(xa,ya,midx,ya,INK,1.5); ln(midx,ya,midx,yb,INK,1.5); ln(midx,yb,xb,yb,INK,1.5)
    txt((px+pw+qx)/2,128,"3 control wires",8,MUT)
    # ---- outputs: QA..QH -> 240Ω -> LED -> GND ----
    for nm in ["QA","QB","QC","QD","QE","QF","QG","QH"]:
        y=Rpin[nm]; x0=qx+qw+16; xr=x0+40; xl=x0+95
        ln(x0,y,xr-13,y); res(xr,y,26,"240Ω" if nm=="QA" else "")
        ln(xr+13,y,xl,y); led(xl,y); ln(xl,y+8,xl,yG);
        if nm=="QA": dot(xl,yG,INK)
        else: dot(xl,yG,INK)
        txt(xl+16,y+2,nm,8,MUT,"start")
    txt((qx+qw+16+qx+qw+16+95)/2+20,128,"8 × ( 240 Ω + LED )",8,MUT)
    return wrap("".join(s), W, H)

DIAGRAMS = {
    "geometry": svg_geometry(),
    "encoding": svg_encoding(),
    "vernier":  svg_vernier(),
    "layout":   svg_layout(),
    "wiring":   svg_wiring(),
    "wiring_b": svg_wiring_b(),
    "schematic": svg_schematic(),
    "blink":    svg_blink(),
}

# validate every SVG before writing the page
for name, svg in DIAGRAMS.items():
    ET.fromstring(svg)
    print(f"SVG ok: {name} ({len(svg)} bytes)")

CSS = """
:root{--ink:#1f2937;--mute:#6b7280;--line:#e5e7eb;--accent:#b45309;}
*{box-sizing:border-box}
body{font-family:-apple-system,'Helvetica Neue',Helvetica,Arial,sans-serif;color:var(--ink);
 line-height:1.6;max-width:880px;margin:0 auto;padding:48px 24px 96px;background:#fff}
h1{font-size:30px;margin:0 0 4px;letter-spacing:-.01em}
h2{font-size:21px;margin:46px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--line)}
h3{font-size:15px;margin:26px 0 6px;color:#374151}
.meta{color:var(--mute);font-size:13px;margin-bottom:8px}
.lead{font-size:16px;color:#374151}
figure{margin:20px 0;text-align:center}
figcaption{color:var(--mute);font-size:12.5px;margin-top:6px}
table{border-collapse:collapse;width:100%;font-size:14px;margin:14px 0}
th,td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}
th{background:#f9fafb;font-weight:600}
code{background:#f3f4f6;padding:1px 5px;border-radius:4px;font-size:13px}
a{color:#0f4c81}
.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:18px;margin:18px 0}
.card{border:1px solid var(--line);border-radius:8px;padding:12px;text-align:center}
.card img{width:100%;height:130px;object-fit:contain}
.card .name{font-weight:600;font-size:13.5px;margin-top:8px}
.card .price{color:var(--accent);font-weight:600;font-size:13px}
.card .role{color:var(--mute);font-size:12px}
.note{background:#fffbeb;border:1px solid #fcd34d;border-radius:8px;padding:10px 14px;font-size:13.5px}
.k{color:var(--mute);font-size:13px}
ul{margin:6px 0 6px 0}
.slide{border:1px solid var(--line);border-radius:8px;max-width:860px;margin:20px auto;padding:18px 26px;display:flex;flex-direction:column;background:#fff}
.slide h3{margin:0 0 10px;padding:0;border:none;text-align:center;font-size:18px;color:var(--ink)}
.slide-body{display:flex;flex-direction:column;align-items:center;gap:18px}
.slide-fig{width:100%;max-width:820px}
.slide-fig svg{width:100%;height:auto}
.slide-bom{width:100%;max-width:660px}
.slide-bom table{width:100%;border-collapse:collapse;font-size:12px;margin:0}
.slide-bom th,.slide-bom td{border:none;border-bottom:1px solid var(--line);padding:4px 5px;text-align:left}
.slide-bom td{vertical-align:middle}
.slide-bom th:nth-child(3),.slide-bom td:nth-child(3){text-align:center}
.slide-bom th:last-child,.slide-bom td:last-child{text-align:right;white-space:nowrap}
.slide-bom td.th{width:100px;padding:5px 4px}
.slide-bom td.th img{height:52px;width:92px;object-fit:contain;display:block;margin:0 auto;border:1px solid var(--line);border-radius:4px}
.slide-bom td.th2{width:84px}
.slide-bom td.th2 img{height:34px;width:38px;object-fit:cover;display:inline-block;margin:1px;border:1px solid var(--line);border-radius:3px}
.slide-bom .tot td{border-top:2px solid var(--ink);border-bottom:none;font-weight:700}
.slide-bom .shot{color:var(--accent);text-decoration:none;font-size:11px;white-space:nowrap}
.slide-bom .shot:hover{text-decoration:underline}
.card .ours{margin-top:7px;font-size:11.5px;line-height:1.7}
.card .ours a{color:var(--accent);text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:2px 9px;white-space:nowrap;display:inline-block}
.card .ours a:hover{background:#f1f5f9}
"""

def card(img, name, price, role, href, ours=None):
    """ours: optional (url, label) for a second link to a photo we took ourselves."""
    ours_html = ''
    if ours:
        ours_url, ours_label = ours
        ours_html = (f'<div class="ours"><a href="{ours_url}" target="_blank">'
                     f'&#128247;&nbsp;{ours_label}</a></div>')
    return (f'<div class="card"><a href="{href}" target="_blank">'
            f'<img src="assets/{img}" alt="{name}"></a>'
            f'<div class="name">{name}</div><div class="price">{price}</div>'
            f'<div class="role">{role}</div>{ours_html}</div>')

P = []  # page body parts
P.append('<h1>Multi-camera sync evaluation: a large flat LED time-code panel</h1>')
P.append('<div class="meta">DIY design plan &middot; updated 2026-06-17 &middot; working draft &middot; '
         'step-time 200&nbsp;µs, driver 74HC595, sweep encoding (Gray-bar upgrade), 2-camera same-row bring-up (sim-validated) &middot; 11&times;Pixel&nbsp;7 / Argus rig</div>')
P.append('<p class="k"><b>Reader&rsquo;s map:</b> <b>build guide first</b> (wire the first light-up, just below) &middot; '
         'then &sect;1 what this tool is for &middot; &sect;2 the order list &middot; &sect;3 the driver choice + exact parts &middot; '
         '&sect;4&ndash;&sect;9 the design rationale.</p>')
P.append('<h2>The circuit &mdash; academic schematic</h2>')
P.append('<p class="k">The logical circuit, independent of the breadboard: the Pico clocks a byte into the 595 over three control lines (<b>SER</b> data, <b>SRCLK</b> shift clock, <b>RCLK</b> latch); the chip latches the byte to its eight parallel outputs; each output drives an LED through a <b>240&nbsp;&Omega;</b> resistor to ground. <b>OE</b> tied low keeps the outputs enabled, <b>MR&nbsp;(SRCLR)</b> tied high prevents reset, and a <b>0.1&nbsp;&micro;F</b> cap decouples VCC.</p>')
P.append(f'<figure>{DIAGRAMS["schematic"]}<figcaption><b>Figure. Circuit schematic.</b> Pico &rarr; 74HC595 &rarr; 8&times;(240&nbsp;&Omega; + LED) &mdash; the &ldquo;science&rdquo; the breadboard figures below realise physically.</figcaption></figure>')
P.append('<h2 style="color:#f59e0b">Layout experiment &mdash; 595 on the left vs. the right (temporary)</h2>')
P.append('<p class="k">Two physical layouts of that same circuit &mdash; we&rsquo;ll keep whichever reads cleaner, then delete this section. '
         '<b>Option&nbsp;A</b> stacks the Pico + 595 on the left and runs the eight outputs across the middle as one parallel ribbon. '
         '<b>Option&nbsp;B (revised)</b> raises the 595 onto the right strip <i>beside the Pico&rsquo;s GP17&ndash;19</i>, so the 3 control wires become short horizontal hops and the outputs stay local on the right, running down to a comb spread out below. '
         'Either way, <b>QA</b> is the one output that must bridge the chip (the 595&rsquo;s 7+1 pinout split).</p>')
P.append(f'<figure>{DIAGRAMS["wiring"]}<figcaption><b>Option A (current) &mdash; 595 on the LEFT strip.</b> Pico + 595 stacked on the left; the eight outputs cross the centre rails as a parallel ribbon to the comb on the right.</figcaption></figure>')
P.append(f'<figure>{DIAGRAMS["wiring_b"]}<figcaption><b>Option B (revised) &mdash; 595 raised beside GP17&ndash;19, comb spread below.</b> The 3 control wires are short, near-horizontal hops (GP19&rarr;SER lines up exactly); the 8 outputs run down the right side to the spread-out comb; every jumper and resistor sits in its own hole.</figcaption></figure>')
P.append('<h2>Step 0 &mdash; blink one LED (the simplest possible test)</h2>')
P.append('<p class="k">Before the 595 panel, prove the whole chain with the <b>smallest possible circuit</b>: the Pico drives '
         '<b>one</b> LED through <b>one</b> resistor, with <b>one</b> jumper to ground. If it blinks, your Pico, toolchain, and '
         'breadboard wiring are all good &mdash; then move on to the 595 below.</p>')
P.append(f'<figure>{DIAGRAMS["blink"]}<figcaption><b>Figure 0. Simplest blink.</b> '
         '<b>GP15</b>&nbsp;(pin&nbsp;20) &rarr; <b>240&nbsp;&Omega;</b> resistor &rarr; LED <b>long leg (+)</b>; LED <b>short leg (&ndash;)</b> &rarr; '
         'one jumper &rarr; a Pico <b>GND</b> pin. The firmware just toggles GP15 high/low to blink it.</figcaption></figure>')
P.append('<table>'
         '<tr><th>#</th><th>From (hole)</th><th>To (hole)</th><th>Why</th></tr>'
         '<tr><td>1</td><td><b>240&nbsp;&Omega; resistor</b> &mdash; into GP15&rsquo;s row <code>Lb20</code></td><td><code>Lb23</code></td><td>current limit (~4&ndash;5&nbsp;mA)</td></tr>'
         '<tr><td>2</td><td><b>LED</b> long leg&nbsp;(+) <code>Lc23</code></td><td>short leg&nbsp;(&ndash;) <code>Lc25</code></td><td>anode to the resistor, cathode toward ground</td></tr>'
         '<tr><td>3</td><td><b>one jumper</b> <code>La25</code> (cathode row)</td><td><code>La18</code> (GND pin&rsquo;s row)</td><td>completes the circuit to GND</td></tr>'
         '</table>')
P.append('<p class="k"><b>Firmware</b> (C/C++ SDK, <code>firmware/blink/main.c</code>) &mdash; toggle GP15 twice a second:</p>')
P.append('<pre style="background:#0f172a;color:#e2e8f0;padding:11px 13px;border-radius:8px;overflow-x:auto;font-size:12.5px;line-height:1.5">'
         '#include "pico/stdlib.h"\n#define LED 15            // GP15\n\nint main() {\n    gpio_init(LED);\n    gpio_set_dir(LED, GPIO_OUT);\n'
         '    while (true) {\n        gpio_put(LED, 1); sleep_ms(250);\n        gpio_put(LED, 0); sleep_ms(250);\n    }\n}</pre>')
P.append('<p class="k"><b>Build &amp; flash</b> (CLI): <code>cmake&nbsp;..&nbsp;&amp;&amp;&nbsp;make</code> &rarr; <code>blink.uf2</code>; '
         'hold <b>BOOTSEL</b> while plugging in USB, then <code>picotool&nbsp;load&nbsp;blink.uf2&nbsp;&amp;&amp;&nbsp;picotool&nbsp;reboot</code>. '
         'The LED blinks. Full build steps are in <code>firmware/blink/README.md</code>.</p>')
P.append('<h2>Build the bring-up first &mdash; wiring the first light-up</h2>')
P.append('<p class="k"><b>Got the parts? Start here.</b> This is the hands-on build; the numbered sections below'
         '(&sect;1 onward) explain what the panel is for and why each part was chosen.</p>')
P.append('<p class="k"><b>Bring-up</b> = power on the smallest version of the circuit and get it working in verified steps, '
         'before scaling to the full panel. Here that is just <b>the Pico + one 74HC595 + eight LEDs</b>, powered at '
         '<b>3.3&nbsp;V from the Pico</b> (no ULN2803, no external supply): the Pico&rsquo;s 3.3&nbsp;V logic drives a '
         '3.3&nbsp;V-powered 595 directly, so <b>no level shifter is needed</b>. Green LEDs through 240&nbsp;&Omega; at '
         '3.3&nbsp;V draw ~5&nbsp;mA &mdash; a little dim, but plenty to confirm the chain works.</p>')
P.append('<p class="k"><b>No display panel needed yet.</b> For this first light-up the LEDs <b>plug straight into the '
         'breadboard</b> (as drawn). You only need the separate display panel <i>later</i>, for the actual multi-camera '
         'filming &mdash; there the LEDs must spread out at 3&ndash;5&nbsp;cm pitch so every camera can resolve them, and '
         '10&nbsp;mm domes are too wide to pack on a breadboard. The panel board is in &sect;2.</p>')
P.append(f'<figure>{DIAGRAMS["wiring"]}<figcaption><b>Figure 1. Bring-up wiring (exact holes).</b> The Pico and 595 sit on the '
         '<b>left strip</b>; the eight LEDs form a comb on the <b>right strip</b>. The Pico clocks a byte into the 595 over three '
         'wires (data&nbsp;SER, clock&nbsp;SRCLK, latch&nbsp;RCLK); each output QA&ndash;QH drives one green LED through a '
         '240&nbsp;&Omega; resistor to ground. The 595&rsquo;s outputs face right, so <b>each LED sits in the same row as its '
         'output</b> and the eight output&rarr;LED wires run straight across as a tidy ribbon. Holes use the '
         '<b>L&hellip;&nbsp;/&nbsp;R&hellip;</b> convention (Left or Right strip, column&nbsp;a&ndash;j, row&nbsp;1&ndash;63).</figcaption></figure>')
P.append('<p class="k"><b>Connect it in this order</b> &mdash; USB unplugged the whole time. First seat both chips across the centre channel: the Pico up top, and the <b>595 just below with its notch / pin-1 dot pointing DOWN</b> (away from the Pico) so <b>VCC lands at <code>Le31</code> and GND at <code>Lf24</code></b>; add the 0.1&nbsp;&micro;F cap across the 595&rsquo;s VCC&harr;GND. Power runs on the <b>central rails</b> '
         'between the strips &mdash; Pico <b>3V3&nbsp;&rarr;&nbsp;+</b> rail and <b>GND&nbsp;&rarr;&nbsp;&ndash;</b> rail &mdash; with short '
         'ties carrying + / &ndash; to the left rails (for the 595) and ground out to the right rail (for the LED cathodes). Every '
         '<b>LED has two leads in two holes</b>: the <b>long lead (anode,&nbsp;+)</b> into the resistor&rsquo;s hole, the '
         '<b>short lead (cathode,&nbsp;&ndash;)</b> into the adjacent ground rail.</p>')
P.append('<table>'
         '<tr><th>#</th><th>From (hole)</th><th>To (hole)</th><th>Why</th></tr>'
         '<tr><td>1</td><td>Pico <b>3V3</b> (pin&nbsp;36) at <code>Lh5</code></td><td><b>+ rail</b> &mdash; centre <code>MIDa+</code></td><td>3.3&nbsp;V for the whole board</td></tr>'
         '<tr><td>2</td><td>Pico <b>GND</b> (pin&nbsp;23) at <code>Lh18</code></td><td><b>&ndash; rail</b> &mdash; centre <code>MIDa&ndash;</code></td><td>common ground</td></tr>'
         '<tr><td>3</td><td><b>rail ties</b></td><td><code>MIDa+&harr;LEFT+</code>, <code>MIDa&ndash;&harr;LEFT&ndash;</code>, <code>MIDa&ndash;&harr;RIGHT&ndash;</code></td><td>brings + / &ndash; to the left rails (595) and ground to the right rail (LED cathodes)</td></tr>'
         '<tr><td>4</td><td>595 <b>VCC</b> <code>Le31</code>, <b>MR</b> <code>Le25</code></td><td><b>LEFT+</b> rail</td><td>power the chip; MR high = never reset</td></tr>'
         '<tr><td>5</td><td>595 <b>GND&nbsp;(8)</b> <code>Lf24</code>; <b>OE</b> <code>Le28</code></td><td><code>MIDa&ndash;</code> ; <b>LEFT&ndash;</b></td><td>ground the chip; OE low = outputs on</td></tr>'
         '<tr><td>6</td><td>Pico <b>GP19</b> <code>Lh16</code></td><td>595 <b>SER</b> <code>Le29</code></td><td>serial <b>data</b></td></tr>'
         '<tr><td>7</td><td>Pico <b>GP18</b> <code>Lh17</code></td><td>595 <b>SRCLK</b> <code>Le26</code></td><td>shift <b>clock</b></td></tr>'
         '<tr><td>8</td><td>Pico <b>GP17</b> <code>Lh19</code></td><td>595 <b>RCLK</b> <code>Le27</code></td><td><b>latch</b></td></tr>'
         '<tr><td>9</td><td>each output QB&ndash;QH <code>Lf31&ndash;Lf25</code>, QA <code>Le30</code></td><td><code>Ra</code> of that LED&rsquo;s row (ribbon straight across)</td><td>output &rarr; right strip, same row</td></tr>'
         '<tr><td>10</td><td>per LED row: <b>240&nbsp;&Omega;</b> <code>Rc&rarr;Rg</code>, then <b>LED</b> long&nbsp;lead&nbsp;(+) <code>Rh</code>, short&nbsp;lead&nbsp;(&ndash;) &rarr; <b>RIGHT&ndash;</b></td><td>rows 24&ndash;31</td><td>resistor across the channel, LED to ground; long lead is +</td></tr>'
         '</table>')
P.append('<p class="k"><b>LED rows</b> (notch-down, so outputs run bottom&ndash;up): QB&rarr;31, QC&rarr;30, QD&rarr;29, QE&rarr;28, QF&rarr;27, QG&rarr;26, QH&rarr;25, QA&rarr;24.</p>')
P.append('<p class="k"><b>Before you plug in USB &mdash; check:</b> &#9744; 595 <b>notch points down</b> (VCC <code>Le31</code>, GND <code>Lf24</code>) &middot; '
         '&#9744; no jumper shorts <b>+ straight to &ndash;</b> &middot; &#9744; <b>OE&rarr;&ndash;</b> (outputs on) and <b>MR&rarr;+</b> (no reset) &middot; '
         '&#9744; every LED&rsquo;s <b>long lead = +</b> (toward its resistor) &middot; &#9744; each lead in its own hole. Then plug in USB and run the test firmware.</p>')
P.append('<p class="k"><b>Reading the diagram.</b> A <b>line is a jumper you add</b>; the <b>rails are inherent buses</b> (shown by the red/blue tint, not a line) &mdash; you never wire <i>along</i> a rail, you just tap a free hole. '
         'Every jumper plugs into a <b>free hole of the pin&rsquo;s 5-hole group</b> (e.g. output QB at <code>Lf31</code> is tapped at the edge hole <code>Lj31</code>) &mdash; <b>never a second lead in an occupied hole</b>. '
         'One caveat: large boards occasionally <b>split a rail in the middle</b> (the tutorial&rsquo;s &ldquo;exception&rdquo;); to be safe, <b>multimeter each rail end-to-end</b> (continuity mode) and add a bridge jumper only if it reads open.</p>')
P.append('<p class="k"><b>Finding the Pico&rsquo;s pins.</b> The <b>Pico&nbsp;H</b> has its headers pre-soldered, so it drops '
         'straight into the breadboard <b>straddling the centre channel</b> (USB hanging off one end). All five pins we use '
         'are along <b>one long edge</b>: <b>3V3</b> (pin&nbsp;36) up near the USB, then a <b>GND</b> with '
         '<b>GP17 / GP18 / GP19</b> (pins&nbsp;22&ndash;25) grouped together toward the far end. Count pins from the USB end, or read '
         'the labels printed beside each pin, to find them.</p>')
P.append('<p class="k"><b>First test:</b> plug in USB and run firmware that shifts out <code>0b10101010</code> then pulses '
         'RCLK &mdash; four alternating LEDs should light. If they do, the data&rarr;shift&rarr;latch&rarr;LED chain works, and '
         'you can scale up: chain more 595s off <b>QH&rsquo;&nbsp;(9)</b>, and add the ULN2803 buffer for full brightness. '
         'GP18/GP19 are the Pico&rsquo;s hardware <b>SPI0</b> pins (SCK/TX), so the firmware can drive them with the SPI '
         'peripheral; GP17 is a spare GPIO toggled by hand as the latch.</p>')
P.append('<h2>1. Purpose &mdash; what this is for, and why DIY</h2>')
P.append('<p class="lead">Build a large, flat LED panel that shows a fast-advancing, '
         'visually-decodable <b>time code</b>. All 11 cameras film it at once; each frame decodes '
         'to a timestamp; the spread of timestamps across cameras <i>is</i> the inter-camera offset. '
         'One clock, many readers.</p>')
P.append('<p>The Image&nbsp;Engineering / Imatest <b>LED-Panel</b> (ISO&nbsp;15781) is the calibrated '
         'reference we clone. But it is a <b>240&times;130&times;55&nbsp;mm, 1&nbsp;kg</b> benchtop unit with a '
         '50&ndash;100&deg; viewing cone, built to be filmed by <b>one</b> camera at a time, and it costs '
         '<b>$3,980&ndash;$57,850</b>. It cannot face an 11-camera ring. We keep its principle and rebuild '
         'it large, flat, and multi-camera-friendly.</p>')
P.append('<figure><img src="assets/commercial-led-panel.png" style="max-width:420px;width:100%;border:1px solid #e5e7eb;border-radius:8px">'
         '<figcaption><b>Figure 2. The commercial reference panel.</b> Image Engineering / Imatest LED-Panel V5: '
         '110 LEDs (10&times;10 grid + a &times;100 row), step 20&nbsp;µs–10&nbsp;s, accuracy &lt;0.06%.</figcaption></figure>')
P.append('<p class="k">How it encodes time: in the timing modes a single lit LED sweeps across the grid '
         'one position per step, and the &times;100 bottom row counts each wrap, giving a spatial '
         'base-100 counter (range up to 1000 steps). The lit position decodes to '
         '<code>elapsed = count × step</code>.</p>')

P.append('<h2>2. The build &mdash; connection diagram &amp; order list</h2>')
P.append('<p class="k">The whole rig on one screen: the build diagram, and the bill of materials as its '
         'colour-coded legend with buy links. The design rationale is in &sect;4&ndash;&sect;9 below.</p>')
P.append('<div class="slide">'
         '<h3>Multi-camera sync LED panel &mdash; build &amp; bill of materials (~CAD)</h3>'
         '<div class="slide-body">'
         f'<div class="slide-fig">{DIAGRAMS["layout"]}</div>'
         '<div class="slide-bom"><table>'
         '<tr><th></th><th>Part</th><th>Qty</th><th>Buy</th><th>~CAD</th></tr>'
         '<tr><td class="th th2"><a href="assets/bought/pico-h.jpg" target="_blank"><img src="assets/bought/pico-h.jpg" alt="our Pico H (DigiKey, ready to use)"></a><a href="assets/bought/pico-spare-headers.jpg" target="_blank"><img src="assets/bought/pico-spare-headers.jpg" alt="spare bare Pico + headers (RobotShop)"></a></td>'
         '<td>&#9745; <b style="color:#0d9488">Microcontroller</b> <span class="k">('
         '<a href="https://www.digikey.ca/en/products/detail/raspberry-pi/SC0917/16608257">Pico&nbsp;H</a> from DigiKey, ready to use; RobotShop bare Pico + headers #1482457 = spare, received)</span></td><td>1</td>'
         '<td>DigiKey.ca / RobotShop.ca</td><td>$8</td></tr>'
         '<tr><td class="th th2"><a href="assets/bought/sn74hc595.jpg" target="_blank"><img src="assets/bought/sn74hc595.jpg" alt="our SN74HC595 ×4 (DigiKey)"></a><a href="assets/bought/sn74hc595-robotshop.jpg" target="_blank"><img src="assets/bought/sn74hc595-robotshop.jpg" alt="SN74HC595 ×1 (RobotShop)"></a></td>'
         '<td>&#9745; <b style="color:#2563eb">Static-latch shift register</b> <span class="k">(SN74HC595N &mdash; <a href="https://www.ti.com/lit/ds/symlink/sn74hc595.pdf">TI&nbsp;datasheet</a>; 5 total: 1 from <a href="https://ca.robotshop.com/products/shift-register-8-bit-74hc595?variant=42411288395927">RobotShop</a>&nbsp;#1482457 + 4 from <a href="https://www.digikey.ca/en/products/detail/texas-instruments/SN74HC595N/277246">DigiKey</a>)</span></td><td>4</td>'
         '<td><a href="https://ca.robotshop.com/products/shift-register-8-bit-74hc595?variant=42411288395927">RobotShop</a> + <a href="https://www.digikey.ca/en/products/detail/texas-instruments/SN74HC595N/277246">DigiKey.ca</a></td><td>$10</td></tr>'
         '<tr><td class="th"><a href="assets/bought/leds-green-ss555.jpg" target="_blank"><img src="assets/bought/leds-green-ss555.jpg" alt="our green LEDs"></a></td>'
         '<td>&#9745; <b style="color:#dc2626">Direct-emission LEDs</b> <span class="k">(green SS-555-0, &times;20 &mdash; verify 10&nbsp;mm)</span></td><td>20</td>'
         '<td><a href="https://www.ecl.ca" target="_blank">Electronic Connections</a></td><td>$7</td></tr>'
         '<tr><td class="th"><a href="assets/bought/resistors-240ohm.jpg" target="_blank"><img src="assets/bought/resistors-240ohm.jpg" alt="our 240Ω resistors"></a></td>'
         '<td>&#9745; <b style="color:#b45309">Current-limit resistors</b> <span class="k">(240&nbsp;&Omega; &times;100)</span></td><td>&mdash;</td>'
         '<td><a href="https://www.ecl.ca" target="_blank">Electronic Connections</a></td><td>$6</td></tr>'
         '<tr><td class="th"><a href="assets/bought/uln2803.jpg" target="_blank"><img src="assets/bought/uln2803.jpg" alt="our ULN2803 ×4"></a></td>'
         '<td>&#9745; <b>Current-buffer array</b> <span class="k">(<a href="https://www.digikey.ca/en/products/detail/stmicroelectronics/ULN2803A/599591">ULN2803A</a> &times;4 &mdash; bright panel)</span></td><td>4</td>'
         '<td>DigiKey.ca</td><td>$15</td></tr>'
         '<tr><td class="th"><a href="assets/bought/decoupling-caps.jpg" target="_blank"><img src="assets/bought/decoupling-caps.jpg" alt="our decoupling caps"></a></td>'
         '<td>&#9745; <b>Decoupling caps</b> <span class="k">(0.1&nbsp;µF <a href="https://www.digikey.ca/en/products/detail/kemet/C320C104J5R5TA7301/3726081">ceramic</a> &times;10)</span></td><td>10</td>'
         '<td>DigiKey.ca</td><td>$4</td></tr>'
         '<tr><td class="th"></td>'
         '<td>&#9745; <b style="color:#16a34a">5&nbsp;V power</b> <span class="k">(USB &mdash; the microcontroller&rsquo;s 5&nbsp;V pin, or a phone charger; no mains)</span></td><td>&mdash;</td>'
         '<td>on hand</td><td>$0</td></tr>'
         '<tr><td class="th th2"><a href="assets/bought/breadboard-mb104.jpg" target="_blank"><img src="assets/bought/breadboard-mb104.jpg" alt="our breadboard"></a><a href="assets/bought/jumpers-zipwire.jpg" target="_blank"><img src="assets/bought/jumpers-zipwire.jpg" alt="our jumper wires"></a></td><td>&#9745; <b style="color:#475569">Breadboard + jumper wires</b> <span class="k">(MB-104 + 120-pc flexible kit)</span></td><td>&mdash;</td><td><a href="https://www.ecl.ca" target="_blank">Electronic Connections</a></td><td>$55</td></tr>'
         '<tr><td class="th"><a href="assets/bought/rigid-jumpers-jw140.jpg" target="_blank"><img src="assets/bought/rigid-jumpers-jw140.jpg" alt="our Elenco JW-140 rigid jumper kit"></a></td><td>&#9745; <b>Rigid jumper kit</b> <span class="k">(Elenco JW-140 &mdash; received #1482457)</span></td><td>1</td><td><a href="https://ca.robotshop.com/products/elenco-jw-140-jumper-wire-kit">RobotShop.ca</a></td><td>$10</td></tr>'
         '<tr><td class="th"></td>'
         '<td>&#9744; <b style="color:#7c3aed">Panel board</b> <span class="k">(black foam-core 20&times;30&Prime;; later &#8539;&Prime; hardboard)</span></td><td>&mdash;</td>'
         '<td>Dollarama / Home&nbsp;Depot</td><td>$5&ndash;15</td></tr>'
         '<tr><td class="th"></td><td><span style="color:#9ca3af">Micro-USB cable</span> <span class="k">&#42;</span></td><td>1</td><td>Amazon.ca / on hand</td><td>$8</td></tr>'
         '<tr><td class="th"></td><td><span style="color:#9ca3af">Soldering iron + solder</span> <span class="k">(if needed) &#42;</span></td><td>&mdash;</td><td>Amazon.ca / local</td><td>$25</td></tr>'
         '<tr class="tot"><td></td><td>Total</td><td></td><td></td><td>~$135 (+$25)</td></tr>'
         '</table>'
         '<p class="k" style="margin:8px 0 0;font-size:10.5px;line-height:1.45">'
         '&#9745; bought / ordered &middot; &#9744; still to buy. <b>Bought (Electronic Connections, 2026-06-15, $116.52):</b> '
         'breadboard, jumpers, 20 green LEDs, 240&nbsp;&Omega; resistors, and a 5&nbsp;V/5&nbsp;A mains supply '
         '(<b>set aside for safety</b> &mdash; see &sect;3; the rig runs on USB 5&nbsp;V) <a class="shot" href="assets/bought/all-items-group.jpg" target="_blank">&#128247;&nbsp;all items</a>. '
         '<b>Received &mdash; RobotShop #1482457 ($36.16):</b> bare Pico + headers (spare), rigid jumper kit, 1 shift register. '
         '<b>DigiKey #99883073 ($47.87, all in stock):</b> Pico&nbsp;H (start-now), 4 more shift registers, 4 ULN2803 buffers, 10 decoupling caps. '
         '<b>Still needed:</b> just the panel board (craft / hardware store). '
         'Each <b>coloured</b> name marks the same-coloured part in the diagram; '
         '<b style="color:#9ca3af">&#42;</b> = tool / accessory not in the diagram.</p>'
         '</div>'
         '</div></div>')
P.append('<p class="k"><b>Reading the diagram:</b> the breadboard carries only the microcontroller, the static-latch '
         'shift register(s) and the current-limit resistors; the 10&nbsp;mm LEDs are too wide to pack on it (~4 holes each), '
         'so they mount on the display panel at 3&ndash;5&nbsp;cm pitch and connect back by jumper wires. The signal path '
         'runs 5&nbsp;V supply &rarr; microcontroller &rarr; shift register(s) &rarr; LEDs. Each part&rsquo;s photo, price '
         'and store link: &sect;3.</p>')
P.append('<h3>What each part does</h3>')
P.append('<table><tr><th>Part</th><th>Its job in the rig</th></tr>'
         '<tr><td><b>Microcontroller</b> <span class="k">(Raspberry Pi Pico)</span></td><td>The clock. Its PIO (or a hardware timer) advances the time code every τ and shifts the new on/off pattern out over 3 SPI wires.</td></tr>'
         '<tr><td><b>Static-latch shift register</b> <span class="k">(SN74HC595)</span></td><td>The fan-out. Turns those 3 wires into many parallel outputs that all switch at the same instant (no PWM) — one output per LED.</td></tr>'
         '<tr><td><b>Direct-emission LEDs</b> <span class="k">(10 mm red)</span></td><td>The display. The time code the cameras film; on/off per LED, with no phosphor tail to smear the edge.</td></tr>'
         '<tr><td><b>Current-limit resistors</b> <span class="k">(one per LED)</span></td><td>Protection. Set each LED&rsquo;s current so it stays bright but does not burn out.</td></tr>'
         '<tr><td><b>Current-buffer array</b> <span class="k">(ULN2803, big panel only)</span></td><td>Muscle. Lets every LED run at full brightness without overloading the shift register; skip it for the first few-LED test.</td></tr>'
         '<tr><td><b>Regulated 5 V supply</b></td><td>Power. Feeds the LED rail — the USB port alone cannot drive ~40 bright LEDs.</td></tr>'
         '<tr><td><b>Breadboard + jumper wires</b></td><td>The chassis. Holds the chips and carries signals out to the panel; no soldering for the first prototype.</td></tr>'
         '<tr><td><b>Panel board</b> <span class="k">(matte black sheet)</span></td><td>The canvas. The flat surface the LEDs mount on at '
         '3&ndash;5&nbsp;cm pitch so every camera resolves them. Matte <b>black</b> maximises LED contrast and avoids glare into the camera '
         'ring. First build: black <b>foam-core</b>, 20&times;30&Prime; (craft / dollar store, ~$5) &mdash; knife-cut the 10&nbsp;mm holes, the foam grips '
         'the domes. Permanent build: <b>&#8539;&Prime; hardboard</b> (hardware store, cut to size, ~$12) &mdash; drill, hot-glue the LEDs from behind, '
         'spray matte black. Avoid glossy acrylic: it cracks when drilled and reflects the room at the cameras. A commodity sheet, so the list has no link.</td></tr>'
         '<tr><td><b>Micro-USB cable</b></td><td>Programs the microcontroller and powers the small bench test.</td></tr>'
         '</table>')
P.append('<p class="k"><b>Ordering notes:</b> buying within Canada avoids USD exchange and courier brokerage / customs '
         'fees (which can exceed a small order) &mdash; one-stop: DigiKey.ca or Mouser.ca for the commodity parts (duties '
         'handled, fast to Alberta), plus ABRA Electronics (Montreal) or RobotShop.ca for the Teensy; confirm prices on each '
         'page. Order the LEDs in two passes: <b>3&ndash;5 first</b> to eyeball brightness and colour on a Pixel&nbsp;7 '
         '(opened LEDs are non-returnable), then the rest. Returns &amp; de-risking: &sect;3.</p>')
P.append('<h3>Walk-in plan (Edmonton)</h3>')
P.append('<p class="k">Where to handle real parts and get advice in person &mdash; shopping stops first, then places to build and learn:</p>')
P.append('<table>'
         '<tr><th>Place</th><th>Go for</th><th>Where / when</th></tr>'
         '<tr><td><b>Electronic Connections</b></td>'
         '<td>Loose components over the counter: resistors, LEDs, breadboards, jumpers, power supplies &mdash; and likely the shift registers. This rig&rsquo;s parts came from here.</td>'
         '<td>4411 - 97 St NW &middot; (780) 469-7222 &middot; ecl.ca</td></tr>'
         '<tr><td>Dollarama / Staples / Michaels</td>'
         '<td>Black foam-core 20&times;30&Prime; &mdash; the first-build panel board.</td>'
         '<td>any location</td></tr>'
         '<tr><td>Home Depot / Rona</td>'
         '<td>&#8539;&Prime; hardboard cut to size (the permanent panel board), 10&nbsp;mm drill bit, matte-black spray.</td>'
         '<td>any location</td></tr>'
         '<tr><td><a href="https://www.ualberta.ca/en/engineering/student-services/experiential-learning/elko-engineering-garage.html">Elko Engineering Garage</a></td>'
         '<td>Build and test with help: soldering benches, oscilloscopes, staff. Free for U&nbsp;of&nbsp;A members; do the online orientation first.</td>'
         '<td>U of A &middot; ETLC</td></tr>'
         '<tr><td><a href="https://ents.ca/">ENTS</a></td>'
         '<td>Community makerspace (a member-run shared workshop with an electronics lab): advice, project help.</td>'
         '<td>12001 149 St NW &middot; weekly tour</td></tr>'
         '</table>')
P.append('<p class="k">The former components store on Gateway Blvd (Active Electronics) has closed; Fatwire '
         'Distributors stocks finished products, not loose components. Bring this page along: &sect;2 is the shopping '
         'list, &sect;3 the part-by-part rationale.</p>')

P.append('<h2>3. The driver &mdash; why a static-latch shift register, and the exact parts</h2>')
P.append('<h3>How the driver works, in plain words</h3>')
P.append('<p>A <b>shift register</b> is a chip with a row of memory cells: you feed it bits one at a time, and each '
         'clock tick <i>shifts</i> them along the row (that is the &ldquo;shift&rdquo;; &ldquo;register&rdquo; just means the row of cells). '
         'After 8 ticks it holds 8 bits, which appear on its 8 output pins &mdash; so a few wires in become many on/off '
         'lines out (chain four to reach 32 outputs &mdash; one per LED, and this panel has ~27). <b>Latch</b> means the outputs hold '
         'steady while you load the next pattern; you then pulse a separate <i>latch</i> line and <b>all</b> outputs flip '
         'to the new pattern at the same instant. <b>Static</b> means each output then simply sits at a steady on or off '
         '&mdash; unlike a PWM driver, which rapidly pulses the pin to fake brightness and would smear the on/off edge the '
         'cameras are timing. So a <b>static-latch shift register</b> = serial-in, many parallel outputs, all switched '
         'together and held rock-steady.</p>')
P.append('<p>The microcontroller loads the pattern over <b>SPI</b> (Serial Peripheral Interface), a simple serial link '
         'of <b>three wires</b>: <b>data</b> (the bit pattern, sent one bit at a time), <b>shift&nbsp;clock</b> (ticks '
         'each bit in), and <b>latch</b> (the pulse that copies the shifted-in pattern to the outputs at once). On the '
         'SN74HC595 these are the SER, SRCLK and RCLK pins; that shared latch line is what makes every LED change '
         'together to sub-microsecond skew.</p>')
P.append('<p>The driver must switch the LEDs <b>statically</b> (no PWM) for a clean edge. That rules out PWM-based '
         'parts (PWM drivers and addressable strips like the TLC5947 and APA102/WS2812) and points to a <b>static-latch shift register</b> (outputs latch in ~13 ns on RCLK; the SN74HC595 is one part). '
         'LEDs are <b>direct-emission</b> (red/amber/green), <b>never white or PC-amber</b> (phosphor smears the edge). '
         'This static chain handles both 200 µs and 20 µs.</p>')
P.append('<p><b>Logic levels &mdash; a 3.3 V / 5 V note.</b> The recommended Raspberry Pi Pico (like the Teensy) drives '
         '<b>3.3 V</b> logic, while a 74HC595 powered at 5 V wants ~3.5 V for a guaranteed logic-high &mdash; so 3.3 V is '
         'marginal. Two clean fixes: power the 595 at <b>3.3 V</b> for bring-up (logic matches exactly; the LEDs just run a '
         'little dimmer), or for the bright panel run the 595 at 5 V with the TTL-input <b>SN74HCT595</b> (accepts 3.3 V) or '
         'a level shifter.</p>')
P.append('<table><tr><th>Driver approach</th><th>Switching</th><th>Verdict (after datasheet review)</th></tr>'
         '<tr style="background:#fffbeb"><td><b>Static-latch shift register + discrete direct LEDs &nbsp;← chosen</b><br><span class="k">e.g. SN74HC595</span></td><td>static latch ~13 ns; no PWM</td><td>clean edges at 200 µs <i>and</i> 20 µs; ±6 mA/pin (add a current-buffer array, e.g. ULN2803, for full brightness)</td></tr>'
         '<tr><td>PWM addressable LED <span class="k">(e.g. APA102 / DotStar)</span></td><td>8-bit PWM @ ~1 MHz osc</td><td>✗ ~256 µs PWM cycle smears the edge</td></tr>'
         '<tr><td>PWM constant-current LED driver <span class="k">(e.g. TLC5947)</span></td><td>12-bit PWM @ 4 MHz osc</td><td>✗ ~1 ms grayscale frame floor — far too slow</td></tr>'
         '<tr><td>Scan-multiplexed LED matrix + single-board computer <span class="k">(e.g. HUB75 RGB panel + Raspberry Pi)</span></td>'
         '<td>1-of-8&hellip;32 row strobe + PWM; OS-timed</td>'
         '<td>✗ never holds a frame statically — a rolling shutter sees scan bands and duty-cycle flicker, not the code; '
         '2&nbsp;mm pixels at 4&ndash;5&nbsp;mm pitch are far too small for the camera ring (&sect;4); and Linux (not a real-time OS) '
         'jitters the 200&nbsp;µs step. (The Raspberry Pi <b>Pico</b>, a bare-metal microcontroller, <i>would</i> work as the clock '
         '&mdash; it is the matrix panel that fails.)</td></tr></table>')

P.append('<h3>The parts shortlist (verified against datasheets)</h3>')
P.append('<div class="gallery">')
P.append(card("commercial-led-panel.png", "Camera-timing reference panel", "$3,980–$57,850",
              "the calibrated device we clone, not buy · IE / Imatest LED-Panel", "https://www.imatest.com/product/camera-timing-system-led-panel/"))
P.append(card("teensy40.jpg", "Microcontroller board", "~$25–$30",
              "the clock · Cortex-M7 @ 600 MHz · e.g. Teensy 4.0", "https://www.pjrc.com/store/teensy40.html",
              ours=("assets/bought/pico-h.jpg", "our Pico H")))
P.append(card("sn74hc595.jpg", "Static-latch shift register", "$1.05",
              "drives the LEDs · static latch ~13 ns, no PWM · ×4 · e.g. SN74HC595", "https://www.sparkfun.com/products/13699",
              ours=("assets/bought/sn74hc595.jpg", "our 595s (×4)")))
P.append(card("led-red-10mm.jpg", "Direct-emission LED (10 mm)", "~$1",
              "the measurement target · red AlInGaP, no phosphor, Vf 2.1–2.3 V · e.g. SparkFun COM-08862", "https://www.sparkfun.com/super-bright-led-red-10mm.html",
              ours=("assets/bought/leds-green-ss555.jpg", "our green LEDs")))
P.append(card("psu-5v4a.jpg", "Regulated 5 V supply", "$14.95",
              "powers the LED rail · e.g. Mean Well RS-25-5", "https://www.adafruit.com/product/1466"))
P.append('</div>')
P.append('<h3>Rejected / set aside</h3>')
P.append('<div class="gallery">')
P.append(card("tlc5947.jpg", "PWM constant-current LED driver ✗", "$14.95",
              "~1 ms grayscale floor, too slow · e.g. TLC5947", "https://www.adafruit.com/product/1429"))
P.append(card("dotstar.jpg", "PWM addressable LED ✗", "$49.95",
              "8-bit PWM @ ~1 MHz → ~256 µs edge smear · e.g. APA102 / DotStar", "https://www.adafruit.com/product/2241"))
P.append(card("cree-xpe2-amber.jpg", "Phosphor-converted amber LED ✗", "$5.14",
              "PC amber = phosphor, Vf 3.05 V → decay tail smears the edge · e.g. Cree XP-E2", "https://www.ledsupply.com/leds/cree-xlamp-xp-e2-color-high-power-led-star"))
P.append(card("psu-5v4a.jpg", "Mains 5 V supply ✗ (set aside)", "$43 · bought",
              "Circuit-Test PSF25-5 · 120 V screw-terminal wiring is the one shock/fire hazard in a bench rig — power from USB 5 V instead; keep for a future enclosed build", "https://www.rpelectronics.com/psf25-5-ac-dc-power-supply-25w-5vdc-5a.html",
              ours=("assets/bought/psu-psf25-5.jpg", "our unit")))
P.append('</div>')
P.append('<p class="k">Full running evaluation log (every part considered + its verdict, kept across sessions): <code>wiki/analyses/sync-eval-equipment-log.md</code> in memex.</p>')
P.append('<p class="k"><b>Now shown via our own photos in &sect;2:</b> the green LEDs, 240&nbsp;&Omega; resistors, breadboard + jumper wires, microcontroller (Pico&nbsp;H), shift registers (SN74HC595), current-buffer array (ULN2803), and decoupling caps. '
         'Not pictured (generic): '
         'a <b>micro-USB cable</b> for the microcontroller, a <b>soldering iron + solder</b> (to fit the board&rsquo;s header pins and wire the LEDs to the panel), and the panel board + diffuser. '
         'Ballpark for the basic rig: <b>~$120–$150 CAD</b>.</p>')

P.append('<div class="note"><b>First LED order &mdash; how many?</b> The full panel is <b>~27 LEDs</b> '
         '(16 Gray bar + 1 parity + ~10 coarse row), driven by <b>4&times; static-latch shift registers</b> (8 outputs each; e.g. the SN74HC595). '
         'Buy <b>~40 LEDs</b> (~$20&ndash;40): enough to build and film the complete panel for a comprehensive '
         'multi-camera test, plus ~13 spares (LEDs crack on insertion or die while you tune the resistor value). '
         'A failed approach costs &lt;&nbsp;$40. Extra caution: order <b>3&ndash;5 first</b> to eyeball brightness '
         'and colour on a Pixel&nbsp;7 (LEDs cannot be returned once opened), then buy the rest. Buy <b>4&times; the shift register (SN74HC595)</b> '
         'and a <b>spare microcontroller board</b> while you are at it &mdash; both are cheap and the long-lead items if one fails. You also need a <b>breadboard + jumper (Dupont) wires</b> for the bench build.</div>')
P.append('<h3>Returns &amp; de-risking (vendor policies checked 2026-06-06)</h3>')
P.append('<table>'
         '<tr><th>Vendor (its parts)</th><th>Window</th><th>Opened but unsuitable</th><th>Defective</th></tr>'
         '<tr><td><a href="https://learn.adafruit.com/how-do-i-return-my-order/adafruit-s-return-policy">Adafruit</a> (5V PSU)</td><td>30 days</td><td><b>unopened only</b>; 5% restock if &#8805;$500</td><td>replaced / refunded</td></tr>'
         '<tr><td><a href="https://www.sparkfun.com/returns">SparkFun</a> (74HC595, red LED)</td><td>30 days</td><td><b>unopened/unused only</b>; restock fee case-by-case</td><td>RMA by email</td></tr>'
         '<tr><td><a href="https://www.pjrc.com/teensy/troubleshoot.html">PJRC</a> (Teensy)</td><td>RMA by email</td><td>no change-of-mind policy</td><td>RMA replacement; buy direct (counterfeit risk)</td></tr>'
         '</table>')
P.append('<p class="k"><b>Takeaway:</b> opened parts that work but do not suit are mostly <b>non-returnable</b> '
         '(Adafruit, SparkFun, and PJRC are unopened/RMA-only); defective items are covered everywhere. So <b>validate with '
         '1&ndash;2 units before bulk-buying</b> (especially the red LEDs, which cannot be returned once opened), and '
         'rely on returns only for genuinely dead parts. '
         'You pay return shipping unless the item is defective. Policies change, so re-check before ordering.</p>')
P.append('<p class="k"><b>Where to buy:</b> the order list in &sect;2 carries the per-part vendors, buy links, quantities and prices.</p>')
P.append('<h2>4. Geometry &mdash; Option C: one large flat panel</h2>')
P.append('<p>You will place the cameras to face one large flat panel, so a single planar matrix is all '
         'that is needed (no prism, no multi-face latching). The only requirement is that the panel be '
         'large/bright enough for every camera to resolve individual LEDs. Rule of thumb: ~1&nbsp;cm (10&nbsp;mm) LEDs '
         'at ~3&ndash;5&nbsp;cm pitch make a 16-LED bar ~0.5&ndash;0.8&nbsp;m wide, cleanly resolved by a Pixel&nbsp;7 out to ~5&nbsp;m. '
         'Each 10&nbsp;mm dome is ~4 breadboard holes wide, so the LEDs mount on the panel surface (foam-core / hardboard / 3D-printed grid), not the breadboard &mdash; see &sect;2.</p>')
P.append(f'<figure>{DIAGRAMS["geometry"]}<figcaption><b>Figure 3. Panel geometry.</b> All 11 cameras are placed to face one large flat panel showing the time code &mdash; a single planar matrix, no prism or multi-face latching.</figcaption></figure>')
P.append('<p><b>Bring-up scope (current): two cameras.</b> The full rig faces 11 cameras (Figure&nbsp;3); the first '
         'measurement uses just <b>two</b> Pixel&nbsp;7s. Place them so the panel falls on <b>approximately the same sensor '
         'row</b> in each frame. Because both are the same model (same rolling-shutter line time), equal panel rows make the '
         'readout delay cancel in the subtraction &mdash; this removes the rolling-shutter row bias (&sect;8) by construction, '
         'with no per-camera correction. The placement is forgiving: at &tau;&nbsp;=&nbsp;200&nbsp;µs you have ~13 rows of slack '
         'before the residual even shows. Scaling to all 11 cameras later restores the bias and is handled in software (&sect;8).</p>')

P.append('<h2>5. Encoding &mdash; Gray-coded bar + parity + coarse row</h2>')
P.append('<p>Do not read &ldquo;which of 100 dots&rdquo;; it is hard to resolve at distance. Use a '
         '<b>Gray-coded binary bar</b>: a row of large LEDs showing a counter that increments every step '
         '<code>τ</code>. On/off per LED is robust to blur and oblique viewing; Gray coding means only one '
         'bit flips per step, so a code caught mid-transition is at most 1&nbsp;LSB off. A single <b>parity LED</b> '
         'is switched so the number of lit LEDs is always even; a camera that reads an <b>odd</b> count knows a bit was misread (glare, an occlusion, or an LED caught mid-flip) and discards that frame.</p>')
P.append(f'<figure>{DIAGRAMS["encoding"]}<figcaption><b>Figure 4. Readout layout.</b> A 16-bit Gray-coded bar (one bit per LED) plus a parity LED and a redundant coarse row; software thresholds each LED, converts Gray&rarr;binary, and reads <code>t = count &times; &tau;</code>.</figcaption></figure>')
P.append('<table><tr><th>Bits / step τ</th><th>Unambiguous range</th><th>Resolution</th><th>LEDs</th></tr>'
         '<tr><td>16-bit @ τ = 20 µs</td><td>~1.3 s</td><td>20 µs</td><td>16</td></tr>'
         '<tr style="background:#fffbeb"><td>16-bit @ τ = 200 µs &nbsp;<b>← operating point</b></td><td>~13 s</td><td>200 µs</td><td>16</td></tr></table>')
P.append('<p class="k">Sizing: <code>#codes = range / τ</code>; binary needs <code>ceil(log2(#codes))</code> '
         'LEDs, base-W spatial needs <code>ceil(logW(#codes))</code> digits of W. For a 1&nbsp;s safety range: '
         '<b>16 binary LEDs vs ~50 spatial LEDs</b>. You can interpolate below τ (down to the sensor line '
         'time ~10 µs) using the row where the code increments within a rolling-shutter frame.</p>')
P.append('<h3>Bring-up encoding: a single-blob sweep</h3>')
P.append('<p>The bar above packs the counter densely (16 on/off bits &rarr; 65&nbsp;536 codes). For bring-up we use a '
         'simpler, eye-readable <b>sweep</b> instead: one lit LED steps along the <b>fine</b> row, one position per '
         '<code>τ</code>, and a slower <b>coarse</b> row advances one position each time the fine row wraps &mdash; the same '
         'scheme as the commercial and Google panels. You can watch it run and a misread is obvious, which is exactly what you '
         'want while first bringing the rig up.</p>')
P.append('<p>The trade-off is <b>range</b>: a sweep gives only <code>fine_n &times; coarse_n</code> codes &mdash; far fewer '
         'than binary for the same LEDs. Size the coarse row so the range exceeds the largest offset you expect: '
         '<b>unambiguous offset = &plusmn;(fine_n &times; coarse_n &times; &tau;) / 2</b>. A 16&times;16 sweep at 200&nbsp;µs gives '
         '<b>&plusmn;25.6&nbsp;ms</b> (enough for two cameras started close together); 16&times;24 gives &plusmn;38&nbsp;ms '
         '(covers a full 30&nbsp;fps frame). The dense Gray bar stays available as the long-range upgrade &mdash; it is a '
         'firmware change, same LEDs. The simulator in <code>sim/</code> implements this sweep and recovers the offset, '
         'including the coarse-row disambiguation.</p>')

P.append('<h2>6. The coarse scale is mandatory (your disambiguation point)</h2>')
P.append('<p>Without a coarse scale, two cameras can show the <b>identical</b> fine reading while sitting '
         'one fine-wrap period apart. The fix is the <b>vernier / positional-counter</b> principle, the same '
         'trick as Google&rsquo;s slow bottom row (&times;10), the commercial &times;100 row, and a clock&rsquo;s '
         'hour/minute/second hands. In a binary bar you get it for free: the high-order bits <i>are</i> the '
         'slow row, so a 16-bit Gray bar already covers &gt;1&nbsp;s of offset.</p>')
P.append(f'<figure>{DIAGRAMS["vernier"]}<figcaption><b>Figure 5. The vernier.</b> Two cameras can show the identical fine reading yet sit a full fine-wrap apart; the coarse scale (in binary, the high-order bits) resolves the ambiguity.</figcaption></figure>')

P.append("""<h3>Step-time: τ = 200 µs (decided 2026-06-03)</h3>
<p>Match τ to the camera's rolling-shutter line time so each code value spans several rows. The Pixel 7 line time is ≈ 10–20 µs, so <b>200 µs</b> (~10–20 rows per code) is the operating point, not 20 µs.</p>
<ul>
<li><b>The line time is the resolution floor.</b> One frame localises an event to ≈ one row (~10–20 µs); 20 µs already sits on that floor, so a finer step buys nothing the camera can resolve.</li>
<li><b>Fine resolution comes from the rolling shutter, not a tiny step.</b> Fitting code-vs-row over thousands of rows reaches sub-µs precision at any τ. At 200 µs each code spans ~10–20 rows (clean, fittable, blur-tolerant); at 20 µs each spans ~1 row (a 2-row blur is a 2-LSB error).</li>
<li><b>Exposure smear.</b> Fine bits stay crisp only if exposure ≲ τ. 200 µs allows ≤ 1/5000 s (easy against a bright panel); 20 µs would need ≤ 1/50000 s (impractical).</li>
<li><b>Hardware.</b> A <b>static-latch</b> driver (74HC595 shift register) switches cleanly at any τ; PWM drivers (TLC5947, APA102) cannot — their brightness PWM smears the edge.</li>
</ul>
<p><b>Build choice:</b> drive the LEDs with <b>74HC595 shift registers</b> (static latch, no PWM), which switch cleanly at <b>both 200 µs and 20 µs</b>. Operate at 200 µs and cross-validate at 20 µs: two step sizes agreeing on the same offset is a strong validation result. First measure the actual Pixel 7 line time (readout ÷ rows); the sweet spot is τ ≈ 5–15× that.</p>""")
P.append('<h2>7. Timing integrity</h2>')
P.append('<p>The clock itself is already trustworthy: the microcontroller crystal (±30 ppm) drifts &lt;0.1 ms over a '
         'multi-second sweep, ample for sub-ms. The formal timing <b>audit and cross-validation</b> — recording the exact '
         'step period and jitter, and agreeing with an independent method — are a <b>later phase</b>, deferred until the basic '
         'rig decodes correctly, so the audit gear is left off this build and its purchase list.</p>')

P.append('<h2>8. Decoding pipeline</h2>')
P.append('<p>Per camera: locate the panel, threshold each LED on/off, decode the pattern to a timestamp '
         '(Gray&rarr;binary, or sweep positions&rarr;count, then <code>t = count &times; &tau;</code>); subtract across '
         'cameras for offsets; read the code at the panel&rsquo;s sensor row, optionally interpolating with the within-frame '
         'increment row for ~10 µs resolution. ~100 lines on top of the existing rig&rsquo;s analysis code.</p>')
P.append('<p><b>Rolling-shutter row bias (important).</b> A camera exposes sensor row <code>r</code> at '
         '<code>frame_start + r &times; line_time</code>, so it reads the panel at the instant of <b>the row the panel '
         'occupies</b>. If the panel lands on a different row in two cameras, their decoded times differ by '
         '<code>(row<sub>A</sub> &minus; row<sub>B</sub>) &times; line_time</code> &mdash; a systematic offset of '
         '<b>milliseconds</b> (e.g. 400&nbsp;rows &times; 15&nbsp;µs = 6&nbsp;ms) that is nothing to do with sync and would '
         'swamp the sub-µs goal. Two ways to remove it: <b>(a)</b> place the cameras so the panel sits at the same row &mdash; '
         'the two-camera bring-up (&sect;4); <b>(b)</b> subtract each camera&rsquo;s <code>panel_row &times; line_time</code> '
         'to refer every timestamp to frame-start &mdash; the general N-camera fix. Both are quantified in <code>sim/</code> '
         '(the 6&nbsp;ms artifact above is a simulator measurement).</p>')

P.append('<h2>9. Decisions (resolved)</h2>')
P.append('<ul>'
         '<li><b>Step-time τ = 200 µs</b> operating point; fine timing from the rolling-shutter row fit; cross-validated at 20 µs (see §5).</li>'
         '<li><b>Driver = static-latch shift register</b> (no PWM, ~13 ns latch; the SN74HC595 is one part); the datasheet audit ruled out the PWM options — a PWM constant-current driver (TLC5947, ~1 ms floor) and a PWM addressable LED (APA102, ~256 µs smear).</li>'
         '<li><b>Microcontroller = Raspberry Pi Pico</b> (~$6) — its PIO clocks the shift-register chain with cycle-exact timing; the Teensy 4.0 works but is overkill. 3.3 V logic, so power the 595 at 3.3 V for bring-up (or use the HCT variant / a level shifter at 5 V).</li>'
         '<li><b>Bring-up scope = two cameras</b> placed to frame the panel at the same sensor row, which cancels the rolling-shutter bias by construction (§4, §8). Scale to 11 cameras later with the software row-correction.</li>'
         '<li><b>Bring-up encoding = single-blob sweep</b> (one-hot fine + coarse rows), chosen for eye-readable debugging over the dense Gray bar; the Gray bar stays the long-range upgrade (firmware-only).</li>'
         '<li><b>Unambiguous range</b> — sweep gives ±(fine·coarse·τ)/2 (16×16 → ±25.6 ms, enough for two cameras started close; widen the coarse row for more); the Gray-bar upgrade gives ≈13 s at 200 µs.</li>'
         '<li><b>Rolling-shutter row bias identified &amp; handled</b> — decoded time shifts by (Δrow × line time), ms-scale; removed now by same-row placement, at scale by per-camera subtraction. Quantified in <code>sim/</code>.</li>'
         '<li><b>Coarse row: included</b> — extends range and gives a redundant, human-readable cross-check (mirrors the Google / ISO design).</li>'
         '<li><b>Validated in simulation</b> — the <code>sim/</code> decode model (test-driven) confirms encode→film→decode→offset recovery, including the coarse-row disambiguation, before any parts are bought.</li>'
         '</ul>')

P.append('<h2>References</h2>')
P.append('<ul>'
         '<li>Imatest Camera Timing System LED-Panel — <a href="https://www.imatest.com/product/camera-timing-system-led-panel/">product page</a> '
         '(<a href="https://www.imatest.com/wp-content/uploads/2024/03/LED-Panel_V5_data_sheet.pdf">datasheet</a>, '
         '<a href="https://www.imatest.com/wp-content/uploads/2024/03/LED-Panel_V5_manual.pdf">manual</a>, '
         'local copies in <code>memex/raw/assets/</code>)</li>'
         '<li>Image Engineering LED-Panel — <a href="https://www.image-engineering.de/products/equipment/measurement-devices/900-led-panel">product page</a></li>'
         '<li>Teensy 4.0 — <a href="https://www.pjrc.com/store/teensy40.html">pjrc.com</a></li>'
         '<li>Adafruit DotStar (APA102) — <a href="https://www.adafruit.com/product/2241">product 2241</a></li>'
         '<li>Adafruit TLC5947 — <a href="https://www.adafruit.com/product/1429">product 1429</a></li>'
         '<li>Google panel design: Ansari et&nbsp;al. 2019, &ldquo;Wireless Software Synchronization of Multiple Distributed Cameras&rdquo; (see memex summary)</li>'
         '<li>memex pages: <i>DIY LED sync evaluation rig</i>, <i>LED-Panel (camera-timing measurement device)</i>, '
         '<i>Rolling-shutter LED sync measurement</i>, <i>Argus</i>, <i>Faizullin et al. 2021 — Twist-n-Sync</i>.</li>'
         '</ul>')

html = ("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<base target='_blank'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>LED sync panel — design plan</title>"
        f"<style>{CSS}</style></head><body>{''.join(P)}</body></html>")

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print(f"\nWROTE {OUT} ({len(html)} bytes)")
