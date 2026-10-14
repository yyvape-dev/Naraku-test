extends Node2D
## GPT Image materials + image-designed keyframes, animated by Godot.
const FRAME_COUNT = 36
const FPS = 40.0
const CENTER = Vector2(200,225)
var clock := 0.0
var layer := "all"
var baking := false
var art := {}
var shards: Array = []
var rays: Array = []
var cracks: Array = []
var textures := {}
var slash: Sprite2D
var impact: Sprite2D
var smoke: Sprite2D
var trail: Sprite2D
var shader = load("res://reveal.gdshader")

func material(seed_value:float) -> ShaderMaterial:
 var m=ShaderMaterial.new()
 m.shader=shader
 m.set_shader_parameter("seed",seed_value)
 return m

func sprite(texture_name:String,seed_value:float) -> Sprite2D:
 var s=Sprite2D.new()
 s.texture=art[texture_name]
 s.position=CENTER
 s.material=material(seed_value)
 add_child(s)
 return s

func _ready():
 get_viewport().transparent_bg=true
 for name in ["slash","impact","rock","dust"]:
  var img=Image.load_from_file("res://art/"+name+".png")
  if img.is_empty():
   push_error("Missing GPT Image material: "+name)
   get_tree().quit(1)
   return
  art[name]=ImageTexture.create_from_image(img)
 var rng=RandomNumberGenerator.new()
 rng.seed=621409
 for i in range(12):
  var angle=TAU*i/12.0+rng.randf_range(-.2,.2)
  shards.append({"v":Vector2(cos(angle)*rng.randf_range(80,170),rng.randf_range(-280,-100)),"size":rng.randf_range(9,21),"rot":rng.randf_range(-PI,PI),"spin":rng.randf_range(-6,6),"delay":rng.randf_range(.07,.105)})
 for i in range(27):
  rays.append({"a":rng.randf_range(-PI,PI),"speed":rng.randf_range(120,310),"delay":rng.randf_range(.055,.10),"life":rng.randf_range(.16,.32)})
 for i in range(8):
  var points=PackedVector2Array([Vector2.ZERO])
  var angle=TAU*i/8.0+rng.randf_range(-.18,.18)
  for j in range(1,8):
   points.append(Vector2(cos(angle)*j*17+rng.randf_range(-6,6),sin(angle)*j*9+rng.randf_range(-4,4)))
  cracks.append(points)
 # Smoke belongs under enemies. Slash/impact are above them in the web bake.
 smoke=sprite("dust",7)
 trail=sprite("slash",11)
 slash=sprite("slash",3)
 impact=sprite("impact",5)
 baking="--bake" in OS.get_cmdline_user_args()
 if baking:
  set_process(false)
  call_deferred("bake")
 else:
  animate(0)

func _process(dt):
 clock=fmod(clock+dt,1.7)
 animate(clock)

func configure(s:Sprite2D,width:float,alpha:float,reveal:float=1.1,dissolve:float=-.2):
 s.scale=Vector2.ONE*width/1254.0
 s.material.set_shader_parameter("opacity",alpha)
 s.material.set_shader_parameter("reveal",reveal)
 s.material.set_shader_parameter("dissolve",dissolve)

func animate(t:float):
 var airborne=layer!="floor"
 smoke.visible=layer!="air" and t>.095 and t<.78
 slash.visible=airborne and t<.18
 impact.visible=airborne and t>.035 and t<.22
 trail.visible=airborne and t>.06 and t<.36
 # Fast direction reveal, minimal scaling: a strike, rather than a popping sticker.
 var slash_alpha=pow(clampf(1-(t-.045)/.135,0,1),1.2)
 configure(slash,280,slash_alpha,lerpf(.23,1.1,clampf(t/.048,0,1)),lerpf(-.2,.98,clampf((t-.075)/.105,0,1)))
 slash.position=CENTER+Vector2(0,-11)
 var age=maxf(0,t-.035)
 var grow=1-pow(1-clampf(age/.05,0,1),3)
 configure(impact,lerpf(60,210,grow),clampf(age/.015,0,1)*pow(clampf(1-(t-.08)/.14,0,1),1.6),1.1,lerpf(-.2,1.0,clampf((t-.11)/.11,0,1)))
 impact.position=CENTER
 configure(trail,285,pow(clampf(1-(t-.06)/.3,0,1),1.8)*.25,1.1,clampf((t-.09)/.26,0,1))
 trail.position=CENTER+Vector2(-5,-10-t*15)
 trail.self_modulate=Color(.55,.12,.05,1)
 var dust_age=maxf(0,t-.095)
 configure(smoke,lerpf(150,310,1-exp(-dust_age*5)),clampf(dust_age/.06,0,1)*pow(maxf(0,1-dust_age/.685),1.5)*.32,1.1,lerpf(-.15,.97,clampf((dust_age-.15)/.54,0,1)))
 smoke.position=CENTER+Vector2(0,-18-dust_age*20)
 smoke.scale.y*=.60
 queue_redraw()

func radial(color:Color) -> Texture2D:
 var key=color.to_html()
 if textures.has(key):return textures[key]
 var g=Gradient.new()
 g.offsets=PackedFloat32Array([0,.15,.42,.7,1])
 g.colors=PackedColorArray([color,Color(color,color.a*.8),Color(color,color.a*.35),Color(color,color.a*.07),Color(color,0)])
 var tex=GradientTexture2D.new()
 tex.gradient=g
 tex.width=128
 tex.height=128
 tex.fill=GradientTexture2D.FILL_RADIAL
 tex.fill_from=Vector2(.5,.5)
 tex.fill_to=Vector2(1,.5)
 textures[key]=tex
 return tex

func glow(p:Vector2,size:Vector2,color:Color):
 draw_texture_rect(radial(color),Rect2(p-size*.5,size),false)

func _draw():
 var t=clock
 if t>=.9:return
 if layer!="air":
  var reveal=clampf(t/.11,0,1)
  var fade=pow(maxf(0,1-t/.9),1.7)
  for path in cracks:
   var pts=PackedVector2Array()
   for i in range(clampi(int(reveal*path.size()),2,path.size())):pts.append(CENTER+path[i])
   draw_polyline(pts,Color(.035,.018,.012,.75*fade),3,true)
   draw_polyline(pts,Color(.86,.17,.035,.55*fade),1.1,true)
   draw_polyline(pts,Color(1,.63,.23,.7*pow(maxf(0,1-t/.3),2)),.55,true)
 if layer!="floor":
  # Tiny center flash, never an opaque white disk.
  var peak=clampf(1-abs(t-.075)/.055,0,1)
  glow(CENTER,Vector2(68,48),Color(1,.80,.48,.48*peak))
  for ray in rays:
   var age=t-ray.delay
   if age<0 or age>ray.life:continue
   var fade=pow(1-age/ray.life,1.7)
   var dir=Vector2(cos(ray.a),sin(ray.a)*.55)
   var p=CENTER+dir*(12+ray.speed*age)
   draw_line(p-dir*(3+7*fade),p,Color(1,.68,.24,.8*fade),.9,true)
  for rock in shards:
   var age=t-rock.delay
   if age<0:continue
   var alpha=clampf((.57-age)/.18,0,1)*clampf(age/.025,0,1)
   if alpha<=0:continue
   var pos=CENTER+rock.v*age+Vector2(0,280*age*age)
   var size=rock.size*(1-age*.2)
   draw_set_transform(pos,rock.rot+rock.spin*age,Vector2.ONE)
   draw_texture_rect(art.rock,Rect2(-size*.5,-size*.5,size,size),false,Color(1,1,1,alpha))
   draw_set_transform(Vector2.ZERO)

func bake():
 DirAccess.make_dir_recursive_absolute("res://frames")
 for pass_name in ["floor","air"]:
  layer=pass_name
  for frame in range(FRAME_COUNT):
   clock=frame/FPS
   animate(clock)
   await get_tree().process_frame
   await RenderingServer.frame_post_draw
   var img=get_viewport().get_texture().get_image()
   var err=img.save_png("res://frames/%s_%02d.png" % [pass_name,frame])
   if err!=OK:
    push_error("PNG export failed: %s" % err)
    get_tree().quit(1)
    return
 print("BAKE OK: GPT Image materials + motion board, 36 frames x 2 transparent layers")
 get_tree().quit()
