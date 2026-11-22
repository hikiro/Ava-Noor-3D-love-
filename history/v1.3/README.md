# Villa Verse — Cast model look-development v1.3

**Date:** 2026-11-20  
**Status:** Editable 3D look-development meshes with 4-view renders. **Not final production models, not a skinned animation rig.**

## What was created

All six recurring cast members—Ava Moreno, Kai Okafor, Noor Farah, Jules Vega, Sloane Park, Remy Bell—are 3D mesh objects in independent Godot-oriented glTF 2.0 `.glb` files. Their outfit colors and silhouette correspond to `reference/cast_style_reference.png`, the earlier Villa Verse reference sheet. Each file contains roughly 90–110 named, independent meshes for individual editing in Blender, not a single still picture. This is a stylized, simple-geometry pass; the supplied reference art is substantially more detailed. The characters are standing in a common scale and rest pose so full turnarounds can be compared.

Model coordinates: **Godot/glTF Y-up**, metres, front facing **+Z**. Procedural source code (`source/build_cast.py`) works in Z-up and rotates every exported mesh to Y-up. The local preview renderer uses separate `models/source_zup` assets. Do not mix axes when adding rigs.

## Files

- `models/{ava,kai,noor,jules,sloane,remy}_model_v1_3.glb` — the six independent editable glTF models.
- `models/cast_manifest.json` — real piece names and parent *intents* (not enforced in GLB).
- `models/rig_targets_y_up.json` — measured pivot coordinates and lengths for the subsequent armature pass.
- `previews/CAST_LOOKDEV_BOARD.png` — all six on one contact sheet.
- `previews/{name}_TURNAROUND.png` — front, 3/4, side, back for each.
- `previews/{name}_portrait_35.png` — high-resolution close-up render per character.
- `godot/` — untested Godot 4 static-model viewer scaffold, including copies of models.
- `source/` — editable procedural model, renderer, QA, and rig target source code.
- `qa/` — actual validation results and iteration log.
- `archive/v1.2_rigged_previous.zip` — complete previous version for recoverability.

## Run

Generate and re-export all six model files in a Python environment with `numpy`, `trimesh`, `Pillow`, `vtk`:

```bash
python source/build_cast.py
python source/render_models.py
python source/write_rig_spec.py
python source/validate_models.py
```

In Godot 4.x, open `godot/project.godot`, let Godot import GLBs, then press F6/F5 to run the viewer. Keys 1–6 select characters, A/D or arrow keys orbit, drag to orbit, R reset. **Godot itself was not available in this environment; import/runtime has not been tested.** Blender is also unavailable in this environment, so no `.blend` file or tested Blender rig exists yet. You can import any `.glb` through Blender > File > Import > glTF 2.0 and edit meshes.

## Explicit limitations and next production gate

1. **No deforming rig:** GLBs contain separate static meshes. The `node_parent_intent` metadata does not create a Blender armature, skeletal weights, blend shapes, or attachment constraints.
2. **Visual polish incomplete:** geometry is simplified, especially hair silhouette, shoulder transitions, facial features, garments and drape. It is suitable for selecting visual direction, not the requested final-quality romance/reality animation.
3. **Do not animate individual mesh translations independently.** First build a humanoid armature, skin appropriate meshes, measure rest pose and test FK/IK and stationary foot goals.
4. **Do not assert weight transfer from static lookdev.** The old v1.2 numeric checks concern the previous 2D motion rig and do not transfer to this new 3D cast.
5. **No extra API/subscription usage:** this package was built with locally available Python/VTK tooling and existing references.

## Reference provenance

The cast reference picture was generated earlier in this ChatGPT conversation and is stored unchanged. This build contains original custom procedural geometry and code, not a borrowed Blender/Godot rig. The preferred source format glTF 2.0 follows Godot's official recommendations: https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html and skeleton import guidance at https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/retargeting_3d_skeletons.html.