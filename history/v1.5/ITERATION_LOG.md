# Villa Verse v1.5 — implemented changes and QC record

The user's standing rule is to **measure, inspect, identify the defect, correct the source, and rerender**. A completed numerical test is not a completed artistic redesign. This release includes **two model-preview revisions**, not twenty independent artistic iteration cycles.

| Iteration | Action / test | Visible defect | Likely cause | Applied change | Verified / remaining |
|---|---|---|---|---|---|
| v1.5-01 | Replaced original face & arm parts, generated skinned GLBs, rendered 79 frames, inspected six poses and face crop | Upper deltoids appeared more bulbous than v1.4; small chin blob read as beard | Oversized arm tube radii + independent chin ellipsoid | Reduced arm/deltoid/underarm/cuff dimensions; removed floating chin shape | Rebuilt both GLBs, rerendered 79 frames and inspected 6-panel contact sheet |
| v1.5-02 | Added three expression deltas and exported glTF animation track for `weights` | v1.4 eyes, brows and lips could not change expression | All facial components had fixed rest vertices | Introduced `blink`, `concern`, `soft_smile` morphs and keyframed glTF weights | Rendered expression panel and validated nonzero morph deltas and animation accessors |
| v1.5-03 | Numerical and structural validation including 20 chronological samples per character, checked 3D hand proximity | No further automated structural failure found | Numerical metrics cannot assess artistic face quality or contact penetration | No further change claimed | See `numeric_validation.json` for complete checks. Art quality remains a failure against full Sims-like reference fidelity. |

## Persistent prevention rules

- Before adding skin/cartoon face volumes, inspect front and 3/4 close-up; avoid free-standing chin/cheek spheres.
- Use at least 4 full-body angles and contact poses before calling a shoulder fix an improvement.
- Parent every head/neck bone through the torso, check bone-length invariants at 20 time positions, and monitor grounded feet.
- Morph animation must exist in the GLB and be independently testable, not a JSON-only 'expression spec'.
- Physical hand proximity is not proof of a plausible grasp or of zero penetration. Test contact as meshes, not only joint pivots.
- Validate a portable build without relying on absolute paths; include full previous sources and preserve history.
- Distinguish source inspection, geometry/unit tests, rendered visual inspection, Godot runtime tests and audience/production quality.

## Technical reference provenance

- Godot docs `https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/import_configuration.html` — glTF skin, importer settings and animation data.
- Blender manual `https://docs.blender.org/manual/en/5.2/modeling/modifiers/deform/corrective_smooth.html` — why blended joints can need volume-preserving corrective smoothing (NOT implemented as a Blender modifier in v1.5).
- Godot docs `https://docs.godotengine.org/en/latest/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html` — glTF as recommended exchange format.
- Original v1.3 and v1.4 procedural model source embedded inside the historical archive. No third-party character geometry copied.