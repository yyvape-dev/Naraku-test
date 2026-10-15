extends Node2D
## 狐火乱舞 (Yuzunamiki) — user's 5 keyframes (dev/cardart/foxfire_src) brought to life in Godot.
## Motif (user, 2026-10-15): 紫・薄いピンク・火・墨絵のような黒.
## 36 frames at 30 fps = 1.2 s (reload is 5 s, so it is gone well before the next cast). t=0 is the damage moment.
##   0.00-0.07  the pillar of light falls (keyframe 1 wiped top-down), pink spark burst, ink splash
##   0.05-0.52  the lotus blooms: each keyframe burns in from the heart outward while the previous one burns away
##   0.04-0.30  sumi ink bleeds across the ground under the flower
##   0.05-0.80  fox-fire wisps rise; pale pink petals scatter
##   0.62-1.18  fall-off: last keyframe drifts apart, a second petal gust, ink fades
## Same two-pass bake as quake_bloom: light (black, additive, 2D HDR glow) / matte (transparent, normal blend).

const FRAME_COUNT := 36
const FPS := 30.0
const C := Vector2(200, 262)        # flower heart; game anchor (0.5, 0.655)
const SQ := 0.5
const ART_SCALE := 0.5               # art resized to 800px -> 400px canvas (1536 px original)
const PIVOT_Y := 0.736               # flower heart / pillar base in the art (measured)
const LIGHT_GAIN := 1.06             # pushes the hottest pixels over the bloom threshold
const ART_LIGHT := 0.26               # additive copy of the art that feeds the bloom
# keyframe schedule: [in_start, in_end, out_start, out_end] (keyframe 1 comes in by a top-down wipe)
const KEYS := [[0.0, 0.07, 0.13, 0.30], [0.05, 0.20, 0.25, 0.42], [0.20, 0.34, 0.45, 0.60], [0.38, 0.52, 0.68, 0.85], [0.62, 0.78, 0.86, 1.18]]

var clock := 0.0
var layer := "all"
var pass_mode := "all"
var env: Environment
var black: ColorRect
var light: Node2D
var matte: Node2D
var root_m: Node2D
var root_l: Node2D
var keys_m: Array = []
var keys_l: Array = []
var stain: ColorRect
var glow_tex: Texture2D
var parts: Array = []

static func clamp01(v: float) -> float: return clampf(v, 0.0, 1.0)
static func win(t: float, a: float, b: float) -> float: return clamp01((t - a) / (b - a))
static func out_cubic(v: float) -> float: v = clamp01(v); return 1.0 - pow(1.0 - v, 3.0)

func _ready():
	get_viewport().transparent_bg = true
	glow_tex = soft_tex(128, 128)
	black = ColorRect.new(); black.color = Color.BLACK; black.size = Vector2(400, 400); add_child(black)
	matte = Node2D.new(); add_child(matte)
	light = Node2D.new(); add_child(light)
	var lm := CanvasItemMaterial.new(); lm.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD; light.material = lm
	light.modulate = Color(LIGHT_GAIN, LIGHT_GAIN, LIGHT_GAIN)
	light.draw.connect(_draw_light)

	# floor: sumi ink blot (matte)
	stain = ColorRect.new(); stain.size = Vector2(300, 300); stain.position = C - Vector2(150, 150)
	stain.pivot_offset = Vector2(150, 150); stain.scale = Vector2(1, SQ)
	var sm := ShaderMaterial.new(); sm.shader = load("res://ink_stain.gdshader"); sm.set_shader_parameter("seed", 3.0)
	stain.material = sm; matte.add_child(stain)

	# the user's keyframes, twice: true colours (matte) and an additive copy (light)
	var art_m = load("res://fox_art.gdshader"); var art_a = load("res://fox_art_add.gdshader")
	root_m = Node2D.new(); root_m.position = C; matte.add_child(root_m)
	root_l = Node2D.new(); root_l.position = C; light.add_child(root_l)
	for i in 5:
		var img := Image.load_from_file("res://art/vfx_frame_%02d.png" % (i + 1))
		if img.is_empty(): push_error("missing art %d" % (i + 1)); get_tree().quit(1); return
		img.resize(800, 800, Image.INTERPOLATE_LANCZOS)
		var tex := ImageTexture.create_from_image(img)
		for pair in [[root_m, art_m, keys_m, 1.0], [root_l, art_a, keys_l, ART_LIGHT]]:
			var s := Sprite2D.new(); s.texture = tex; s.scale = Vector2.ONE * ART_SCALE
			s.offset = Vector2(0, 400.0 - PIVOT_Y * 800.0)
			s.self_modulate = Color(pair[3], pair[3], pair[3])
			var m := ShaderMaterial.new(); m.shader = pair[1]; m.set_shader_parameter("seed", float(i) * 2.7)
			m.set_shader_parameter("pivot", Vector2(0.5, PIVOT_Y)); s.material = m
			pair[0].add_child(s); pair[2].append(s)

	env = Environment.new()
	env.background_mode = Environment.BG_CANVAS
	env.glow_enabled = true; env.glow_intensity = 0.45; env.glow_strength = 0.9; env.glow_bloom = 0.0
	env.glow_hdr_threshold = 1.0; env.glow_blend_mode = Environment.GLOW_BLEND_MODE_ADDITIVE
	for i in 7: env.set_glow_level(i, [0.0, 0.5, 0.9, 0.7, 0.35, 0.0, 0.0][i])
	var we := WorldEnvironment.new(); we.environment = env; add_child(we)
	build_particles()
	if "--bake" in OS.get_cmdline_user_args():
		set_process(false); call_deferred("bake")
	else:
		animate(0.0)

func soft_tex(w: int, h: int) -> Texture2D:
	var g := Gradient.new(); g.offsets = PackedFloat32Array([0.0, 0.25, 0.6, 1.0])
	g.colors = PackedColorArray([Color(1,1,1,1), Color(1,1,1,0.7), Color(1,1,1,0.18), Color(1,1,1,0)])
	var t := GradientTexture2D.new(); t.gradient = g; t.width = w; t.height = h
	t.fill = GradientTexture2D.FILL_RADIAL; t.fill_from = Vector2(0.5, 0.5); t.fill_to = Vector2(1.0, 0.5)
	return t

func ramp(cols: Array, offs: Array) -> GradientTexture1D:
	var g := Gradient.new(); g.offsets = PackedFloat32Array(offs); g.colors = PackedColorArray(cols)
	var t := GradientTexture1D.new(); t.gradient = g; return t

func curve(pts: Array) -> CurveTexture:
	var c := Curve.new()
	for q in pts: c.add_point(Vector2(q[0], q[1]))
	var t := CurveTexture.new(); t.curve = c; return t

func gp(parent: Node2D, tex: Texture2D, amount: int, life: float, start: float, l: String, p: String, seed_v: int, pos: Vector2) -> Array:
	var n := GPUParticles2D.new()
	n.amount = amount; n.lifetime = life; n.one_shot = true; n.emitting = false
	n.fixed_fps = int(FPS); n.interpolate = false; n.local_coords = false
	n.texture = tex; n.position = pos; n.use_fixed_seed = true; n.seed = seed_v
	n.visibility_rect = Rect2(-400, -400, 800, 800)
	var m := ParticleProcessMaterial.new(); n.process_material = m
	parent.add_child(n)
	parts.append({"node": n, "start": start, "layer": l, "pass": p, "on": false})
	return [n, m]

func build_particles():
	var petal := soft_tex(24, 60)     # long soft petal
	var flame := soft_tex(22, 72)     # tongue of fox fire
	# 1) pink sparks when the pillar lands
	var a := gp(light, soft_tex(14, 70), 46, 0.32, 0.03, "air", "light", 5, C)
	var n: GPUParticles2D = a[0]; var m: ParticleProcessMaterial = a[1]
	n.explosiveness = 1.0
	m.direction = Vector3(0, -1, 0); m.spread = 180.0; m.initial_velocity_min = 180.0; m.initial_velocity_max = 430.0
	m.damping_min = 280.0; m.damping_max = 420.0; m.particle_flag_align_y = true
	m.scale_min = 0.12; m.scale_max = 0.26; m.scale_curve = curve([[0.0, 1.0], [1.0, 0.2]])
	m.color_ramp = ramp([Color(1, 0.93, 0.98, 1), Color(1, 0.6, 0.88, 1), Color(0.6, 0.3, 1.0, 0)], [0.0, 0.35, 1.0])
	# 2) fox-fire wisps rising around the flower (火)
	a = gp(light, flame, 34, 0.62, 0.05, "air", "light", 9, C + Vector2(0, -4))
	n = a[0]; m = a[1]
	n.explosiveness = 0.3
	m.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX; m.emission_box_extents = Vector3(80, 16, 0)
	m.direction = Vector3(0, -1, 0); m.spread = 12.0; m.initial_velocity_min = 50.0; m.initial_velocity_max = 120.0
	m.gravity = Vector3(0, -70, 0); m.particle_flag_align_y = true
	m.turbulence_enabled = true; m.turbulence_noise_strength = 2.5; m.turbulence_noise_scale = 2.0
	m.turbulence_influence_min = 0.06; m.turbulence_influence_max = 0.14
	m.scale_min = 0.22; m.scale_max = 0.42; m.scale_curve = curve([[0.0, 0.3], [0.25, 1.0], [1.0, 0.0]])
	m.color_ramp = ramp([Color(1, 0.95, 1, 0), Color(1, 0.72, 0.92, 0.95), Color(0.75, 0.35, 1.0, 0.7), Color(0.35, 0.1, 0.6, 0)], [0.0, 0.15, 0.55, 1.0])
	# 3) pale pink petals scattering (薄いピンク)
	a = gp(light, petal, 44, 0.85, 0.1, "air", "light", 13, C + Vector2(0, -20))
	n = a[0]; m = a[1]
	n.explosiveness = 0.6
	m.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE; m.emission_sphere_radius = 30.0
	m.direction = Vector3(0, -0.4, 0); m.spread = 180.0; m.initial_velocity_min = 70.0; m.initial_velocity_max = 190.0
	m.gravity = Vector3(0, 45, 0); m.damping_min = 70.0; m.damping_max = 110.0
	m.angle_min = -180.0; m.angle_max = 180.0; m.angular_velocity_min = -220.0; m.angular_velocity_max = 220.0
	m.scale_min = 0.09; m.scale_max = 0.17
	m.color_ramp = ramp([Color(1, 0.88, 0.95, 0.95), Color(1, 0.72, 0.9, 0.85), Color(0.7, 0.5, 1.0, 0)], [0.0, 0.5, 1.0])
	# 4) second gust of petals as the flower comes apart
	a = gp(light, petal, 30, 0.55, 0.66, "air", "light", 17, C + Vector2(0, -24))
	n = a[0]; m = a[1]
	n.explosiveness = 0.85
	m.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE; m.emission_sphere_radius = 55.0
	m.direction = Vector3(0, -1, 0); m.spread = 180.0; m.initial_velocity_min = 90.0; m.initial_velocity_max = 220.0
	m.gravity = Vector3(0, 30, 0); m.damping_min = 90.0; m.damping_max = 140.0
	m.angle_min = -180.0; m.angle_max = 180.0; m.angular_velocity_min = -260.0; m.angular_velocity_max = 260.0
	m.scale_min = 0.08; m.scale_max = 0.15
	m.color_ramp = ramp([Color(1, 0.85, 0.95, 0.9), Color(0.85, 0.6, 1.0, 0.6), Color(0.5, 0.3, 0.9, 0)], [0.0, 0.45, 1.0])
	# 5) sumi ink droplets flung out by the impact (墨しぶき, matte so they stay black)
	a = gp(matte, glow_tex, 30, 0.5, 0.05, "air", "matte", 21, C)
	n = a[0]; m = a[1]
	n.explosiveness = 1.0
	m.direction = Vector3(0, -1, 0); m.spread = 75.0; m.initial_velocity_min = 140.0; m.initial_velocity_max = 330.0
	m.gravity = Vector3(0, 650, 0); m.scale_min = 0.05; m.scale_max = 0.11
	m.color_ramp = ramp([Color(0.04, 0.01, 0.05, 0.95), Color(0.06, 0.02, 0.08, 0.85), Color(0.06, 0.02, 0.08, 0)], [0.0, 0.7, 1.0])

func reset_particles():
	for q in parts:
		var n: GPUParticles2D = q.node
		n.emitting = false; n.restart(); n.emitting = false; q.on = false

func shows(l: String, p: String) -> bool:
	return (layer == "all" or layer == l) and (pass_mode == "all" or pass_mode == p)

func animate(t: float):
	clock = t
	black.visible = pass_mode == "light"
	env.glow_enabled = pass_mode != "matte"
	get_viewport().use_hdr_2d = pass_mode == "light"
	for q in parts:
		var n: GPUParticles2D = q.node
		n.visible = shows(q.layer, q.pass)
		if not q.on and t >= q.start:
			q.on = true; n.emitting = true
	# whole flower: settles in scale and turns slowly with the ink spiral
	var sc := 0.9 + 0.1 * out_cubic(t / 0.45) + 0.05 * win(t, 0.6, 1.2)
	var rot := 0.18 * out_cubic(t / 1.2)
	for r in [root_m, root_l]:
		r.scale = Vector2.ONE * sc; r.rotation = rot
	root_m.visible = shows("air", "matte"); root_l.visible = shows("air", "light")
	for i in 5:
		var k: Array = KEYS[i]
		var vis: bool = t >= k[0] and t <= k[3]
		for s in [keys_m[i], keys_l[i]]:
			s.visible = vis
			var m: ShaderMaterial = s.material
			if i == 0:
				m.set_shader_parameter("ywipe", lerpf(-0.05, 1.05, out_cubic(win(t, k[0], k[1]))))
				m.set_shader_parameter("burn", 2.0)
			else:
				m.set_shader_parameter("burn", lerpf(-0.1, 1.25, out_cubic(win(t, k[0], k[1]))))
			m.set_shader_parameter("dissolve", lerpf(-0.45, 1.05, win(t, k[2], k[3])))
	# ink blot on the ground
	stain.visible = shows("floor", "matte") and t > 0.03
	var sm: ShaderMaterial = stain.material
	sm.set_shader_parameter("spread", 0.85 * out_cubic(win(t, 0.03, 0.32)))
	sm.set_shader_parameter("opacity", 0.75 * (1.0 - win(t, 0.75, 1.15)))
	light.queue_redraw()

func _process(dt):
	animate(fmod(clock + dt * 0.5, 1.4))

func glow_at(p: Vector2, size: Vector2, col: Color):
	light.draw_texture_rect(glow_tex, Rect2(p - size * 0.5, size), false, col)

func _draw_light():
	var t := clock
	if shows("floor", "light"):
		# violet light pooling on the ground, a pink flash where the pillar lands
		var pool := clamp01(t / 0.06) * (1.0 - win(t, 0.5, 1.15))
		glow_at(C, Vector2(250, 120), Color(0.55, 0.22, 0.95, 0.45 * pool))
		var fl := clamp01(1.0 - absf(t - 0.05) / 0.06)
		glow_at(C, Vector2(170, 70), Color(1.0, 0.6, 0.9, 0.7 * fl))
	if shows("air", "light"):
		var fl := clamp01(1.0 - absf(t - 0.045) / 0.05)
		glow_at(C + Vector2(0, -6), Vector2(90, 60), Color(1.0, 0.75, 0.95, 0.55 * fl))

func bake():
	DirAccess.make_dir_recursive_absolute("res://frames")
	for l in ["floor", "air"]:
		for p in ["light", "matte"]:
			layer = l; pass_mode = p
			reset_particles()
			await get_tree().process_frame
			for f in FRAME_COUNT:
				animate(f / FPS)
				await get_tree().process_frame
				await RenderingServer.frame_post_draw
				var img := get_viewport().get_texture().get_image()
				if img.save_png("res://frames/%s_%s_%02d.png" % [l, p, f]) != OK:
					push_error("save failed"); get_tree().quit(1); return
	print("BAKE OK")
	get_tree().quit()
