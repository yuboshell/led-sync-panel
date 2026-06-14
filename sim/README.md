# sim — decode simulator for the LED time-code panel

Software model that **proves the measurement works before any parts are bought**:
it encodes a timestamp into the panel's LED pattern, simulates two unsynchronised
rolling-shutter cameras filming it, decodes what each one sees, and recovers their
capture-time offset — including the vernier disambiguation from §6 of the design doc.

This attacks the project's real risk (does the encode → film → decode → offset chain
actually work?) with zero hardware. The decode logic carries straight over to real
Pixel 7 footage later.

## Run it

```
cd sim
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # first time
.venv/bin/python -m pytest          # 10 tests — the correctness proof
.venv/bin/python decode_sim.py      # end-to-end demo + renders frames/two-cameras.png
```

`decode_sim.py` prints a table of true-vs-recovered offsets and writes
`frames/two-cameras.png` — the two synthetic camera frames, so you can *see* the lit
LEDs at different positions and the decoded offset between them.

## What it shows

- Within the unambiguous range (±25.6 ms for a 16×16 panel at τ=200 µs), the recovered
  offset matches the true offset exactly.
- The **coarse row earns its place**: an offset larger than one fine wrap (3.2 ms) that
  fine-alone would alias is recovered correctly once the coarse row is used.

## Layout

```
ledsync/
  codec.py    positional (fine+coarse) time-code: encode/decode, wrap
  panel.py    the panel as a clock: count_at(t), reading_at(t)
  camera.py   rolling-shutter sampling: row r exposed at frame_start + r*line_time
  offset.py   recover_offset() between two cameras (with/without the coarse row)
  render.py   draw a reading as a matte-black panel frame with red LEDs
tests/        one behaviour per test; all logic here is test-driven
decode_sim.py end-to-end demo harness (the runnable story)
wokwi/        (next) firmware + diagram.json to simulate the driver on a Pi Pico
```

## Model vs. reality

The simulator validates the **logic** (encoding, decoding, rolling-shutter sampling,
offset recovery). It does **not** model LED brightness, exposure smear, glare, or the
real microcontroller's timing jitter — those are hardware-phase checks (a logic
analyser / scope, and filming a real LED with a Pixel 7).
