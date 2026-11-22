# Villa Verse production agent directive (version 2.1)

## Priority order
1. Preserve Ava/Noor identity, scale, costume, and the existing 43-bone/skin conventions.
2. Character physics/anatomy over smooth interpolation or visual tricks: head-neck-torso remains connected; 7–8-head-height adult-like proportions; fixed bone lengths; stable feet; weight/COM moves in physical travel direction; elbow/knee motion consistent with anatomy.
3. Never exaggerate arm/leg movement by an order of magnitude when the torso only moves slightly; separate gestures from locomotion.
4. Production imagery and QA must come from actual deformed geometry and encoded frames, not from storyboard drawings mislabeled as final animation.
5. Every new edit requires contact collision probes, finger self-contact consideration, mouth/joint mesh deformation checks, visual inspection from front, quarter, and side, and comparison to previous render.
6. Numerical tests are necessary, NOT sufficient. Approval needs actual visual inspection at normal playback speed, especially small fingers and lips.
7. Never claim Godot engine validation unless native executable loads the GLBs, displays the animation, and a test log/screenshots are saved.
8. No silent substitutions: if a model, library, or executable is unavailable, record exactly which step is untested.

## v2.1 learned regressions
- Huge cavity dilation (v1.6 original 4.6× jaw / 3.3× O per full morph) created >5× stretch. Use bounded mouth-cavity morph displacements and run all-125-frame edge length checks; keep the limits in code and tests.
- For the current topology, revised 1.50× jaw and .65× O cavity deltas passed 2.5× at actual sampled speech weights; these coefficients are prototype-specific and must NOT be assumed safe for other mesh topology.
- Lips move separately from the face, so reduced geometric stretch can still yield visually detached layers. Check geometry + actual mouth closeups, including combined jaw/O and jaw/EE.
- Four finger-flex profiles and five wrist biases did not create a believable grasp; a pose being close is not evidence of an interlocked grip.
- All-125-frame opposing-hand zero-collision results are useful, but a 39 mm depth offset can artificially keep hands apart. Perform *contact plausibility* QA in addition to collision detection.
- Full-body video views hide close-up fingertip and facial defects. Keep fixed closeup and two oblique camera angles in every character acting audit.

## Iteration ledger schema, mandatory
For every attempted correction record: ID, action/variant, observed defect, hypothesis, exact fix, code and render files, tests actually executed, result, unresolved visual issue, prevention rule. Distinguish parameter probes from independent design iterations. Never inflate counts.

## Current release quality gate
v2.1 accepts **technical prototype** only. Do not start full series production until native Godot import/playback, believable contact, mouth-corner topology, and face/garment design reach visual approval.