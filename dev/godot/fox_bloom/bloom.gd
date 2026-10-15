extends Node3D
const LIFE=1.8
var clock:=0.0
var layer:="all"
var petals:Array=[]
var particles:Array=[]
var times:Array=[]
var water:MeshInstance3D
var camera:Camera3D
var petal_shader=load("res://petal.gdshader")
var water_shader=load("res://water.gdshader")
var textures:Array=[]

func mesh_grid()->ArrayMesh:
 var st=SurfaceTool.new()
 st.begin(Mesh.PRIMITIVE_TRIANGLES)
 for y in range(24):
  for x in range(8):
   for d in [Vector2(0,0),Vector2(1,0),Vector2(0,1),Vector2(1,0),Vector2(1,1),Vector2(0,1)]:
    var uv=Vector2((x+d.x)/8.,(y+d.y)/24.)
    st.set_uv(uv)
    st.set_normal(Vector3(0,0,1))
    st.add_vertex(Vector3(uv.x,uv.y,0))
 return st.commit()

func material(tex:int,angle:float,width:float,length_value:float,twist:float,reflection:bool=false)->ShaderMaterial:
 var m=ShaderMaterial.new()
 m.shader=petal_shader
 for key in {"art":textures[tex],"angle":angle,"width":width,"petal_length":length_value,"twist":twist,"reflection":1.0 if reflection else 0.0}:
  m.set_shader_parameter(key,{"art":textures[tex],"angle":angle,"width":width,"petal_length":length_value,"twist":twist,"reflection":1.0 if reflection else 0.0}[key])
 if reflection:m.render_priority=-10
 return m

func instance(mesh:Mesh,mat:ShaderMaterial)->MeshInstance3D:
 var node=MeshInstance3D.new()
 node.mesh=mesh
 node.material_override=mat
 add_child(node)
 return node

func _ready():
 get_viewport().transparent_bg=true
 for name in ["petal_wide","petal_curl"]:textures.append(ImageTexture.create_from_image(Image.load_from_file("res://art/"+name+".png")))
 camera=Camera3D.new()
 camera.projection=Camera3D.PROJECTION_ORTHOGONAL
 camera.size=4.8
 add_child(camera)
 camera.position=Vector3(0,5,7)
 camera.look_at(Vector3.ZERO)
 camera.current=true
 var plane=PlaneMesh.new()
 plane.size=Vector2(3.7,3.7)
 plane.subdivide_width=50
 plane.subdivide_depth=50
 var wm=ShaderMaterial.new()
 wm.shader=water_shader
 wm.set_shader_parameter("surface_art",ImageTexture.create_from_image(Image.load_from_file("res://art/water_source.png")))
 wm.render_priority=-5
 water=instance(plane,wm)
 var mesh=mesh_grid()
 # Deliberately unequal shapes, inclinations and launch times; six petals make one flower.
 var specs=[[3.48,.56,1.65,.18,.0,0],[4.52,.46,1.96,-.36,.018,1],[5.65,.59,1.77,.32,.04,0],[.25,.51,1.60,-.22,.06,1],[1.30,.63,1.75,.18,.027,0],[2.38,.43,1.88,-.28,.075,1]]
 for s in specs:
  var mat=material(s[5],s[0],s[1]*1.25,s[2]*1.25,s[3])
  var refmat=material(s[5],s[0],s[1]*1.25,s[2]*1.25,s[3],true)
  petals.append({"node":instance(mesh,mat),"reflection":instance(mesh,refmat),"mat":mat,"refmat":refmat,"angle":s[0],"delay":s[4]})
 var rng=RandomNumberGenerator.new()
 rng.seed=151015
 for i in range(9):
  var a=TAU*i/9.+rng.randf_range(-.22,.22)
  var size_value=rng.randf_range(.18,.35)
  var quad=QuadMesh.new()
  quad.size=Vector2(size_value,size_value*1.7)
  var mat=material(i%2,a,1.,1.,0.)
  mat.set_shader_parameter("detached",1.)
  particles.append({"node":instance(quad,mat),"mat":mat,"a":a,"delay":.30+rng.randf_range(0,.25),"speed":rng.randf_range(.8,1.5),"rise":rng.randf_range(1.0,2.0),"spin":rng.randf_range(-3.,3.)})
 for i in range(30):times.append(i/60.)
 for i in range(39):times.append(.5+i/30.)
 if "--bake" in OS.get_cmdline_user_args():
  set_process(false)
  call_deferred("bake")

func animate(t:float):
 var fade=pow(clampf(1.-(t-.48)/1.32,0,1),1.25)
 water.visible=layer!="air"
 water.scale=Vector3.ONE*lerpf(.25,1.,1.-exp(-t*11.))
 water.material_override.set_shader_parameter("age",t)
 water.material_override.set_shader_parameter("opacity",clampf(t/.045,0,1)*fade)
 for p in petals:
  var a=maxf(0,t-p.delay)
  var opening=smoothstep(.045,.34,a)
  var growth=smoothstep(0,.09,a)
  var alpha=pow(clampf(1.-(a-.48)/.6,0,1),1.25)
  var erosion=lerpf(-.2,1.15,smoothstep(.52,1.07,a))
  p.node.visible=a>0 and (layer=="all" or (layer=="floor" and sin(p.angle)<0) or (layer=="air" and sin(p.angle)>=0))
  p.reflection.visible=a>0 and layer!="air"
  for m in [p.mat,p.refmat]:
   m.set_shader_parameter("opening",opening)
   m.set_shader_parameter("growth",growth)
   m.set_shader_parameter("age",t)
   m.set_shader_parameter("erosion",erosion)
  p.mat.set_shader_parameter("opacity",alpha)
  p.refmat.set_shader_parameter("opacity",alpha*.28*fade)
 for p in particles:
  var a=t-p.delay
  var node:MeshInstance3D=p.node
  node.position=Vector3(cos(p.a)*(.9+maxf(a,0)*p.speed),.65+maxf(a,0)*p.rise-maxf(a,0)*maxf(a,0)*1.4,sin(p.a)*(.9+maxf(a,0)*p.speed))
  node.rotation=Vector3(a*p.spin,.3+p.a,a*p.spin*.6)
  node.visible=a>=0 and a<.9 and (layer=="all" or (layer=="floor" and node.position.z<0) or (layer=="air" and node.position.z>=0))
  p.mat.set_shader_parameter("age",t)
  p.mat.set_shader_parameter("opacity",clampf(a/.04,0,1)*pow(clampf(1-a/.9,0,1),1.5))
  p.mat.set_shader_parameter("erosion",lerpf(-.2,1.,smoothstep(.5,.9,a)))

func _process(dt):
 clock=fmod(clock+dt,2.6)
 animate(clock)

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
 f.store_string(JSON.stringify({"times":times,"frames":times.size(),"cols":8,"life":LIFE,"anchor":[.5,.5]},"  "))
 print("BLOOM BAKE OK: %d frames x 2 depth layers" % times.size())
 get_tree().quit()
