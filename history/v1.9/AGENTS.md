# Villa Verse animation director rules — v1.9

This file is a persistent project directive. Preserve previous versioned files rather than silently rewriting history. When working on this project in another chat, load this file and the complete prior-version archive first.

## Locked user-defined constraints

- Heads and necks visibly connected; joint hierarchy alone is insufficient.
- Adult proportions measured consistently from reference; preserve each named cast member's clothes, hair, silhouette and approximate stature.
- Bone lengths, shoulder–elbow–wrist alignment, and finger parentage must be stable under pose. No accidental 30× amplification of hand movement relative to small torso movement.
- Grounded feet stay grounded in world coordinates. Forward and backward lean must reflect coherent whole-body weight transfer, not disconnected limbs.
- Close-ups and 3/4 views are compulsory for hands, shoulders, elbows and eye lines; always review normal-speed render as well as numeric tests.
- Never call a scene production-approved solely because watertightness, GLB parsing, frame decode or vertex-distance checks pass.
- For every real iteration: record defect, likely root cause, correction, test run, result, remaining gaps and a preventive/regression rule.
- Do not claim Godot, Blender, or other engine playback was performed if the executable was absent; include executable validation harnesses instead.
- Preserve source, rig parameters, the unedited prior archive, QA outputs and a reproducible reconstruction process.

## New evidence and rules from v1.9

1. **Disconnected finger cylinders are a mesh-topology failure even when they are all parented to hand bones.** v1.9 replaces palm/finger/thumb pieces with one connected, watertight isosurface per hand, skinned with inherited two-phalange joint bones.
2. **Watertight generation must include full SDF margins.** The first hand build clipped the upper-wrist surface at its bounding volume and failed the watertight test; extending the upper Y bound and rerunning fixed it.
3. **Finger appearance must be audited in camera close-ups.** At full-body scale even many floating joints can hide. Produce matching before/after frames at 0° and 45° with the same lighting and scene positions.
4. **Nearest vertex distance is not a collision test.** The original 3.4-second pose had ~903 opposing-hand triangle contacts even with tiny vertex gap; v1.9 uses VTK's triangle-contact filter at sampled poses.
5. **Avoid solving hand collision by sliding both characters' planted feet.** Use a fixed scene-staging offset that passes sampled collisions; in this shot 38 mm forward depth for Noor gave 0 colliding opposing-hand triangles in 25 sampled poses. Additional motion would need grounded root/foot compensation.
6. **Separate absence of intersection from a believable grasp.** A 10mm palm gap at mid-hold and disconnected wrist contour remain, so collision-free staging is not an artistic pass.
7. **Rig export needs independent parse and native-engine check.** The v1.9 GLBs reparse with an external Python loader, but Godot executable was unavailable; a Windows PowerShell and Linux headless import harness is included but unexecuted.
8. **Recheck test assumptions.** An initial v1.9 audit wrongly expected 42 rotation tracks; exported v1.8/v1.9 clips contain 25 keyed rotation channels and one morph-weight channel. The assertion was fixed, not the animation.
9. **Research samples:** v1.9 adds zero independently annotated real-world animation examples to the existing 100-example milestone. It does not establish the cumulative prior count. URL research and procedural tests do not qualify as inspected examples.

## Next hard gates

1. Run the engine-level headless Godot import audit on an actual machine with Godot 4 installed and inspect normal-speed runtime playback, especially the contact orbit.
2. Weld/reshape wrist-to-forearm skin and test the seam under wrist flexion, preserving wrist articulation and four-weight constraint.
3. Build physically plausible thumb opposition, modeled knuckle pads, joint loop shape and realistic finger wrap; check **self**-intersections in each hand, not only hand-to-hand collisions.
4. Rework faces, shoulders, jacket edges and clothing geometry using Blender sculpted models or established character base meshes; the procedural model remains below final art quality.
5. Once rig and art pass in-engine, move on to Ava walking to Noor and an interaction with true weight transfer.