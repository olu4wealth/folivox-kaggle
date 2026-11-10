# Folivox on Kaggle GPUs

A deployment toolkit for running **[Folivox](https://github.com/vatavale/folivox)** on
free Kaggle GPUs: a notebook that installs and starts the app, a patch that makes its
local web UI reachable through a tunnel, and notes from real runs.

**This repository is not the text-to-speech engine.** Folivox does the synthesis and
QA; this repo is the wiring that gets it running on Kaggle and keeps a browser
session usable while it works.

## What it produces

FB2 / EPUB / DOCX / PDF / TXT in, chaptered `.m4b` or `.mp3` out, using CosyVoice 3
(~6 GB) for synthesis plus faster-whisper (~1.6 GB) for quality checking.

## Files

| File | Purpose |
|---|---|
| `kaggle_folivox.ipynb` | Upload to Kaggle, run top to bottom. Checks the runtime, points model and cache paths at `/kaggle/working`, installs `folivox[all]`, and starts it. |
| `kaggle_patch.py` | Shim that binds the UI on `0.0.0.0` and normalises `Host`/`Origin` headers so the tunnel works. Token auth stays on. |
| `kernel-metadata.json` | Kaggle kernel metadata (GPU on, internet on). Change the `id` to your own username before pushing from the CLI. |
| `README_KAGGLE.md` | Step-by-step setup notes. |
| `testrun_report.md` | What a real run actually did, timings included. |

## Running it

1. Kaggle → Create → Notebook.
2. Settings: accelerator **GPU T4 x2**, internet **on**, persistence on.
3. Upload `kaggle_folivox.ipynb` and `kaggle_patch.py`.
4. Run the cells in order.

Details and gotchas are in `README_KAGGLE.md`.

## Not in this repository

- `downloads/` — generated audio and source e-books. Deliberately ignored: the
  output is derived from copyrighted books and does not belong in git.
- `freevoice-radio/` — the Freevoice Radio desktop app. Unrelated to this
  notebook; it is its own project with its own repository.
- `build/`, `dist_new/`, `__pycache__/` — build artifacts.

## Credit and licence

Folivox is by [vatavale](https://github.com/vatavale/folivox) and licensed
**Apache-2.0**. This toolkit calls it as a dependency and ships none of its source.
If you reuse or extend anything here, keep both attributions.
