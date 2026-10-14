extends Node2D
const CENTER=Vector2(100,160)
const LIFE=0.8
var clock:=0.0
var layer:="all"
var sprites:={}
var shader=load("res://flow.gdshader")
var times:Array=[]

func sprite(key:String,path:String):
 var s=Sprite2D.new()
 s.texture=ImageTexture.create_from_image(Image.load_from_file(path))
 var mat=ShaderMaterial.new()
 mat.shader=shader
 s.material=mat
 add_child(s)
 sprites[key]=s

func _ready():
 get_viewport().transparent_bg=true
 sprite("smoke","res://art/smoke.png")
 sprite("jettelly","res://art/jettelly_smoke.png")
 sprites.jettelly.hframes=8
 sprites.jettelly.vframes=8
 sprite("support","res://art/support_smoke.png")
 sprite("flame","res://art/flame.png")
 sprite("fragments","res://art/fragments.png")
 sprite("embers","res://art/embers.png")
 for i in range(18):times.append(i/60.0)
 for i in range(15):times.append(.3+i/30.0)
 if "--bake" in OS.get_cmdline_user_args():
  set_process(false)
  call_deferred("bake")

func place(key:String,width:float,pos:Vector2,alpha:float,reveal:float,erosion:float,t:float):
 var s:Sprite2D=sprites[key]
 s.position=pos
 s.scale=Vector2.ONE*width/(s.texture.get_width()/s.hframes)
 s.material.set_shader_parameter("age",t)
 s.material.set_shader_parameter("opacity",alpha)
 s.material.set_shader_parameter("reveal",reveal)
 s.material.set_shader_parameter("erosion",erosion)
 s.material.set_shader_parameter("seed",float(key.length())*2.3)
 s.material.set_shader_parameter("thermal",1.0 if key in ["flame","fragments","embers"] else 0.0)
 s.material.set_shader_parameter("cooling",smoothstep(.08,.43,t))
 s.visible=alpha>.001

func animate(t:float):
 var air=layer!="floor"
 var floor_on=layer!="air"
 var launch=1.0-exp(-t*38.0)
 var decay=pow(clampf(1.0-(t-.06)/.29,0,1),1.5)
 var flame_width=lerpf(73,150,launch)
 # Keep the piercing root at the contact point as the fire expands.
 place("flame",flame_width,CENTER+Vector2(.42*flame_width,-.42*flame_width*681.0/725.0),decay if air else 0.0,lerpf(.12,1.2,smoothstep(0,.085,t)),lerpf(-.2,.95,clampf((t-.13)/.23,0,1)),t)
 var a=maxf(0,t-.045)
 var frag=clampf(a/.025,0,1)*pow(clampf(1-a/.38,0,1),1.8)
 place("fragments",lerpf(68,100,1-exp(-a*12)),CENTER+Vector2(48+40*a,-40-70*a),frag*.85 if air else 0.0,1.2,lerpf(-.2,1.05,clampf((a-.08)/.32,0,1)),t)
 var smoke_age=maxf(0,t-.075)
 var sm=clampf(smoke_age/.08,0,1)*pow(clampf(1-smoke_age/.68,0,1),1.6)
 place("smoke",lerpf(74,121,1-exp(-smoke_age*5)),CENTER+Vector2(25+smoke_age*13,-10-smoke_age*27),sm*.23 if floor_on else 0.0,1.2,-.2+smoke_age*.9,t)
 place("support",lerpf(35,74,1-exp(-smoke_age*5)),CENTER+Vector2(5,-smoke_age*14),sm*.11 if floor_on else 0.0,1.2,-.2+smoke_age,t)
 place("jettelly",lerpf(46,90,1-exp(-smoke_age*5)),CENTER+Vector2(13,-10-smoke_age*26),sm*.14 if floor_on else 0.0,1.2,-.2+smoke_age,t)
 sprites.jettelly.material.set_shader_parameter("flow",0.0)
 sprites.jettelly.frame=clampi(8+int(smoke_age*62),8,60)
 sprites.jettelly.material.set_shader_parameter("tint",Color(.22,.12,.24,1))
 sprites.support.material.set_shader_parameter("flow",.25)
 sprites.support.material.set_shader_parameter("tint",Color(.27,.15,.23,1))
 var em=clampf(t/.02,0,1)*pow(clampf(1-t/.55,0,1),2)
 place("embers",lerpf(45,119,1-exp(-t*9)),CENTER+Vector2(39+t*46,-28-t*52),em*.8 if air else 0.0,1.2,-.2+t,t)

func _process(dt):
 clock=fmod(clock+dt,1.5)
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
 f.store_string(JSON.stringify({"times":times,"frames":times.size(),"cols":8,"life":LIFE,"anchor":[.390625,.625]},"  "))
 print("FOX BAKE OK: %d frames x 2 layers" % times.size())
 get_tree().quit()
