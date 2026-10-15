extends Node2D
const C=Vector2(200,240)
const LIFE=1.4
var clock:=0.0
var layer:="all"
var baking:=false
const MASTER=1280
var times:Array=[]
var parts:Array=[]
var motes:Array=[]
var flames:={}
var shader=load("res://flow.gdshader")
var glow:GradientTexture2D
var water:Sprite2D
var smoke:Sprite2D

func mesh_flame(key:String,origin:Vector2,source:String=""):
 if source=="":source=key
 var tex=ImageTexture.create_from_image(Image.load_from_file("res://art/"+source+".png"))
 var vertices=PackedVector2Array()
 var uvs=PackedVector2Array()
 var indices=PackedInt32Array()
 for y in range(25):
  for x in range(19):
   var uv=Vector2(x/18.0,y/24.0)
   vertices.append((uv-origin)*Vector2(tex.get_size()))
   uvs.append(uv)
 for y in range(24):
  for x in range(18):
   var i=y*19+x
   indices.append_array([i,i+1,i+19,i+1,i+20,i+19])
 var arrays=[]
 arrays.resize(Mesh.ARRAY_MAX)
 arrays[Mesh.ARRAY_VERTEX]=vertices
 arrays[Mesh.ARRAY_TEX_UV]=uvs
 arrays[Mesh.ARRAY_INDEX]=indices
 var mesh=ArrayMesh.new()
 mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
 var node=MeshInstance2D.new()
 node.mesh=mesh
 node.texture=tex
 var mat=ShaderMaterial.new()
 mat.shader=shader
 mat.set_shader_parameter("root",origin)
 mat.set_shader_parameter("seed",float(flames.size())*4.17)
 node.material=mat
 add_child(node)
 flames[key]=node

func _ready():
 get_viewport().transparent_bg=true
 scale=Vector2.ONE*(MASTER/400.0)
 baking="--bake" in OS.get_cmdline_user_args()
 water=Sprite2D.new()
 water.texture=ImageTexture.create_from_image(Image.load_from_file(ProjectSettings.globalize_path("res://../fox_bloom/art/water_source.png")))
 var wm=ShaderMaterial.new()
 wm.shader=load("res://reflection.gdshader")
 water.material=wm
 water.position=C+Vector2(-5,9)
 water.scale=Vector2(220.,45.)/Vector2(water.texture.get_size())
 add_child(water)
 smoke=Sprite2D.new()
 smoke.texture=ImageTexture.create_from_image(Image.load_from_file(ProjectSettings.globalize_path("res://../fox/art/smoke.png")))
 var sm=ShaderMaterial.new()
 sm.shader=load("res://../fox_skill/flow.gdshader")
 sm.set_shader_parameter("thermal",0.)
 sm.set_shader_parameter("tint",Color(.35,.26,.29,1))
 sm.set_shader_parameter("spread",1.2)
 smoke.material=sm
 add_child(smoke)
 mesh_flame("sakura_burst",Vector2(.5,.53))
 mesh_flame("rear",Vector2(.5,.94))
 mesh_flame("front",Vector2(.12,.88))
 mesh_flame("root",Vector2(.5,.8))
 mesh_flame("fragment_a",Vector2(.5,.85))
 mesh_flame("fragment_b",Vector2(.15,.88))
 var grad=Gradient.new()
 grad.set_color(0,Color(1,.30,.08,.20))
 grad.set_color(1,Color(1,.14,.03,0))
 glow=GradientTexture2D.new()
 glow.gradient=grad
 glow.width=128
 glow.height=128
 glow.fill=GradientTexture2D.FILL_RADIAL
 glow.fill_from=Vector2(.5,.5)
 glow.fill_to=Vector2(1,.5)
 var rng=RandomNumberGenerator.new()
 rng.seed=14927
 # Bursts are attached to two sources, never placed on an evenly divided circle.
 for i in range(57):
  var burst=i%3
  var born=[.045,.115,.225][burst]+rng.randf_range(-.018,.027)
  var petal=i>=43
  var heavy=i%5==0 or petal
  var source=Vector2(-22,-5) if burst!=1 else Vector2(24,-10)
  parts.append({"born":born,"life":rng.randf_range(.48,1.02) if not heavy else rng.randf_range(.70,1.08),"p":C+source+Vector2(rng.randf_range(-13,13),rng.randf_range(-8,4)),"v":Vector2(rng.randf_range(-65,115),rng.randf_range(-180,-55)),"drag":rng.randf_range(5,12) if not heavy else rng.randf_range(2,4),"heavy":heavy,"size":rng.randf_range(.8,1.7) if not heavy else rng.randf_range(2.0,3.5),"seed":rng.randf_range(0,6),"front":i%3==1,"petal":(i%2) if petal else -1,"width":rng.randf_range(19.,36.) if petal else 0.})
 for i in range(30):times.append(i/60.0)
 for i in range(27):times.append(.5+i/30.0)
 if baking:
  set_process(false)
  call_deferred("bake")

func wind(p:Vector2,t:float)->Vector2:
 var pulse=exp(-pow((t-.22)/.16,2.0))
 var q=(p-C)/90.0
 return Vector2(38+145*pulse+25*sin(q.y*2.4-t*8),-23-50*pulse+20*sin(q.x*3+t*6))

func put(key:String,pos:Vector2,width:float,height:float,alpha:float,t:float,erosion:float,deform:float=1.):
 var n=flames[key]
 n.position=pos
 n.scale=Vector2(width/n.texture.get_width(),height/n.texture.get_height())
 n.visible=alpha>.001
 var params={"age":t,"opacity":alpha,"consume":erosion,"cooling":smoothstep(.16,.85,t),"gust":(wind(C,t).x-38)/145.,"deform":deform,"peeling":1. if key=="sakura_burst" else 0.,"base_feather":0. if key in ["sakura_burst","root"] else 1.}
 for k in params:
  n.material.set_shader_parameter(k,params[k])

func animate(t:float):
 clock=t
 var rear=layer!="air"
 var front=layer!="floor"
 var reflected=maxf(0,t-.035)
 water.visible=rear
 water.material.set_shader_parameter("age",t)
 water.material.set_shader_parameter("opacity",clampf(reflected/.025,0,1)*pow(clampf(1.-reflected/.64,0,1),1.5)*.52)
 var haze=maxf(0,t-.24)
 smoke.visible=rear
 smoke.position=C+Vector2(10+haze*42,-16-haze*24)
 smoke.scale=Vector2(155.+haze*30,66.+haze*18)/Vector2(smoke.texture.get_size())
 smoke.material.set_shader_parameter("age",t)
 smoke.material.set_shader_parameter("opacity",clampf(haze/.13,0,1)*pow(clampf(1.-haze/.76,0,1),1.7)*.11)
 smoke.material.set_shader_parameter("erosion",haze*.7)
 # A short five-cleft ignition silhouette, then wind consumes the lobes.
 var bloom=clampf((t-.018)/.045,0,1)*(1.-smoothstep(.17,.32,t))
 var bloom_size=1.-exp(-maxf(t-.025,0)*22.)
 put("sakura_burst",C+Vector2(-3,-12),lerpf(180,330,bloom_size),lerpf(70,182,bloom_size),bloom*.94 if rear else 0.,t,lerpf(-.20,1.25,smoothstep(.10,.32,t)),1.25)
 flames.sakura_burst.rotation=-.13+.07*smoothstep(.08,.28,t)
 var rise=1.-exp(-t*30.)
 var strength=clampf(t/.025,0,1)*pow(clampf(1.-maxf(0,t-.13)/.50,0,1),.75)
 var consume=lerpf(-.22,1.18,smoothstep(.12,.64,t))
 # The rooted rear rises first; the low foreground follows instead of opening in unison.
 put("rear",C+Vector2(-18,-6),lerpf(48,116,rise),lerpf(58,186,rise),strength*.94 if rear else 0.,t,consume,.85)
 var front_age=maxf(0,t-.028)
 var front_rise=1.-exp(-front_age*29.)
 var front_strength=clampf(front_age/.025,0,1)*pow(clampf(1.-maxf(0,front_age-.09)/.43,0,1),.85)
 put("front",C+Vector2(-35,5),lerpf(70,232,front_rise),lerpf(18,83,front_rise),front_strength*.90 if front else 0.,t+.025,consume+.04,.55)
 put("root",C+Vector2(-12,0),lerpf(18,50,rise),lerpf(13,40,rise),pow(clampf(1.-t/.13,0,1),1.3) if front else 0.,t,-.3,0.)
 # Two very different ruptures: a narrow rising tongue, then a low tearing shred.
 var a=maxf(t-.16,0.)
 var detached=clampf(a/.035,0,1)*pow(clampf(1.-a/.35,0,1),1.35)
 put("fragment_a",C+Vector2(2+a*77,-83-a*110),24+9*a,62-30*a,detached*.82 if rear else 0.,t,lerpf(-.12,1.15,smoothstep(.19,.54,t)),.8)
 flames.fragment_a.rotation=.06+a*.38
 var b=maxf(t-.215,0.)
 var shred=clampf(b/.03,0,1)*pow(clampf(1.-b/.29,0,1),1.45)
 put("fragment_b",C+Vector2(67+b*122,-19-b*30),51-20*b,25-7*b,shred*.68 if front else 0.,t+.06,lerpf(-.10,1.15,smoothstep(.24,.55,t)),.55)
 flames.fragment_b.rotation=.10-b*.45
 motes.clear()
 for part in ([] if baking else parts):
  var age=t-part.born
  if age<0 or age>part.life:continue
  var pos:Vector2=part.p
  var vel:Vector2=part.v
  var u=0.0
  while u<age:
   var dt=minf(1./180.,age-u)
   var w=wind(pos,u+part.born)
   var gravity=Vector2(0,85) if part.heavy else Vector2(0,-37)
   var curl=Vector2(sin(pos.y*.06+u*9+part.seed)*35,cos(pos.x*.05-u*7+part.seed)*23)
   vel+=(part.drag*(w-vel)+gravity+curl)*dt
   pos+=vel*dt
   u+=dt
  var heat=clampf(1.-age/part.life,0,1)
  var col=Color(1,lerpf(.11,.72,heat),lerpf(.035,.32,heat),pow(heat,.8)*smoothstep(0.,.035,age))
  motes.append({"p":pos,"v":vel,"col":col,"size":part.size*(.65+.55*heat),"front":part.front})
 queue_redraw()

func _draw():
 var t=clock
 if layer!="air":
  var light=clampf(t/.022,0,1)*pow(clampf(1.-t/.44,0,1),1.7)
  draw_set_transform(C+Vector2(-8,1),0,Vector2(1,.29))
  draw_texture_rect(glow,Rect2(-132,-90,264,180),false,Color(1,1,1,light*.8))
  draw_set_transform(Vector2.ZERO)
 for p in motes:
  if (layer=="air" and not p.front) or (layer=="floor" and p.front):continue
  var trail=p.v.normalized()*clampf(p.v.length()*.022,1.0,4.0)
  draw_texture_rect(glow,Rect2(p.p-Vector2.ONE*7.,Vector2.ONE*14.),false,Color(1,1,1,p.col.a*.55))
  draw_line(p.p-trail,p.p,p.col,p.size,true)

func _process(dt):
 animate(fmod(clock+dt,2.1))

func bake():
 DirAccess.make_dir_recursive_absolute("res://frames")
 for pass_name in ["floor","air"]:
  layer=pass_name
  for i in range(times.size()):
   animate(times[i])
   await get_tree().process_frame
   await RenderingServer.frame_post_draw
   var err=get_viewport().get_texture().get_image().save_png("res://frames/%s_%02d.png" % [pass_name,i])
   if err!=OK:
    get_tree().quit(1)
    return
 var f=FileAccess.open("res://timeline.json",FileAccess.WRITE)
 f.store_string(JSON.stringify({"times":times,"frames":times.size(),"cols":8,"life":LIFE,"anchor":[.5,.6],"native":MASTER},"  "))
 var recipe=[]
 for part in parts:
  var q=part.duplicate()
  q.p=[part.p.x,part.p.y]
  q.v=[part.v.x,part.v.y]
  recipe.append(q)
 var pf=FileAccess.open("res://particles.json",FileAccess.WRITE)
 pf.store_string(JSON.stringify(recipe,"  "))
 print("FOX GUST BAKE OK: %d frames x 2 layers" % times.size())
 get_tree().quit()
