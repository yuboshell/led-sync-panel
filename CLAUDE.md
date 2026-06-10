# led-sync-panel

The design doc for a **multi-camera sync-evaluation LED time-code panel** — a flat
panel of LEDs showing a fast-advancing, decodable time code, filmed by all cameras
at once so per-frame decode gives the inter-camera offset. Built for Yubo's
11×Pixel 7 / Argus motion-capture rig. Split out of `memex` into its own repo on
2026-06-07; public on GitHub since 2026-06-10
(https://github.com/yubohuangai/led-sync-panel, doc served via GitHub Pages).

## What's here
- `build.py` — **the source of truth.** A Python builder that generates `index.html`:
  a self-contained illustrated design doc with inline SVG diagrams and product
  photos from `assets/`.
- `index.html` — the generated doc. **Do not hand-edit it; edit `build.py` and rebuild.**
- `assets/` — product photos used in the doc.

## Build & verify
```
python3 build.py        # validates every inline SVG with xml.etree, then writes index.html
```
To check rendering, screenshot a diagram or the page with headless Chrome, e.g.:
```
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --screenshot=/tmp/doc.png --window-size=940,1200 --hide-scrollbars index.html
```
When changing the SVG-generating code, prefer an **atomic Python string-replace with a
count check** (assert each old string matches exactly once) over piecemeal edits.

## Doc conventions
- **Name parts by engineering function, not vendor SKU** — "static-latch shift register",
  with "SN74HC595" as a secondary identifier.
- **Self-contained**: explain any new term (SPI, "shift register", etc.) where it appears,
  or leave it out.
- **Figures**: every figure gets a number + name + caption; never bake an explanatory
  paragraph into the figure image (that's the caption's job).
- **Colour-code a parts list to its diagram** so the list reads as a legend; grey out +
  mark items not shown in the diagram.
- Clean / monochrome by default; use colour only when it carries information.

## Relationship to memex
This is the *project workspace*; the durable knowledge lives in `~/github/memex` (the
knowledge base) — see its `LED time-code panel` and `sync-eval-equipment-log` pages.
Note Claude Code's auto-memory is **per-directory**, so the feedback/preferences saved
during memex sessions do **not** auto-load here — that's why the conventions above are
written out. When a session here produces a transferable lesson, propose ingesting it
back into memex.
