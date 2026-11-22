# Villa Verse v2.1 — bounded speech morphs and contact rig audit

**Release status:** Rendered, mechanically checked technical prototype, **NOT visually approved character art**.

## Scope
- Ava and Noor only. Preserve existing cast, costumes, 43-bone skeletons, fully connected shoulder/elbow/wrist/hand meshes, eight facial/clothing blend targets, and original v2.0 scene staging.
- Replace defective inherited mouth-opening morphs that stretched inner mouth triangles 5.47× (Ava) / 6.36× (Noor) in the 125-frame video.
- Add per-finger differentiated curl control and evaluate wrist variants without claiming the result is a natural grasp.
- Re-render the **actual skinned triangles** at 540×960, 24 fps, 125 frames (5.208 seconds).

## Key visual files
- `previews/MOUTH_BEFORE_AFTER_v21.png` — frame/time matched portraits: v2.0 vs v2.1.
- `previews/ava_FACIAL_CONTROL_STATES_v21.png`, `noor_FACIAL_CONTROL_STATES_v21.png` — six mouth control configurations per actor (neutral, JAW, O, EE, jaw+O, jaw+EE).
- `previews/GRIP_VARIANTS_v21.png` — four digit-curl profiles, two camera angles; differences are slight and do **not** demonstrate a natural grasp.
- `previews/WRIST_ORIENTATION_VARIANTS_v21.png` — five wrist correction biases; none is visually approved; final uses the conservative original alignment.
- `previews/SIX_POSE_V21_INSPECTION.png` — six sample frames.
- `previews/Ava_Noor_v21_MOUTH_REPAIR_GRIP.mp4` — 125-frame video; `Ava_Noor_v21_PREVIEW.gif` — reduced-resolution convenience preview.

## Editable 3D assets
- `models/ava_MOUTH_GRIP_v2_1.glb`, `models/noor_MOUTH_GRIP_v2_1.glb` — valid glTF 2.0, 43 bones each, eight shape targets, retained armature animations.
- Source is Python in `source/`, which generates the original mesh, morph-target vertex arrays, animation tracks, and GLB files.
- `godot/` contains a Godot 4 viewer and import validation script. **These are authoring/test inputs, not evidence that native Godot import passed.**

## Rebuild
From the project root, in a Python environment with numpy, scipy, trimesh, vtk, scikit-image, cv2, Pillow and ffmpeg:

```
python source/build_v21.py
python source/audit_mouth_v21.py
python source/render_motion_v21.py
python source/validate_v21.py
```

The full opposing-hand collision sweep was run and preserved in `qa/ALL_125_HAND_COLLISION_v21.json`. Reproduce the sweep with the included source or run it via the command recorded in `qa/ITERATION_LOG.md`.

## Actual verification
- 43/43 **scoped mechanical and file-format** tests passed in `qa/validation_v21.json`.
- The **mouth-cavity** maximum edge stretch over 125 frames fell: Ava **5.4715× -> 2.0713×**, Noor **6.3577× -> 2.1787×**.
- Opposing palm/finger triangles: **125/125 frames**, zero reported intersections at Noor's existing 39 mm scene-depth offset. The collision test does not validate a genuine grasp or all possible self-collisions.
- Expanded distal forearm/wrist vs opposite distal arm: five sampled frames, zero reported intersections.
- Independent GLB parser passed; full MP4 has 125 decodable frames.
- Global worst edge stretch is still **3.32× Ava / 3.48× Noor** in other mesh parts; the mouth-specific repair does not resolve every deforming feature.

## Open visual defects and next milestones
1. **Lips still appear as layered/partly detached shapes at wide-open poses.** Correct by facial retopology around mouth corners; a numerical edge improvement is not visual acceptance.
2. **Hands do not form a believable interlocking grasp.** Proposed cure is the appropriate finger-joint/thumb-opposition topology and hand-contact IK targets, not more uncontrolled wrist rotation.
3. Fingers/wrists are simplified, and some finger triangles still undergo high stretch; refine skin weights and manual topology with multiple viewing angles.
4. 3D faces, clothing and body silhouette remain below original stylized-3D reference quality.
5. Actual **Godot import/playback and on-engine screenshots are unverified**. Godot executable is absent, and remote download failed DNS in this environment. Run `godot/run_godot_checks.sh /path/to/godot` or PowerShell counterpart, review rendered output.
6. Speech visemes are not synchronized to audio; the rendered test has no voice track.

## Provenance and version retention
- `archive/VillaVerse_v2_0_Wrist_Connected_Characters_HANDOVER.zip` preserves the complete earlier v2.0 project history.
- `qa/ITERATION_LOG.md`, `AGENTS.md`, `CLAUDE.md` capture decisions, research, failures, regression tests, and unverified items.
- Local model build and render use Python, VTK and FFmpeg. No extra paid API services or private GitHub repos were involved.
