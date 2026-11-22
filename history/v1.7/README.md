# Villa Verse — v1.7: continuous shoulder-to-wrist upper-body geometry

**Status:** Experimental rigging/motion test. NOT approved for production animation fidelity.

## Contents

- `models/ava_CONTINUOUS_SHOULDER_v1_7.glb`, `models/noor_CONTINUOUS_SHOULDER_v1_7.glb` — editable glTF 2.0 actor meshes, 43-bone skin hierarchy, 8 facial/cloth morph targets, and 5.2-s animation.
- `models/*_continuous_upperbody_v17.ply` — stand-alone original replacement upper-body meshes for independent inspection/retopology (no skeleton in PLY).
- `models/base/*` — original v1.5 source arrays used to faithfully reconstruct the versioned rig and preserve identity.
- `source/build_v16.py` — unmodified legacy exporter class used as input/reference; original v1.6 complete release is in `archive/`.
- `source/build_v17.py` — **active** unified-body authoring and export script; does not require Blender or Godot to generate models.
- `source/render_motion_v17.py` — full local CPU-skinning render; uses VTK + FFmpeg.
- `source/render_shoulder_comparison.py` — identical v1.6 / v1.7 front and 3/4 comparisons.
- `source/elbow_corrective_experiments.py` — 36 measured elbow corrective candidates (18 per actor); experimental, not active production script.
- `source/validate_v17.py` — GLB, connectivity, skeleton and 20-sample time domain checks. Requires generated MP4.
- `source/render_qc_sheet.py` — 20 chronological sampled frames + lower-fps GIF.
- `godot/` — unverified Godot viewer with the new GLBs (import/test on Godot 4 required).
- `qa/` — validation JSON, research sources, failure/iteration log and reproducibility SHA.
- `previews/` — 5.21-second 540x960 24fps render, GIF, comparisons.

## Main change

Old v1.6 body geometry was assembled from separate torso, sleeve/deltoid, armpit and forearm components. The v1.7 authoring script generates **one** watertight, connected surface running from the waist through both shoulders and forearms down to the wrists. It removes old overlapping parts, adds four-influence skin weights blended across joint boundaries, and preserves all 43 bones and 8 existing expression/clothing controls.

Ava's gold outfit and Noor's teal jacket/white top remain color-coded. Visual fidelity remains stylized/procedural, NOT final detailed Sims-like art. Separate hands, heads, neck and pants are still separate meshes, connected via the preserved skeletal hierarchy as before; only **upper-body surface** is welded. The neck/head geometry is not welded to the torso mesh.

## Run

Python dependencies: `numpy`, `scipy`, `scikit-image`, `trimesh`, `vtk`, `Pillow`, `opencv-python`, `imageio`. FFmpeg executable required for MP4. See also `requirements.txt`.

```bash
python source/build_v17.py
python source/render_motion_v17.py
python source/render_shoulder_comparison.py
python source/validate_v17.py
python source/render_qc_sheet.py
```

To inspect in Godot: open `godot/project.godot` in Godot 4, import assets, run `Main.tscn`, use LEFT/RIGHT to orbit, SPACE to pause and R to restart. **This has not been executed in Godot in the current environment.** Open in Blender via File > Import > glTF 2.0 to inspect or retopologize; actual Blender import is similarly unverified.

## Quality gate

- **Mechanical:** 128 of 128 numerical/structural tests passed on generated assets; 20 sampled times per actor; deterministic portable GLB rebuild; 125/125 MP4 frames decoded.
- **Visual:** The previously separated shoulder/elbow edges disappear in same-angle close-ups; early bulging was reduced by relocating elbow skin influences near the true elbow hinge.
- **Open failures:** approximately 92 Ava and 89 Noor elbow triangles are flagged at the hold pose by a pose-normal *proxy* (not a definitive self-intersection count); strong local elbow edge compression persists. There is no collision-resolving grasp or anatomical facial/lip-sync solution. No Blender/Godot runtime check. Not a production quality pass.
- **Iterations:** This release includes multiple mesh/reweighting revisions and 36 measured elbow-corrective candidate probes, **not** 20 independent artistic redesign cycles. This distinction is preserved in `qa/ITERATION_LOG.md`.

Research provenance and all known carry-forward constraints are in `AGENTS.md`, `CLAUDE.md`, `qa/RESEARCH_SOURCES.md` and `qa/ITERATION_LOG.md`.