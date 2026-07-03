#!/usr/bin/env python3
"""Build report.html — a concise, SELF-CONTAINED build report for the LED Timecode Panel.

Reuses build.py's inline-SVG diagrams and CSS so the report can't drift from the design
page. Self-contained means: no design-page-only terms (e.g. no "Option C"), and the
jargon a general reader wouldn't know (shift register, Gray code, microcontroller) is
glossed where it appears.

    python3 build_report.py    # -> writes report.html next to index.html
"""
import contextlib
import io
import os
from datetime import datetime

with contextlib.redirect_stdout(io.StringIO()):   # build.py prints + writes index.html
    import build                                    # exposes CSS, DIAGRAMS, svg_wiring_c

D = build.DIAGRAMS

# Styling matches Yubo's homepage (Jon Barron / Leonid Keselman template): Lato, blue
# #1772d0 links, white background, a centered single column. Width is 1040 px (wider than
# the homepage's 800 px) so the report's side-by-side figures fit, not stack. Replaces the
# design page's denser CSS so the report reads like the rest of the site.
CSS = """
html,body{margin:0;padding:0;background:#fff;}
body{font-family:'Lato',Verdana,Helvetica,sans-serif;font-size:14px;color:#000;line-height:1.5;max-width:1040px;margin:0 auto;padding:22px 18px 64px;}
a{color:#1772d0;text-decoration:none;}
a:hover,a:focus{color:#f09228;}
h1{font-family:'Lato',Verdana,Helvetica,sans-serif;font-size:32px;font-weight:normal;text-align:center;margin:16px 0 4px;}
h2{font-family:'Lato',Verdana,Helvetica,sans-serif;font-size:22px;font-weight:normal;margin:30px 0 8px;}
h3{font-family:'Lato',Verdana,Helvetica,sans-serif;font-size:16px;font-weight:700;margin:18px 0 6px;}
p{line-height:1.5;margin:10px 0;}
.lead{font-size:15px;}
.k{color:#555;}
figure{margin:18px 0;text-align:center;}
figure svg,figure img,figure video{max-width:100%;height:auto;}
figcaption{font-size:13px;color:#555;line-height:1.45;margin-top:6px;text-align:left;}
table{border-collapse:collapse;width:100%;font-size:14px;margin:14px 0;}
th,td{border:1px solid #e5e7eb;padding:6px 10px;text-align:left;vertical-align:top;}
th{background:#f6f7f9;font-weight:700;}
"""
OUT = os.path.join(os.path.dirname(build.OUT), "report.html")

# A report-only breadboard diagram with a plain title. The design page's copy keeps the
# "Option C" title (where Options A/B/C are actually compared); the report never sees it.
WIRING = build.svg_wiring_c(
    title="Breadboard wiring",
    subtitle="Controller on the right; the seven outputs form an LED row on the left.")
BLINK = build.svg_blink(title="The simplest test — one LED, one resistor, one jumper")


def fig(svg, cap):
    return f"<figure>{svg}<figcaption>{cap}</figcaption></figure>"


def clip(src, cap, style):
    return (f'<figure><video src="{src}" autoplay loop muted playsinline '
            f'style="{style};border:1px solid #e5e7eb;border-radius:8px;display:block"></video>'
            f"<figcaption>{cap}</figcaption></figure>")


def pair(a, wa, b, wb, grow=1):
    """Diagram | built, side by side. Each goes in a flex column of basis wa/wb px,
    keeping its own caption. The basis widths are chosen so the two render at equal
    height (diagram-aspect vs clip-aspect). grow=1 fills the column proportionally
    (a wide SVG shrinks to its share); grow=0 keeps narrow art at natural width,
    centered. min-width:0 + flex-wrap keeps it responsive on small screens."""
    cell = '<div style="flex:{g} 1 {w}px;min-width:0">{c}</div>'
    return ('<div style="display:flex;gap:22px;flex-wrap:wrap;align-items:flex-start;'
            'justify-content:center;margin:14px 0">'
            + cell.format(g=grow, w=wa, c=a) + cell.format(g=grow, w=wb, c=b)
            + "</div>")


P = []
P.append("<p style='margin:0 0 .6rem'><a href='https://yuboshell.github.io/'>&larr; Home</a></p>")
P.append("<h1>LED Timecode Panel</h1>")
P.append('<p style="text-align:center;font-size:15px;margin:4px 0">'
         "Build report &mdash; the design, and the hardware working</p>")
P.append('<p style="text-align:center;font-size:16px;margin:12px 0 2px">'
         "Yubo&nbsp;Huang, Antonio&nbsp;Neves, Jun&nbsp;Zhou, Pengyu&nbsp;Zhang, Li&nbsp;Cheng</p>")
P.append(f'<p class="k" style="text-align:center;font-size:12px;margin:2px 0 2px">updated '
         f'{datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")}</p>')
P.append('<p class="k" style="text-align:center;margin:0 0 26px"><a href="index.html">&larr; Full design &amp; build log</a></p>')
P.append('<p class="lead">A row of LEDs shows a fast-advancing <b>timecode</b> &mdash; a number that '
         "ticks up many times a second. Every camera pointed at the panel can read that number off each "
         "frame it captures, so comparing what two cameras read at the same moment shows how far apart "
         "their shutters actually fired &mdash; their synchronization error.</p>")

# 0.5 — Background (the paper's motivation + prior-work landscape)
P.append("<h2>Background</h2>")
P.append("<p>Multi-camera rigs &mdash; motion-capture stages, light-stage domes, phone arrays &mdash; "
         "only work if every camera's shutter fires at the same instant. Yet recent large capture "
         "datasets report synchronized capture <i>without ever measuring the error</i>: "
         "<b>HumanOLAT</b> (ICCV&nbsp;2025, 40&nbsp;cameras) and <b>MVHumanNet</b> (CVPR&nbsp;2024, "
         "48&nbsp;cameras) both claim sync but publish no number for it. Without a measurement a "
         "sync-quality claim is unverifiable &mdash; so a trustworthy <i>evaluation</i> tool is the "
         "prerequisite for any work that tries to <i>improve</i> synchronization.</p>")
P.append("<p>A handful of tools come close, but none is a ready fit. <b>libsoftwaresync</b> "
         "(Google, ICCP&nbsp;2019) is a 10&times;10 LED panel that encodes time by <i>position</i> on the "
         "grid, reaching ~200&nbsp;&micro;s. <b>Twist-n-Sync</b> (MDPI&nbsp;Sensors&nbsp;2021) uses an LED "
         "strip read out by the camera's <b>rolling shutter</b> &mdash; a camera exposes the image one row "
         "at a time, top to bottom, so a brief flash lands on a specific row, pinning timing to finer than "
         "one video frame. <b>RecSync</b> (IEEE&nbsp;Sensors&nbsp;2021) and subframe post-processing "
         "(VISAPP&nbsp;2017) either need special hardware or act at the wrong layer &mdash; aligning "
         "already-recorded video rather than the capture itself.</p>")
P.append("<p>This project &mdash; the <b>LED timecode panel</b> described below &mdash; is a small, "
         "self-built entry in that lineage: neat, affordable, and customizable, and currently resolving "
         "inter-camera offset to <b>sub-millisecond</b> (0.5&nbsp;ms). Beyond measuring today's rigs, it "
         "can serve as a reference signal for developing <b>event-based</b> synchronization methods.</p>")

# 1 — Step 0
P.append("<h2>Blink one LED</h2>")
P.append('<p class="k">The smallest possible test: the microcontroller (a Raspberry&nbsp;Pi Pico) drives '
         "<b>one</b> LED through <b>one</b> resistor to ground. If it blinks, the code, the board, and the "
         "wiring are all good &mdash; a foundation to build on.</p>")
P.append(pair(
    fig(BLINK, "<b>Figure 1. The blink test.</b> One Pico pin &rarr; a 240&nbsp;&Omega; resistor "
        "&rarr; the LED &rarr; ground."), 344,
    clip("assets/report/blink.mp4", "<b>Built and running.</b> One LED blinking on the breadboard.",
         "width:100%"), 325,
    grow=0))

# 2 — the circuit
P.append("<h2>The circuit</h2>")
P.append('<p class="k">To drive several LEDs from just a few pins, the Pico feeds a '
         "<b>shift-register chip</b> &mdash; it turns three control wires into eight independent on/off "
         "outputs. Seven of those outputs each light an LED through a 240&nbsp;&Omega; resistor, and the "
         "seven on/off states together form one number: the timecode.</p>")
P.append('<p class="k">That number is shown in <b>Gray code</b> &mdash; a counting scheme in which only '
         "<b>one</b> LED changes from one step to the next. So a camera frame that happens to catch a "
         "change still reads a clean value (off by at most one), never a scrambled one.</p>")
P.append(fig(D["schematic"], "<b>Figure 2. Circuit schematic.</b> Pico &rarr; shift-register chip &rarr; "
             "seven (240&nbsp;&Omega; + LED) branches."))
P.append(pair(
    fig(WIRING, "<b>Figure 3. Breadboard wiring.</b> The Pico and the driver chip share one strip; their "
        "seven outputs form a single clean row of LEDs."), 475,
    clip("assets/report/panel.mp4", "<b>Built and running.</b> The seven-LED panel running the timecode "
         "(filmed at a 50&nbsp;ms step).", "width:100%"), 335,
    grow=1))

# 3 — the raw synchronized footage the analysis runs on (preface to the capture analysis)
P.append("<h2>What the two cameras filmed</h2>")
P.append('<p class="k">Before the analysis, the raw input. These are the last 100 frames of the clip, with '
         "each camera&rsquo;s frame paired to the other camera&rsquo;s nearest frame in time and played side "
         "by side &mdash; so every pair shows the same moment, seen twice. The timecode steps every "
         "0.5&nbsp;ms here (the panel&rsquo;s fastest setting), and both cameras film with a matching "
         "0.5&nbsp;ms exposure &mdash; short enough to freeze each fast-changing pattern into a clean, "
         "readable frame. The lit pattern tracks together across both views; the small residual difference "
         "is what the decode below measures.</p>")
P.append(clip("assets/report/last100_twocam.mp4",
         "<b>Last 100 synchronized frames &mdash; left: camera&nbsp;1, right: camera&nbsp;2.</b> Paired by "
         "nearest capture time; the bright cluster is the LED panel each camera reads. The decode below "
         "turns this footage into a per-frame offset.",
         "width:100%"))

# 4 — the panel actually measuring camera sync (the payoff; adapted to stand alone here)
P.append("<h2>Sampled across the whole video</h2>")
P.append('<p class="k">The payoff. With two cameras pointed at the running panel, every frame each one '
         "captures carries a readable timecode &mdash; so the gap between what the two cameras read at the "
         "same instant is how far apart their shutters actually fired: their <b>synchronization error</b>. "
         "Below it is measured not once but at six points spread across a full 60&nbsp;s clip &mdash; five "
         "frames around each 10&nbsp;s mark (10, 20, &hellip; 60&nbsp;s). The offset is the same everywhere, "
         "about <b>+2&nbsp;ms</b>, not just at the end.</p>")
P.append(fig(
    '<img src="assets/report/sampled_across_video.jpg" alt="Five frames around each 10 s mark" '
    'style="display:block;width:100%;border:1px solid #e5e7eb;border-radius:8px">',
    "<b>Figure 4. The offset holds across the clip.</b> Five frames around each of the "
    "10/20/30/40/50/60&nbsp;s marks. Each cell shows the two cameras&rsquo; LED crops (one above the "
    "other), the timecode each one decoded, and the resulting per-frame offset. Every frame at every "
    "mark reads about +2&nbsp;ms &mdash; a stable, repeatable sync error, not drift."))

# 5 — glossary (makes the diagram labels readable without any project context)
P.append("<h2>Glossary</h2>")
P.append('<p class="k">Every term and label that appears above, in plain language.</p>')
GLOSSARY = [
    ("Microcontroller", "A tiny computer on a single chip. Here it&rsquo;s a Raspberry&nbsp;Pi Pico, which runs the code that drives the LEDs."),
    ("Raspberry Pi Pico", "The microcontroller board used &mdash; the &ldquo;controller&rdquo; in the diagrams."),
    ("Breadboard", "A reusable board for wiring circuits by pushing parts into rows of holes &mdash; no soldering."),
    ("LED", "Light-emitting diode &mdash; the small lights that show the code."),
    ("Resistor (240&nbsp;&Omega;)", "Limits the current through an LED so it lights safely; &Omega; (ohm) is the unit of resistance."),
    ("Shift register (74HC595)", "A chip that turns a few control wires into many on/off outputs &mdash; here, three wires from the Pico into eight outputs. The &ldquo;driver chip.&rdquo;"),
    ("Timecode", "A number that counts up at a steady, known rate. Read it off a camera frame and you know when that frame was captured."),
    ("Gray code", "A way of counting in which only one bit (one LED) changes between consecutive values &mdash; so a frame catching a mid-change still reads a clean value, off by at most one."),
    ("Synchronization error", "How far apart two cameras&rsquo; shutters actually fired for &ldquo;the same&rdquo; frame &mdash; what the panel measures. Read the timecode off each camera at the same instant and the difference is the sync error."),
    ("GP15, GP17&ndash;GP19", "Numbered general-purpose pins on the Pico. GP15 drives the single blink LED; GP17&ndash;GP19 carry the three control signals to the shift register."),
    ("SER, SRCLK, RCLK", "The shift register&rsquo;s three control inputs &mdash; SER: data in; SRCLK: shift clock (loads each bit); RCLK: latch clock (shows the whole byte on the outputs at once)."),
    ("QA, QB&ndash;QH", "The shift register&rsquo;s eight outputs. QB&ndash;QH each light one LED (seven in all); QA is unused."),
    ("OE, MR", "Output&nbsp;Enable and Master&nbsp;Reset &mdash; tied to the levels that keep the outputs on and stop the chip from resetting."),
    ("VCC, GND, 3V3", "Power and ground: VCC = the chip&rsquo;s supply; GND = 0&nbsp;V (the common return); 3V3 = the Pico&rsquo;s 3.3&nbsp;V output, which powers the chip."),
]
P.append('<table><tr><th>Term</th><th>Meaning</th></tr>'
         + "".join(f"<tr><td><b>{t}</b></td><td>{d}</td></tr>" for t, d in GLOSSARY)
         + "</table>")

html = ("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>LED Timecode Panel &mdash; build report</title>"
        "<link href='https://fonts.googleapis.com/css?family=Lato:400,700,400italic,700italic' rel='stylesheet'>"
        f"<style>{CSS}</style></head><body>{''.join(P)}</body></html>")

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print(f"WROTE {OUT} ({len(html)} bytes)")
