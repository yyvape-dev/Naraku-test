extends Node2D
const C=Vector2(200,240)
const LIFE=1.35
var clock:=0.0
var layer:="all"
var sprites:={}
var shader=load("res://flow.gdshader")
var times:Array=[]

func sprite(key:String,path:String):
 var s=Sprite2D.new()
 var image=Image.load_from_file(path)
 if image.is_empty():
  push_error("Missing material: "+path)
  get_tree().quit(1)
  return
 s.texture=ImageTexture.create_from_image(image)
 var mat=ShaderMaterial.new()
 mat.shader=shader
 s.material=mat
 add_child(s)
 sprites[key]=s

func shared(name:String)->String:
 return ProjectSettings.globalize_path("res://").path_join("../fox/art/"+name+".png").simplify_path()

func _ready():
 get_viewport().transparent_bg=true
 sprite("smoke",shared("smoke"))
 sprite("jettelly",shared("jettelly_smoke"))
 sprites.jettelly.hframes=8
 sprites.jettelly.vframes=8
 sprite("support",shared("support_smoke"))
 sprite("main","res://art/main.png")
 sprite("fragments",shared("fragments"))
 sprite("embers",shared("embers"))
 for i in range(24):times.append(i/60.0)
 for i in range(21):times.append(.4+i/30.0)
 for i in range(6):times.append(1.1+i/24.0)
 if "--bake" in OS.get_cmdline_user_args():
  set_process(false)
  call_deferred("bake")

func place(key:String,width:float,pos:Vector2,alpha:float,spread:float,erosion:float,t:float,thermal:float=0.0):
 var s:Sprite2D=sprites[key]
 s.position=pos
 s.scale=Vector2.ONE*width/(s.texture.get_width()/s.hframes)
 s.visible=alpha>.001
 var parameters={"age":t,"opacity":alpha,"spread":spread,"erosion":erosion,"cooling":smoothstep(.12,.72,t),"thermal":thermal,"seed":float(key.length())*3.7}
 for setting in parameters:s.material.set_shader_parameter(setting,parameters[setting])

func animate(t:float):
 var air=layer!="floor"
 var floor_on=layer!="air"
 # A connected expanding fire swathe; the contact point stays fixed.
 var expansion=1-exp(-t*19.0)
 var width=lerpf(170,280,expansion)
 var main_alpha=pow(clampf(1-(t-.15)/.52,0,1),1.25)
 place("main",width,C+Vector2(-.09*width,-.30*width),main_alpha if air else 0.0,lerpf(.10,.84,1-pow(1-clampf(t/.19,0,1),2)),lerpf(-.25,1.12,smoothstep(.30,.76,t)),t,1.0)
 # One offset curling fragment has a different acceleration and dies after the main wave.
 var a=maxf(0,t-.105)
 var trail=clampf(a/.055,0,1)*pow(clampf(1-a/.62,0,1),1.65)
 place("fragments",lerpf(75,127,1-exp(-a*5)),C+Vector2(56+23*a,-42-48*a),trail*.66 if air else 0.0,1.2,lerpf(-.2,1.1,smoothstep(.24,.72,a)),t,1.0)
 sprites.fragments.rotation=-.42+a*.14
 var b=maxf(0,t-.15)
 var smoke=clampf(b/.14,0,1)*pow(clampf(1-b/1.16,0,1),1.65)
 place("smoke",lerpf(163,246,1-exp(-b*3)),C+Vector2(-8+9*b,-13-23*b),smoke*.24 if floor_on else 0.0,1.2,-.2+b*.76,t)
 sprites.smoke.scale.y*=.58
 place("support",lerpf(120,219,1-exp(-b*3)),C+Vector2(0,5-9*b),smoke*.15 if floor_on else 0.0,1.2,-.2+b*.70,t)
 sprites.support.scale.y*=.4
 sprites.support.material.set_shader_parameter("tint",Color(.33,.23,.26,1))
 place("jettelly",lerpf(118,225,1-exp(-b*3)),C+Vector2(7,-13-18*b),smoke*.16 if floor_on else 0.0,1.2,-.2+b*.55,t)
 sprites.jettelly.scale.y*=.6
 sprites.jettelly.frame=clampi(7+int(b*43),7,60)
 sprites.jettelly.material.set_shader_parameter("flow",0.0)
 sprites.jettelly.material.set_shader_parameter("tint",Color(.28,.18,.28,1))
 var em=clampf(t/.05,0,1)*pow(clampf(1-t/.92,0,1),1.9)
 place("embers",lerpf(105,227,1-exp(-t*4.5)),C+Vector2(14+t*17,-23-t*38),em*.62 if air else 0.0,1.2,-.2+t*.65,t,1.0)
 sprites.embers.rotation=-.20

func _process(dt):
 clock=fmod(clock+dt,2.1)
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
 f.store_string(JSON.stringify({"times":times,"frames":times.size(),"cols":8,"life":LIFE,"anchor":[.5,.6]},"  "))
 print("FOX SKILL BAKE OK: %d frames x 2 layers" % times.size())
 get_tree().quit()
