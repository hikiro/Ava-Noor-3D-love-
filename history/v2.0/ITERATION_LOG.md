# v2.0 implementation ledger — actions, defects, causes, fixes, verified tests

**Iteration count:** ONE major wrist-topology redesign, TWO finger-weight correction passes, staging trials and QC reruns. NOT 20 independent artistic redesigns; not a new empirical sample toward any 100-video director-study target.

| ID | Observed defect / action | Root cause | Correction | Test actually run | Result / gap | Prevention rule |
|---|---|---|---|---|---|---|
| 01 | v1.9 wrist cap meets independent hand shell, visibly creating hard ring | Separate meshes share neither edges nor index topology | Clip both surfaces at measured wrist levels; construct 4 intervening skinned loops per arm and angular zipper onto hand seam | Mesh generation, watertightness, winding checks, matched 25°/55° close-ups | Connected surface, seam removed in tested angles. This is not automatically a photorealistic wrist | Check shared vertex graph, not only visual overlaps |
| 02 | Initial unified hand still stretched 9–11× around knuckles during reach | Nearest-finger assignment + sharp thumb-index mask generated adjacent triangles driven by unrelated bones | Spatial Gaussian finger weighting across neighboring bones | 6 motion poses, edge-length comparison at 6 timestamps | Initial reduction to ~7–10× only; failed stricter standard | Always inspect local edge stretch, not just bone hierarchy |
| 03 | Finger-web stretching remained with first smoothing pass | Thumb mask still hard-switched some edges from thumb/hand to outer finger | Introduced a continuous thumb-to-index web weight function | Rebuilt two GLBs and measured edge ratios at six sampled poses | At t=3.4s worst stretch ~3.05× Ava / ~3.12× Noor; far better, still visible mesh inaccuracies | Avoid hard if/else assignments for adjacent finger/hand regions |
| 04 | v1.9 depth offset (38mm) produced collision late in changed v2.0 handhold | Reweighted digits altered deformed mesh, prior staging was pose-specific | Tested offsets 38–45mm; fixed 39mm depth | VTK triangle-triangle collision comparisons and late contact probes | 26 sampled palm frames and five wider distal-arm samples 0 hits; not exhaustive between samples | Retest collision after **every** geometry or skin-weight edit |
| 05 | Full 125-frame VTK collision audit stalled | VTK close-surface numerical warnings (`vtkMath::Jacobi`) and repeated near-tangent tests; full audit could not finish reliably in current runtime | Kept independent 125-frame geometry/edge scan; narrowed collision to 26+5 selected frames | 125-frame skinning/foot/bone/edge checks, 26 palm and 5 full distal-arm VTK collision tests | Report measured sampling honestly; no 125-frame collision-coverage claim | Track coverage and numerical-tool failure separately from collision result |
| 06 | Whole-mesh edge stretching exceeded 3.5× on facial parts | **Inherited** v1.6 mouth cavity morph stretches tightly meshed facial vertices under dialogue | Not changed in this wrist-specific release; registered open defect | Max stretch search over all 125 encoded frames and model ranges | Ava up to 5.47×; Noor up to 6.36× in mouth cavity; visual QC remains incomplete | Mechanical pass must not hide out-of-scope discovered faults |
| 07 | GLB file accepted by independent loader but native Godot import unavailable | No installed Godot/Blender executables; downloading Godot from host fails DNS | Updated Godot 4 viewer, model paths, animation name, headless import harness and user-side instructions | `command -v godot`, `command -v blender`, `curl` host probe; independent glTF parse | Godot runtime NOT tested; no native playback certification | Engine playback must run before production approval |
| 08 | Need reproducible handover with source and history | Prior experiments should remain reconstructible | Bundled model source, scene, metadata and complete v1.9 archive | Rebuilt both GLBs, compared SHA256; separate video decoding check, ZIP manifest | Byte-identical GLB hashes, 125 encoded frames decoded, ZIP verified | Preserve artifact files and logs, not only instructions |

## Performed checks

- v2.0 numerical/structural test suite: **38/38 scoped tests passed**; the *known* 125-frame facial-morph overextension is an explicit open defect, not a hidden passing visual gate.
- Topology audit confirms connected body-to-L/R-hand vertex graphs for both characters and 2 watertight merged upper-body surfaces.
- 125 timestamp tests per actor for bone length, motion finiteness, planted feet, wrist bridge edge stretch; wrist support edges stay below 2.5× rest length.
- 26 sampled frames for palm/finger opposing-hand mesh collision; 5 sampled frames also include the distal forearm and welded wrist region. Those samples showed zero contacts at the final fixed 39mm offset. Self-collision, full-frame collision coverage and physical pressure-based grip remain unverified.
- Third-party GLB parse, 43 bones, 8 morph targets and 25 animated rotation tracks verified for both actors.
- 1 final 125-frame 540×960 MP4 decoded; 24fps rendering; comparison close-ups and six-pose sheet inspected.
- Deterministic GLB rebuild confirmed with matching hashes on both actors.

## Unresolved and next recommended work

1. Correct inherited mouth-cavity morph topology/displacement before dialogue animation.
2. Upgrade the natural handhold from palm touch to intentional finger wrapping and resolve per-hand self-collisions; do not force hands through each other to simulate contact.
3. Rebuild face and garment surfaces to meet character reference quality, improve lighting/shaders.
4. Test both GLBs inside actual Godot 4 and capture native engine animation/screenshots before starting walking and more complex interactions.