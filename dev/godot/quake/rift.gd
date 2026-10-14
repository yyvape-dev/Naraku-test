extends Node2D
## One connected torn ground scar, revealed by an irregular advancing cut.
const LIFE=3.0
var clock=0.0
var layer="all"
var scar:Sprite2D
var art={}
var debris=[]
var dust=[]
var path_points=[Vector2(225,369),Vector2(181,326),Vector2(201,277),Vector2(235,230),Vector2(180,183),Vector2(223,139),Vector2(207,88),Vector2(193,33)]
var strikes=[0.0,.085,.175,.29,.355,.48,.575,.70]
func _ready():
 get_viewport().transparent_bg=true
 for name in ["rift_scar","rock","support_smoke"]:
  art[name]=ImageTexture.create_from_image(Image.load_from_file("res://art/"+name+".png"))
 scar=Sprite2D.new()
 scar.texture=art.rift_scar
 scar.position=Vector2(200,200)
 scar.scale=Vector2(290.0/scar.texture.get_width(),385.0/scar.texture.get_height())
 var mat=ShaderMaterial.new()
 mat.shader=load("res://reveal.gdshader")
 mat.set_shader_parameter("mode",2)
 mat.set_shader_parameter("seed",61.0)
 scar.material=mat
 add_child(scar)
 var rng=RandomNumberGenerator.new()
 rng.seed=93172
 for i in range(18):
  var section=i%7
  var side=-1 if i%2==0 else 1
  debris.append({"p":path_points[section].lerp(path_points[section+1],rng.randf_range(.15,.80)),"v":Vector2(side*rng.randf_range(34,105),rng.randf_range(-135,-65)),"start":strikes[section]+rng.randf_range(.015,.085),"life":rng.randf_range(.5,.85),"size":rng.randf_range(9,23),"rot":rng.randf_range(-PI,PI),"spin":rng.randf_range(-5,5)})
 for i in range(21):
  var section=i%7
  dust.append({"p":path_points[section]+Vector2(rng.randf_range(-34,34),rng.randf_range(-9,9)),"start":strikes[section]+rng.randf_range(.04,.15),"size":rng.randf_range(22,55),"drift":Vector2(rng.randf_range(-17,17),rng.randf_range(-25,-10))})
 if "--bake" in OS.get_cmdline_user_args():
  set_process(false)
  call_deferred("bake")
 else:animate(0.0)
func _process(dt):
 clock=fmod(clock+dt,3.7)
 animate(clock)
func front_at(t):
 for i in range(7):
  if t<strikes[i+1]:return (i+clampf((t-strikes[i])/(strikes[i+1]-strikes[i]),0,1))/7.0
 return 1.0
func animate(t):
 var front=front_at(t)
 var fade=clampf((t-2.52)/.48,0,1)
 scar.visible=layer!="air" and t<LIFE
 scar.material.set_shader_parameter("reveal",lerpf(-.03,1.08,front))
 scar.material.set_shader_parameter("opacity",1-fade*.85)
 scar.material.set_shader_parameter("dissolve",lerpf(-.2,1.15,fade))
 scar.material.set_shader_parameter("pulse",exp(-pow(fmod(maxf(0,t),.5)/.085,2))*maxf(0,1-t/3)*1.2)
 queue_redraw()
func _draw():
 var t=clock
 if t>=LIFE:return
 if layer!="air":
  for p in dust:
   var age=t-p.start
   if age<0 or age>1.15:continue
   var a=sin(clampf(age/1.15,0,1)*PI)*.14
   var size=p.size*(1+age*1.4)
   var pos=p.p+p.drift*age
   draw_texture_rect(art.support_smoke,Rect2(pos-Vector2(size*.5,size*.23),Vector2(size,size*.46)),false,Color(.46,.32,.26,a))
 if layer=="floor":return
 # Unequal connected sword strokes advance along the torn seam, never as repeated sprites.
 for i in range(7):
  var age=t-strikes[i]
  if age<0 or age>.25:continue
  var u=clampf(age/(strikes[i+1]-strikes[i]),0,1)
  var end=path_points[i].lerp(path_points[i+1],1-pow(1-u,2))
  var a=pow(clampf(1-age/.25,0,1),1.3)
  draw_line(path_points[i],end,Color(.25,.005,.015,a),16-i*.8,true)
  draw_line(path_points[i],end,Color(1,.025,.045,a*.55),9-i*.5,true)
  draw_line(path_points[i],end,Color(1,.18,.09,a),3.8-i*.25,true)
  draw_line(path_points[i],end,Color(1,.86,.67,a),1.3,true)
 # Narrow, irregular red-black blades of light thrust from the wound on damage pulses.
 for i in range(1,7):
  if t<strikes[i]:continue
  var phase=fmod(t+float(i)*.022,.5)
  var strength=exp(-pow(phase/.085,2))*clampf((3-t)/.55,0,1)
  var p=path_points[i]
  var tip=p+Vector2((-1 if i%2==0 else 1)*(8+i*2),-12-i*2)*strength
  draw_colored_polygon(PackedVector2Array([p+Vector2(-3,1),tip,p+Vector2(4,2)]),Color(.55,.005,.026,strength*.9))
  draw_line(p,tip,Color(1,.16,.065,strength*.8),1.2,true)
 for p in debris:
  var age=t-p.start
  if age<0 or age>p.life:continue
  var pos=p.p+p.v*age+Vector2(0,145*age*age)
  var a=clampf((p.life-age)/.22,0,1)
  draw_set_transform(pos,p.rot+p.spin*age,Vector2.ONE)
  draw_texture_rect(art.rock,Rect2(-Vector2.ONE*p.size*.5,Vector2.ONE*p.size),false,Color(.82,.66,.61,a))
  draw_set_transform(Vector2.ZERO,0,Vector2.ONE)
func bake():
 DirAccess.make_dir_recursive_absolute("res://rift_frames")
 var times=[]
 for i in range(75):times.append(i/25.0)
 for pass_name in ["floor","air"]:
  layer=pass_name
  for frame in range(times.size()):
   clock=times[frame]
   animate(clock)
   await get_tree().process_frame
   await RenderingServer.frame_post_draw
   var err=get_viewport().get_texture().get_image().save_png("res://rift_frames/%s_%02d.png" % [pass_name,frame])
   if err!=OK:get_tree().quit(1);return
 var f=FileAccess.open("res://rift_timeline.json",FileAccess.WRITE)
 f.store_string(JSON.stringify({"frames":75,"cols":8,"life":LIFE,"times":times,"anchor":[.5,.5]},"  "))
 print("RIFT BAKE OK: connected gouged scar, irregular cuts, emissive blades; 75 frames x 2 layers")
 get_tree().quit()
