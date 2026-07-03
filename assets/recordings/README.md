# Capture recordings

- **`*.mp4`** — web-compressed (H.264, ≤ 720 px, no audio). **Committed** — safe to share / embed.
- **`*.MOV`** — the raw full-resolution originals (16–79 MB each). **Git-ignored, kept local**
  (the decoders read these). Recompress a raw clip with:

  ```bash
  ffmpeg -i IN.MOV -vf "scale='min(1280,iw)':-2" -c:v libx264 -crf 28 -an -movflags +faststart OUT.mp4
  ```

Clips: `IMG_3577` (Step-0 blink) · `IMG_3580` (panel run) · `IMG_3584` (Gray timecode @ 50 ms —
the single-camera decode source).
