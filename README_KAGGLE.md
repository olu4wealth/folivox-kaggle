# Folivox on Kaggle (GPU) — Web Studio via tunnel + CLI fallback

Original repo: https://github.com/vatavale/folivox
What it does: FB2 / EPUB / DOCX / PDF / TXT → chaptered `.m4b` / `.mp3`
via local CosyVoice 3 (~6 GB) + faster-whisper QA (~1.6 GB).

Files here:

- `kaggle_folivox.ipynb` — upload to Kaggle → run top to bottom.
- `kaggle_patch.py` — shim that starts `folivox ui` on 0.0.0.0 and
  normalises Host/Origin so the tunnel works. Token auth stays ON.

## 1. Kaggle setup

1. kaggle.com → Create → Notebook.
2. Right panel Settings:
   - Accelerator: **GPU T4 x2** (required for local CosyVoice).
   - Internet: **ON** (pip + Hugging Face model download).
   - Persistence: files in `/kaggle/working` persist as run output.
3. Add → Upload `kaggle_folivox.ipynb` content (copy cells) and
   `kaggle_patch.py` (Add → Upload, or paste as first cell file).
4. Run cells 0 → 8 in order.

## 2. What each cell does

| Cell | Purpose |
|---|---|
| 0 | Checks Python 3.10–3.12, nvidia-smi, ~10 GB free, net |
| 1 | Points FOLIVOX_MODEL_DIR / HF_HOME / config to /kaggle/working; ffmpeg |
| 2 | pip install torch (reuse Kaggle's if present) + folivox[all] from GitHub |
| 3 | folivox setup — downloads ~6 GB voice (+1.6 GB QA; --skip-asr to skip) |
| 4 | Upload book + voice.wav to /kaggle/working/books; inspect; voices |
| 5 | Smoke test: --preview 500 chars --no-qa → preview.m4b |
| 6 | Launch patched Studio on 0.0.0.0:8765 in background thread |
| 6b | cloudflared tunnel → OPEN <url>/?token=<token> in your browser |
| 7 | CLI full render (same pipeline; resume-safe via .folivox journal) |
| 8 | FileLink downloads + doctor bundle; Dataset caching tip |

## 3. Book + voice

- Book: any FB2/EPUB/PDF/DOCX/TXT/ZIP. Paperclip → Upload to
  `/kaggle/working/books/`.
- Voice: 6–15 s clean WAV/FLAC + exact transcript .txt, OR a bundled id
  (`folivox voices` lists e.g. en-kalynda, russlib).
- Register yours:
  `folivox voices add myvoice books/myvoice.wav --text books/myvoice.txt --gender f`

## 4. Why the patch is needed

`folivox ui` binds 127.0.0.1 and rejects non-loopback Host/Origin
(DNS-rebinding guard) + auto-opens a desktop browser. On Kaggle your
browser is remote, so `kaggle_patch.launch()`:

- serves on 0.0.0.0:8765 with proxy_headers,
- rewrites Host→127.0.0.1 only as seen by the inner guard,
- keeps ?token= auth (never disabled — don't share the URL).

If the Studio page is blank/blocked, skip to Cell 7 CLI — identical result.

## 5. Limits

- Kaggle sessions cap ~12 h + 20 GB /kaggle/working output. Render
  chapters 1–2 first, then whole book; re-running resumes from the journal.
- T4 16 GB fits CosyVoice3-0.5B; on OOM use --max-chars 200 or --no-qa.
- To avoid re-downloading 7.6 GB: Save Version → Save Output, or push
  models/ to a Dataset and attach it next session (set FOLIVOX_MODEL_DIR
  to the attached path before Cell 3).

## 6. Local check (this PC)

  python gen_nb_part1.py; python gen_nb_part2.py; python gen_nb_part3.py
  python -c "import json,py_compile; json.load(open('kaggle_folivox.ipynb')); py_compile.compile('kaggle_patch.py',doraise=True); print('nb+patch OK')"
