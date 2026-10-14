extends Node2D
## Deterministic timeline: sharp impact, floor shock, stone shards, then dust.
## Run normally to preview; -- --bake exports two transparent layers at 40 fps.
const FRAME_COUNT = 36
const FPS = 40.0
const CENTER = Vector2(200, 225)
var clock := 0.0
var layer := "all"
var shards: Array = []
var rays: Array = []
var cracks: Array = []
var clouds: Array = []
var textures := {}
var baking := false

func _ready():
 get_viewport().transparent_bg = true
 var rng = RandomNumberGenerator.new()
 rng.seed = 621409
 for i in range(23):
  var angle = rng.randf_range(-PI, PI)
  shards.append({"v":Vector2(cos(angle)*rng.randf_range(65,155),rng.randf_range(-255,-95)),"size":rng.randf_range(3.2,9.5),"rot":rng.randf_range(-PI,PI),"spin":rng.randf_range(-8,8),"delay":rng.randf_range(0.015,0.08)})
 for i in range(38):
  rays.append({"a":rng.randf_range(-PI,PI),"speed":rng.randf_range(130,370),"delay":rng.randf_range(0.0,0.065),"life":rng.randf_range(0.19,0.43)})
 for i in range(9):
  var points = PackedVector2Array([Vector2.ZERO])
  var angle = TAU*i/9.0+rng.randf_range(-.16,.16)
  for j in range(1,6):
   points.append(Vector2(cos(angle)*j*23+ rng.randf_range(-8,8),sin(angle)*j*13+rng.randf_range(-5,5)))
  cracks.append(points)
 for i in range(17):
  clouds.append({"p":Vector2(rng.randf_range(-90,90),rng.randf_range(-22,20)),"r":rng.randf_range(13,28),"phase":rng.randf(),"delay":rng.randf_range(.05,.23)})
 baking = "--bake" in OS.get_cmdline_user_args()
 if baking:
  set_process(false)
  call_deferred("bake")

func _process(dt):
 clock = fmod(clock+dt, 1.65)
 queue_redraw()

func radial(color: Color) -> Texture2D:
 var key = color.to_html()
 if textures.has(key): return textures[key]
 var g = Gradient.new()
 g.offsets = PackedFloat32Array([0.0,.15,.42,.7,1.0])
 g.colors = PackedColorArray([color,Color(color,color.a*.8),Color(color,color.a*.35),Color(color,color.a*.07),Color(color,0)])
 var tex = GradientTexture2D.new()
 tex.gradient = g
 tex.width = 128
 tex.height = 128
 tex.fill = GradientTexture2D.FILL_RADIAL
 tex.fill_from = Vector2(.5,.5)
 tex.fill_to = Vector2(1,.5)
 textures[key] = tex
 return tex

func glow(p:Vector2, size:Vector2, color:Color):
 draw_texture_rect(radial(color), Rect2(p-size*.5,size),false)

func ellipse(radius:float, aspect:float, color:Color, width:float, gap:float=0):
 var pts = PackedVector2Array()
 for i in range(97):
  var a = TAU*i/96.0
  pts.append(CENTER+Vector2(cos(a)*radius,sin(a)*radius*aspect))
 draw_polyline(pts,color,width,true)

func _draw():
 var t = clock
 if t >= .9: return
 if layer != "air": draw_floor(t)
 if layer != "floor": draw_air(t)

func draw_floor(t:float):
 var fade = pow(maxf(0,1-t/.9),1.3)
 glow(CENTER+Vector2(0,8),Vector2(235,88),Color(.07,.04,.02,.35*fade))
 var reveal = clampf(t/.085,0,1)
 for points in cracks:
  var n = clampi(int(reveal*points.size()),2,points.size())
  var q = PackedVector2Array()
  for j in range(n): q.append(CENTER+points[j])
  draw_polyline(q,Color(.045,.025,.012,.85*fade),3.8,true)
  draw_polyline(q+PackedVector2Array(),Color(.92,.52,.18,.55*fade),.9,true)
 if t < .3:
  var a = pow(1-t/.3,1.1)
  var r = 22+125*(1-pow(1-t/.3,2))
  ellipse(r,.43,Color(1,.64,.22,.14*a),12)
  ellipse(r,.43,Color(1,.86,.55,.85*a),1.6)
  ellipse(r*.86,.43,Color(.78,.48,.15,.45*a),1)
 glow(CENTER,Vector2(150,60),Color(1,.55,.12,.5*pow(maxf(0,1-t/.16),2)))

func draw_air(t:float):
 # A sharp diagonal strike. Broad bloom is brief; the narrow core carries the hit.
 if t < .17:
  var fade = pow(maxf(0,1-t/.17),1.5)
  var a = CENTER+Vector2(-82,46)
  var z = CENTER+Vector2(79,-76)
  draw_line(a,z,Color(1,.39,.08,.065*fade),25,true)
  draw_line(a,z,Color(1,.67,.26,.21*fade),11,true)
  draw_line(a,z,Color(1,.9,.66,.9*fade),3.8,true)
  draw_line(a+Vector2(7,1),z+Vector2(-3,9),Color(1,1,.91,fade),1.3,true)
 glow(CENTER,Vector2(116,103),Color(1,.72,.33,.72*pow(maxf(0,1-t/.16),2)))
 glow(CENTER,Vector2(44,45),Color(1,.97,.8,.95*pow(maxf(0,1-t/.095),1.2)))
 # Distinct hot streaks; no full-screen flash or large opaque cloud.
 for ray in rays:
  var age = t-ray.delay
  if age < 0 or age > ray.life: continue
  var a = pow(1-age/ray.life,1.5)
  var dir = Vector2(cos(ray.a),sin(ray.a)*.62)
  var p = CENTER+dir*(10+ray.speed*age)
  var tail = p-dir*(5+12*a)
  draw_line(tail,p,Color(1,.57,.13,.45*a),3.1*a,true)
  draw_line(tail,p,Color(1,.91,.65,.95*a),.9,true)
 # Rock fragments have dark silhouettes and separate illuminated faces.
 for rock in shards:
  var age = t-rock.delay
  if age < 0: continue
  var alpha = clampf((.66-age)/.22,0,1)
  if alpha <= 0: continue
  var p = CENTER+rock.v*age+Vector2(0,255*age*age)
  var rotation = rock.rot+rock.spin*age
  var r = rock.size*(1-age*.28)
  var vertices = PackedVector2Array()
  for v in [Vector2(-.8,-.5),Vector2(.05,-1),Vector2(.95,-.18),Vector2(.45,.7),Vector2(-.65,.5)]:
   vertices.append(p+v.rotated(rotation)*r)
  draw_colored_polygon(vertices,Color(.12,.095,.075,alpha))
  draw_colored_polygon(PackedVector2Array([vertices[0],vertices[1],p,vertices[4]]),Color(.48,.36,.2,alpha))
  draw_colored_polygon(PackedVector2Array([vertices[1],vertices[2],p]),Color(.83,.65,.37,alpha))
  draw_polyline(PackedVector2Array([vertices[0],vertices[1],vertices[2]]),Color(1,.8,.45,.7*alpha),.65,true)
 # Warm fine dust remains low, moves outward, and fades rather than concealing enemies.
 for cloud in clouds:
  var age = t-cloud.delay
  if age < 0: continue
  var f = clampf(age/.09,0,1)*pow(maxf(0,1-age/.65),1.7)
  var p = CENTER+cloud.p*(.3+age*1.1)+Vector2(0,-age*(13+cloud.phase*20))
  var radius = cloud.r*(.6+age*1.5)
  glow(p,Vector2(radius*2.8,radius*1.6),Color(.61,.47,.30,.085*f))

func bake():
 DirAccess.make_dir_recursive_absolute("res://frames")
 for pass_name in ["floor","air"]:
  layer = pass_name
  for frame in range(FRAME_COUNT):
   clock = frame/FPS
   queue_redraw()
   await get_tree().process_frame
   await RenderingServer.frame_post_draw
   var img = get_viewport().get_texture().get_image()
   var err = img.save_png("res://frames/%s_%02d.png" % [pass_name,frame])
   if err != OK:
    push_error("PNG export failed: %s" % err)
    get_tree().quit(1)
    return
 print("BAKE OK: 36 frames x 2 transparent layers at 40 fps")
 get_tree().quit()
