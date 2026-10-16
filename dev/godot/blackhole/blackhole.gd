extends Node2D
const COUNT := 96
const FPS := 30.0
const C := Vector2(256, 256)
# [source, appear, full, fade begins, gone]. Six supplied stages share the vortex center.
const KEYS := [[0,0.0,0.10,0.30,0.52],[1,0.20,0.48,0.85,1.12],[2,0.72,1.04,1.83,2.12],[3,1.87,2.14,2.36,2.43],[4,2.37,2.43,2.54,2.79],[5,2.54,2.72,2.85,3.20]]
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
 get_viewport().canvas_transform=Transform2D().scaled(Vector2(1.5,1.5))
 noise=NoiseTexture2D.new();noise.width=256;noise.height=256;noise.seamless=true
 var n=FastNoiseLite.new();n.seed=624;n.frequency=.025;n.fractal_octaves=3;noise.noise=n
 await noise.changed
 backdrop=ColorRect.new();backdrop.size=Vector2(512,512);backdrop.color=Color.BLACK;add_child(backdrop)
 var world=WorldEnvironment.new();env=Environment.new();env.background_mode=Environment.BG_CANVAS
 env.glow_enabled=true;env.glow_blend_mode=Environment.GLOW_BLEND_MODE_ADDITIVE
 env.glow_intensity=.65;env.glow_hdr_threshold=1.0
 for i in 7: env.set_glow_level(i,[0.,.5,.8,.6,.25,0.,0.][i])
 world.environment=env;add_child(world)
 for l in ["floor","air"]:
  for p in ["matte","light"]:
   var root=Node2D.new();roots[l+"_"+p]=root;add_child(root)
   if p=="light":
    var blend=CanvasItemMaterial.new();blend.blend_mode=CanvasItemMaterial.BLEND_MODE_ADD;root.material=blend
   if l=="floor":
    var rect=ColorRect.new();rect.size=Vector2(490,490);rect.position=C-rect.size*.5
    var sm=ShaderMaterial.new();sm.shader=load("res://ground.gdshader");sm.set_shader_parameter("noise_tex",noise);sm.set_shader_parameter("light_pass",p=="light");rect.material=sm
    root.add_child(rect);grounds.append(rect)
   else:
    for k in KEYS:
     var im=Sprite2D.new();im.texture=load("res://art/%02d.png" % (k[0]+1))
     im.centered=false;im.position=C;im.offset=Vector2(-768,-768);im.scale=Vector2.ONE*.31
     var sm=ShaderMaterial.new();sm.shader=load("res://flow_light.gdshader" if p=="light" else "res://flow.gdshader");sm.set_shader_parameter("noise_tex",noise);sm.set_shader_parameter("light_pass",p=="light");im.material=sm
     root.add_child(im);sprites.append([im,k])
 build_accents()
 build_particles()
 baking="--bake" in OS.get_cmdline_user_args()
 if "--probe" in OS.get_cmdline_user_args():
  set_process(false);call_deferred("probe");return
 if baking:
  set_process(false);call_deferred("bake")
func build_accents():
 # A brief violet breath at final impact; no screen-wide flash.
 var g=Gradient.new();g.offsets=PackedFloat32Array([0.,.22,.58,1.])
 g.colors=PackedColorArray([Color(1,1,1,.8),Color(1,1,1,.48),Color(1,1,1,.08),Color(1,1,1,0)])
 var tex=GradientTexture2D.new();tex.width=128;tex.height=128;tex.gradient=g
 tex.fill=GradientTexture2D.FILL_RADIAL;tex.fill_from=Vector2(.5,.5);tex.fill_to=Vector2(1.,.5)
 for l in ["floor","air"]:
  var sp=Sprite2D.new();sp.texture=tex;sp.position=C if l=="floor" else C
  sp.scale=Vector2(3.6,3.6) if l=="floor" else Vector2(1.35,1.35)
  var blend=CanvasItemMaterial.new();blend.blend_mode=CanvasItemMaterial.BLEND_MODE_ADD;sp.material=blend
  roots[l+"_light"].add_child(sp);accents.append([sp,l])
func build_particles():
 var gradient=Gradient.new();gradient.colors=PackedColorArray([Color(1,1,1,1),Color(1,1,1,.25),Color(1,1,1,0)]);gradient.offsets=PackedFloat32Array([0.,.3,1.])
 var tex=GradientTexture2D.new();tex.width=16;tex.height=16;tex.gradient=gradient;tex.fill=GradientTexture2D.FILL_RADIAL;tex.fill_from=Vector2(.5,.5);tex.fill_to=Vector2(1.,.5)
 var gp=GPUParticles2D.new();gp.texture=tex;gp.amount=40;gp.lifetime=.55;gp.one_shot=true;gp.explosiveness=1.0;gp.emitting=false
 gp.use_fixed_seed=true;gp.seed=617;gp.fixed_fps=30;gp.interpolate=false;gp.position=C;gp.visibility_rect=Rect2(-250,-250,500,500)
 var pm=ParticleProcessMaterial.new();pm.particle_flag_disable_z=true
 pm.emission_shape=ParticleProcessMaterial.EMISSION_SHAPE_BOX;pm.emission_box_extents=Vector3(16,16,0)
 pm.direction=Vector3(0,-1,0);pm.spread=180;pm.initial_velocity_min=90;pm.initial_velocity_max=220;pm.gravity=Vector3(0,12,0)
 pm.scale_min=.09;pm.scale_max=.23;pm.angular_velocity_min=-100;pm.angular_velocity_max=100
 var g=Gradient.new();g.offsets=PackedFloat32Array([0.,.25,.7,1.]);g.colors=PackedColorArray([Color(.15,.2,.8,0),Color(.6,.45,1.,.7),Color(.2,.3,1.,.35),Color(.2,.3,1.,0)])
 var gt=GradientTexture1D.new();gt.gradient=g;pm.color_ramp=gt;gp.process_material=pm
 var light_shader=ShaderMaterial.new();light_shader.shader=load("res://particle_light.gdshader");gp.material=light_shader
 roots["air_light"].add_child(gp);particles.append(gp)
func animate(t: float):
 clock=t
 var light=pass_name=="light"
 get_viewport().use_hdr_2d=light;backdrop.visible=light;env.glow_enabled=light
 env.glow_intensity=.65 if layer=="air" else .45
 var levels=[0.,.5,.8,.6,.25,0.,0.] if layer=="air" else [0.,.3,.6,.4,.15,0.,0.]
 for i in 7:env.set_glow_level(i,levels[i])
 for k in roots: roots[k].visible=k==layer+"_"+pass_name
 for pair in sprites:
  var im: Sprite2D=pair[0];var k: Array=pair[1]
  im.visible=t>=k[1] and t<k[4]
  var m: ShaderMaterial=im.material
  var gain=ramp(t,k[1],k[2])*(1.-ramp(t,k[3],k[4]))
  m.set_shader_parameter("clock",t);m.set_shader_parameter("opacity",gain)
  m.set_shader_parameter("reveal",lerpf(.0,1.2,ramp(t,k[1],k[2])))
  m.set_shader_parameter("erode",ramp(t,k[3],k[4])*.85)
  # Expand the vortex, compress the core, then release the final burst.
  var sc=.31
  if k[0]<=2:sc*=lerpf(.72,1.0,ramp(t,0.,.9))*(1.-.18*ramp(t,1.7,2.12))
  if k[0]==3:sc*=lerpf(1.0,.72,ramp(t,2.10,2.38))
  if k[0]>=4:sc*=lerpf(.85,1.18,ramp(t,2.38,3.2))
  im.scale=Vector2(sc,sc);im.position=C

 for ground in grounds:
  ground.material.set_shader_parameter("clock",t)
  ground.material.set_shader_parameter("strength",ramp(t,0.,.18)*(1.-ramp(t,2.65,3.20)))
 # Final impact remains at 2.4 seconds.
 var pulse=exp(-pow((t-2.40)/.065,2.))
 for item in accents:
  var sp: Sprite2D=item[0]
  sp.modulate=Color(.52,.16,1.0,pulse*(.22 if item[1]=="floor" else .08))
 for gp in particles:
  if t>=2.4 and t<2.44 and not gp.emitting:gp.emitting=true
func _process(dt):
 animate(fmod(clock+dt,3.8))
func bake():
 DirAccess.make_dir_recursive_absolute("res://frames")
 for l in (["air"] if "--air-only" in OS.get_cmdline_user_args() else (["floor"] if "--floor-only" in OS.get_cmdline_user_args() else ["floor","air"])):
  for p in (["light"] if "--light-only" in OS.get_cmdline_user_args() else ["matte","light"]):
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
 print("BLACKHOLE BAKE OK")
 get_tree().quit()

func probe():
 DirAccess.make_dir_recursive_absolute("res://frames/probe")
 layer="air";pass_name="light"
 for gp in particles:gp.visible=false
 for t in [1.2,2.433333]:
  for on in [false,true]:
   animate(t);env.glow_enabled=on
   for j in 3:await get_tree().process_frame
   await RenderingServer.frame_post_draw
   get_viewport().get_texture().get_image().save_png("res://frames/probe/%s_%s.png" % [str(t),"on" if on else "off"])
 print("GLOW PROBE OK");get_tree().quit()
