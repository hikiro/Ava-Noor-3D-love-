# Upload and recovery status — 2026-11-23

Repository: https://github.com/hikiro/Ava-Noor-3D-love-
Visibility: **PUBLIC**. This is a working source-and-asset recovery, not a claim of final visual approval.

## Uploaded and verified

- Original *The Wrong Choice* E01 script, illustrated storyboard (16 opening/closing frames), original backgrounds, sprites, scene renderer and viewer.
- Six cast v1.3 direct GLB models, look-development sheet, measured proportions, turnarounds, original design reference.
- v2.1 Ava/Noor source scripts, Godot project and import-check scripts, manifests, QA data and latest v2.1 MP4/GIF/preview images.
- Both large v2.1 rigged GLBs, preserved as **63 individually Git-SHA-verified chunks** (30 Ava / 33 Noor). `PARTS_MANIFEST.json` includes whole-file SHA-256 and a reconstruction script.
- Fourteen v2.1 source-model binary inputs (PLY meshes, NPZ runtime/geometry, base GLBs), preserved as **57 individually Git-SHA-verified chunks**. `EXTRA_ASSETS_MANIFEST.json` includes whole-file checksums.
- GitHub Actions workflow for reconstructing and checking both final GLBs and source binary inputs.
- v1.2 through v2.1 historical quality/failure and direction records (in `history/`) and producer-led v3.0 workflow, specialist agent definitions, and public Producer–Auditor experiment files.

## Still excluded or not recovered

- Full **nested historical ZIP archives** for v1.1–v2.1, producer-v3, locked QA and experiments were *not* committed verbatim. They contain considerable redundant files and potentially sensitive sealed material; see the conversation attachments/handovers for those original archives.
- Older intermediate 3D GLB files and every old version's MP4/GIF were *not* all individually restored. The v2.1 runnable source/binary inputs, latest MP4/GIF, original storyboard and original six cast models were prioritized.
- **Private key files, credentials, sealed internal QA reports and private agent memories were intentionally excluded**, especially important given public repository visibility.
- A real multi-language-model autonomous run of Producer/Auditor has **not** been completed.
- A native Godot import/playback evaluation has **not** been completed.

## Reconstruction

Run from the repository root:

```bash
python tools/reassemble_extra_assets.py
python tools/reassemble_glb.py
```

These validate each part and the completed files with SHA-256 and abort on mismatch. The same verification runs in GitHub Actions and its output artifact contains the reconstructed assets.

## Known artistic defects

The latest Ava–Noor v2.1 handhold is visually unconvincing; lip/mouth-corner geometry still needs correction. Structural rig checks are not evidence of production-ready visual quality. All future iterations must preserve attached head/neck, anatomically plausible proportions, stable pivots and physically plausible foot contact, center-of-mass shift and hand motion.
