# LED sync panel — design doc

**📄 Read the rendered doc: https://yubohuangai.github.io/led-sync-panel/**

(Clicking `index.html` in the file list shows raw source — GitHub doesn't render
HTML files; use the link above.)

Design plan for a DIY multi-camera sync-evaluation **LED time-code panel**: a flat
panel of LEDs shows a fast-advancing, visually decodable time code; all cameras
film it at once, and decoding each frame gives the inter-camera time offset.
Built for an 11×Pixel 7 motion-capture rig. The doc reads in show-an-expert
order: §1 purpose, §2 connection diagram + order list (bill of materials with
buy links), §3 the driver choice + exact parts, §4–§9 design rationale.

## Build

`index.html` is generated — don't edit it by hand. Edit `build.py` and rebuild:

```
python3 build.py
```

The rendered page at the link above updates ~1 minute after a push to `main`.
