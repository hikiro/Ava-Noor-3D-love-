# Villa Verse v1.9 — Unified Hands + Collision-Aware Contact

**Release type:** measured modeling and interaction prototype, **not final production art**.

## What actually changed

- Ava and Noor now each have **two watertight, single-surface hands**, rather than independent palm, finger-cylinder, knuckle and fingernail objects. Each hand retains the inherited 43-bone system with separately animated finger bases/tips.
- Models remain glTF 2.0 (`models/*_CONTINUOUS_HANDS_v1_9.glb`) with eight inherited facial/cloth blend shapes, existing character costumes, and unchanged v1.8 elbow/shoulder topology.
- The two actors' positions in the scene are now Ava `(-0.48,0,0)` and Noor `(0.48,0,0.038)`. This static **3.8 cm Z-depth offset** avoids hand mesh intersections at the tested motion samples without dragging planted feet along the ground.
- A dedicated 3D triangle-triangle collision test uses VTK, not merely nearest-vertex distances. At 25 sampled times 0–5.19 seconds, it observed zero opposing-hand mesh intersections. At 3.4 seconds the hands are approximately 10 mm apart, so the 'handhold' is still visually suggestive rather than fully physical.
- Rest-pose continuous hand geometry is also available as standalone `.ply` files for later Blender sculpting.

## Inspection

- `previews/Ava_Noor_v19_CONTINUOUS_HANDS.mp4` — 540×960 at 24 FPS, 125 frames; actual CPU skinning of the new mesh.
- `previews/Ava_Noor_v19_PREVIEW.gif` — short looping review.
- `previews/HANDS_BEFORE_AFTER_V18_V19.png` — identical 0° and 45° contact close-ups for both versions.
- `previews/SIX_POSE_V19_INSPECTION.png` — six temporal poses of the full-body animation.
- `qa/validation_v19.json` — detailed geometry, animation and 25-sample collision results.
- `qa/ITERATION_LOG.md` — failures, causes, changes, rechecks, and new prevention rules.

## Offline reproduction

```bash
python source/build_v19.py
python source/render_motion_v19.py
python source/render_compare_v19.py
python source/validate_v19.py
```

Dependencies: Python, NumPy, SciPy, trimesh, scikit-image, Pillow, VTK, OpenCV; FFmpeg for MP4/GIF. Optional `pip install -r requirements.txt` where a package index is reachable. All referenced model base assets are included under `models/base/`. The legacy build scripts are retained in `source` for reproducibility.

## Real Godot import — **not run here**

The Godot executable is absent from this environment; network resolution also prevented downloading the engine. The following is an **executable user-side test**, not a completed test:

On Windows PowerShell:

```powershell
cd godot
.\run_godot_checks.ps1 -GodotExe 'C:\Tools\Godot_v4.5-stable_win64_console.exe'
```

On Linux/macOS with Godot in PATH:

```bash
./godot/run_godot_checks.sh godot
```

For visual QC, open `godot/project.godot`, run `Main.tscn`, press `C` for hand close-up, `LEFT`/`RIGHT` for orbit, `SPACE` to pause and `R` to restart. Check all six motion phases and wrist seams, and record engine screenshots or video. **The scripts have not been executed under Godot in this container.**

Reference: <https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html> and <https://docs.godotengine.org/en/stable/classes/class_resourceimporterscene.html>.

## Remaining open problems

- The new hand shell is continuous **within each hand**, not welded anatomically to the forearm. The visible wrist seam is still an open art defect.
- Mid-hold gap ~10mm, even though the final hold gets to ~1.8mm; the interaction is not true pressure-based grasping. There may be self-intersections within a single hand that the opposing-hand collision filter does not check.
- Finger knuckles/nails, shoulder deformation and garment construction remain stylized/procedural, visibly below the original Sims-like art target.
- No Godot runtime verification and no audio-driven lip-sync.
- 25 timeline samples are not 25 independent artistic improvement loops; one connected-hand geometry pass was created after an initial clipped-mesh failure, with several staging tests.

Full previous v1.8 handover is preserved unchanged under `archive/v1_8_COMPLETE_HANDOVER.zip`; it contains the earlier v1.7 history chain.