# Villa Verse v2.0 — Wrist-connected character models

**Status:** Working *technical prototype*, not a visually approved Sims-like character system.

## What is new

- Ava and Noor's earlier segmented hand-to-forearm connection is replaced by a **true shared-index continuous surface** from torso through elbow, wrist and hand. This uses the existing v1.8 ring-topology elbows and the v1.9 continuous fingers, with four new wrist support loops and tapered cross-sections. Neck/head hierarchy, clothing colors and 43-bone skeletons are preserved.
- Finger/knuckle weights now use a smooth spatial blend, including the thumb-index web. This addressed the extreme mesh stretching caused by nearest-finger/hard-thumb assignments.
- The scene depth separation was revised from 38 to **39 mm** to avoid one sampled late-handhold collision introduced by the new deformation.
- **Both** models are re-exported as editable `.glb` assets, with the upper body + arms + hands also extracted into standalone `.ply` rest-pose surfaces for sculpting.
- Matching before/after close-ups, 5.21-second 24fps MP4, a small GIF, source scripts, reproducible QC and the entire v1.9 ZIP are included.

## Files

- `models/ava_WRIST_WELDED_v2_0.glb`, `models/noor_WRIST_WELDED_v2_0.glb` — skinned, animated glTF 2.0 models.
- `models/*BODY_ARMS_HANDS_WELDED_rest_v20.ply` — 1 connected rest-pose upper-body surface per actor (without unrelated clothing shells).
- `previews/WRIST_SEAM_BEFORE_AFTER.png` — camera-matched v1.9 vs v2.0 view.
- `previews/SIX_POSE_V20_INSPECTION.png`, `previews/Ava_Noor_v20_WRIST_WELDED.mp4`, `.gif` — rendered review assets.
- `qa/validation_v20.json`, `qa/CONTINUITY_AUDIT.json` — detailed, machine-readable test evidence.
- `qa/ITERATION_LOG.md` — failures, corrections and remaining problems.
- `godot/` — updated Godot 4 viewer and **unexecuted** import test scripts.
- `archive/v1_9_COMPLETE_HANDOVER.zip` — preserved original v1.9 package.

## Rebuild & test (Python)

The portable build requires Python with NumPy, SciPy, trimesh, scikit-image, Pillow, VTK, OpenCV and FFmpeg. The source base assets are included.

```bash
python source/build_v20.py
python source/audit_connectivity_v20.py
python source/render_motion_v20.py
python source/render_hand_closeups_v20.py
python source/validate_v20.py
```

## Native Godot test — pending

Godot was **not installed** in the build environment, and its download host could not be reached. glTF files successfully parsed with an independent loader, but that is **not equivalent to Godot validation**.

Use Godot 4 on your own computer:

```powershell
cd godot
.\run_godot_checks.ps1 -GodotExe 'C:\Tools\Godot_v4.5-stable_win64_console.exe'
```

Or with Godot in PATH on Linux/macOS:

```bash
./godot/run_godot_checks.sh godot
```

In the viewer: press **C** for contact close-up, **LEFT/RIGHT** to orbit, **SPACE** to pause, **R** to replay.

## Verification and open defects

- 38/38 scoped **technical checks passed**, including independent GLB parse, bone/morph channels, topology, skin weights, foot stability, a 125-frame deformation scan, 26 samples of opposing palm/finger collision, five wider distal-arm collision samples and complete video decoding.
- Shared-surface connectivity was independently confirmed for both hands on both actors; the surface is watertight.
- The new wrist support loop edges stayed below 2.5× rest-edge stretching throughout the 125 encoded frames.
- Rebuilding the models yields identical GLB hashes, and the ZIP has its own checksum manifest.
- **Known defect:** inherited mouth-cavity morphs produce some local edge stretching around **5.47× (Ava) and 6.36× (Noor)** in a 125-frame scan. These were not corrected during this wrist-specific milestone.
- The hands are still **not** a convincingly wrapped natural grasp and may self-intersect within each hand. The finger position and visual acting still need improvement.
- Godot playback, final shaders/materials, refined face/hair and realistic garment deformation are unfinished.

This release includes one wrist-surface redesign, two major finger-weight adjustments, staging experiments and separate QC tests. Those are **not** 20 independent artistic redesign cycles.