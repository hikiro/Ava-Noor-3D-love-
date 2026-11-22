# V1.8 actual actions, failure causes, fixes, tests — 2026-11-20

### Attempt 1 — source audit, no model change
- **Observed defect:** v1.7 voxelled elbow surface folds in sharp reach; 108 Ava / 109 Noor suspicious face orientations in active-elbow region at t=3.4.
- **Likely cause:** no deliberately arranged elbow edge-flow, narrow skin weighting transition, LBS compresses near bend.
- **Action:** inspected mesh and actor source; read Godot/Blender documentation. No upstream code or Godot executable used.
- **Outcome:** selected a physical ring-retopology approach instead of another v1.7 surface-bulge-only fix.

### Attempt 2 — high-cut retopology failed
- **Observed defect:** arm cut at Y≈1.158 produced an irregular 110-vertex boundary extending to Y≈1.113, because the arm was still fused to torso under the cut.
- **Cause:** X-threshold selection did not cleanly separate the arm component.
- **Correction:** label connected surface components below Y≈1.117 and cut only the actual left/right arm islands.
- **Test:** one watertight manifold surface per actor after triangulated seam stitching; no boundary loops.
- **Prevent:** identify topological arm island before clipping; never infer arm membership from X alone.

### Attempt 3 — first video, seam shelf visible
- **Observed defect:** at rest, a horizontal shelf/line formed at the top of each new forearm.
- **Cause:** first generated ring jumped immediately from the source seam contour to fixed elliptical radius.
- **Correction:** interpolate the initial few rings from exact sampled seam coordinates to new profiles across 48 mm.
- **Test:** before/after front and three-quarter view render, 5.2 s full video render. Shelf visibly reduced; remaining elbow crease still present.
- **Prevent:** enforce tangent/geometric continuity as well as manifold topology.

### Attempt 4 — first weight blend worsened compression
- **Observed defect:** initial elbow ring fit reduced orientation errors but increased compressed triangle fraction compared to v1.7.
- **Cause:** thin ring spacing combined with abruptly changing shoulder/elbow/wrist weights.
- **Correction:** 40 numerical weight candidates (20 per actor) varying hinge blend width and distal wrist transition; selected 75mm elbow band/75mm distal blending as candidate.
- **Test:** full active-elbow surface metrics at t=3.4, not 40 real-world artistic QC cycles.
- **Prevent:** measure orientation risk AND area shrink; do not optimize one at expense of the other.

### Attempt 5 — alternative pose correctives rejected
- **Observed defect:** dual-quaternion-derived morph correction worsened the measured folded/compressed faces.
- **Likely cause:** target morph distorted existing LBS topology and was derived only at one reference pose.
- **Correction:** discarded the approach instead of promoting unverified complex behavior.
- **Test:** 10 targeted probes (5 strengths per actor), source retained under `source/dual_quat_elbow_corrective_v18.py`.
- **Prevent:** no technique is adopted solely because its theory suggests better volume preservation.

### Attempt 6 — critical seam stretch failure (blocking)
- **Observed defect:** local edges ~0.07–0.15 mm in rest separated by ~13–15 mm at reach; computed peak stretch up to ≈196×; an early validation run failed 2/134 checks.
- **Cause:** weight assignment overwrote seam vertices, placing adjacent vertices under mismatched bone weight maps.
- **Correction:** preserve inherited seam weights exactly and blend all new-ring weights gradually over a tunable length.
- **Test:** 134/134 structural checks after seam transition; new weight sweeps re-opened to optimize compression as well.
- **Prevent:** include an edge-stretch QC metric at welded boundaries, including near-zero rest-edge length.

### Attempt 7 — final seam-band selection
- **Observed defect:** 15–25 mm blends still overstretched seams; 63 mm blended too much chest motion into the elbow causing extra folds.
- **Correction:** tested 16 seam-width candidates (8/actor), selected 45 mm. Final active-elbow proxy at t=3.4: Ava 61/3584 suspicious and 0.84% severe compression (v1.7: 108/3053 and 1.08%); Noor 65/3753 suspicious and 0.67% (v1.7: 109/3234 and 0.90%).
- **Test:** 20 chronological kinematic samples per actor; maximum edge stretch under 2.5×; comparison renders front and 3/4; final MP4 complete 125-frame decode.
- **Prevent:** retain regression thresholds, not just one still image.

### Attempt 8 — export and clean reproducibility
- **Result:** both final GLB files reparsed externally; retained 43 bones, 8 morph targets, animation; independent `source+base` clean rebuild produced byte-for-byte identical exported GLBs, SHA256 recorded.
- **Video:** silent 540×960 24fps, 125 encoded frames, 5.208sec. GIF created at half sampling rate.
- **Godot:** engine binary not available; attempted network access failed DNS; included `godot/validate_import.gd` but **did not run it**.
- **Remaining visible defects:** elbow still creases awkwardly, costume transitions are simple, hands can intersect, expressions/mouths are not matched to voice. Visual quality **not approved**, despite numerical pass.

**Completion accounting:** 2 full motion render iterations plus close-up render revisions; 40 initial weight candidates, 16 seam trials and 10 DQ correction numeric probes. **Not 20 distinct full artistic QC redesigns.** No new real external animation examples independently inspected/annotated.