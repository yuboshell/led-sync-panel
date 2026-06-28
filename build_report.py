#!/usr/bin/env python3
"""Build report.html — a concise build report for the LED Timecode Panel.

Reuses build.py's inline-SVG DIAGRAMS and CSS, so the report can never drift from
the design page. Importing build also re-validates the SVGs and regenerates index.html.

    python3 build_report.py    # -> writes report.html next to index.html
"""
import contextlib
import io
import os

with contextlib.redirect_stdout(io.StringIO()):   # build.py prints "SVG ok …" + writes index.html
    import build                                    # exposes CSS + DIAGRAMS (errors still raise)

D, CSS = build.DIAGRAMS, build.CSS
OUT = os.path.join(os.path.dirname(build.OUT), "report.html")


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
P.append('<p class="lead">A row of LEDs shows a fast-advancing, camera-decodable <b>Gray timecode</b>. '
         "Every camera filming the panel reads its own capture instant from it, so the per-frame "
         "differences between cameras are their synchronization error.</p>")

# 1 — Step 0
P.append("<h2>Step 0 &mdash; blink one LED</h2>")
P.append('<p class="k">The smallest possible test: the Pico drives <b>one</b> LED through <b>one</b> '
         "resistor to ground. If it blinks, the toolchain, board, and wiring are all good.</p>")
P.append(row(
    fig(D["blink"], "<b>Figure 1. Simplest blink.</b> GP15 &rarr; 240&nbsp;&Omega; &rarr; LED &rarr; GND."),
    clip("assets/report/blink.mp4", "<b>The real thing.</b> One LED blinking on the breadboard.",
         "max-height:340px"),
))

# 2 — current circuit
P.append("<h2>The current circuit</h2>")
P.append('<p class="k">A <b>74HC595</b> shift register, driven by the Pico over three SPI wires '
         "(<b>SER</b>, <b>SRCLK</b>, <b>RCLK</b>), latches a byte to seven outputs "
         "(<b>QB&ndash;QH</b>), each lighting an LED through 240&nbsp;&Omega; &mdash; the timecode "
         "the cameras read.</p>")
P.append(fig(D["schematic"],
             "<b>Figure 2. Circuit schematic.</b> Pico &rarr; 74HC595 &rarr; "
             "7&times;(240&nbsp;&Omega; + LED); QA unused."))
P.append(row(
    fig(D["wiring_c"],
        "<b>Figure 3. Option C breadboard layout.</b> Pico + 595 on one strip; "
        "the seven outputs make one clean LED row."),
    clip("assets/report/panel.mp4",
         "<b>The real thing.</b> The 7-LED panel running the Gray timecode "
         "(filmed at a 50&nbsp;ms step).",
         "max-width:420px"),
))

html = ("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>LED Timecode Panel &mdash; build report</title>"
        f"<style>{CSS}</style></head><body>{''.join(P)}</body></html>")

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print(f"WROTE {OUT} ({len(html)} bytes)")
