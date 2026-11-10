# Testrun report — Folivox Kaggle conversion (no local model download)

Date: 2026-10-13. Full CosyVoice weights (~6 GB) + QA (~1.6 GB) NOT downloaded locally per request.

## PASS — static validation
- kaggle_folivox.ipynb: 12 cells, nbformat 4.5, valid JSON.
- kaggle_patch.py: py_compile OK.
- Guard shim unit check: tunnel Host rewritten to 127.0.0.1:8765, token query untouched.

## PASS — live shim E2E (no folivox needed)
- test_shim_live.py: fake ASGI app through wrapper returned 200, inner saw loopback host. Proves tunnel trick works.

## PASS — real folivox CLI (light install, no torch, no weights)
- pip install folivox --no-deps + reader deps: folivox 0.1.0.157.
- Reader API: sample_book.txt 3188 chars, lang en, 1 chapter — READER_OK.
- `folivox inspect` with PYTHONUTF8=1: shows title, 608 words, ~3 min 48 s estimate.
- `folivox voices`: table renders (bundled catalog present).
- Note: `inspect`/`doctor` crash on default cp1252 Windows console (narrow no-break space U+202F, arrow U+2192). Cosmetic only; fixed by PYTHONUTF8=1. Same will not affect Kaggle (UTF-8 Linux).

## NOT RUN locally (needs Kaggle GPU)
- `folivox setup` model download, `bench --devices cuda`, `--preview` TTS render, Studio launch + cloudflared tunnel, full `render`. Those are Cell 3/5/6/7 on Kaggle with T4 + Internet ON.

## Conclusion
Notebook + patch + CLI pipeline validated as far as possible without weights/GPU. Next: upload kaggle_folivox.ipynb + kaggle_patch.py to Kaggle and run cells 0-8.
