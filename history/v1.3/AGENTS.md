# Villa Verse / permanent production rules

## Quality gates

- The six original character identities, clothes and proportions are canonical, based on `reference/cast_style_reference.png`. Never silently swap designs.
- Show multiple angles, including front/side/back, before calling a model polished. Never certify an appearance based on one camera angle.
- The head must remain physically contiguous with the neck, which attaches to the shoulder/chest/spine via a rig hierarchy. Measure actual geometry gaps and verify skin deformations once skinning exists.
- Use physically plausible adult proportions and keep bone lengths fixed. `models/rig_targets_y_up.json` is the current measured STARTING POINT, not a completed rig.
- For walking: a small torso lean must NOT amplify wrists/feet 30x. Root/COM momentum, planted-foot world locking, counter-rotation of arms, correct direction of weight transfer, body inertia and hip/shoulder timing need independent video-level tests.
- For reaching: verify IK target reachability and physical palm alignment, shoulder strain, penetration and z-depth occlusion.
- Do not score untested tests as passed; numerical checks are not proof of believable motion; do not say 20 iterations took place when they did not.
- Preserve versioned previous sources and real failure/repair logs, provide a reproducible bundle after meaningful work. Nothing in v1.2 may be represented as already running in v1.3.
- Cinema and performance goals: stylized but mature, expressive, polished reality dating-drama with reusable characters and locations, side/front/back coverage, realistic interactions.

## Coordinate system and implementation restrictions

- Author code Z-up but export glTF in **Y-up**; physical unit metres.
- A GLB mesh mesh-part name is not a functioning skeleton/rig. Until Blender weight painting and Godot Skeleton3D import are tested, label static asset as static.
- Maintain one shared rig naming scheme for all 6 characters; measure different character heights rather than adding arbitrary per-limb scale multipliers.
- For v1.3: source `source/build_cast.py`, viewer `godot/viewer.gd`, QA `source/validate_models.py`, raw results `qa/geometry_validation.json`.