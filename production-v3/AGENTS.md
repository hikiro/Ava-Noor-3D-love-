# Villa Verse — Producer-led directive v3.0

The user supervises the EXECUTIVE PRODUCER. The producer handles task selection, assignment, specialist review, issue escalation, QC and release. Preserve the original `baseline/` archive and the v2.1 failure ledger.

## Agents and trust
Definitions in `.claude/agents/` are **runnable Claude Code subagent configurations**, not proof that agents have been spawned. In this ChatGPT environment there is no Claude Code runtime/subagent launcher. ChatGPT may conduct sequential, clearly labeled single-model role reviews; do not call them independent multi-agent evaluations. Native agent teams are optional and cost more usage.

## Directives carried forward
- Anatomical continuity and realistic scale: head/neck/trunk anchored, measured skeleton, fixed bone lengths, ground foot stability, plausible pelvis/COM shifts, correct elbow/knee axes and proportional limb response to small trunk motion.
- Use original character reference as identity target; Ava gold top, wavy hair; Noor teal jacket, braid; preserve all six cast identities.
- Appearance above metrics: watertight meshes, no collision and 125 frames decoded do NOT equal visual approval.
- If two rounds of patching one structural flaw cannot improve the observable result, prototype a mature rigged human base instead of proceeding with more procedural microfixes. Compare against Blender/MPFB2 and Rigify; verify compatibility and licenses before production use.
- All reviews must cite inspected output and exact test logs; no self-approval and no silent substitutions; actual native Godot runtime validation must be explicitly logged.
- Keep filenames and asset IDs stable, source provenance recorded, red/amber severity failures open until retested; never pretend an aesthetic judgement was independently verified when it wasn't.

## Execution order
Brief → Creative direction → 3D art direction → [junior AD shot/asset plan + technical feasibility] → [artist mesh work + animator target research] → integrated render → independent auditor → feedback triage and correction → creative/3D direction final review → producer release.

## Release
The producer may present unfinished **research/prototype** as labeled if it serves an explicit user request. A final approved video is not released until all required gates in `docs/ACCEPTANCE_GATES.md` have PASS with specific evidence and independent review. `scripts/producer.py` enforces status mechanically; prompts alone cannot verify that reviewers really ran.
