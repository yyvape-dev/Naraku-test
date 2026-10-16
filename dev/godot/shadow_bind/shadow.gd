extends Node2D
const COUNT := 54
const FPS := 30.0
const C := Vector2(256, 365)
# [source, appear, full, fade begins, gone]. All five supplied stages keep a common contact point.
const KEYS := [[0,0.0,0.075,0.17,0.30],[1,0.10,0.27,0.40,0.56],[2,0.30,0.50,0.80,1.02],[3,0.72,0.91,1.10,1.32],[4,1.04,1.26,1.40,1.80]]
var noise: NoiseTexture2D
var roots := {}
var sprites: Array = []
var grounds: Array = []
var particles: Array = []
var accents: Array = []
var env: Environment
var backdrop: ColorRect
var clock := 0.0
var baking := false
var layer := "air"
var pass_name := "matte"
func ramp(t: float,a: float,b: float)->float:
 return smoothstep(a,b,t)
func _ready():
 get_viewport().transparent_bg=true
 get_viewport().canvas_transform=Transform2D().scaled(Vector2(2,2))
 noise=NoiseTexture2D.new();noise.width=256;noise.height=256;noise.seamless=true
 var n=FastNoiseLite.new();n.seed=624;n.frequency=.025;n.fractal_octaves=3;noise.noise=n
 await noise.changed
 backdrop=ColorRect.new();backdrop.size=Vector2(512,512);backdrop.color=Color.BLACK;add_child(backdrop)
 var world=WorldEnvironment.new();env=Environment.new();env.background_mode=Environment.BG_CANVAS
 env.glow_enabled=true;env.glow_blend_mode=Environment.GLOW_BLEND_MODE_ADDITIVE
 env.glow_intensity=.45;env.glow_hdr_threshold=1.0
 for i in 7: env.set_glow_level(i,[0.,.3,.6,.4,.15,0.,0.][i])
 world.environment=env;add_child(world)
 for l in ["floor","air"]:
  for p in ["matte","light"]:
   var root=Node2D.new();roots[l+"_"+p]=root;add_child(root)
   if p=="light":
    var blend=CanvasItemMaterial.new();blend.blend_mode=CanvasItemMaterial.BLEND_MODE_ADD;root.material=blend
   if l=="floor":
    var rect=ColorRect.new();rect.size=Vector2(360,160);rect.position=C-rect.size*.5
    var sm=ShaderMaterial.new();sm.shader=load("res://ground_add.gdshader" if p=="light" else "res://ground.gdshader");sm.set_shader_parameter("noise_tex",noise);sm.set_shader_parameter("light_pass",p=="light");rect.material=sm
    root.add_child(rect);grounds.append(rect)
   else:
    for k in KEYS:
     var im=Sprite2D.new();im.texture=load("res://art/%s" % ["01_start.png","02_build.png","03_converge.png","04_peak.png","05_dissipate.png"][k[0]])
     im.centered=false;im.position=C;im.offset=Vector2(-627,-1020);im.scale=Vector2.ONE*.30
     var sm=ShaderMaterial.new();sm.shader=load("res://flow_add.gdshader" if p=="light" else "res://flow.gdshader");sm.set_shader_parameter("noise_tex",noise);sm.set_shader_parameter("light_pass",p=="light");im.material=sm
     root.add_child(im);sprites.append([im,k])
 build_accents()
 build_particles()
 baking="--bake" in OS.get_cmdline_user_args()
 if baking:
  set_process(false);call_deferred("bake")
func build_accents():
 # Two brief blue-violet breaths at the hit and the tightening; no screen-wide flash.
 var g=Gradient.new();g.offsets=PackedFloat32Array([0.,.22,.58,1.])
 g.colors=PackedColorArray([Color(1,1,1,.8),Color(1,1,1,.48),Color(1,1,1,.08),Color(1,1,1,0)])
 var tex=GradientTexture2D.new();tex.width=128;tex.height=128;tex.gradient=g
 tex.fill=GradientTexture2D.FILL_RADIAL;tex.fill_from=Vector2(.5,.5);tex.fill_to=Vector2(1.,.5)
 for l in ["floor","air"]:
  var sp=Sprite2D.new();sp.texture=tex;sp.position=C if l=="floor" else C+Vector2(0,-80)
  sp.scale=Vector2(2.5,.9) if l=="floor" else Vector2(1.25,1.05)
  var blend=CanvasItemMaterial.new();blend.blend_mode=CanvasItemMaterial.BLEND_MODE_ADD;sp.material=blend
  roots[l+"_light"].add_child(sp);accents.append([sp,l])
func build_particles():
 var gradient=Gradient.new();gradient.colors=PackedColorArray([Color(1,1,1,1),Color(1,1,1,.25),Color(1,1,1,0)]);gradient.offsets=PackedFloat32Array([0.,.3,1.])
 var tex=GradientTexture2D.new();tex.width=16;tex.height=16;tex.gradient=gradient;tex.fill=GradientTexture2D.FILL_RADIAL;tex.fill_from=Vector2(.5,.5);tex.fill_to=Vector2(1.,.5)
 var gp=GPUParticles2D.new();gp.texture=tex;gp.amount=32;gp.lifetime=.65;gp.one_shot=true;gp.explosiveness=.15;gp.emitting=false
 gp.use_fixed_seed=true;gp.seed=617;gp.fixed_fps=30;gp.interpolate=false;gp.position=C-Vector2(0,90);gp.visibility_rect=Rect2(-250,-250,500,500)
 var pm=ParticleProcessMaterial.new();pm.particle_flag_disable_z=true
 pm.emission_shape=ParticleProcessMaterial.EMISSION_SHAPE_BOX;pm.emission_box_extents=Vector3(95,60,0)
 pm.direction=Vector3(0,-1,0);pm.spread=60;pm.initial_velocity_min=24;pm.initial_velocity_max=65;pm.gravity=Vector3(0,-28,0)
 pm.scale_min=.09;pm.scale_max=.23;pm.angular_velocity_min=-100;pm.angular_velocity_max=100
 var g=Gradient.new();g.offsets=PackedFloat32Array([0.,.25,.7,1.]);g.colors=PackedColorArray([Color(.15,.2,.8,0),Color(.6,.45,1.,.7),Color(.2,.3,1.,.35),Color(.2,.3,1.,0)])
 var gt=GradientTexture1D.new();gt.gradient=g;pm.color_ramp=gt;gp.process_material=pm
 var blend=CanvasItemMaterial.new();blend.blend_mode=CanvasItemMaterial.BLEND_MODE_ADD;gp.material=blend
 roots["air_light"].add_child(gp);particles.append(gp)
func animate(t: float):
 clock=t
 var light=pass_name=="light"
 get_viewport().use_hdr_2d=light;backdrop.visible=light;env.glow_enabled=light
 for k in roots: roots[k].visible=k==layer+"_"+pass_name
 for pair in sprites:
  var im: Sprite2D=pair[0];var k: Array=pair[1]
  im.visible=t>=k[1] and t<k[4]
  var m: ShaderMaterial=im.material
  var gain=ramp(t,k[1],k[2])*(1.-ramp(t,k[3],k[4]))
  m.set_shader_parameter("clock",t);m.set_shader_parameter("opacity",gain)
  m.set_shader_parameter("reveal",lerpf(.0,1.2,ramp(t,k[1],k[2])))
  m.set_shader_parameter("erode",ramp(t,k[3],k[4])*.85)
  # Growth at the start, a firm silhouette while binding, a rising escape at release.
  var sc=.30*lerpf(.9,1.,ramp(t,0.,.35));im.scale=Vector2(sc,sc)
  im.position=C+Vector2(0,-10.*ramp(t,1.15,1.8))
 for ground in grounds:
  ground.material.set_shader_parameter("clock",t)
  ground.material.set_shader_parameter("strength",ramp(t,0.,.16)*(1.-ramp(t,1.05,1.8)))
 # Authored at 30fps; game plays at 60fps, so source .32 is the .16s hit.
 var pulse=exp(-pow((t-.32)/.10,2.))+.65*exp(-pow((t-.78)/.14,2.))
 for item in accents:
  var sp: Sprite2D=item[0]
  sp.modulate=Color(.25,.32,1.0,pulse*(.22 if item[1]=="floor" else .12))
 for gp in particles:
  if t>=.18 and t<.22 and not gp.emitting:gp.emitting=true
func _process(dt):
 animate(fmod(clock+dt,2.2))
func bake():
 DirAccess.make_dir_recursive_absolute("res://frames")
 for l in ["floor","air"]:
  for p in ["matte","light"]:
   layer=l;pass_name=p
   for gp in particles:gp.emitting=false;gp.restart()
   animate(0.)
   await get_tree().process_frame
   for i in COUNT:
    animate(float(i)/FPS)
    await get_tree().process_frame
    await RenderingServer.frame_post_draw
    var img=get_viewport().get_texture().get_image()
    var error=img.save_png("res://frames/%s_%s_%02d.png" % [l,p,i])
    if error!=OK: get_tree().quit(1);return
 print("SHADOW BAKE OK")
 get_tree().quit()
