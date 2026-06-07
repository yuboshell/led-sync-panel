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

# ---------- Diagram 4: electronics block ----------
def svg_block():
    s = [txt(20, 26, "Electronics (one clock drives every LED)", 14, INK, "start", "bold")]
    def box(x, y, w, h, l1, l2=""):
        g = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#f8fafc" stroke="{INK}"/>']
        if l2:
            g.append(txt(x+w/2, y+h/2-4, l1, 12.5, INK, "middle", "bold"))
            g.append(txt(x+w/2, y+h/2+14, l2, 10.5, MUTE, "middle"))
        else:
            g.append(txt(x+w/2, y+h/2+4, l1, 12.5, INK, "middle", "bold"))
        return "".join(g)
    def arrow(x1, y1, x2, y2, lbl=""):
        g = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="1.6"/>',
             f'<polygon points="{x2},{y2} {x2-8},{y2-4} {x2-8},{y2+4}" fill="{INK}"/>']
        if lbl:
            g.append(txt((x1+x2)/2, y1-8, lbl, 10, MUTE, "middle"))
        return "".join(g)
    s.append(box(20, 60, 150, 56, "Teensy 4.0", "hardware timer @ τ"))
    s.append(arrow(170, 88, 250, 88, "SPI"))
    s.append(box(250, 60, 160, 56, "LED driver", "TLC5947 / APA102"))
    s.append(arrow(410, 88, 470, 88))
    s.append(box(470, 60, 170, 56, "LED bar", "on the flat panel"))
    # audit branch
    s.append(arrow(555, 116, 555, 158))
    s.append(box(470, 158, 170, 50, "photodiode → scope /", "logic analyser (audit)"))
    s.append(txt(555, 228, "records step period + jitter", 10, MUTE, "middle"))
    # power
    s.append(box(250, 158, 160, 50, "5 V supply"))
    s.append(arrow(330, 158, 330, 116))
    s.append(txt(300, 246, "common LATCH: all LEDs change together (sub-µs skew)", 11, MUTE, "middle"))
    return wrap("".join(s), 720, 262)

# ---------- Diagram 5: pictorial wiring (real product photos + links) ----------
def svg_wiring():
    s = [txt(20, 22, "How the parts connect (click any photo to open its store page)", 13.5, INK, "start", "bold")]
    def pnode(x, y, img, name, price, href, w=132, h=84):
        return (f'<a href="{href}" target="_blank">'
                f'<rect x="{x}" y="{y}" width="{w}" height="{h+34}" rx="7" fill="#fff" stroke="{LINE}"/>'
                f'<image href="assets/{img}" x="{x+6}" y="{y+5}" width="{w-12}" height="{h-10}" preserveAspectRatio="xMidYMid meet"/>'
                + txt(x+w/2, y+h+13, name, 11, "#0f4c81", "middle", "bold")
                + txt(x+w/2, y+h+27, price, 9.5, MUTE, "middle")
                + '</a>')
    def onode(x, y, name, sub, href, w=132, h=84):
        return (f'<a href="{href}" target="_blank">'
                f'<rect x="{x}" y="{y}" width="{w}" height="{h+34}" rx="7" fill="#f8fafc" stroke="{LINE}" stroke-dasharray="5 3"/>'
                + txt(x+w/2, y+h/2-3, name, 11, "#0f4c81", "middle", "bold")
                + txt(x+w/2, y+h/2+13, "(optional)", 9.5, MUTE, "middle")
                + txt(x+w/2, y+h+13, sub, 8.5, MUTE, "middle")
                + '</a>')
    def harrow(x1, x2, y, lbl):
        return (f'<line x1="{x1}" y1="{y}" x2="{x2-7}" y2="{y}" stroke="{INK}" stroke-width="1.7"/>'
                f'<polygon points="{x2},{y} {x2-8},{y-4} {x2-8},{y+4}" fill="{INK}"/>'
                + txt((x1+x2)/2, y-8, lbl, 9.5, MUTE, "middle"))
    s.append(pnode(40, 170, "teensy40.jpg", "Teensy 4.0", "~$30 · USB-powered", "https://www.pjrc.com/store/teensy40.html"))
    s.append(pnode(360, 170, "sn74hc595.jpg", "74HC595 ×2–3", "$1.05 ea · static latch", "https://www.sparkfun.com/products/13699"))
    s.append(pnode(700, 170, "led-red-10mm.jpg", "direct-red 10mm ×N", "+ resistor · no phosphor", "https://www.sparkfun.com/super-bright-led-red-10mm.html"))
    s.append(pnode(40, 24, "psu-5v4a.jpg", "5 V 4 A supply", "$14.95", "https://www.adafruit.com/product/1466"))
    s.append(pnode(234, 352, "saleae-logic8.png", "Saleae Logic 8", "~$199 · audit", "https://www.saleae.com/products/logic-8"))
    s.append(onode(700, 352, "Photodiode &#8594; scope", "Thorlabs DET10A2 / BPW34", "https://www.thorlabs.com/thorproduct.cfm?partnumber=DET10A2"))
    s.append(harrow(172, 360, 212, "SPI: SER &#183; SRCLK &#183; RCLK"))
    s.append(harrow(492, 700, 212, "static outputs &#8594; resistors"))
    s.append(f'<polyline points="106,144 106,157 426,157 426,167" fill="none" stroke="{INK}" stroke-width="1.6"/>')
    s.append(f'<polygon points="426,170 422,162 430,162" fill="{INK}"/>')
    s.append(txt(250, 151, "5 V", 9.5, MUTE, "middle"))
    s.append(f'<line x1="300" y1="213" x2="300" y2="352" stroke="{INK}" stroke-width="1.4" stroke-dasharray="5 4"/>')
    s.append(f'<circle cx="300" cy="212" r="3" fill="{INK}"/>')
    s.append(txt(312, 300, "taps RCLK &#8594; step + jitter", 9.5, MUTE, "start"))
    s.append(f'<line x1="766" y1="256" x2="766" y2="350" stroke="{INK}" stroke-width="1.4" stroke-dasharray="5 4"/>')
    s.append(f'<polygon points="766,352 762,344 770,344" fill="{INK}"/>')
    s.append(txt(776, 305, "optical witness", 9.5, MUTE, "start"))
    return wrap("".join(s), 900, 478)

DIAGRAMS = {
    "geometry": svg_geometry(),
    "encoding": svg_encoding(),
    "vernier":  svg_vernier(),
    "block":    svg_block(),
    "wiring":   svg_wiring(),
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
"""

def card(img, name, price, role, href):
    return (f'<div class="card"><a href="{href}" target="_blank">'
            f'<img src="assets/{img}" alt="{name}"></a>'
            f'<div class="name">{name}</div><div class="price">{price}</div>'
            f'<div class="role">{role}</div></div>')

P = []  # page body parts
P.append('<h1>Multi-camera sync evaluation: a large flat LED time-code panel</h1>')
P.append('<div class="meta">DIY design plan &middot; updated 2026-06-06 &middot; working draft &middot; '
         'step-time 200&nbsp;µs, driver 74HC595 (datasheet-audited); range + coarse-row pending &middot; 11&times;Pixel&nbsp;7 / Argus rig</div>')
P.append('<p class="lead">Build a large, flat LED panel that shows a fast-advancing, '
         'visually-decodable <b>time code</b>. All 11 cameras film it at once; each frame decodes '
         'to a timestamp; the spread of timestamps across cameras <i>is</i> the inter-camera offset. '
         'One clock, many readers.</p>')

P.append('<h2>1. Why not just buy the commercial panel</h2>')
P.append('<p>The Image&nbsp;Engineering / Imatest <b>LED-Panel</b> (ISO&nbsp;15781) is the calibrated '
         'reference we clone. But it is a <b>240&times;130&times;55&nbsp;mm, 1&nbsp;kg</b> benchtop unit with a '
         '50&ndash;100&deg; viewing cone, built to be filmed by <b>one</b> camera at a time, and it costs '
         '<b>$3,980&ndash;$57,850</b>. It cannot face an 11-camera ring. We keep its principle and rebuild '
         'it large, flat, and multi-camera-friendly.</p>')
P.append('<figure><img src="assets/commercial-led-panel.png" style="max-width:420px;width:100%;border:1px solid #e5e7eb;border-radius:8px">'
         '<figcaption>The commercial reference: Image Engineering / Imatest LED-Panel V5. '
         '110 LEDs (10&times;10 grid + a &times;100 row), step 20&nbsp;µs–10&nbsp;s, accuracy &lt;0.06%.</figcaption></figure>')
P.append('<p class="k">How it encodes time: in the timing modes a single lit LED sweeps across the grid '
         'one position per step, and the &times;100 bottom row counts each wrap, giving a spatial '
         'base-100 counter (range up to 1000 steps). The lit position decodes to '
         '<code>elapsed = count × step</code>.</p>')

P.append('<h2>2. Geometry &mdash; Option C: one large flat panel</h2>')
P.append('<p>You will place the cameras to face one large flat panel, so a single planar matrix is all '
         'that is needed (no prism, no multi-face latching). The only requirement is that the panel be '
         'large/bright enough for every camera to resolve individual LEDs. Rule of thumb: ~1&nbsp;cm LED blobs '
         'at ~3&ndash;5&nbsp;cm pitch make a 16-LED bar ~0.5&ndash;0.8&nbsp;m wide, cleanly resolved by a Pixel&nbsp;7 out to ~5&nbsp;m.</p>')
P.append(f'<figure>{DIAGRAMS["geometry"]}</figure>')

P.append('<h2>3. Encoding &mdash; Gray-coded bar + parity + coarse row</h2>')
P.append('<p>Do not read &ldquo;which of 100 dots&rdquo;; it is hard to resolve at distance. Use a '
         '<b>Gray-coded binary bar</b>: a row of large LEDs showing a counter that increments every step '
         '<code>τ</code>. On/off per LED is robust to blur and oblique viewing; Gray coding means only one '
         'bit flips per step, so a code caught mid-transition is at most 1&nbsp;LSB off. A single <b>parity LED</b> '
         'gives an integrity check.</p>')
P.append(f'<figure>{DIAGRAMS["encoding"]}</figure>')
P.append('<table><tr><th>Bits / step τ</th><th>Unambiguous range</th><th>Resolution</th><th>LEDs</th></tr>'
         '<tr><td>16-bit @ τ = 20 µs</td><td>~1.3 s</td><td>20 µs</td><td>16</td></tr>'
         '<tr style="background:#fffbeb"><td>16-bit @ τ = 200 µs &nbsp;<b>← operating point</b></td><td>~13 s</td><td>200 µs</td><td>16</td></tr></table>')
P.append('<p class="k">Sizing: <code>#codes = range / τ</code>; binary needs <code>ceil(log2(#codes))</code> '
         'LEDs, base-W spatial needs <code>ceil(logW(#codes))</code> digits of W. For a 1&nbsp;s safety range: '
         '<b>16 binary LEDs vs ~50 spatial LEDs</b>. You can interpolate below τ (down to the sensor line '
         'time ~10 µs) using the row where the code increments within a rolling-shutter frame.</p>')

P.append('<h2>4. The coarse scale is mandatory (your disambiguation point)</h2>')
P.append('<p>Without a coarse scale, two cameras can show the <b>identical</b> fine reading while sitting '
         'one fine-wrap period apart. The fix is the <b>vernier / positional-counter</b> principle, the same '
         'trick as Google&rsquo;s slow bottom row (&times;10), the commercial &times;100 row, and a clock&rsquo;s '
         'hour/minute/second hands. In a binary bar you get it for free: the high-order bits <i>are</i> the '
         'slow row, so a 16-bit Gray bar already covers &gt;1&nbsp;s of offset.</p>')
P.append(f'<figure>{DIAGRAMS["vernier"]}</figure>')

P.append("""<h3>Step-time: τ = 200 µs (decided 2026-06-03)</h3>
<p>Match τ to the camera's rolling-shutter line time so each code value spans several rows. The Pixel 7 line time is ≈ 10–20 µs, so <b>200 µs</b> (~10–20 rows per code) is the operating point, not 20 µs.</p>
<ul>
<li><b>The line time is the resolution floor.</b> One frame localises an event to ≈ one row (~10–20 µs); 20 µs already sits on that floor, so a finer step buys nothing the camera can resolve.</li>
<li><b>Fine resolution comes from the rolling shutter, not a tiny step.</b> Fitting code-vs-row over thousands of rows reaches sub-µs precision at any τ. At 200 µs each code spans ~10–20 rows (clean, fittable, blur-tolerant); at 20 µs each spans ~1 row (a 2-row blur is a 2-LSB error).</li>
<li><b>Exposure smear.</b> Fine bits stay crisp only if exposure ≲ τ. 200 µs allows ≤ 1/5000 s (easy against a bright panel); 20 µs would need ≤ 1/50000 s (impractical).</li>
<li><b>Hardware.</b> A <b>static-latch</b> driver (74HC595 shift register) switches cleanly at any τ; PWM drivers (TLC5947, APA102) cannot — their brightness PWM smears the edge.</li>
</ul>
<p><b>Build choice:</b> drive the LEDs with <b>74HC595 shift registers</b> (static latch, no PWM), which switch cleanly at <b>both 200 µs and 20 µs</b>. Operate at 200 µs and cross-validate at 20 µs: two step sizes agreeing on the same offset is a strong validation result. First measure the actual Pixel 7 line time (readout ÷ rows); the sweet spot is τ ≈ 5–15× that.</p>""")
P.append('<h2>5. Electronics</h2>')
P.append(f'<figure>{DIAGRAMS["wiring"]}<figcaption>The chosen build, wired up. Click any photo to open its store page; dashed lines are the optional audit branch.</figcaption></figure>')
P.append('<p>The driver must switch the LEDs <b>statically</b> (no PWM) for a clean edge. That rules out PWM-based '
         'parts (TLC5947, APA102/WS2812) and points to <b>74HC595 shift registers</b> (outputs latch in ~13 ns on RCLK). '
         'LEDs are <b>direct-emission</b> (red/amber/green), <b>never white or PC-amber</b> (phosphor smears the edge). '
         'This static chain handles both 200 µs and 20 µs.</p>')
P.append('<table><tr><th>Driver</th><th>Switching</th><th>Verdict (after datasheet review)</th></tr>'
         '<tr style="background:#fffbeb"><td><b>74HC595 + discrete direct LEDs &nbsp;← chosen</b></td><td>static latch ~13 ns; no PWM</td><td>clean edges at 200 µs <i>and</i> 20 µs; ±6 mA/pin (add ULN2803 for full brightness)</td></tr>'
         '<tr><td>APA102 / DotStar</td><td>8-bit PWM @ ~1 MHz osc</td><td>✗ ~256 µs PWM cycle smears the edge</td></tr>'
         '<tr><td>TLC5947</td><td>12-bit PWM @ 4 MHz osc</td><td>✗ ~1 ms grayscale frame floor — far too slow</td></tr></table>')

P.append('<h2>6. Parts (verified against datasheets)</h2>')
P.append('<div class="gallery">')
P.append(card("commercial-led-panel.png", "IE / Imatest LED-Panel", "$3,980–$57,850",
              "reference device (cloned, not bought)", "https://www.imatest.com/product/camera-timing-system-led-panel/"))
P.append(card("teensy40.jpg", "Teensy 4.0", "~$25–$30",
              "controller · Cortex-M7 @ 600 MHz", "https://www.pjrc.com/store/teensy40.html"))
P.append(card("sn74hc595.jpg", "SN74HC595", "$1.05",
              "static-latch shift register (×2–3); no PWM", "https://www.sparkfun.com/products/13699"))
P.append(card("led-red-10mm.jpg", "Super-bright red 10mm", "~$1",
              "the LEDs · direct AlInGaP, no phosphor (Vf 2.1–2.3 V)", "https://www.sparkfun.com/super-bright-led-red-10mm.html"))
P.append(card("psu-5v4a.jpg", "5 V 4 A supply", "$14.95",
              "powers the LED rail", "https://www.adafruit.com/product/1466"))
P.append(card("saleae-logic8.png", "Saleae Logic 8", "~$199",
              "timing audit (RCLK line); 24 MHz clones ~$10 also work", "https://www.saleae.com/products/logic-8"))
P.append('</div>')
P.append('<h3>Rejected after reading the datasheet</h3>')
P.append('<div class="gallery">')
P.append(card("tlc5947.jpg", "TLC5947 ✗", "$14.95",
              "PWM @ 4 MHz osc → ~1 ms frame floor (too slow)", "https://www.adafruit.com/product/1429"))
P.append(card("dotstar.jpg", "APA102 / DotStar ✗", "$49.95",
              "8-bit PWM @ ~1 MHz → ~256 µs edge smear", "https://www.adafruit.com/product/2241"))
P.append(card("cree-xpe2-amber.jpg", "Cree XP-E2 amber ✗", "$5.14",
              "PC Amber = phosphor (Vf 3.05 V) → smears the edge", "https://www.ledsupply.com/leds/cree-xlamp-xp-e2-color-high-power-led-star"))
P.append('</div>')
P.append('<p class="k">Full running evaluation log (every part considered + its verdict, kept across sessions): <code>wiki/analyses/sync-eval-equipment-log.md</code> in memex.</p>')
P.append('<p class="k">Not pictured (generic): current-limit resistors (one per LED), an optional <b>ULN2803</b> '
         'sink driver for full 20 mA brightness, an optional photodiode for the optical audit (BPW34 ~$1, or '
         'Thorlabs DET10A2 ~$300), and the 3D-printed or acrylic panel frame + diffuser. Ballpark total: '
         '<b>~$120–$180 minimal</b> (the 595 chain is cheaper than the driver-IC paths), <b>~$600–$1,100 cornerstone</b>.</p>')

P.append('<h3>Returns &amp; de-risking (vendor policies checked 2026-06-06)</h3>')
P.append('<table>'
         '<tr><th>Vendor (its parts)</th><th>Window</th><th>Opened but unsuitable</th><th>Defective</th></tr>'
         '<tr style="background:#fffbeb"><td><a href="https://support.saleae.com/180-day-return-policy-and-3-year-warranty">Saleae</a> (analyser)</td><td><b>180 days</b></td><td>full refund incl. shipping (direct purchase only)</td><td>3-year warranty, any cause</td></tr>'
         '<tr><td><a href="https://learn.adafruit.com/how-do-i-return-my-order/adafruit-s-return-policy">Adafruit</a> (5V PSU)</td><td>30 days</td><td><b>unopened only</b>; 5% restock if &#8805;$500</td><td>replaced / refunded</td></tr>'
         '<tr><td><a href="https://www.sparkfun.com/returns">SparkFun</a> (74HC595, red LED)</td><td>30 days</td><td><b>unopened/unused only</b>; restock fee case-by-case</td><td>RMA by email</td></tr>'
         '<tr><td><a href="https://www.pjrc.com/teensy/troubleshoot.html">PJRC</a> (Teensy)</td><td>RMA by email</td><td>no change-of-mind policy</td><td>RMA replacement; buy direct (counterfeit risk)</td></tr>'
         '</table>')
P.append('<p class="k"><b>Takeaway:</b> opened parts that work but do not suit are mostly <b>non-returnable</b> '
         '(Adafruit, SparkFun, and PJRC are unopened/RMA-only); defective items are covered everywhere. So <b>validate with '
         '1&ndash;2 units before bulk-buying</b> (especially the red LEDs, which cannot be returned once opened), and '
         'rely on returns only for the expensive analyser (the Saleae 180-day refund) or genuinely dead parts. '
         'You pay return shipping unless the item is defective. Policies change, so re-check before ordering.</p>')
P.append('<h3>Canadian sourcing (Edmonton)</h3>')
P.append('<p class="k">Buying from within Canada avoids USD exchange, cross-border shipping, and courier '
         'brokerage / customs fees (which can exceed a small order). Suggested split (~CAD, confirm on each page):</p>')
P.append('<table>'
         '<tr><th>Item</th><th>Qty</th><th>Canadian source</th><th>~CAD</th></tr>'
         '<tr><td><a href="https://ca.robotshop.com/products/teensy-40-usb-microcontroller-development-board">Teensy 4.0</a></td><td>1</td><td>RobotShop.ca / ABRA</td><td>~$34</td></tr>'
         '<tr><td><a href="https://www.digikey.ca/en/products/detail/texas-instruments/SN74HC595N/277246">SN74HC595N</a> shift register</td><td>3</td><td>DigiKey.ca / ABRA</td><td>~$2.50 ea</td></tr>'
         '<tr><td>Direct-red 10 mm LED (625 nm AlInGaP)</td><td>~24</td><td>DigiKey.ca / ABRA</td><td>~$12</td></tr>'
         '<tr><td>Resistors + ULN2803 (opt.) + BPW34 (opt.)</td><td>—</td><td>DigiKey.ca / Mouser.ca</td><td>~$10</td></tr>'
         '<tr><td><a href="https://www.digikey.ca/en/products/detail/mean-well-usa-inc/RS-25-5/7706180">Mean Well RS-25-5</a> (5 V 5 A)</td><td>1</td><td>DigiKey.ca / Amazon.ca</td><td>~$20</td></tr>'
         '<tr><td>USB logic analyser (24 MHz clone)</td><td>1</td><td>Amazon.ca</td><td>~$18</td></tr>'
         '<tr><td>Panel substrate + hook-up wire</td><td>—</td><td>Amazon.ca / local</td><td>~$20</td></tr>'
         '</table>')
P.append('<p class="k"><b>One-stop:</b> DigiKey.ca or Mouser.ca for the commodity parts (duties handled, fast to '
         'Alberta), plus ABRA Electronics (Montreal) or RobotShop.ca for the Teensy. Total ≈ $120 CAD. Ordering '
         'US-direct (PJRC / SparkFun / Adafruit) risks courier brokerage fees, so prefer the Canadian sources above.</p>')
P.append('<h2>7. Timing integrity (cornerstone-defensible)</h2>')
P.append('<ul>'
         '<li>The Teensy crystal (±30 ppm) drifts &lt;0.1 ms over a multi-second sweep — ample for sub-ms.</li>'
         '<li>Capture the <b>latch line</b> on a logic analyser and a photodiode on one LED to a scope; record '
         'step period, jitter, rise/fall <b>once</b> as the audit artifact.</li>'
         '<li><b>Cross-validate</b> against an independent method on the same capture (the single-LED edge method, '
         'or Twist-n-Sync gyro sync). Agreement of two independent methods is what makes a DIY instrument publishable.</li>'
         '</ul>')

P.append('<h2>8. Decoding pipeline</h2>')
P.append('<p>Per camera: locate the panel, threshold each LED on/off, decode Gray&rarr;binary&rarr;timestamp; '
         'subtract across cameras for offsets; read the code at the panel&rsquo;s sensor row, optionally '
         'interpolating with the within-frame increment row for ~10 µs resolution. ~100 lines on top of the '
         'existing rig&rsquo;s analysis code.</p>')

P.append('<h2>9. Decisions (resolved)</h2>')
P.append('<ul>'
         '<li><b>Step-time τ = 200 µs</b> operating point; fine timing from the rolling-shutter row fit; cross-validated at 20 µs (see §3).</li>'
         '<li><b>Driver = 74HC595</b> static-latch shift registers (no PWM); the datasheet audit ruled out TLC5947 (~1 ms frame floor) and APA102 (~256 µs PWM smear).</li>'
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
