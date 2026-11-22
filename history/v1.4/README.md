# Villa Verse — Character Model & Contact Rig v1.4

**Output:** actual GLB-embedded skinned/animated 3D character models for Ava and Noor and a locally rendered 5.27-second 15-FPS vertical motion test. This is **not** yet production-fidelity Sims art.

## What changed from v1.3

- Ava and Noor: new geometry for articulated-looking four-finger hands with two phalanges, thumbs, corrected shoulder bridges, extra lashes/eyelids and hair relief, preserving their distinct costumes and facial characteristics.
- True glTF 2.0 skins: 23 named joints per character; valid joint-weight arrays and inverse-bind matrices with baked animation channels; these are no longer only rigid static GLBs with joint tags.
- Shared bone naming hierarchy and measured segment lengths, 5.2-second reach/hand-contact clip. Ground-floor correction: both characters' shoe soles now touch local Y=0 in rest pose.
- Fixed initial hand-target spacing and ran deformed-mesh 3D proximity checks; nearest *sampled vertices* ~3.8 mm at the hold, **not** a proof of non-penetrating collision or realistic fingers.
- New Godot project for importing both character GLBs and playing the embedded animation.

## Contents

- `models/ava_SKINNED_ANIMATED_v1_4.glb`, `models/noor_SKINNED_ANIMATED_v1_4.glb` — Y-up, metres; each includes 23-bone skin and a 5.2-second named animation.
- `models/*EDITABLE_PARTS_ZUP_v1_4.glb` — individually editable mesh elements in original modeling coordinate system; not skinned. Exported source provenance is in previous ZIP.
- `models/*render_data_v14.npz` and `models/*mesh_ranges.json` — independent reproducible geometry and numerical quality tests.
- `godot/` — Godot 4.x scene, GLB assets and GDScript viewer. Open `godot/project.godot` with Godot; Play. Space pause, R restart, left/right orbit.
- `previews/` — real CPU skinned-render MP4, GIF, six-pose inspection board and model turnarounds.
- `source/` — complete rig generator, glTF exporter, IK pose sampler, VTK renderer, numerical validations and portable rebuild script.
- `archive/VillaVerse_Cast_Models_Godot_3D_v1_3.zip` — previous complete v1.3 project including earlier v1.2 archive.

## Running on another computer

```
python -m pip install -r requirements.txt
python source/rebuild_portable.py
python source/rebuild_portable.py --render  # additionally requires ffmpeg in PATH
```

The rebuilding script unpacks the included v1.3 baseline into a temporary directory. It does not require a subscription, API key or network service apart from acquiring standard open-source libraries if unavailable.

## Honest validation scope

**Done here:** two independent GLB exports and parser round trips; quantitative checks for skin arrays, animation structure, rigid bone lengths at 20 time samples per actor, planted feet, no NaNs and 3D hand proximity. Rendered final 79 video frames and both four-angle geometry reviews. See `qa/numeric_validation.json` and `qa/ITERATION_LOG.md`.

**Not done:** import/playback verification inside Godot or Blender (not installed here), independent Khronos glTF Validator run, soft-body clothing, collision-free finger interleaving, production facial animation, proper walking weight transfer, fully hand-authored expressions, 20 creative animation redesign passes.

**Visible art limitations:** Shoulder topology/garment interiors and hand anatomy remain simplified; facial features, lips and brows are still rudimentary, and realistic acting requires further look development. No evidence of final Sims-like quality is claimed.