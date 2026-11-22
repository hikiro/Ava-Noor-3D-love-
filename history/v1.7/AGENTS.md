# Villa Verse — versioned animation director rules (v1.7)

This is the portable persistent direction file. Read at the start of every future iteration and preserve it in every handover.

## Requirements from user direction

- Preserve recognizable characters, outfit palettes, all previously approved components and versioned source; do not silently replace character identities or accepted shot plans.
- Heads remain connected to necks and torso with measurable stable pivots and no floating disconnects.
- Measure body proportions; keep limbs fixed-length and anatomically plausible. Do not hide length errors with interpolation or arbitrary mesh positioning.
- Shoulder, elbow, wrist, knee, ankle and finger pivots are hierarchical; moving torso by a small distance cannot move a hand/foot 30 times farther unless a deliberate reach/swing is choreographed.
- Forward body weight should visually and mechanically progress forward; backward recoil should act backward. Feet planted during stationary interaction must not slip.
- Hands and actors must obey physically plausible contact and occlusion; proximity is not a substitute for a collision/penetration check.
- Every animation shot must be reviewed at normal speed and sampled through all motion phases. Rendering and numeric tests do NOT prove artistic fidelity.
- For every attempted improvement record: source of idea, action, visible/numeric defect, likely cause, change, tests actually performed, remaining risk, and prevention rule. Count actual iterations; never claim a 20-loop artistic QC unless 20 distinct iterative cycles were performed and evidenced.
- When reviewing other repositories or references, record source URL and exactly whether information was studied, tested or merely found. Preserve research provenance.
- Maintain versioned handovers and prior versions, including the entire original history where possible.

## v1.7 findings to carry forward

1. A connected skeleton is not the same as connected surface topology. Previous separate deltoid, torso and forearm shells created visible seam breaks. A single watertight upper-body surface is a real improvement, but it covers only that body region.
2. A large upper-arm envelope influenced too heavily by the elbow causes an ugly shoulder balloon when the forearm reaches. Restrict elbow weight transition close to true elbow; examine front AND 3/4 motion before release.
3. Shoulder radius reduction alone does not fix joint deformation. Pivot, skin weights and pose-space correctives must be addressed together.
4. At ~90° elbow flex, linear blend skinning compresses and may locally fold the elbow even with welded topology. The v1.7 forward correction reduces a measured orientation anomaly but does not eliminate it. Need anatomy-aware elbow twist bone/pose correctives or Blender-authored retopology with skin weights.
5. Original clothes may disappear when fused skin overlaps them. Repaint necessary costume zones in the body topology and retain trim/cuffs; check character identity against source sheet.
6. VTK/FFmpeg CPU rendering verified locally is not Godot editor/playback. Import must be independently executed before calling scene engine integration verified.
7. A ~0mm closest hand-vertex gap can indicate overlap, not correct grasp. Finger-to-finger collision and occlusion remain unverified.
8. 20 timeline windows and 36 candidate parameter probes must not be called 20 artistic iterations. Record distinct runs honestly.

## Next actionable requirements

- Improve inner elbow creasing and pose-space volume preservation, measure triangle/edge distortion, inspect at bent and straight pose from 3+ angles.
- Retopologize shoulders and elbow rings in Blender and paint clavicle + upper-arm + twist-bone influences to preserve silhouette in reaching and shrugging.
- Create proper continuous palm/finger rig and surface contact with collision or constraint solving, then animate direct handhold with no interpenetration.
- Test actual Godot engine import and animation tracks; capture evidence from the engine and reject models if imported rotations or morphs differ from CPU test.
- Only then expand to walking, speaking, camera blocking and next episode.