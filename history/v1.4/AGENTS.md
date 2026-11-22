# Agent instructions — Villa Verse (persistent)

Current version v1.4. Maintain complete, portable, versioned handovers with source, assets, QA, history, external research references, failing tests and exact verification scope. Read README and qa/ITERATION_LOG before modifying.

## Rig requirements

- Head is connected to torso through actual skeleton hierarchy: root > hips > spine_lower > spine_chest > neck_base > neck_top > head.
- Use measured body proportions with actual unit units (metres); do not let movement create telescoping limbs or unbounded motion multipliers.
- Root and torso motion must agree with direction of travel and momentum; planted feet need world-space locking; reaching hands require IK and deliberate contact targets.
- Small body lean must not amplify into extreme wrist/ankle motion unless expressly an intentional separate action.
- View from front, 3/4, side and rear; verify geometry and occlusion and all relevant joints, including fingers and elbows.
- IK target convergence alone is not a contact solution; inspect meshes and penetration/occlusion visually.
- Validate every migration in Godot before claiming Godot playback works. Current runtime test is pending; no Godot executable available in this environment.
- Keep original characters' identifying designs; never silently replace cast with an unrelated story.

## Technical

- `source/build_v14.py`: original glTF 2.0 exporter / procedural model polish / skin and embedded animation.
- `source/validate_v14.py`: numeric QA; 20 timeline sample points per actor are not 20 independent redesigns.
- `source/rebuild_portable.py`: rebuild from zipped v1.3 base.
- Source reuses earlier v1.3 geometry; do not erase archive or lossy convert it to images.

## Production gate next

1. Open `godot/project.godot` in Godot 4 and verify actual skeleton animation import and playback.
2. Polish realistic eyes/lips/ears, clothing topology, skin smoothness, hand grasp and 3D collision/non-penetration.
3. Test head yaw and spine motion jointly; validate shoulder volume conservation and elbow deformations under side view.
4. Only after these tests, start walking, turns, contact blocking and complete reel.