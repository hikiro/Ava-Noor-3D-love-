# Villa Verse v1.9 — actual interventions, failures, and QA evidence

**Scope:** One new anatomical hand-surface modeling pass, and scene contact staging improvement for Ava and Noor. This is not a 20-artistic-redesign loop. We used actual rendered geometry and an exact opposing-hand triangle-contact filter.

| ID | Action/defect observed | Likely cause | Correction | Checks actually performed | Result and remaining gap | Prevention/regression rule |
|---|---|---|---|---|---|---|
| 01 | Inspected v1.8 hands at 3.4s in 0°/24°/55° camera close-ups. Visible detached finger capsules and palm gaps | v1.4–v1.8 finger pieces each were separate primitive meshes, rigidly weighted to bones | Replaced with a unified rest-pose palm, knuckles, 4 tapered fingers and thumb per hand, with shared topology and blended joint weights | VTK close-up render; trimesh watertightness and connectivity | Original detached pieces removed. New surface continuous at rest but still procedural and not welded to forearm | A bone parented mesh is not guaranteed to be connected skin; inspect actual triangles and external silhouette |
| 02 | First new hand surface failed `is_watertight` | SDF bounding grid upper Y clipped the wrist cap | Expanded signed-distance field upper Y from +72 mm to +110 mm above palm center | Built and checked both hands for Ava and Noor | Four hand shells watertight with single component; initial failure preserved in ledger | Keep geometric SDF safety margins, assert positive volume + watertight and connected surface |
| 03 | Opposing hands interpenetrated heavily in v1.8 hold pose (~1185 old-triangle contacts at zero depth; new hand with zero depth ~903) | Both mesh volumes occupy near-identical Z plane; manual pose optimized visually from frontal view only | Tested fixed Z scene offsets 0–70 mm and preserved fixed feet; selected Noor +38 mm in depth | VTK `vtkCollisionDetectionFilter` on actual posed hand triangles, sweep at 3.4 and 5.15s | 0 opposing-hand triangle contacts at 25 final sampled positions. At 3.4s closest vertex gap ~10 mm, so gesture still not a credible tight grip | Contact acceptance requires triangle collision + proximity, never proximity alone |
| 04 | A 35 mm staging offset appeared good mid-hold but produced 86 contacts at t=5.15s | End-of-shot wrist/finger rotation changes after 4.4s | Increased **static** depth offset to 38 mm instead of animated root sliding | Sampled 25 times across 0–5.19 seconds; checked 3D proximity | All 25 samples: zero opposing-hand triangle intersections; late gap ~1.8 mm | Validate entire timeline, especially late retiming/finger curls; preserve planted foot locations |
| 05 | First independent QA showed 43/45 due to rotation-channel assertion | Audit mistakenly treated all 43 bones as animated | Compared exported JSON tracks to previous v1.8; changed requirement to 25 actual rotation channels | Reopened both GLBs via external loader; checked tracks and 8 morph targets | 45/45 checks passed after correcting assertion; animation unmodified | Assertions must reflect export contract, not assumed track count |
| 06 | Actual engine test blocked | No Godot binary installed; network DNS failed | Added run_godot_checks.ps1/.sh with log capture, added camera closeup (`C`) in viewer source | Tested for available executable, attempted remote download HEAD (DNS error); verified launcher files exist | Actual Godot import/playback **not performed** | Never claim native engine success from GLB parse or static GDScript alone |
| 07 | User-visible simplification remains in wrist, hand anatomy, faces | Hands are separate from forearm geometry and inherited rig controls allow limited sculpting | Recorded as open defects, no false 'passed visual quality' | Viewed encoded 6-phase sheet and matching before/after contact closeups | Realistic grasp and Sims-like appearance still fail intended quality bar | Do not conflate numerical pass with artistic approval |

## Actual test inventory

- 2 hand mesh builds (first clipped, second successful), then one final reproducibility build after metadata corrections.
- 13 finer Z-depth candidates at selected poses, plus earlier coarse staging tests.
- 25 timestamp samples of opposing-hand **triangle contact** at the fixed 38 mm offset, all zero intersections.
- 45/45 final numerical/structural/video tests, following correction to a test assertion (initial 43/45).
- 1 complete v1.9 125-frame MP4 at 24 FPS; 6 frame temporal sheet; 2 close-up views per version under matched staging; additional 9 VTK diagnostic closeups.
- **Independent artistic redesign iterations:** 1 unified-hand mesh topology intervention. No 20-cycle claim.

## Unresolved

- Godot editor/animation import not run; browser-verified Godot documentation is not engine evidence.
- v1.9 mid-hold is around 10 mm apart; last phase much closer. The two hands remain separate meshes; self-penetration within each individually deformed hand was not checked.
- Wrist seam and elbow/shoulder silhouette still visibly simplified. Faces and garment deformation below final quality target.
- Actual Blender sculpt/weight painting, voice-driven lip-sync and fully physical grasp not completed.