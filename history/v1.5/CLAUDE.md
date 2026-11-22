# Villa Verse character pipeline — long-term production directives

## Mandatory physical and design constraints

1. Head connected through neck_base → neck_top → head; anatomically plausible skin overlap at throat. The current mesh parts are overlapping, NOT welded, so keep a known-gap issue until repaired.
2. Adult proportions and skeletal rest lengths measured and invariant. Never fake independent-moving body parts by arbitrarily multiplying root movement into limbs.
3. World-space planted foot targets, swing trajectories separately; center-of-mass shifts must match body weight and direction. No walk animation is certified in this release.
4. Shoulder insertion must be visually inspected during reaching and at rest, not only checked by joint lengths; minimize sleeve gaps and crushed volume.
5. Finger/contact paths: measure mesh distance AND check visible contact for collisions and depth interpenetration before calling natural handholding done.
6. Preserve cast colors, outfits, recognizability, and all six character identity sheets; Ava/Noor are pilot, others remain unchanged in archive.
7. Every output version includes original/source, model geometry, rig/export, previews, QA raw results, iteration log, failures, provenance, archive and portable rebuild.
8. Never claim a production-quality model, successful Godot import, twenty artistic loops, independent research samples, or complete video unless actually verified.

## Status v1.5

- New Ava/Noor expressive 23-bone GLBs produced, actual VTK 3D rendered test clip and expression previews.
- Numeric checks and parser roundtrips passed; engine integration remains untested.
- **Art style gate not passed:** not yet close enough to original illustrated cast reference for final episodes.

## Follow-on priority

Use a mature open-source Blender/Godot 3D character workflow if possible rather than escalating procedural primitive shapes. Sculpt cohesive surfaces; topology/weight-paint test at shoulders and hand; lip-sync morphs and eye tracking; animation with visible weight transfer; retest movie-night episode blocking.