#!/usr/bin/env python3
"""Build report.html — a short, NeurIPS-styled paper for the LED Timecode Panel.

Reuses build.py's inline-SVG diagrams so the figures can't drift from the design page.
The prose is organized as a paper: Abstract, Introduction, Related Work, System Design,
Evaluation, Conclusion, References, and an Appendix glossary. Visual style follows the
NeurIPS 2025 template (serif single column, rules around the title, centered abstract,
bold numbered sections).

    python3 build_report.py    # -> writes report.html next to index.html
"""
import contextlib
import io
import os
from datetime import datetime

with contextlib.redirect_stdout(io.StringIO()):   # build.py prints + writes index.html
    import build                                    # exposes DIAGRAMS, svg_wiring_c, svg_blink

D = build.DIAGRAMS

# NeurIPS-style look: serif (Times) single column, rules around the title, a centered
# narrow abstract, bold numbered sections, a reference list. The column is 900 px so the
# side-by-side figures still fit without wrapping.
CSS = """
html,body{margin:0;padding:0;background:#fff;}
body{font-family:'Times New Roman',Times,Georgia,serif;font-size:16px;color:#111;line-height:1.55;max-width:900px;margin:0 auto;padding:22px 26px 56px;}
a{color:#1a4fa0;text-decoration:none;}
a:hover{text-decoration:underline;}
.nav{font-family:Georgia,serif;font-size:13px;color:#666;margin:0 0 6px;}
hr.rule{border:0;border-top:2.5px solid #000;margin:6px 0;}
h1.title{font-size:26px;font-weight:bold;text-align:center;line-height:1.28;margin:14px 0;}
.authors{text-align:center;font-size:16px;margin:12px 0 2px;}
.affil{text-align:center;font-size:13px;color:#777;margin:0;}
.abstract-h{text-align:center;font-size:16px;font-weight:bold;margin:26px 0 8px;}
.abstract{max-width:660px;margin:0 auto;font-size:15px;line-height:1.5;}
.abstract p{text-align:justify;margin:0;}
h2{font-size:18px;font-weight:bold;margin:28px 0 8px;}
h3{font-size:15.5px;font-weight:bold;margin:18px 0 6px;}
p{line-height:1.55;margin:10px 0;text-align:justify;}
figure{margin:18px 0;text-align:center;}
figure svg,figure img,figure video{max-width:100%;height:auto;}
figcaption{font-size:13px;color:#444;line-height:1.45;margin-top:6px;text-align:left;}
ol.refs{font-size:14px;line-height:1.5;padding-left:22px;}
ol.refs li{margin:5px 0;}
table{border-collapse:collapse;width:100%;font-size:14px;margin:14px 0;}
th,td{border:1px solid #ccc;padding:6px 10px;text-align:left;vertical-align:top;}
th{background:#f2f2f2;font-weight:bold;}
.footer{font-family:Georgia,serif;font-size:12px;color:#777;text-align:center;margin-top:10px;}
"""
OUT = os.path.join(os.path.dirname(build.OUT), "report.html")

# Report-only diagram titles (the design page keeps the "Option C" / "Step 0" wording).
WIRING = build.svg_wiring_c(
    title="Breadboard wiring",
    subtitle="Controller on the right; the seven outputs form an LED row on the left.")
BLINK = build.svg_blink(title="The simplest test — one LED, one resistor, one jumper")


def fig(svg, cap):
    return f"<figure>{svg}<figcaption>{cap}</figcaption></figure>"


def clip(src, cap, style):
    return (f'<figure><video src="{src}" autoplay loop muted playsinline '
            f'style="{style};border:1px solid #ccc;border-radius:6px;display:block"></video>'
            f"<figcaption>{cap}</figcaption></figure>")


def pair(a, wa, b, wb, grow=1):
    """Two items side by side (diagram | built), each in a flex column of basis wa/wb px,
    keeping its own caption; flex-wrap keeps it responsive on small screens."""
    cell = '<div style="flex:{g} 1 {w}px;min-width:0">{c}</div>'
    return ('<div style="display:flex;gap:22px;flex-wrap:wrap;align-items:flex-start;'
            'justify-content:center;margin:16px 0">'
            + cell.format(g=grow, w=wa, c=a) + cell.format(g=grow, w=wb, c=b)
            + "</div>")


P = []

# --- Title block (NeurIPS: thick rules above/below the title, centered authors) ---
P.append("<p class='nav'><a href='https://yuboshell.github.io/'>&larr; Home</a></p>")
P.append("<hr class='rule'>")
P.append("<h1 class='title'>An LED Timecode Panel for Sub-Millisecond<br>"
         "Multi-Camera Synchronization Evaluation</h1>")
P.append("<hr class='rule'>")
P.append("<p class='authors'>Yubo&nbsp;Huang &nbsp;&nbsp; Antonio&nbsp;Neves &nbsp;&nbsp; "
         "Jun&nbsp;Zhou &nbsp;&nbsp; Pengyu&nbsp;Zhang &nbsp;&nbsp; Li&nbsp;Cheng</p>")
P.append("<p class='affil'>Affiliations to be added</p>")
P.append("<p class='affil' style='margin-top:5px'>Code: "
         "<a href='https://github.com/yuboshell/led-sync-panel'>github.com/yuboshell/led-sync-panel</a></p>")

# --- Abstract ---
P.append("<div class='abstract-h'>Abstract</div>")
P.append("<div class='abstract'><p>Multi-camera capture &mdash; motion-capture stages, light-stage "
         "domes, phone arrays &mdash; depends on every camera's shutter firing at the same instant, yet "
         "recent large datasets report synchronized capture without ever measuring the residual error. We "
         "present a small, self-built <b>LED timecode panel</b> that makes that error directly observable: a "
         "flat panel of LEDs displays a fast-advancing, Gray-coded timecode that every camera decodes per "
         "frame, so the difference between what two cameras read at the same instant is precisely their "
         "synchronization error. The rig is neat, affordable, and customizable, and currently resolves "
         "inter-camera offset to <b>sub-millisecond</b> precision (0.5&nbsp;ms). Beyond measuring today's "
         "rigs, it can serve as a reference signal for developing event-based synchronization methods."
         "</p></div>")

# --- 1 Introduction ---
P.append("<h2>1&nbsp;&nbsp;Introduction</h2>")
P.append("<p>Multi-camera rigs only work if every camera's shutter fires at the same instant. Yet recent "
         "large capture datasets report synchronized capture <i>without ever measuring the error</i>: "
         "<b>HumanOLAT</b> (ICCV&nbsp;2025, 40&nbsp;cameras) and <b>MVHumanNet</b> (CVPR&nbsp;2024, "
         "48&nbsp;cameras) both claim synchronization but publish no number for it. Without a measurement a "
         "sync-quality claim is unverifiable &mdash; so a trustworthy <i>evaluation</i> tool is the "
         "prerequisite for any work that hopes to <i>improve</i> synchronization.</p>")
P.append("<p>We build such a tool. A row of LEDs shows a fast-advancing timecode &mdash; a number that "
         "ticks up thousands of times a second; every camera pointed at the panel reads that number off "
         "each frame it captures, and comparing what two cameras read at the same moment reveals how far "
         "apart their shutters actually fired. Our contributions are: (i)&nbsp;a low-cost, self-built LED "
         "timecode panel that measures inter-camera synchronization directly from the captured video; "
         "(ii)&nbsp;a latched, Gray-coded design that stays robust when a frame's exposure straddles a "
         "transition; and (iii)&nbsp;a working demonstration resolving inter-camera offset to 0.5&nbsp;ms on "
         "a two-camera rig.</p>")

# --- 2 Related Work (Twist-n-Sync trimmed to a one-line mention) ---
P.append("<h2>2&nbsp;&nbsp;Related Work</h2>")
P.append("<p>The closest analogue is <b>libsoftwaresync</b> (Google, ICCP&nbsp;2019), a 10&times;10 LED "
         "panel that encodes time by <i>position</i> on the grid and reaches ~200&nbsp;&micro;s. Other "
         "LED-based rigs (e.g. <b>Twist-n-Sync</b>, MDPI&nbsp;Sensors&nbsp;2021) and camera-side "
         "post-processing (subframe alignment, VISAPP&nbsp;2017) target a "
         "different setting or act at the wrong layer &mdash; aligning already-recorded video rather than "
         "the capture itself. None is a drop-in evaluation tool for a small, reconfigurable multi-camera "
         "rig, which is the gap this panel fills.</p>")

# --- 3 System Design ---
P.append("<h2>3&nbsp;&nbsp;System Design</h2>")
P.append("<h3>3.1&nbsp;&nbsp;A minimal test: blink one LED</h3>")
P.append("<p>The smallest possible test: the microcontroller (a Raspberry&nbsp;Pi Pico) drives <b>one</b> "
         "LED through <b>one</b> resistor to ground. If it blinks, the code, the board, and the wiring are "
         "all sound &mdash; a foundation to build on.</p>")
P.append(pair(
    fig(BLINK, "<b>Figure&nbsp;1: The blink test.</b> One Pico pin &rarr; a 240&nbsp;&Omega; resistor "
        "&rarr; the LED &rarr; ground."), 344,
    clip("assets/report/blink.mp4", "<b>Built and running.</b> One LED blinking on the breadboard.",
         "width:100%"), 325,
    grow=0))
P.append("<h3>3.2&nbsp;&nbsp;Driving seven LEDs with a shift register</h3>")
P.append("<p>To drive several LEDs from just a few pins, the Pico feeds a <b>shift-register chip</b>, which "
         "turns three control wires into eight independent on/off outputs. Seven of those outputs each "
         "light an LED through a 240&nbsp;&Omega; resistor, and the seven on/off states together form one "
         "number: the timecode. That number is shown in <b>Gray code</b> &mdash; a counting scheme in which "
         "only <b>one</b> LED changes from one step to the next &mdash; so a frame that happens to catch a "
         "change still reads a clean value (off by at most one), never a scrambled one.</p>")
P.append(fig(D["schematic"], "<b>Figure&nbsp;2: Circuit schematic.</b> Pico &rarr; shift-register chip "
             "&rarr; seven (240&nbsp;&Omega; + LED) branches."))
P.append(pair(
    fig(WIRING, "<b>Figure&nbsp;3: Breadboard wiring.</b> The Pico and the driver chip share one strip; "
        "their seven outputs form a single clean row of LEDs."), 475,
    clip("assets/report/panel.mp4", "<b>Built and running.</b> The seven-LED panel running the timecode "
         "(filmed at a 50&nbsp;ms step).", "width:100%"), 335,
    grow=1))

# --- 4 Evaluation ---
P.append("<h2>4&nbsp;&nbsp;Evaluation</h2>")
P.append("<h3>4.1&nbsp;&nbsp;What the two cameras filmed</h3>")
P.append("<p>Before the analysis, the raw input. These are the last 100 frames of a two-camera clip, with "
         "each camera's frame paired to the other camera's nearest frame in time and played side by side, so "
         "every pair shows the same moment seen twice. The timecode steps every 0.5&nbsp;ms here (the "
         "panel's fastest setting), and both cameras film with a matching 0.5&nbsp;ms exposure &mdash; short "
         "enough to freeze each fast-changing pattern into a clean, readable frame. The lit pattern tracks "
         "together across both views; the small residual difference is what the decode measures.</p>")
P.append(clip("assets/report/last100_twocam.mp4",
         "<b>Figure&nbsp;4: Last 100 synchronized frames</b> (left: camera&nbsp;1, right: camera&nbsp;2), "
         "paired by nearest capture time. The bright cluster is the LED panel each camera reads.",
         "width:100%"))
P.append("<h3>4.2&nbsp;&nbsp;Inter-camera offset across the clip</h3>")
P.append("<p>With two cameras pointed at the running panel, every frame each one captures carries a "
         "readable timecode, so the gap between what the two cameras read at the same instant is how far "
         "apart their shutters actually fired: their <b>synchronization error</b>. We measure it not once "
         "but at six points spread across a full 60&nbsp;s clip &mdash; five frames around each 10&nbsp;s "
         "mark. The offset is the same everywhere, about <b>+2&nbsp;ms</b>: a stable, repeatable error, not "
         "drift.</p>")
P.append(fig(
    "<img src='assets/report/sampled_across_video.jpg' alt='Five frames around each 10 s mark' "
    "style='display:block;width:100%;border:1px solid #ccc;border-radius:6px'>",
    "<b>Figure&nbsp;5: The offset holds across the clip.</b> Five frames around each of the "
    "10/20/30/40/50/60&nbsp;s marks. Each cell shows the two cameras' LED crops (one above the other), the "
    "timecode each decoded, and the resulting per-frame offset &mdash; about +2&nbsp;ms throughout."))

# --- 5 Conclusion and Future Work ---
P.append("<h2>5&nbsp;&nbsp;Conclusion and Future Work</h2>")
P.append("<p>We have built and validated a compact LED timecode panel that makes inter-camera "
         "synchronization error directly measurable, demonstrating 0.5&nbsp;ms resolution on a two-camera "
         "rig. The immediate next step is scaling the evaluation to the full 11-camera Pixel&nbsp;7 / Argus "
         "rig, targeting millisecond resolution at that scale. Because the panel emits a fast, decodable "
         "timing signal, it also makes a natural reference for developing and benchmarking <b>event-based</b> "
         "synchronization methods.</p>")

# --- References (placeholders — full bibliographic details to be completed) ---
P.append("<h2>References</h2>")
REFS = [
    "libsoftwaresync &mdash; Wireless software synchronization of multiple distributed cameras. ICCP&nbsp;2019 (Google).",
    "Twist-n-Sync &mdash; software time synchronization. MDPI&nbsp;Sensors, 2021.",
    "Subframe temporal alignment of multi-view video. VISAPP&nbsp;2017.",
    "HumanOLAT &mdash; a large multi-view relightable human-capture dataset. ICCV&nbsp;2025.",
    "MVHumanNet &mdash; a large-scale multi-view human-capture dataset. CVPR&nbsp;2024.",
]
P.append("<ol class='refs'>" + "".join(f"<li>{r}</li>" for r in REFS) + "</ol>")
P.append("<p class='footer'>References are placeholders &mdash; author names, titles, and page numbers "
         "still to be filled in.</p>")

# --- Appendix A: Glossary (plain-language definitions for a general reader) ---
P.append("<h2>Appendix&nbsp;A&nbsp;&nbsp;Glossary</h2>")
P.append("<p>Every technical term and diagram label above, in plain language.</p>")
GLOSSARY = [
    ("Microcontroller", "A tiny computer on a single chip. Here it&rsquo;s a Raspberry&nbsp;Pi Pico, which runs the code that drives the LEDs."),
    ("Raspberry Pi Pico", "The microcontroller board used &mdash; the &ldquo;controller&rdquo; in the diagrams."),
    ("Breadboard", "A reusable board for wiring circuits by pushing parts into rows of holes &mdash; no soldering."),
    ("LED", "Light-emitting diode &mdash; the small lights that show the code."),
    ("Resistor (240&nbsp;&Omega;)", "Limits the current through an LED so it lights safely; &Omega; (ohm) is the unit of resistance."),
    ("Shift register (74HC595)", "A chip that turns a few control wires into many on/off outputs &mdash; here, three wires from the Pico into eight outputs. The &ldquo;driver chip.&rdquo;"),
    ("Timecode", "A number that counts up at a steady, known rate. Read it off a camera frame and you know when that frame was captured."),
    ("Gray code", "A way of counting in which only one bit (one LED) changes between consecutive values &mdash; so a frame catching a mid-change still reads a clean value, off by at most one."),
    ("Synchronization error", "How far apart two cameras&rsquo; shutters actually fired for &ldquo;the same&rdquo; frame &mdash; what the panel measures."),
    ("GP15, GP17&ndash;GP19", "Numbered general-purpose pins on the Pico. GP15 drives the single blink LED; GP17&ndash;GP19 carry the three control signals to the shift register."),
    ("SER, SRCLK, RCLK", "The shift register&rsquo;s three control inputs &mdash; SER: data in; SRCLK: shift clock (loads each bit); RCLK: latch clock (shows the whole byte on the outputs at once)."),
    ("QA, QB&ndash;QH", "The shift register&rsquo;s eight outputs. QB&ndash;QH each light one LED (seven in all); QA is unused."),
    ("OE, MR", "Output&nbsp;Enable and Master&nbsp;Reset &mdash; tied to the levels that keep the outputs on and stop the chip from resetting."),
    ("VCC, GND, 3V3", "Power and ground: VCC = the chip&rsquo;s supply; GND = 0&nbsp;V (the common return); 3V3 = the Pico&rsquo;s 3.3&nbsp;V output, which powers the chip."),
]
P.append("<table><tr><th>Term</th><th>Meaning</th></tr>"
         + "".join(f"<tr><td><b>{t}</b></td><td>{d}</td></tr>" for t, d in GLOSSARY)
         + "</table>")

# --- Footer ---
P.append("<hr class='rule' style='border-top-width:1px;margin-top:24px'>")
P.append(f"<p class='footer'>Updated {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')} "
         "&middot; <a href='index.html'>Full design &amp; build log</a></p>")

html = ("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>An LED Timecode Panel for Multi-Camera Synchronization Evaluation</title>"
        f"<style>{CSS}</style></head><body>{''.join(P)}</body></html>")

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print(f"WROTE {OUT} ({len(html)} bytes)")
