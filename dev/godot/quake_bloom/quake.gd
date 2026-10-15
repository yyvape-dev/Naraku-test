extends Node2D
## 大地割り (Lana) — Claude's Godot take, using the same GPT Image materials and motion board as Codex.
## Timing chart (seconds, 40 fps, 36 frames = 0.9 s; t=0 is the damage moment, so no wind-up):
##   0.000-0.050  strike : slash wipes along the diagonal, its leading edge white-hot
##   0.035-0.120  climax : core flash + impact burst (ease-out expo), ground shock ring, light streaks
##   0.045-0.600  debris : rocks with real arcs, tumble, motion smear, ground shadows, heat cooling
##   0.030-0.880  ground : branching cracks open outward fast, then cool white→orange→red→dark
##   0.070-0.880  dust   : low puffs crawl outward along the ground and erode with noise
##   0.080-0.880  embers : sparks rise and drift; the fall-off fades element by element
## Each layer (floor = under enemies, air = over allies) is rendered twice:
##   light pass on black with additive blending, matte pass on transparent with normal blending.
## pack.py turns the light pass into straight alpha and composites it over the matte pass.

const FRAME_COUNT := 36
const FPS := 40.0
const C := Vector2(200, 225)       # same anchor as the game (0.5, 0.5625)
const SQ := 0.5                    # ground-plane squash (back-view perspective)
const CLIMAX_HEAT := 0.36          # 1 = white-hot burst, 0 = deep red (user: 炸裂を赤黒く、白を半分に)

var clock := 0.0
var layer := "all"                 # floor / air / all
var pass_mode := "all"             # light / matte / all
var art := {}
var glow_tex: Texture2D
var cracks: Array = []
var rocks: Array = []
var rays: Array = []
var embers: Array = []
var puffs: Array = []
var light: Node2D
var matte: Node2D
var black: ColorRect
var s_slash: Sprite2D
var s_trail: Sprite2D
var s_impact: Sprite2D
var env: Environment
var parts: Array = []        # [{node, start, pass, layer}]
var add_shader = load("res://fx_add.gdshader")
var mix_shader = load("res://fx_mix.gdshader")

static func clamp01(v: float) -> float: return clampf(v, 0.0, 1.0)
static func out_expo(v: float) -> float: return 1.0 if v >= 1.0 else 1.0 - pow(2.0, -10.0 * clamp01(v))
static func out_cubic(v: float) -> float: v = clamp01(v); return 1.0 - pow(1.0 - v, 3.0)
static func win(t: float, a: float, b: float) -> float: return clamp01((t - a) / (b - a))
static func ground(p: Vector2) -> Vector2: return C + Vector2(p.x, p.y * SQ)

## Heat ramp: 1 white-hot → 0.66 yellow-orange → 0.33 deep red → 0 black
static func heat_color(h: float, a: float) -> Color:
	h = clamp01(h)
	var c: Color
	if h > 0.66: c = Color(1.0, 0.72, 0.35).lerp(Color(1.0, 0.96, 0.85), (h - 0.66) / 0.34)
	elif h > 0.33: c = Color(0.95, 0.22, 0.04).lerp(Color(1.0, 0.72, 0.35), (h - 0.33) / 0.33)
	else: c = Color(0.25, 0.02, 0.0).lerp(Color(0.95, 0.22, 0.04), h / 0.33)
	c.a = a
	return c

func _ready():
	get_viewport().transparent_bg = true
	for n in ["slash", "impact", "rock", "dust"]:
		var img := Image.load_from_file("res://art/" + n + ".png")
		if img.is_empty():
			push_error("missing art: " + n); get_tree().quit(1); return
		img.resize(512, 512, Image.INTERPOLATE_LANCZOS)
		art[n] = ImageTexture.create_from_image(img)
	glow_tex = make_glow()
	var rng := RandomNumberGenerator.new()
	rng.seed = 90210
	build_cracks(rng)
	build_rocks(rng)
	build_particles(rng)

	black = ColorRect.new(); black.color = Color.BLACK; black.size = Vector2(400, 400); add_child(black)
	matte = Node2D.new(); add_child(matte)
	for i in puffs.size():
		var s := Sprite2D.new(); s.texture = art.dust
		var m := ShaderMaterial.new(); m.shader = mix_shader; m.set_shader_parameter("seed", float(i) * 3.1)
		s.material = m; matte.add_child(s); puffs[i].node = s
	matte.draw.connect(_draw_matte)
	light = Node2D.new()
	var lm := CanvasItemMaterial.new(); lm.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	light.material = lm
	add_child(light)
	light.draw.connect(_draw_light)
	s_trail = add_sprite("slash", 11.0)
	s_slash = add_sprite("slash", 3.0)
	s_impact = add_sprite("impact", 5.0)
	light.modulate = Color(1.12, 1.12, 1.12)
	s_slash.self_modulate = Color(0.8, 0.5, 0.42); s_impact.self_modulate = Color(0.8, 0.42, 0.34); s_trail.self_modulate = Color(0.85, 0.85, 0.85)   # push hot parts above the bloom threshold (2D HDR)
	env = Environment.new()
	env.background_mode = Environment.BG_CANVAS
	env.glow_enabled = true
	env.glow_intensity = 0.55
	env.glow_strength = 0.85
	env.glow_bloom = 0.0
	env.glow_hdr_threshold = 1.0
	env.glow_blend_mode = Environment.GLOW_BLEND_MODE_ADDITIVE
	for i in 7: env.set_glow_level(i, [0.0, 0.5, 0.8, 0.6, 0.3, 0.0, 0.0][i])
	var we := WorldEnvironment.new(); we.environment = env; add_child(we)
	embers = []   # replaced by GPU embers
	build_gpu_particles()

	if "--bake" in OS.get_cmdline_user_args():
		set_process(false); call_deferred("bake")
	else:
		animate(0.0)

func add_sprite(n: String, seed_v: float) -> Sprite2D:
	var s := Sprite2D.new(); s.texture = art[n]
	var m := ShaderMaterial.new(); m.shader = add_shader; m.set_shader_parameter("seed", seed_v)
	s.material = m; s.position = C; light.add_child(s)
	return s

func make_glow() -> Texture2D:
	var g := Gradient.new()
	g.offsets = PackedFloat32Array([0.0, 0.12, 0.35, 0.65, 1.0])
	g.colors = PackedColorArray([Color(1,1,1,1), Color(1,1,1,0.75), Color(1,1,1,0.28), Color(1,1,1,0.06), Color(1,1,1,0)])
	var t := GradientTexture2D.new(); t.gradient = g; t.width = 128; t.height = 128
	t.fill = GradientTexture2D.FILL_RADIAL; t.fill_from = Vector2(0.5, 0.5); t.fill_to = Vector2(1.0, 0.5)
	return t

# ---------- procedural layout (deterministic) ----------
func crack_path(rng: RandomNumberGenerator, start: Vector2, ang: float, length: float, width: float, depth: int, d0: float):
	var pts := PackedVector2Array([start]); var dists := PackedFloat32Array([d0])
	var p := start; var a := ang; var seg := 6.0; var travelled := 0.0
	while travelled < length:
		a = lerpf(a, ang, 0.35) + rng.randf_range(-0.75, 0.75)
		p += Vector2(cos(a), sin(a)) * seg; travelled += seg
		pts.append(p); dists.append(d0 + travelled)
		if depth < 2 and rng.randf() < 0.13 and travelled > 18.0:
			crack_path(rng, p, a + rng.randf_range(0.5, 1.1) * (1.0 if rng.randf() < 0.5 else -1.0), length * rng.randf_range(0.3, 0.5), width * 0.6, depth + 1, d0 + travelled)
	cracks.append({"pts": pts, "d": dists, "w": width})

func build_cracks(rng: RandomNumberGenerator):
	# the main fissure follows the slash (lower-left to upper-right on screen)
	crack_path(rng, Vector2.ZERO, deg_to_rad(-38), 150, 3.2, 0, 0)
	crack_path(rng, Vector2.ZERO, deg_to_rad(142), 140, 3.2, 0, 0)
	for i in 7:
		var a := TAU * i / 7.0 + rng.randf_range(-0.25, 0.25)
		crack_path(rng, Vector2.ZERO, a, rng.randf_range(70, 125), 2.2, 1, 0)

func build_rocks(rng: RandomNumberGenerator):
	for i in 24:
		var big := i < 3; var mid := i >= 3 and i < 10
		var a := rng.randf_range(-PI, PI)
		var spd := rng.randf_range(200, 280) if big else rng.randf_range(260, 460)
		rocks.append({
			"dir": Vector2(cos(a) * 1.35, sin(a) * 0.8).normalized(), "spd": spd,
			"up": rng.randf_range(420, 520) if big else rng.randf_range(420, 680),
			"size": rng.randf_range(44, 56) if big else (rng.randf_range(22, 32) if mid else rng.randf_range(9, 15)),
			"rot": rng.randf_range(-PI, PI), "spin": rng.randf_range(-9, 9) * (0.5 if big else 1.0),
			"delay": rng.randf_range(0.045, 0.075), "life": rng.randf_range(0.5, 0.62) if big else rng.randf_range(0.32, 0.5),
		})

func build_particles(rng: RandomNumberGenerator):
	for i in 34:
		rays.append({"a": rng.randf_range(-PI, PI), "spd": rng.randf_range(260, 520), "delay": rng.randf_range(0.035, 0.07), "life": rng.randf_range(0.10, 0.22), "len": rng.randf_range(10, 26)})
	for i in 38:
		var a := rng.randf_range(-PI, PI); var r := rng.randf_range(10, 120)
		embers.append({"p": Vector2(cos(a) * r, sin(a) * r), "delay": rng.randf_range(0.07, 0.42), "life": rng.randf_range(0.28, 0.5),
			"rise": rng.randf_range(60, 140), "drift": rng.randf_range(-30, 30), "wob": rng.randf_range(6, 14), "ph": rng.randf_range(0, TAU), "size": rng.randf_range(1.2, 2.6)})
	for i in 14:
		var core := i >= 10
		var a := TAU * i / 10.0 + rng.randf_range(-0.2, 0.2)
		puffs.append({"core": core, "a": a, "r1": rng.randf_range(20, 45) if core else rng.randf_range(105, 150), "delay": rng.randf_range(0.065, 0.11), "w0": rng.randf_range(90, 120), "w1": rng.randf_range(170, 230),
			"rot": rng.randf_range(-0.25, 0.25), "flip": rng.randf() < 0.5, "node": null})

# ---------- GPU particles (fixed seed, stepped at exactly 40 fps by --fixed-fps) ----------
func ramp(cols: Array, offs: Array) -> GradientTexture1D:
	var g := Gradient.new(); g.offsets = PackedFloat32Array(offs); g.colors = PackedColorArray(cols)
	var t := GradientTexture1D.new(); t.gradient = g; return t

func curve(pts: Array) -> CurveTexture:
	var c := Curve.new()
	for q in pts: c.add_point(Vector2(q[0], q[1]))
	var t := CurveTexture.new(); t.curve = c; return t

func streak_tex() -> Texture2D:
	var g := Gradient.new(); g.offsets = PackedFloat32Array([0.0, 0.3, 1.0]); g.colors = PackedColorArray([Color(1,1,1,1), Color(1,1,1,0.5), Color(1,1,1,0)])
	var t := GradientTexture2D.new(); t.gradient = g; t.width = 16; t.height = 72
	t.fill = GradientTexture2D.FILL_RADIAL; t.fill_from = Vector2(0.5, 0.5); t.fill_to = Vector2(1.0, 0.5)
	return t

func gp(parent: Node2D, tex: Texture2D, amount: int, life: float, start: float, l: String, p: String, seed_v: int) -> Array:
	var n := GPUParticles2D.new()
	n.amount = amount; n.lifetime = life; n.one_shot = true; n.emitting = false
	n.fixed_fps = 40; n.interpolate = false; n.local_coords = false
	n.texture = tex; n.position = C; n.use_fixed_seed = true; n.seed = seed_v
	n.visibility_rect = Rect2(-400, -400, 800, 800)
	var m := ParticleProcessMaterial.new(); n.process_material = m
	parent.add_child(n)
	parts.append({"node": n, "start": start, "layer": l, "pass": p, "on": false})
	return [n, m]

func build_gpu_particles():
	# 1) spark burst: one explosive impulse, streaks aligned to velocity, fall with gravity
	var a := gp(light, streak_tex(), 110, 0.42, 0.045, "air", "light", 7)
	var n: GPUParticles2D = a[0]; var m: ParticleProcessMaterial = a[1]
	n.explosiveness = 1.0; n.position = C + Vector2(0, -10)
	m.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE; m.emission_sphere_radius = 6.0
	m.direction = Vector3(0, -1, 0); m.spread = 180.0
	m.initial_velocity_min = 180.0; m.initial_velocity_max = 520.0
	m.gravity = Vector3(0, 700, 0); m.damping_min = 120.0; m.damping_max = 260.0
	m.particle_flag_align_y = true
	m.scale_min = 0.12; m.scale_max = 0.3
	m.scale_curve = curve([[0.0, 1.0], [1.0, 0.25]])
	m.color_ramp = ramp([Color(1, 0.62, 0.3, 1), Color(0.95, 0.32, 0.08, 1), Color(0.85, 0.15, 0.03, 0.8), Color(0.3, 0.02, 0, 0)], [0.0, 0.25, 0.6, 1.0])
	# 2) embers: rise from the cracks with turbulence, a slow rhythm against the impulse
	a = gp(light, glow_tex, 46, 0.55, 0.08, "air", "light", 11)
	n = a[0]; m = a[1]
	n.explosiveness = 0.35; n.position = C + Vector2(0, -2)
	m.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX; m.emission_box_extents = Vector3(110, 26, 0)
	m.direction = Vector3(0, -1, 0); m.spread = 25.0
	m.initial_velocity_min = 30.0; m.initial_velocity_max = 110.0
	m.gravity = Vector3(0, -90, 0)
	m.turbulence_enabled = true; m.turbulence_noise_strength = 3.0; m.turbulence_noise_scale = 2.5
	m.turbulence_influence_min = 0.05; m.turbulence_influence_max = 0.15
	m.scale_min = 0.03; m.scale_max = 0.07
	m.color_ramp = ramp([Color(1, 0.85, 0.5, 1), Color(1, 0.4, 0.08, 0.9), Color(0.5, 0.05, 0.0, 0)], [0.0, 0.4, 1.0])
	# 3) dark aura: soot-black smoke curling up out of the fissures (matte, under enemies)
	a = gp(matte, art.dust, 26, 0.6, 0.09, "floor", "matte", 23)
	n = a[0]; m = a[1]
	n.explosiveness = 0.5
	m.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX; m.emission_box_extents = Vector3(90, 22, 0)
	m.direction = Vector3(0, -1, 0); m.spread = 30.0
	m.initial_velocity_min = 20.0; m.initial_velocity_max = 55.0
	m.gravity = Vector3(0, -30, 0); m.damping_min = 10.0; m.damping_max = 20.0
	m.angle_min = -30.0; m.angle_max = 30.0; m.angular_velocity_min = -25.0; m.angular_velocity_max = 25.0
	m.scale_min = 0.12; m.scale_max = 0.2
	m.scale_curve = curve([[0.0, 0.5], [1.0, 1.0]])
	m.color_ramp = ramp([Color(0.12, 0.03, 0.02, 0), Color(0.09, 0.02, 0.02, 0.55), Color(0.05, 0.02, 0.02, 0.35), Color(0.03, 0.02, 0.02, 0)], [0.0, 0.2, 0.6, 1.0])

func reset_particles():
	for q in parts:
		var n: GPUParticles2D = q.node
		n.emitting = false; n.restart(); n.emitting = false; q.on = false

# ---------- per-frame state ----------
func shows(l: String, p: String) -> bool:
	return (layer == "all" or layer == l) and (pass_mode == "all" or pass_mode == p)

func set_fx(s: Sprite2D, width: float, op: float, rev: float, dis: float, heat: float):
	s.scale = Vector2.ONE * width / 512.0
	var m: ShaderMaterial = s.material
	m.set_shader_parameter("opacity", op); m.set_shader_parameter("reveal", rev)
	m.set_shader_parameter("dissolve", dis); m.set_shader_parameter("heat", heat)

func animate(t: float):
	clock = t
	black.visible = pass_mode == "light"
	if env: env.glow_enabled = pass_mode != "matte"
	get_viewport().use_hdr_2d = pass_mode == "light"
	for q in parts:
		var n: GPUParticles2D = q.node
		n.visible = shows(q.layer, q.pass)
		if not q.on and t >= q.start:
			q.on = true; n.emitting = true
	var air_light := shows("air", "light")
	# strike: 0-0.05 wipe, burning edge; dissolves from 0.07
	s_slash.visible = air_light and t < 0.22
	set_fx(s_slash, 300, 1.0, lerpf(0.0, 1.08, out_cubic(t / 0.05)), lerpf(-0.3, 1.05, win(t, 0.07, 0.21)), CLIMAX_HEAT * (1.0 - win(t, 0.05, 0.2) * 0.7))
	s_slash.position = C + Vector2(0, -10)
	# red tendrils linger and drift (contrast: slower element against the fast strike)
	s_trail.visible = air_light and t > 0.03 and t < 0.5
	set_fx(s_trail, 330, 0.55 * (1.0 - win(t, 0.2, 0.48)), 2.0, lerpf(-0.2, 1.05, win(t, 0.1, 0.48)), 0.0)
	s_trail.position = C + Vector2(-4, -14 - t * 26); s_trail.rotation = -0.06
	# impact burst: expo ease, peak 0.07, cools and erodes
	var ia := t - 0.035
	s_impact.visible = air_light and ia > 0.0 and t < 0.26
	set_fx(s_impact, lerpf(70, 250, out_expo(ia / 0.08)), clamp01(ia / 0.012), 2.0, lerpf(-0.3, 1.05, win(t, 0.1, 0.25)), CLIMAX_HEAT * (1.0 - win(t, 0.07, 0.22)))
	s_impact.rotation = 0.12 * out_cubic(ia / 0.2)
	# dust puffs (matte, floor)
	for q in puffs:
		var s: Sprite2D = q.node; var age: float = t - q.delay
		s.visible = shows("floor", "matte") and age > 0.0 and t < 0.89
		if not s.visible: continue
		var k := out_cubic(age / 0.45)
		var r := lerpf(28, q.r1, k)
		s.position = ground(Vector2(cos(q.a), sin(q.a)) * r) + Vector2(0, -10 - (55.0 if q.core else 18.0) * k)
		var w := lerpf(q.w0, q.w1, out_cubic(age / 0.6))
		s.scale = Vector2(w / 512.0 * (-1.0 if q.flip else 1.0), w / 512.0 * (0.85 if q.core else 0.72))
		s.rotation = q.rot
		var m: ShaderMaterial = s.material
		var warm := 1.0 - win(t, 0.08, 0.35)
		m.set_shader_parameter("tint", Color(lerpf(0.72, 1.0, warm), lerpf(0.6, 0.78, warm), lerpf(0.5, 0.55, warm), 1.0))
		m.set_shader_parameter("opacity", (0.45 if q.core else 0.6) * clamp01(age / 0.05))
		m.set_shader_parameter("dissolve", lerpf(-0.45, 1.1, win(age, 0.2, 0.78)))
	light.queue_redraw(); matte.queue_redraw()

func _process(dt):
	animate(fmod(clock + dt * 0.5, 1.2))

# ---------- drawing ----------
func glow_at(n: CanvasItem, p: Vector2, size: Vector2, col: Color):
	n.draw_texture_rect(glow_tex, Rect2(p - size * 0.5, size), false, col)

func crack_front(t: float) -> float: return 160.0 * out_expo(win(t, 0.03, 0.16))

func _draw_matte():
	var t := clock; var n := matte
	if shows("floor", "matte"):
		# scorched bed under the cracks and a soft ground shadow at the centre
		var bed := 0.5 * (1.0 - win(t, 0.45, 0.75))
		glow_at(n, C, Vector2(190, 95) * out_expo(win(t, 0.03, 0.12)), Color(0.05, 0.02, 0.01, 0.55 * bed))
		var front := crack_front(t)
		for c in cracks:
			var pts := PackedVector2Array()
			for i in c.pts.size():
				if c.d[i] > front: break
				pts.append(ground(c.pts[i]))
			if pts.size() >= 2:
				n.draw_polyline(pts, Color(0.05, 0.02, 0.01, bed), c.w + 1.8, true)
		# rock shadows: grounded depth cue
		for r in rocks:
			var age: float = t - r.delay
			if age <= 0.0 or age > r.life: continue
			var st := rock_state(r, age)
			var fade := 1.0 - win(age, r.life - 0.15, r.life)
			var hgt: float = st.h
			var sz: float = r.size * (1.1 - clampf(hgt / 220.0, 0.0, 0.7))
			glow_at(n, st.g, Vector2(sz * 1.6, sz * 0.55), Color(0, 0, 0, 0.45 * fade * (1.0 - clampf(hgt / 260.0, 0.0, 0.8))))
	if shows("air", "matte"):
		# 赤黒い炸裂：the burst's silhouette in near-black red, slightly larger, under the light pass
		var ia := t - 0.03
		if ia > 0.0 and t < 0.32:
			var w := lerpf(90, 290, out_expo(ia / 0.09))
			var a := clamp01(ia / 0.015) * (1.0 - win(t, 0.12, 0.32))
			n.draw_set_transform(C, 0.12 * out_cubic(ia / 0.2) + 0.2, Vector2.ONE)
			n.draw_texture_rect(art.impact, Rect2(Vector2(-w, -w) * 0.5, Vector2(w, w)), false, Color(0.16, 0.015, 0.01, 0.8 * a))
			n.draw_set_transform(C + Vector2(0, -10), 0.0, Vector2.ONE)
			n.draw_texture_rect(art.slash, Rect2(Vector2(-160, -160), Vector2(320, 320)), false, Color(0.12, 0.01, 0.01, 0.55 * a))
			n.draw_set_transform(Vector2.ZERO)
		for r in rocks:
			var age: float = t - r.delay
			if age <= 0.0 or age > r.life: continue
			draw_rock(n, r, age, Color(1, 1, 1, 1))

func rock_state(r: Dictionary, age: float) -> Dictionary:
	var travel: float = r.spd * (1.0 - exp(-age * 3.2)) / 3.2       # air drag
	var g := ground(r.dir * travel)
	var h: float = maxf(0.0, r.up * age - 1150.0 * age * age)      # gravity, lands and stops
	return {"g": g, "h": h, "p": g - Vector2(0, h)}

func draw_rock(n: CanvasItem, r: Dictionary, age: float, tint: Color):
	var fade := (1.0 - win(age, r.life - 0.15, r.life)) * clamp01(age / 0.02)
	var st := rock_state(r, age)
	var landed: bool = st.h <= 0.0 and age > 0.1
	var rot: float = r.rot + r.spin * (minf(age, 0.35) if landed else age)
	var sz: float = r.size
	# motion smear while fast
	if age < 0.14:
		for k in [2, 1]:
			var pa := maxf(0.0, age - 0.012 * k)
			var sp := rock_state(r, pa)
			n.draw_set_transform(sp.p, rot - r.spin * 0.012 * k, Vector2.ONE)
			n.draw_texture_rect(art.rock, Rect2(Vector2(-sz, -sz) * 0.5, Vector2(sz, sz)), false, Color(tint.r, tint.g, tint.b, tint.a * fade * 0.18 * (3 - k)))
	n.draw_set_transform(st.p, rot, Vector2.ONE)
	n.draw_texture_rect(art.rock, Rect2(Vector2(-sz, -sz) * 0.5, Vector2(sz, sz)), false, Color(tint.r, tint.g, tint.b, tint.a * fade))
	n.draw_set_transform(Vector2.ZERO)

func _draw_light():
	var t := clock; var n := light
	if shows("floor", "light"):
		# ground glow pool under the strike
		var pool := clamp01(t / 0.05) * (1.0 - win(t, 0.08, 0.7))
		glow_at(n, C, Vector2(240, 120), heat_color(1.0 - win(t, 0.06, 0.5), 0.55 * pool))
		# ground light rushes outward with the shock (soft, no hard ring)
		var ra := win(t, 0.035, 0.15)
		if ra > 0.0 and ra < 1.0:
			glow_at(n, C, Vector2(330, 165) * out_expo(ra), heat_color(0.75, 0.32 * (1.0 - ra)))
		# glowing cracks: open outward fast, then cool from the tips inward
		var front := crack_front(t)
		for c in cracks:
			for i in range(1, c.pts.size()):
				if c.d[i] > front: break
				var dd: float = c.d[i]
				var h := 0.95 - 0.95 * win(t, 0.04 + dd / 1400.0, 0.42 + (160.0 - dd) / 900.0)
				var edge := clamp01((front - dd) / 25.0)            # freshly opened tip flares
				var a := clamp01(h * 2.2 + 0.15) * (1.0 - win(t, 0.62, 0.86))
				if a <= 0.01: continue
				var p0 := ground(c.pts[i - 1]); var p1 := ground(c.pts[i])
				var w: float = c.w * (1.0 - dd / 220.0)
				n.draw_line(p0, p1, heat_color(h * 0.6, 0.12 * a), w * 5.0 + 4.0, true)
				n.draw_line(p0, p1, heat_color(h * 0.8, 0.45 * a), w * 1.9, true)
				n.draw_line(p0, p1, heat_color(minf(1.0, h + 0.3 * (1.0 - edge)), a), maxf(0.7, w * 0.55), true)
	if shows("air", "light"):
		# core flash, elongated along the slash, never an opaque disc
		var fl := clamp01(1.0 - absf(t - 0.06) / 0.05)
		if fl > 0.0:
			n.draw_set_transform(C + Vector2(0, -12), deg_to_rad(-40), Vector2.ONE)
			glow_at(n, Vector2.ZERO, Vector2(200, 46), Color(0.95, 0.3, 0.12, 0.8 * fl))
			glow_at(n, Vector2.ZERO, Vector2(60, 34), Color(1.0, 0.7, 0.5, 0.3 * fl))
			n.draw_set_transform(Vector2.ZERO)
		# light streaks: fast impulse
		for q in rays:
			var age: float = t - q.delay
			if age < 0.0 or age > q.life: continue
			var k: float = age / q.life
			var d := Vector2(cos(q.a), sin(q.a) * 0.6)
			var p: Vector2 = C + Vector2(0, -10) + d * (10.0 + q.spd * age * (1.0 - k * 0.4))
			n.draw_line(p - d * q.len * (1.0 - k), p, heat_color(0.7 - k * 0.6, 0.9 * (1.0 - k)), 1.6 * (1.0 - k) + 0.5, true)
		# hot rock rims cool quickly
		for r in rocks:
			var age: float = t - r.delay
			if age <= 0.0 or age > r.life: continue
			var h := 1.0 - win(age, 0.0, 0.28)
			if h > 0.0: draw_rock(n, r, age, heat_color(0.5 + 0.5 * h, 0.55 * h))
		# embers: rhythm against the impulse, rise and wobble, cool to red
		for e in embers:
			var age: float = t - e.delay
			if age < 0.0 or age > e.life: continue
			var k: float = age / e.life
			var p: Vector2 = ground(e.p) + Vector2(e.drift * k + sin(e.ph + age * 18.0) * e.wob * k, -e.rise * out_cubic(k))
			var flick := 0.75 + 0.25 * sin(e.ph * 3.0 + age * 55.0)
			var col := heat_color(1.0 - k * 0.85, (1.0 - k) * flick)
			glow_at(n, p, Vector2.ONE * e.size * 7.0, Color(col.r, col.g, col.b, col.a * 0.35))
			n.draw_circle(p, e.size * (1.0 - k * 0.5), col)

# ---------- bake ----------
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
