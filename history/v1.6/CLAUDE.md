# Villa Verse animation source-of-truth — v1.6

## DO NOT repeat old failures

1. **Head and neck joint hierarchy always connected.** Measure head/neck relative to trunk every timeline test; never animate heads via free-floating positions.
2. **Realistic measured proportions** are mandatory. Do not enlarge hands, heads or legs to hide a rigging defect. Compare at least front/side/back view, and measure ratios.
3. **Root motion and limb motion** must match intended physical action. Keep planted feet in world space. Never amplify limb motion relative to small body movement unless reaching/grasping action is intentional, recorded and tested.
4. **Hands are anatomical rigs** with distinct knuckles, proximal/distal phalanges, thumbs, correct pivot/direction, and collision-aware contact. Near-zero vertex distance does NOT prove grasp, and vertex overlap is not a pass.
5. **Shoulders must become genuinely welded/deformable topology.** Current separated deltoid/upper arm shells remain visibly wrong. Do not hide them with camera angles and claim completion.
6. **Mouth morphs are not real lip sync** until audio has been aligned and visually inspected with lips, tongue and jaw.
7. **Garment deformation is not cloth simulation** unless fabric responds physically and collision tests pass. Small corrective blendshapes are only correctives.
8. Do not claim successful Godot/Blender imports without actually running those programs. Validate source mesh and glTF in independent tools and label scope.
9. Never equate numeric checks, 20 sampled timestamps, searched references, planned experiments, or screenshot mosaics with 20 independent implementation/QC iterations.
10. Preserve full version history, original wording, repair rationale, actual tested commands, renders and measurable defects in portable packages. When render inspection exposes a failure: log cause, correction, rerender, new result, and prevention rule.

## Aesthetic priorities (Villa Verse)

Adult Sims-inspired stylized 3D: credible head/body ratios; organic unified torso/limb surfaces; differentiable facial anatomy; readable eyes/lips; realistic hair silhouette; fitting period outfits; coherent skin and cloth; controllable camera; character identities unchanged. Model quality is not established by a successful file export.

## Research scope and provenance

- Khronos glTF 2.0 official specification: skin joints, morph target weights and animation channels.
- Godot 4 official importing 3D scenes: named morph targets and skinned GLB import.
- Current geometry derives from v1.5 procedural source; no third-party licensed meshes inserted.

See `qa/RESEARCH_SOURCES.md` and `qa/DEFECT_LEDGER.md`.