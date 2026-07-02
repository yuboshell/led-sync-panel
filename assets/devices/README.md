# Device photos (public)

Web-sized JPGs (≤ 1600 px) of the hardware bought for this project, grouped by
purchase (`<date>-<vendor>/`). Safe to use in the design doc and to share publicly.

The full-resolution originals **and** the receipts / manifests live in the
**git-ignored `purchases/` tree** (kept local — receipts carry personal + payment
info). Regenerate these web copies from the originals with:

```bash
sips -s format jpeg -Z 1600 <original>.heic --out <name>.jpg
```

Note: a few shots (e.g. the DigiKey items) include the vendor packing label, which
shows order numbers (invoice / sales-order). These are published intentionally —
low-sensitivity, and unusable without account access.
