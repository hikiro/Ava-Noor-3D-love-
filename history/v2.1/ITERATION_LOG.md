# Villa Verse v2.1 implementation & outside audit log

**Scope:** one main facial morph redesign with **two tested coefficient passes**, four finger-flex variants, five wrist-orientation variants, one full rendered final clip. This is **NOT 20 independent full redesigns**. All tests are actual computations or rendered frames identified below.

| ID | Action | Observed failure | Root cause / hypothesis | Correction and test actually run | Result / remaining gaps | Prevention rule |
|---|---|---|---|---|---|---|
| 01 | Inspect v2.0 source and six-pose preview | Mouth edge stretch 5.47× Ava, 6.36× Noor | Inner cavity was scaled by original 4.6× jaw and 3.3× O morph; inner membrane is narrow | Analyzed v1.6 `make_morphs()` and evaluated 125 time samples per actor, grouped by real mesh ranges | Localized cavity as dominant speech stretch; separate lips also move 19 mm in full jaw target | Audit per-mesh edge deformation before artistic approval |
| 02 | Mouth pass A | Excessive cavity strain | Oversized jaw/O deformation | Replaced with bounded cavity jaw 1.28× and O .43× and coordinated smaller lip displacements; 125-sample mouth audit; 6-expression images | Ava 1.85× Noor 1.94×; **visually too subtle**, rejected for release | Geometry metrics alone don't establish expression readability |
| 03 | Finger variants | Existing fingers look like touching palms, not a clasp | Same curl angle for all digits; contact hand orientation is unnatural | Rendered baseline, gentle, staggered, strong finger profiles at 25° and 55° | Staggered chosen for natural variation but **no interlocking grip observed** | Don't label small curl change a grasp solution |
| 04 | Wrist variants | More wrist turn might improve handhold | Existing -0.8 rad wrist corrector leaves palms parallel | Rendered biases -0.30, -0.16, 0, +0.16, +0.30 rad from 25° and 55°; measured closest vertices | Some angles closer but no supported visual win, retain zero extra bias | Reject parameter changes that only improve closeness |
| 05 | Mouth pass B | Pass A underplays dialogue and O shape | Lower lip and cavity targets too weak | Increased lip opening and rounded vowel motion; 6-expression face-board rerender; 125-sample comparison | Ava 2.071× Noor 2.179×, both under 2.5×, visually more readable; lip-layers STILL disconnected at extremes | Always compare neutral, jaw, O, EE and combined shapes with fixed camera |
| 06 | Render v2.1 | Need proof output uses edited meshes | Old preview cannot prove new code was executed | Exported `ava_MOUTH_GRIP_v2_1.glb`, `noor_MOUTH_GRIP_v2_1.glb`; VTK CPU skinning, FFmpeg MP4, 125 frames, six-pose sheet; separate expressions | Full video decodes; faces still simple; speech has no audio | Preserve actual output and reproduction commands |
| 07 | Opposing-hand collision sweep | Sampled frame test insufficient | v2.0 previously had 26 sampled hand tests | VTK tested every encoded frame (125/125) against opposite hand surfaces at fixed 39mm scene offset | Zero reported opposing-hand triangle intersections in all 125 samples. Does NOT assess pressure grip, individual self-collision or full-body contact | Include both full-sweep collision and visual contact plausibility |
| 08 | Expanded wrist/forearm test | Contact may intersect farther up the arm | Palm crop excludes connected wrist and forearm | Ran 5 sampled distal-arm tests in `validate_v21.py` | Zero collisions at those 5 times only; NOT exhaustive every frame | Scope sampling correctly |
| 09 | Structural validation and independent GLB parser | Export compatibility unknown | Python build may not guarantee standards | `trimesh.load` read files; checked 43 bones, 8 shape targets, expected animation channels, connected/ watertight meshes, 125-frame motion and feet; 43/43 tests passed | Numeric structural pass, no actual Godot import | Do not equate independent glTF parse with engine render |
| 10 | Native Godot attempt | No playback evidence | No Godot binary and host DNS unavailable | `which godot godot4`; curl GitHub download host failed DNS; prepared updated `godot/` import validator | **BLOCKED / UNTESTED** native engine check | Keep executable check and exact limitation in handover |

## Hard visual limitations (open)
- Upper/lower lips still visibly layer apart at strong mouth shapes; needs dedicated lip/mouth-corner sculpted topology.
- No physically compelling finger wrap; hands are separated by depth to avoid collisions, a contact-compromise, not a final hold.
- Other mesh regions still have worst full-animation edge stretch of 3.32× Ava / 3.48× Noor, even though the cavity itself is under 2.5×.
- Procedural hairstyle, shoulders and garment remain below reference quality.
- Native Godot playback and audio speech sync were not run.

## Test command for every-frame collision (standalone reproducibility)
```
python source/hand_collision_all_frames_v21.py
```

## Relevant grounded references
- Godot import formats and blend shapes: https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html
- Godot import configuration and skinning influences: https://docs.godotengine.org/en/latest/tutorials/assets_pipeline/importing_3d_scenes/import_configuration.html
- Godot official Linux packages: https://godotengine.org/download/linux/
- Disney Animation, hybrid facial rigging / pose-space deformation: https://media.disneyanimation.com/uploads/production/publication_asset/52/asset/hybridFacialTalk.pdf

Reference review informed implementation, but NOT a completed sample toward the separate animation-director 100-example empirical research goal.