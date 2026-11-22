extends SceneTree
## Execute ONLY after a fresh Godot editor --import. Never represented as run by Python QC.
const FILES: Array[String] = ["res://models/ava_MOUTH_GRIP_v2_1.glb", "res://models/noor_MOUTH_GRIP_v2_1.glb"]
var failures: Array[String] = []
func _initialize() -> void:
    call_deferred("_audit")
func _audit() -> void:
    for name in FILES:
        var scene := load(name) as PackedScene
        if scene == null:
            failures.append("GLB not imported: " + name)
            continue
        var actor := scene.instantiate()
        root.add_child(actor)
        var rigs: Array[Skeleton3D] = []
        var meshes: Array[MeshInstance3D] = []
        var players: Array[AnimationPlayer] = []
        _scan(actor, rigs, meshes, players)
        if rigs.size() != 1 or rigs[0].get_bone_count() != 43:
            failures.append("Unexpected 43-bone rig: " + name)
        var found_morphs := false
        for m in meshes:
            if m.mesh != null and m.mesh.get_blend_shape_count() == 8:
                found_morphs = true
        if not found_morphs:
            failures.append("Missing 8 expression blend shapes: " + name)
        var found_anim := false
        for p in players:
            for anim_name in p.get_animation_list():
                if "reach_contact_speech_corrected_v21" in str(anim_name):
                    found_anim = true
                    p.play(anim_name)
                    p.advance(3.4)
                    print(name, " animation at 3.4 seconds is active: ", p.is_playing())
        if not found_anim:
            failures.append("No v2.1 animation: " + name)
        actor.queue_free()
    if failures.is_empty():
        print("GODOT ENGINE IMPORT CHECK PASS (not visual quality proof)")
        quit(0)
    else:
        for f in failures:
            printerr("FAIL: " + f)
        quit(1)
func _scan(n: Node, rigs: Array[Skeleton3D], meshes: Array[MeshInstance3D], players: Array[AnimationPlayer]) -> void:
    if n is Skeleton3D:
        rigs.append(n as Skeleton3D)
    if n is MeshInstance3D:
        meshes.append(n as MeshInstance3D)
    if n is AnimationPlayer:
        players.append(n as AnimationPlayer)
    for child in n.get_children():
        _scan(child, rigs, meshes, players)
