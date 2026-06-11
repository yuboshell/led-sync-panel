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
    s.append(txt(79, 109, "5 V supply", 9.5, C_PSU, "middle"))
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

DIAGRAMS = {
    "geometry": svg_geometry(),
    "encoding": svg_encoding(),
    "vernier":  svg_vernier(),
    "layout":   svg_layout(),
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
.slide-bom td.th{width:54px;padding:3px 4px}
.slide-bom td.th img{height:30px;width:46px;object-fit:contain;display:block;margin:0 auto}
.slide-bom .tot td{border-top:2px solid var(--ink);border-bottom:none;font-weight:700}
"""

def card(img, name, price, role, href):
    return (f'<div class="card"><a href="{href}" target="_blank">'
            f'<img src="assets/{img}" alt="{name}"></a>'
            f'<div class="name">{name}</div><div class="price">{price}</div>'
            f'<div class="role">{role}</div></div>')

P = []  # page body parts
P.append('<h1>Multi-camera sync evaluation: a large flat LED time-code panel</h1>')
P.append('<div class="meta">DIY design plan &middot; updated 2026-06-10 &middot; working draft &middot; '
         'step-time 200&nbsp;µs, driver 74HC595, range &ge;1&nbsp;s, coarse row included (datasheet-audited) &middot; 11&times;Pixel&nbsp;7 / Argus rig</div>')
P.append('<p class="k"><b>Reader&rsquo;s map:</b> &sect;1 what this tool is for &middot; '
         '&sect;2 the wiring diagram + order list &middot; &sect;3 the driver choice + exact parts &middot; '
         '&sect;4&ndash;&sect;9 the design rationale.</p>')
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
         '<figcaption><b>Figure 1. The commercial reference panel.</b> Image Engineering / Imatest LED-Panel V5: '
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
         '<tr><td class="th"><img src="assets/teensy40.jpg" alt="Teensy 4.0"></td>'
         '<td><b style="color:#0d9488">Microcontroller</b> <span class="k">(Teensy 4.0)</span></td><td>1</td>'
         '<td><a href="https://ca.robotshop.com/products/teensy-40-usb-microcontroller-development-board">RobotShop.ca</a> / ABRA</td><td>$34</td></tr>'
         '<tr><td class="th"><img src="assets/sn74hc595.jpg" alt="SN74HC595"></td>'
         '<td><b style="color:#2563eb">Static-latch shift register</b> <span class="k">(SN74HC595N)</span></td><td>4</td>'
         '<td><a href="https://www.digikey.ca/en/products/detail/texas-instruments/SN74HC595N/277246">DigiKey.ca</a> / ABRA</td><td>$10</td></tr>'
         '<tr><td class="th"><img src="assets/led-red-10mm.jpg" alt="10 mm red LED"></td>'
         '<td><b style="color:#dc2626">Direct-emission LEDs, 10&nbsp;mm</b> <span class="k">(red AlInGaP)</span></td><td>~40</td>'
         '<td><a href="https://www.sparkfun.com/super-bright-led-red-10mm.html">SparkFun</a> / DigiKey.ca</td><td>$20</td></tr>'
         '<tr><td class="th"></td>'
         '<td><b style="color:#b45309">Current-limit resistors</b> <span class="k">(+ ULN2803)</span></td><td>&mdash;</td>'
         '<td>DigiKey.ca / Mouser.ca</td><td>$10</td></tr>'
         '<tr><td class="th"><img src="assets/psu-5v4a.jpg" alt="5 V supply"></td>'
         '<td><b style="color:#16a34a">Regulated 5&nbsp;V supply</b> <span class="k">(Mean Well RS-25-5)</span></td><td>1</td>'
         '<td><a href="https://www.digikey.ca/en/products/detail/mean-well-usa-inc/RS-25-5/7706180">DigiKey.ca</a> / Amazon.ca</td><td>$20</td></tr>'
         '<tr><td class="th"></td><td><b style="color:#475569">Breadboard + jumper wires</b></td><td>&mdash;</td><td>Amazon.ca / local</td><td>$18</td></tr>'
         '<tr><td class="th"></td>'
         '<td><b style="color:#7c3aed">Panel board</b> <span class="k">(black foam-core 20&times;30&Prime;; later &#8539;&Prime; hardboard)</span></td><td>&mdash;</td>'
         '<td>Dollarama / Home&nbsp;Depot</td><td>$5&ndash;15</td></tr>'
         '<tr><td class="th"></td><td><span style="color:#9ca3af">Micro-USB cable</span> <span class="k">&#42;</span></td><td>1</td><td>Amazon.ca / on hand</td><td>$8</td></tr>'
         '<tr><td class="th"></td><td><span style="color:#9ca3af">Soldering iron + solder</span> <span class="k">(if needed) &#42;</span></td><td>&mdash;</td><td>Amazon.ca / local</td><td>$25</td></tr>'
         '<tr class="tot"><td></td><td>Total</td><td></td><td></td><td>~$130 (+$25)</td></tr>'
         '</table>'
         '<p class="k" style="margin:8px 0 0;font-size:10.5px;line-height:1.45">Each <b>coloured</b> name marks the '
         'same-coloured part in the diagram. <b style="color:#9ca3af">&#42;</b> = not shown in the diagram (a tool / accessory). '
         'A link opens the product page; unlinked rows are commodity items &mdash; any vendor works.</p>'
         '</div>'
         '</div></div>')
P.append('<p class="k"><b>Reading the diagram:</b> the breadboard carries only the microcontroller, the static-latch '
         'shift register(s) and the current-limit resistors; the 10&nbsp;mm LEDs are too wide to pack on it (~4 holes each), '
         'so they mount on the display panel at 3&ndash;5&nbsp;cm pitch and connect back by jumper wires. The signal path '
         'runs 5&nbsp;V supply &rarr; microcontroller &rarr; shift register(s) &rarr; LEDs. Each part&rsquo;s photo, price '
         'and store link: &sect;3.</p>')
P.append('<h3>What each part does</h3>')
P.append('<table><tr><th>Part</th><th>Its job in the rig</th></tr>'
         '<tr><td><b>Microcontroller</b> <span class="k">(Teensy 4.0)</span></td><td>The clock. A hardware timer advances the time code every τ and shifts the new on/off pattern out over 3 SPI wires.</td></tr>'
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
P.append('<p class="k"><b>Hands-on help (Edmonton):</b> to handle real parts and get advice in person &mdash; '
         '<a href="https://www.ualberta.ca/en/engineering/student-services/experiential-learning/elko-engineering-garage.html">Elko Engineering Garage</a> '
         '(U of A, ETLC; free for university members; soldering benches, scopes, staff), '
         '<a href="https://www.epl.ca/makerspace/">EPL Stanley A. Milner Fab Lab</a> (downtown library; free; beginner soldering training), '
         '<a href="https://ents.ca/">ENTS</a> (community makerspace &mdash; a member-run shared workshop with an electronics lab; 12001 149 St NW; weekly tours), and '
         '<a href="https://www.fatwiredist.ca/">Fatwire Distributors</a> (electronic-parts counter, 9325 63 Ave NW, Mon&ndash;Fri; call ahead about hobby quantities). '
         'The former components store on Gateway Blvd (Active Electronics) has closed.</p>')

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
P.append('<table><tr><th>Driver approach</th><th>Switching</th><th>Verdict (after datasheet review)</th></tr>'
         '<tr style="background:#fffbeb"><td><b>Static-latch shift register + discrete direct LEDs &nbsp;← chosen</b><br><span class="k">e.g. SN74HC595</span></td><td>static latch ~13 ns; no PWM</td><td>clean edges at 200 µs <i>and</i> 20 µs; ±6 mA/pin (add a current-buffer array, e.g. ULN2803, for full brightness)</td></tr>'
         '<tr><td>PWM addressable LED <span class="k">(e.g. APA102 / DotStar)</span></td><td>8-bit PWM @ ~1 MHz osc</td><td>✗ ~256 µs PWM cycle smears the edge</td></tr>'
         '<tr><td>PWM constant-current LED driver <span class="k">(e.g. TLC5947)</span></td><td>12-bit PWM @ 4 MHz osc</td><td>✗ ~1 ms grayscale frame floor — far too slow</td></tr></table>')

P.append('<h3>The parts shortlist (verified against datasheets)</h3>')
P.append('<div class="gallery">')
P.append(card("commercial-led-panel.png", "Camera-timing reference panel", "$3,980–$57,850",
              "the calibrated device we clone, not buy · IE / Imatest LED-Panel", "https://www.imatest.com/product/camera-timing-system-led-panel/"))
P.append(card("teensy40.jpg", "Microcontroller board", "~$25–$30",
              "the clock · Cortex-M7 @ 600 MHz · e.g. Teensy 4.0", "https://www.pjrc.com/store/teensy40.html"))
P.append(card("sn74hc595.jpg", "Static-latch shift register", "$1.05",
              "drives the LEDs · static latch ~13 ns, no PWM · ×4 · e.g. SN74HC595", "https://www.sparkfun.com/products/13699"))
P.append(card("led-red-10mm.jpg", "Direct-emission LED (10 mm)", "~$1",
              "the measurement target · red AlInGaP, no phosphor, Vf 2.1–2.3 V · e.g. SparkFun COM-08862", "https://www.sparkfun.com/super-bright-led-red-10mm.html"))
P.append(card("psu-5v4a.jpg", "Regulated 5 V supply", "$14.95",
              "powers the LED rail · e.g. Mean Well RS-25-5", "https://www.adafruit.com/product/1466"))
P.append('</div>')
P.append('<h3>Rejected after reading the datasheet</h3>')
P.append('<div class="gallery">')
P.append(card("tlc5947.jpg", "PWM constant-current LED driver ✗", "$14.95",
              "~1 ms grayscale floor, too slow · e.g. TLC5947", "https://www.adafruit.com/product/1429"))
P.append(card("dotstar.jpg", "PWM addressable LED ✗", "$49.95",
              "8-bit PWM @ ~1 MHz → ~256 µs edge smear · e.g. APA102 / DotStar", "https://www.adafruit.com/product/2241"))
P.append(card("cree-xpe2-amber.jpg", "Phosphor-converted amber LED ✗", "$5.14",
              "PC amber = phosphor, Vf 3.05 V → decay tail smears the edge · e.g. Cree XP-E2", "https://www.ledsupply.com/leds/cree-xlamp-xp-e2-color-high-power-led-star"))
P.append('</div>')
P.append('<p class="k">Full running evaluation log (every part considered + its verdict, kept across sessions): <code>wiki/analyses/sync-eval-equipment-log.md</code> in memex.</p>')
P.append('<p class="k">Not pictured (generic): current-limit resistors (one per LED), a <b>current-buffer array</b> (e.g. ULN2803) '
         'for full 20 mA brightness on the big panel, a <b>breadboard + jumper wires</b> (perfboard for the permanent build), '
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
P.append(f'<figure>{DIAGRAMS["geometry"]}<figcaption><b>Figure 2. Panel geometry.</b> All 11 cameras are placed to face one large flat panel showing the time code &mdash; a single planar matrix, no prism or multi-face latching.</figcaption></figure>')

P.append('<h2>5. Encoding &mdash; Gray-coded bar + parity + coarse row</h2>')
P.append('<p>Do not read &ldquo;which of 100 dots&rdquo;; it is hard to resolve at distance. Use a '
         '<b>Gray-coded binary bar</b>: a row of large LEDs showing a counter that increments every step '
         '<code>τ</code>. On/off per LED is robust to blur and oblique viewing; Gray coding means only one '
         'bit flips per step, so a code caught mid-transition is at most 1&nbsp;LSB off. A single <b>parity LED</b> '
         'is switched so the number of lit LEDs is always even; a camera that reads an <b>odd</b> count knows a bit was misread (glare, an occlusion, or an LED caught mid-flip) and discards that frame.</p>')
P.append(f'<figure>{DIAGRAMS["encoding"]}<figcaption><b>Figure 3. Readout layout.</b> A 16-bit Gray-coded bar (one bit per LED) plus a parity LED and a redundant coarse row; software thresholds each LED, converts Gray&rarr;binary, and reads <code>t = count &times; &tau;</code>.</figcaption></figure>')
P.append('<table><tr><th>Bits / step τ</th><th>Unambiguous range</th><th>Resolution</th><th>LEDs</th></tr>'
         '<tr><td>16-bit @ τ = 20 µs</td><td>~1.3 s</td><td>20 µs</td><td>16</td></tr>'
         '<tr style="background:#fffbeb"><td>16-bit @ τ = 200 µs &nbsp;<b>← operating point</b></td><td>~13 s</td><td>200 µs</td><td>16</td></tr></table>')
P.append('<p class="k">Sizing: <code>#codes = range / τ</code>; binary needs <code>ceil(log2(#codes))</code> '
         'LEDs, base-W spatial needs <code>ceil(logW(#codes))</code> digits of W. For a 1&nbsp;s safety range: '
         '<b>16 binary LEDs vs ~50 spatial LEDs</b>. You can interpolate below τ (down to the sensor line '
         'time ~10 µs) using the row where the code increments within a rolling-shutter frame.</p>')

P.append('<h2>6. The coarse scale is mandatory (your disambiguation point)</h2>')
P.append('<p>Without a coarse scale, two cameras can show the <b>identical</b> fine reading while sitting '
         'one fine-wrap period apart. The fix is the <b>vernier / positional-counter</b> principle, the same '
         'trick as Google&rsquo;s slow bottom row (&times;10), the commercial &times;100 row, and a clock&rsquo;s '
         'hour/minute/second hands. In a binary bar you get it for free: the high-order bits <i>are</i> the '
         'slow row, so a 16-bit Gray bar already covers &gt;1&nbsp;s of offset.</p>')
P.append(f'<figure>{DIAGRAMS["vernier"]}<figcaption><b>Figure 4. The vernier.</b> Two cameras can show the identical fine reading yet sit a full fine-wrap apart; the coarse scale (in binary, the high-order bits) resolves the ambiguity.</figcaption></figure>')

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
P.append('<p>Per camera: locate the panel, threshold each LED on/off, decode Gray&rarr;binary&rarr;timestamp; '
         'subtract across cameras for offsets; read the code at the panel&rsquo;s sensor row, optionally '
         'interpolating with the within-frame increment row for ~10 µs resolution. ~100 lines on top of the '
         'existing rig&rsquo;s analysis code.</p>')

P.append('<h2>9. Decisions (resolved)</h2>')
P.append('<ul>'
         '<li><b>Step-time τ = 200 µs</b> operating point; fine timing from the rolling-shutter row fit; cross-validated at 20 µs (see §5).</li>'
         '<li><b>Driver = static-latch shift register</b> (no PWM, ~13 ns latch; the SN74HC595 is one part); the datasheet audit ruled out the PWM options — a PWM constant-current driver (TLC5947, ~1 ms floor) and a PWM addressable LED (APA102, ~256 µs smear).</li>'
         '<li><b>Unambiguous range ≥ 1 s</b> — a 16-bit Gray bar gives ~1.3 s at 20 µs (≈ 13 s at 200 µs), far beyond any plausible inter-camera offset.</li>'
         '<li><b>Coarse spatial row: included</b> — a redundant, human-readable cross-check beside the Gray bar (mirrors the Google / ISO design).</li>'
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
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>LED sync panel — design plan</title>"
        f"<style>{CSS}</style></head><body>{''.join(P)}</body></html>")

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print(f"\nWROTE {OUT} ({len(html)} bytes)")
