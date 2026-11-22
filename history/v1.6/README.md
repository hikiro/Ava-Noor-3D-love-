# Villa Verse v1.6 — Ava + Noor: articulated fingers + speech-ready mouth shapes

**Status: validated prototype, not production-fidelity Sims-like artwork.**

## Actual improvements relative to v1.5

- Added **20 real finger/thumb joints per character** to the existing 23-bone rig (43 joints per character). Every finger has a proximal + distal joint, and every thumb has two joints. Existing character heights, eye colors, hairstyle identity, rest transforms and core 23-bone animation are preserved.
- Added timed keyframes for the fingers of **Ava's right hand** and **Noor's left hand**, plus an adjusted wrist orientation for the attempted clasp. Other hands remain static by choice.
- Preserved old face targets (`blink`, `concern`, `soft_smile`), added `jaw_open`, `viseme_O`, `viseme_EE`, and a dark interior lip membrane. The neutral mouth represents a closed MBP-like lip position, **not a complete phoneme rig**. There is no audio or speech recognition in this project.
- Added `cloth_reach` and `cloth_breathe` as limited vertex deformation targets. **Not physical cloth simulation.** The maximum one-shot corrective displacement is reported in `models/*manifest.json`.
- Exported 8 blendshape targets and baked finger/keyframed morphology as a standard glTF 2.0 `.glb` per character.
- Rerendered the animation at **24 fps** in a 540×960 vertical frame. This is a 5.2-second silent rig test, not the 30-second Villa Verse reel.
- Godot `main.gd` loads two new GLBs and provides a runtime diagnostic for 43 bones and 8 blendshapes; diagnostic logic is **unexecuted** until the project runs in Godot.

## Deliverables

- `models/ava_RIGGED_SPEECH_HANDS_v1_6.glb` and `models/noor_RIGGED_SPEECH_HANDS_v1_6.glb` — Y-up, metres, skinned 3D animation.
- `models/base/` — unaltered v1.5 source vertex arrays, part range indexes and source GLBs; these make the new build standalone, without needing to unpack all historical versions.
- `models/*_v16_runtime.npz` — numerical vertex arrays including all eight active morph deltas.
- `godot/` — prepared Godot 4 project; open `godot/project.godot`. Press Space to pause, R to restart, arrow keys to orbit.
- `previews/Ava_Noor_v16_24FPS_FINGER_AND_SPEECH.mp4` — actual 3D geometry rendered after vertex skinning, no static animation substitute.
- `previews/CONTACT_CLOSEUPS_V16.png` — detailed front/angle hand contact before and after curl.
- `previews/FACIAL_AND_CLOTH_CONTROLS_V16.png` — rendered neutral, expression and oral targets.
- `previews/SIX_POSE_V16_INSPECTION.png` — timeline sheet.
- `qa/numerical_validation_v16.json` — actual tested constraints including 20 timestamps/character; **not** 20 artistic redesign loops.
- `qa/DEFECT_LEDGER.md`, `qa/RESEARCH_SOURCES.md`, `AGENTS.md`, `CLAUDE.md` — durable rules and failure evidence.
- `archive/v1_5_complete.zip` — historical model/rig/project preserved intact (it contains v1.4 and v1.3 archives).

## Rebuild

From the unpacked v1.6 folder:

```bash
python -m pip install -r requirements.txt
python source/rebuild_portable.py --test --render
```

Rendering additionally needs FFmpeg in PATH and a usable offscreen VTK renderer. Basic geometry build requires only numpy, scipy, trimesh. No API subscription is required.

## Unresolved failures

1. **The handhold is not physically solved.** The fingers are independently articulated, but close-up renders show some fingers overlap. Per-vertex distance is NOT a watertight mesh penetration test. No physics or haptic contact solver exists yet.
2. Upper arms/shoulders still have separate intersecting mesh shells. Shoulder seams and hollow-looking sleeve transitions remain visible. Do not claim watertight anatomical connection.
3. The mouth controls generate visually distinct O, EE and open shapes, but lack natural jaw rotation, tongue, cheeks or timing driven by audio.
4. Corrective garment targets are small and cosmetic. No cloth solver or self-collision.
5. Original head/neck and skeletal measurements survive, but geometry remains quite far from Sims-like fidelity, especially hair, silhouettes, joints and garments.
6. Blender, Godot runtime import, glTF external validator, collision-free contact, audience quality and a complete episode are **unverified**.

**Recommended next architectural step:** use a mature Blender human mesh/rig workflow for smooth topology rather than continuing to add procedural shoulder capsules. Import that improved human surface into the preserved Godot/glTF pipeline.