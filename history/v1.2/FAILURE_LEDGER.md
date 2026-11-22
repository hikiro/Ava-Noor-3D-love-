# Audited failures, root causes and repair history

**Previous version inspected:** `source/render_storyboard.py` v1.1. It produced separate keyed vector shapes and manually selected walk/reach outlines; it was a still-blocking kit, not a fixed-bone rig.

| ID | Actual finding | Underlying cause | Action and evidence | Status |
|---|---|---|---|---|
| A01 | Earlier heads/neck/torso could have discontinuities across poses | Posed SVG paths were generated without a shared skeleton | New head center derived from `neck_top`, itself a child of `shoulder`; exact hierarchy test in QA 02 | Fixed in coded motion rig |
| A02 | Existing limb shapes could change lengths between standing/walking/reaching | Pose-specific freehand paths and no bone lengths | Added analytic leg and arm IK, normalized FK, enforced fixed lengths; QA 03–06 | Fixed numerically |
| A03 | Initial new-rig contact attempted an unreachable arm extension (`102.110px` needed, `99.970px` maximum) | Contact target set at the wrong world-space height | Moved shared palm target from `(352,603)` to `(349,577)` and checked both actors' reach | Fixed |
| A04 | First SVG export crashed: `Pose` object lacked `lean` | Code used `p.lean` instead of dataclass field `p.leaning` | Corrected property reference, rendered/debugged frame | Fixed |
| A05 | Initial preview showed wrong knee bending side | Analytic IK knee pole used wrong sign for screen-down coordinates | Changed knee pole from `face` to `-face`, QA 12 asserts correct sign across sampled timeline | Fixed |
| A06 | Upper-arm/forearm lengths shifted in ordinary arm motion | FK vectors were freeform screen offsets, not normalized | Normalize each FK vector to locked segment length; QA 05, 06 | Fixed |
| A07 | Shoes could stay on the ground while the swing ankle lifted | Old shoe SVG was positioned from `GROUND`, not per-frame ankle | Shoe now drawn relative to each swing/planted ankle | Fixed |
| A08 | Abrupt lift-off velocity: QA 11 observed `38.803422 px/s` (threshold 2) | `sin(pi*q)` has nonzero derivative at arc start and end | Apply `sin(pi*smooth(q))`; QA 11 reran at `0.181702 px/s` | Fixed |
| A09 | Initial rig appeared narrow-shouldered with arms overlaid on torso | Shoulder span 0.74 head units; arm pivots inside torso | Increased span to 1.4 head units, arm pivots to ±0.61 head units; QA 01 verifies width/skull ratio | Fixed in new study |
| A10 | Root temporarily stopped at each intermediate walking key | Independently smoothstepped segments force derivative zero at each knot | Replaced root curve with C1-continuous cubic Hermite, with nonzero tangents at interior steps | Fixed mathematically; subjective gait still needs improvement |
| A11 | First 20-point suite failed export check (no video yet) | Export pipeline not yet implemented | Wrote frame-stepped renderer and FFmpeg export; 225-frame MP4 and looping GIF generated | Fixed |
| A12 | Need evidence for complete 15-second span, not random screenshots | Initial proof sheet had 16 sampled timestamps | Added 20 consecutive 0.75-sec QC windows with 3 screenshots each + numeric 31-sample checks; generated every-frame MP4 decode report | Completed technical audit |

## Log integrity

- `qa/baseline_run.txt`: first actual 20-check pass, 18 passing, toe-off and missing video failing.
- `qa/after_joint_repairs.txt`: after toe-off repair, 19 passing, export still missing.
- `qa/final_20_checks.log`: exported video and 20/20 checks passing after continuous-velocity root update.
- `qa/20_timeline_windows.log`: exactly 20 chronological windows, 0.00–15.00, 20/20 mechanical passes.
- `qa/full_video_decode_report.json`: 225/225 decoded video frames; no assertion of manual viewing all 225 frames.

## Important unresolved shortcomings

1. **Movement remains stylized and diagrammatic.** The visible art is a simple vector rig; no deformation mesh, muscular soft tissue, secondary cloth/hair, toe roll or realistic feet rotation. Passing bone-length checks does not mean lifelike acting.
2. **Forward/backward weight transfer is kinematic only.** The torso actually translates to the correct side of the pelvis, but no inverse-dynamics solver enforces ground reaction forces or whole-body balance.
3. **One-dimensional staging.** Depth sorting/occlusion has been approximated. True 2.5D floor placement, sit/stand staging and collision with benches are not solved.
4. **Limited acting.** This is a 15-second test movement centered on Ava/Noor and a background Kai, not the scripted full 30-second villa reel, and no complete lip-sync, eye acting or dialogue performance is included.
5. **No subjective motion certification.** Actual video was playable/decoded; 16 timeline frames and 20 triptychs were reviewed, not a continuous human-audited 225-frame playback with corrections on every frame.
6. **Source learning scope.** Research references were read and used, but there were not 20 separate online searches or 20 independent discovered bugs. The 20 passed checks and 20 timeline QC windows are documented without claiming otherwise.