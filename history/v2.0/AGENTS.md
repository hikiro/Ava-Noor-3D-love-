# Villa Verse Model/Animation Director — persistent directives (through v2.0)

## Do not violate
1. Keep each character's head rigidly connected to neck/spine in the bone hierarchy. Preserve measured overall proportions, bone lengths, eye and hand scale, and established cast identity.
2. Body/root translations must not amplify hand/foot displacement beyond the action's physically motivated shoulder-elbow-wrist chain. Animate anatomical axes, body momentum and weight transfer correctly; preserve planted foot positions.
3. A skin with connected bones is NOT the same as a connected skin surface. Enforce manifold/watertight mesh topology and explicit shared-index connectivity through all visible joints. Never fake a seam by overlapping caps when the shot exposes wrists.
4. Weight interpolation must vary continuously in 3D at shoulder, elbow, wrist, knuckle and thumb-index web; hard nearest-bone switches create edge distortion. Four normalized weights per vertex, bone IDs within exported skeleton.
5. Do not confuse **no opposing-hand triangle collision** with a convincing handhold. Measure both intersections and contact distance, inspect multiple camera views, and check each hand's own self-intersections.
6. Run encoded-video QC and relevant sampled numerical checks separately. A numerical pass does not prove beauty, acting or facial fidelity. Never claim Godot or Blender was tested without actually running it.
7. For all changes, preserve a versioned handover ZIP, executable source, raw failure logs, causal explanation, corrections, tests actually executed and open issues. Count iterations honestly; a frame sample is not an artistic iteration.
8. Prioritize the largest visual defects before expanding scenes: finger-wrapping/high-five-like gesture, inherited mouth-cavity morph overextension, facial anatomy, garment deformation, Godot engine import/playback.

## Current stable engineering facts
- v2.0 wrists are now a connected body-arm-hand surface for Ava and Noor, using 4 support loops per side.
- 39 mm scene Z separation avoids collisions at the currently verified samples; **do not assume it is safe for new poses**.
- Technical baseline: 43 bones, 8 blend shape channels, 25 rotation tracks, 24fps/125-frame interaction.
- Known facial mouth-morph distortion remains; do not erase the failed visual finding because scoped mechanical checks pass.
- Native Godot/Blender validation still outstanding.

## Source of truth
Read `README.md`, `qa/ITERATION_LOG.md`, `qa/validation_v20.json`, `qa/CONTINUITY_AUDIT.json`, then inspect the actual rendered MP4 and contact sheet before modifying code.