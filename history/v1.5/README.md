# Villa Verse — Ava + Noor character look-development v1.5

**Status:** Measured, rigged procedural 3D models with three reusable facial expression targets and a 5.27-second reach/hold test. **Not production-quality Sims-like character art.**

## What is actually new vs v1.4

1. Continuous interpolated head surface with slightly refined jaw/temple/cheek geometry, shading and a slimmer nose profile. Replaced the chin blob found during first v1.5 preview. Facial detail remains simplified.
2. Rebuilt upper-arm/deltoid contours and underarm overlap, blending shoulder insertion skin weights toward the chest. A second pass reduced oversized deltoids observed in first v1.5 renders. Anatomical meshes remain distinct overlapping pieces, **not welded** topology.
3. Narrower trouser hems, subtle sewn seams, Ava cowl fold, fitted Noor sleeve cuffs, jacket trim, and a more continuous white inner top. Outfits preserve established identity and colors.
4. Three functional glTF morph targets: `blink`, `concern`, `soft_smile`, with a weight animation embedded alongside the 23-bone reach/hold animation. These are simple facial controls **not** dialogue lip-sync or full FACS.
5. Godot 4.x scene source updated to load the skinned expressive GLBs. **The actual Godot scene was not opened or rendered here**; local CPU/VTK renders and glTF parser checks were run.

## Deliverables

- `models/ava_SKINNED_EXPRESSIVE_v1_5.glb` / `models/noor_SKINNED_EXPRESSIVE_v1_5.glb`: glTF 2.0 Y-up (metres), 23-joint skins, morph targets, embedded reach/contact and expression animation.
- `models/*EDITABLE_PARTS_ZUP_v1_5.glb`: many separately named editable components, original Z-up modeling coordinates. Not skinned.
- `godot/`: Godot 4 project with both models and simple viewer controls (Space, R, arrows). Prepared but not engine-tested.
- `previews/`: `Ava_Noor_5s_POLISHED_MOTION_TEST.mp4`, GIF, two four-angle turnarounds, expression board, six-pose test panel.
- `source/`: procedural model builder, glTF exporter, renderers, independent local validations, and portable archive-based rebuild script.
- `qa/`: numeric validation, defect iteration log, provenance and remaining issues. Each claim is qualified by actual verification scope.
- `archive/v1_4_complete.zip`: intact complete v1.4, which itself includes the v1.3 full project. Previous versions are preserved unmodified.

## Rebuild

Requires Python packages in `requirements.txt`, ffmpeg for the video, and optionally VTK for all 3D previews. No OpenAI API key, no paid service.

```bash
python -m pip install -r requirements.txt
python source/rebuild_portable.py --render --test
```

For Godot, open `godot/project.godot` in Godot 4.x. This is an intended workflow, **not a verified runtime result**. Blender can import GLB, but Blender has not been tested here.

## Unresolved issues

- Hair is still a chunky procedural approximation; clothing is not cloth-simulated or sculpted. Skin geometry can intersect other geometry under extreme bends.
- Facial expressions are narrow in scope, lack mouth-open phonemes, eyeball gaze control and detailed eye/cheek muscle movement.
- The arm still looks simplified in the contact shot. Fingers were not separately re-animated for a convincing physical grasp; sampled hand vertices are close but interpenetration has **not been ruled out**.
- No realistic walking, weight transfer, automated collision management, full facial acting, or episode animation yet.
- Godot runtime import, Blender-specific round trip and external Khronos glTF Validator remain unverified.

**Goal for next pass:** compare these models to the original supplied cast reference, then move to hand-authored sculpt/topology or a free mature character system for a truly production-ready Sims-like visual standard. Do not certify the current models as finished.