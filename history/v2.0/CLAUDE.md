# Villa Verse v2.0 — Claude/AI rigging instructions

Follow `AGENTS.md` as mandatory QC and consistency requirements. Inspect `qa/ITERATION_LOG.md` and actual previews before editing. Treat procedural rest-pose geometry as prototype, not finished sculpt quality.

Edit `source/wrist_bridge_v20.py` to change wrist topology/weights; use `source/build_v20.py` to regenerate both GLBs, then run `source/validate_v20.py` and inspect the render. Never assume that morph-only or rig-only checks prove realistic movement. Report newly discovered visual and numeric defects even if they are outside the feature currently being worked on.

A new version must carry forward all prior handovers and updated source docs, with actual tests and limitations. Use Godot's native engine to verify import when a binary is available. Never state that Godot ran merely because the GDScript exists.