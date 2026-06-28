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

with contextlib.redirect_stdout(io.StringIO()):   # build.py prints + writes index.html
    import build                                    # exposes CSS, DIAGRAMS, svg_wiring_c

D, CSS = build.DIAGRAMS, build.CSS
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


def row(*items):
    return ('<div style="display:flex;gap:22px;flex-wrap:wrap;align-items:flex-start;'
            'margin:14px 0">' + "".join(items) + "</div>")


P = []
P.append("<h1>LED Timecode Panel</h1>")
P.append('<p style="font-size:18px;color:#475569;font-weight:500;margin:-4px 0 12px">'
         "Build report &mdash; the design, and the hardware working.</p>")
P.append('<p class="k" style="margin:0 0 18px"><a href="index.html">&larr; Full design &amp; build log</a></p>')
P.append('<p class="lead">A row of LEDs shows a fast-advancing <b>timecode</b> &mdash; a number that '
         "ticks up many times a second. Every camera pointed at the panel can read that number off each "
         "frame it captures, so comparing what two cameras read at the same moment shows how far apart "
         "their shutters actually fired &mdash; their synchronization error.</p>")

# 1 — Step 0
P.append("<h2>Blink one LED</h2>")
P.append('<p class="k">The smallest possible test: the microcontroller (a Raspberry&nbsp;Pi Pico) drives '
         "<b>one</b> LED through <b>one</b> resistor to ground. If it blinks, the code, the board, and the "
         "wiring are all good &mdash; a foundation to build on.</p>")
P.append(row(
    fig(BLINK, "<b>Figure 1. The blink test.</b> One Pico pin &rarr; a 240&nbsp;&Omega; resistor "
        "&rarr; the LED &rarr; ground."),
    clip("assets/report/blink.mp4", "<b>Built and running.</b> One LED blinking on the breadboard.",
         "max-height:340px"),
))

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
P.append(row(
    fig(WIRING, "<b>Figure 3. Breadboard wiring.</b> The Pico and the driver chip share one strip; their "
        "seven outputs form a single clean row of LEDs."),
    clip("assets/report/panel.mp4", "<b>Built and running.</b> The seven-LED panel running the timecode "
         "(filmed at a 50&nbsp;ms step).", "max-height:420px"),
))

# 3 — glossary (makes the diagram labels readable without any project context)
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
        f"<style>{CSS}</style></head><body>{''.join(P)}</body></html>")

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print(f"WROTE {OUT} ({len(html)} bytes)")
