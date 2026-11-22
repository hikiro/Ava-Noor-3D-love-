# Villa Verse animation director rules — v1.8

This file is the source-controlled memory for future generations. Read at the beginning of every iteration; carry forward unchanged unless evidence justifies changing a rule. `CLAUDE.md` contains the abbreviated operational directive.

## Persistent constraints (user wording normalized to engineering checks)

- **Heads connected, never float:** continuous neck/head bone hierarchy and visibly plausible seam across every camera angle. Do not confuse parentage with watertight skin.
- **Measure proportions:** approximately realistic adult head/body/arm/leg ratios; preserve character identity, colors, outfits, height, and the v1.5 baselines.
- **Connected bones:** elbow always lies between shoulder and wrist, fingers connect to knuckles, anatomical local axes. Support forward vs. backward weight transfer.
- **Proportional secondary motion:** a millimeter of trunk movement must not create tens of centimeters of unintended hand or foot displacement. Deliberate reaches are separate animation states.
- **Foot locking:** planted foot in world coordinates with no unconstrained sliding. Character interaction requires physical and rendered hand contact, not distance-only success.
- **Review the actual encoded video at normal speed**, full duration; separately inspect all motion phases, straight and bent joint poses, close-ups, camera side/three-quarter view and occlusion.
- **Numbered iteration QC:** for each real intervention log defect, probable cause, correction, test performed, outcome, remaining gap, and preventive rule. Do not call multiple samples, numeric parameter sweeps, or research links complete artistic redesign iterations.
- **Preserve all prior versions** in full versioned archives with source, inputs, render and known failures. No untested “Godot verified” assertions.

## New empirical rules from v1.8

1. **Voxel mesh watertightness does not establish elbow edge flow.** In v1.7 the arm region had no deliberate elbow rings; v1.8 replaces each forearm/elbow with 16 sewn ring rows connected to one original shoulder/torso surface.
2. **Keep initial ring geometry tangent to the source seam.** Abruptly choosing radius at first lower ring creates a visible horizontal shelf. Blend from sampled seam coordinates into target elliptical geometry across roughly 48 mm.
3. **Use geometric component identification below the cut, not just X thresholds.** Cut a separated arm only where chest, left and right arm are disconnected below the cut (v1.8 cut near 1.117 × body scale). The earlier higher cut caused unwanted openings.
4. **Skin weight continuity is crucial at welded seams.** Initial v1.8 retopo applied a new weight set directly at the seam, generating up to 196× measured stretch for almost-coincident vertices under motion. Preserve old weights at the cut and blend gradually to new bone weights.
5. **Choose seam blend by BOTH normal orientation AND compression and stretch.** A 45 mm seam-weight transition reduced the active-elbow suspicious orientation fraction and severe compression relative to v1.7 without exceeding measured 2.5× edge-stretch threshold during 20 motion samples. A 15–25 mm transition gave more extreme stretching; a 63 mm transition caused excess elbow folding.
6. **Rejected pose-space volume fix:** A targeted dual-quaternion-derived morph was actually worse on this LBS/glTF rig (higher fold/compression metrics). Do not reuse without an isolated controlled experiment in the target engine.
7. **Surface continuity and contact correctness are distinct:** Grasp remains unapproved; overlap and finger intersections are not measured by closest-vertex distance.
8. **Godot not tested.** GLB reparse, offline render, and deterministic build are confirmed, but Godot editor importer and playback were not run. `godot/validate_import.gd` is an executable-on-user-machine check only.
9. **Visual limitations:** forearm/elbow seam shadows and simple chest/faces remain; structured mesh is a mechanical improvement, not Sims-like art approval.
10. **Research sample target 100:** This release does not include independently inspected and annotated real animation examples, so no increments to that goal can be claimed from this release.

## Next hard gates

1. Run Godot headless asset import and GDScript audit; capture logs; inspect playback with a screen recording and compare 0, 2.5, 3.4, 5.2 seconds.
2. Remodel hands, palms, shoulder muscles and garment layers in Blender/Godot instead of simply increasing polygon count; resolve actual collision-free grasp.
3. Add dedicated elbow/forearm twist and pose-specific volume corrections only after deformation tests, preserving valid shoulder/torso topology.
4. Add sound-driven facial animation only after audio timing exists; the current visemes are procedural, not true lip-sync.