extends Node3D
## Villa Verse v2.1 Godot rig viewer, authored but NOT engine-tested here.
const FILES: Array[String] = ["res://models/ava_MOUTH_GRIP_v2_1.glb", "res://models/noor_MOUTH_GRIP_v2_1.glb"]
const OFFSETS := [Vector3(-0.48, 0.0, 0.0), Vector3(0.48, 0.0, 0.039)]
var players: Array[AnimationPlayer] = []
var cam: Camera3D
var angle := 0.0
var is_paused := false
var closeup := false
func _ready() -> void:
    var env_node := WorldEnvironment.new()
    var env := Environment.new()
    env.background_mode = Environment.BG_COLOR
    env.background_color = Color(0.90, 0.88, 0.81)
    env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color = Color(1.0, 0.96, 0.87)
    env.ambient_light_energy = 0.7
    env_node.environment = env
    add_child(env_node)
    var key := DirectionalLight3D.new()
    key.rotation_degrees = Vector3(-45, -30, 0)
    key.light_energy = 1.3
    key.shadow_enabled = true
    add_child(key)
    var ground := MeshInstance3D.new()
    var plane := PlaneMesh.new()
    plane.size = Vector2(12, 12)
    ground.mesh = plane
    var mat := StandardMaterial3D.new()
    mat.albedo_color = Color(0.72, 0.68, 0.58)
    ground.material_override = mat
    add_child(ground)
    cam = Camera3D.new()
    cam.current = true
    add_child(cam)
    _set_camera()
    for i in range(FILES.size()):
        var scene := load(FILES[i]) as PackedScene
        if scene == null:
            push_error("GLB import failed: " + FILES[i])
            continue
        var actor := scene.instantiate() as Node3D
        if actor == null:
            push_error("Actor not Node3D: " + FILES[i])
            continue
        actor.position = OFFSETS[i]
        add_child(actor)
        _describe_nodes(actor)
        var animation := _find_player(actor)
        if animation == null:
            push_error("AnimationPlayer missing: " + FILES[i])
            continue
        for anim in animation.get_animation_list():
            if "reach_contact_speech_corrected_v21" in str(anim):
                animation.play(anim)
                players.append(animation)
                break
func _describe_nodes(n: Node) -> void:
    if n is Skeleton3D:
        var rig := n as Skeleton3D
        print(n.get_path(), " bones=", rig.get_bone_count())
    if n is MeshInstance3D:
        var inst := n as MeshInstance3D
        if inst.mesh != null:
            print(n.get_path(), " blend shapes=", inst.mesh.get_blend_shape_count())
    for child in n.get_children():
        _describe_nodes(child)
func _find_player(n: Node) -> AnimationPlayer:
    if n is AnimationPlayer:
        return n as AnimationPlayer
    for child in n.get_children():
        var p := _find_player(child)
        if p != null:
            return p
    return null
func _set_camera() -> void:
    if closeup:
        cam.position = Vector3(1.3*sin(angle), 1.42, 1.3*cos(angle))
        cam.look_at(Vector3(0.0, 1.13, 0.0), Vector3.UP)
        cam.fov = 31.0
    else:
        cam.position = Vector3(4.6*sin(angle), 1.9, 4.6*cos(angle))
        cam.look_at(Vector3(0.0, 0.98, 0.0), Vector3.UP)
        cam.fov = 55.0
func _input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_SPACE:
            is_paused = not is_paused
            for p in players:
                if is_paused:
                    p.pause()
                else:
                    p.play()
        elif event.keycode == KEY_R:
            for p in players:
                p.seek(0.0, true)
                p.play()
        elif event.keycode == KEY_C:
            closeup = not closeup
            _set_camera()
        elif event.keycode == KEY_LEFT:
            angle -= 0.19
            _set_camera()
        elif event.keycode == KEY_RIGHT:
            angle += 0.19
            _set_camera()
