# Claude Code / ChatGPT Villa Verse v2.1 handover

The source of truth is `README.md`, `AGENTS.md`, `qa/ITERATION_LOG.md`, and `qa/validation_v21.json`.

## Mandatory workflow
1. Read the above sources and inspect the current full video + fixed closeups before suggesting changes.
2. Modify the existing `source/build_v21.py` unless a new version is explicitly approved; do not rebuild from arbitrary shapes or discard source assets.
3. Keep head/neck/torso and elbow/wrist continuity. Preserve 43 bones and all saved skinning weights unless deliberately migrating and regression-testing them.
4. Rebuild both GLBs, render short geometry-based animation, check frame phases and first/middle/last encoded frames, run contact and mesh-stretch checks, compare before/after, record genuine failure causes.
5. Do not conflate Python/Vtk/trimesh successful export with Godot playback; use `godot/run_godot_checks.sh` or `.ps1` when Godot is available and retain logs.
6. Do not declare production-ready visual fidelity based on watertight meshes, bone counts, or 43/43 tests. Ask visual director to assess eyes, mouths, body proportions, shoulders, hands, and camera clarity.
7. Keep high-quality user feedback verbatim in issue histories and propagate rules into AGENTS.md. Previous full v2.0 release is inside `archive/`.

## v2.1 newly observed failure modes
- Morph target scaling can cause extreme local triangular stretch; long thin triangles and very thin mouth membrane amplify the error.
- Moving lips without connected mouth-corner topology can visually disconnect them even if geometry is finite and the edges are within limits.
- An offset that eliminates hand collisions can also ruin hand contact. Test separation and quality separately.
- Wrist-turn variants are not automatically anatomic improvements; reject unsupported 'solved' claims.

## Remaining milestones
Native Godot engine import + playback; joint-specific finger wrapping and pressure-aware contact; mouth topology/sculpting; more realistic faces and garment art. No claim that these are implemented.