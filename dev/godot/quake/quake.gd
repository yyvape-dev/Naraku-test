extends Node2D
## Red-black blade -> spreading cracks -> rock upheaval -> pulsing scar -> dust collapse.
const CENTER=Vector2(200,225)
const LIFE=2.4
var clock:=0.0
var layer:="all"
var art:={}
var rocks:Array=[]
var embers:Array=[]
var powder:Array=[]
var cracks:Sprite2D
var ridge:Sprite2D
var slash:Sprite2D
var impact:Sprite2D
var trail:Sprite2D
var smoke:Sprite2D
var dust:Sprite2D
var shader=load("res://reveal.gdshader")
var floor_group:Node2D
var air_group:Node2D
var flags={"blade":true,"cracks":true,"ridge":true,"dust":true,"pulse":true,"debris":true}

func bake_times() -> Array:
 var times:Array=[]
 for i in range(16):times.append(i/40.0)
 for i in range(15):times.append(.4+i/25.0)
 for i in range(12):times.append(1.0+i/15.0)
 for i in range(15):times.append(1.8+i/25.0)
 return times

func make_sprite(name:String,parent:Node2D,mode:int,seed_value:float) -> Sprite2D:
 var sprite=Sprite2D.new()
 sprite.texture=art[name]
 sprite.position=CENTER
 var mat=ShaderMaterial.new()
 mat.shader=shader
 mat.set_shader_parameter("mode",mode)
 mat.set_shader_parameter("seed",seed_value)
 if mode==3:mat.set_shader_parameter("dust_mask",art.dust_mask)
 sprite.material=mat
 parent.add_child(sprite)
 return sprite

func _ready():
 get_viewport().transparent_bg=true
 for name in ["slash","impact","rock","dust","fissure","ridge","support_smoke","dust_mask"]:
  var img=Image.load_from_file("res://art/"+name+".png")
  if img.is_empty():
   push_error("Missing material: "+name)
   get_tree().quit(1)
   return
  if name=="dust_mask":img.resize(1024,1024,Image.INTERPOLATE_LANCZOS)
  art[name]=ImageTexture.create_from_image(img)
 var rng=RandomNumberGenerator.new()
 rng.seed=621409
 for i in range(9):
  var angle=TAU*i/9.0+rng.randf_range(-.18,.18)
  rocks.append({"v":Vector2(cos(angle)*rng.randf_range(90,160),rng.randf_range(-220,-105)),"size":rng.randf_range(12,27),"rot":rng.randf_range(-PI,PI),"spin":rng.randf_range(-5,5),"delay":rng.randf_range(.06,.13)})
 for i in range(18):
  embers.append({"a":rng.randf_range(-PI,PI),"speed":rng.randf_range(90,240),"delay":rng.randf_range(.045,.12),"life":rng.randf_range(.18,.42)})
 for i in range(24):
  powder.append({"x":rng.randf_range(-96,96),"y":rng.randf_range(-12,15),"vx":rng.randf_range(-18,18),"vy":rng.randf_range(-30,-12),"delay":rng.randf_range(.10,.35),"life":rng.randf_range(.5,.95),"r":rng.randf_range(.35,.8)})
 floor_group=Node2D.new()
 air_group=Node2D.new()
 add_child(floor_group)
 add_child(air_group)
 cracks=make_sprite("fissure",floor_group,1,3)
 smoke=make_sprite("support_smoke",floor_group,0,19)
 ridge=make_sprite("ridge",floor_group,2,7)
 dust=make_sprite("dust",floor_group,3,13)
 trail=make_sprite("slash",air_group,0,11)
 slash=make_sprite("slash",air_group,0,1)
 impact=make_sprite("impact",air_group,0,5)
 if "--bake" in OS.get_cmdline_user_args():
  set_process(false)
  call_deferred("bake")
 else:animate(0)

func configure(s:Sprite2D,width:float,alpha:float,reveal:float=1.1,dissolve:float=-.2,pulse_value:float=0.0):
 s.scale=Vector2.ONE*width/s.texture.get_width()
 s.material.set_shader_parameter("opacity",alpha)
 s.material.set_shader_parameter("reveal",reveal)
 s.material.set_shader_parameter("dissolve",dissolve)
 s.material.set_shader_parameter("pulse",pulse_value)

func _process(dt):
 clock=fmod(clock+dt,3.4)
 animate(clock)

func animate(t:float):
 floor_group.visible=layer!="air" and t<LIFE
 air_group.visible=layer!="floor" and t<LIFE
 # Cracks grow from the hit outward; most of the footprint is reached by .28s.
 var propagation=clampf((t-.005)/.26,0,1)
 var disappear=clampf((t-1.8)/.6,0,1)
 var pulse_value=0.0
 if flags.pulse:
  pulse_value=exp(-pow((t-.10)/.055,2))+exp(-pow((t-.40)/.09,2))*.9+exp(-pow((t-.82)/.13,2))*.6+exp(-pow((t-1.27)/.16,2))*.35
 cracks.visible=flags.cracks
 configure(cracks,352,1-disappear*.78,propagation*.94,lerpf(-.2,1.15,disappear),pulse_value)
 cracks.scale.y*=.62
 cracks.position=CENTER+Vector2(0,5)
 # Raised slabs remain readable through the hold, then sink and crumble.
 var rise=1-pow(1-clampf((t-.045)/.18,0,1),3)
 ridge.visible=flags.ridge and t>.045
 configure(ridge,205,(1-disappear)*clampf((t-.045)/.035,0,1),lerpf(.18,1.1,rise),lerpf(-.2,1.12,disappear),pulse_value)
 ridge.scale.y*=lerpf(.36,.76,rise)*(1-disappear*.22)
 ridge.position=CENTER+Vector2(0,15-22*rise+19*disappear)
 # Red-black sword strike is decisive and travels across the footprint.
 slash.visible=flags.blade and t<.20
 var fade=pow(clampf(1-(t-.055)/.145,0,1),1.15)
 configure(slash,290,fade,lerpf(.2,1.1,clampf(t/.065,0,1)),lerpf(-.2,1.05,clampf((t-.10)/.10,0,1)))
 slash.scale.y*=.60
 slash.position=CENTER+Vector2(0,-4)
 slash.material.set_shader_parameter("red_tone",.84)
 impact.visible=t>.025 and t<.24
 var age=maxf(0,t-.025)
 configure(impact,lerpf(65,175,1-pow(1-clampf(age/.055,0,1),3)),clampf(age/.015,0,1)*pow(clampf(1-(t-.10)/.14,0,1),1.6),1.1,lerpf(-.2,1,clampf((t-.135)/.105,0,1)))
 impact.scale.y*=.75
 impact.material.set_shader_parameter("red_tone",.80)
 trail.visible=flags.blade and t>.06 and t<.5
 configure(trail,293,pow(clampf(1-(t-.06)/.44,0,1),1.5)*.25,1.1,clampf((t-.15)/.35,0,1))
 trail.scale.y*=.61
 trail.position=CENTER+Vector2(-3,-5-t*9)
 trail.material.set_shader_parameter("red_tone",1.0)
 # CC0 smoke adds small-scale natural density; Jettelly provides the changing silhouette.
 var dust_age=maxf(0,t-.095)
 var burst=clampf(dust_age/.07,0,1)*pow(maxf(0,1-dust_age/1.3),1.3)
 var collapse=clampf((t-1.8)/.06,0,1)*pow(maxf(0,1-(t-1.8)/.55),1.6)
 dust.visible=flags.dust and t>.095
 configure(dust,lerpf(155,325,1-exp(-dust_age*4)),burst*.26+collapse*.14,1.1,lerpf(-.2,.8,clampf((dust_age-.6)/1.7,0,1)))
 dust.scale.y*=.42
 dust.position=CENTER+Vector2(0,9-dust_age*8)
 dust.material.set_shader_parameter("mask_frame",clampi(8+int(dust_age/1.5*48),8,60))
 smoke.visible=flags.dust and t>.075 and t<1.15
 configure(smoke,lerpf(140,270,1-exp(-dust_age*3)),burst*.15,1.1,clampf((dust_age-.45)/.65,0,1))
 smoke.scale.y*=.32
 smoke.position=CENTER+Vector2(0,6-dust_age*9)
 smoke.material.set_shader_parameter("tint",Color(.48,.32,.22,1))
 queue_redraw()

func _draw():
 if layer=="floor" or clock>=LIFE:return
 var t=clock
 if flags.debris:
  for rock in rocks:
   var age=t-rock.delay
   if age<0:continue
   var flight=clampf((.57-age)/.17,0,1)*clampf(age/.022,0,1)
   var settled=clampf((age-.5)/.12,0,1)*(1-clampf((t-1.55)/.45,0,1))*.68
   var alpha=maxf(flight,settled)
   if alpha<=0:continue
   var u=minf(age,.56)
   var p=CENTER+rock.v*u+Vector2(0,260*u*u)
   var size=rock.size*(1-u*.28)
   var turn=rock.rot+rock.spin*u
   draw_set_transform(p,turn,Vector2.ONE)
   draw_texture_rect(art.rock,Rect2(-size*.5,-size*.5,size,size),false,Color(.8,.38,.32,alpha))
   draw_set_transform(Vector2.ZERO)
 for grain in powder:
  var age=t-grain.delay
  if age<0 or age>grain.life:continue
  var alpha=sin(PI*age/grain.life)*.48
  var pos=CENTER+Vector2(grain.x+grain.vx*age,grain.y+grain.vy*age)
  draw_circle(pos,grain.r,Color(.73,.56,.45,alpha),true,-1,true)
 for ember in embers:
  var age=t-ember.delay
  if age<0 or age>ember.life:continue
  var alpha=pow(1-age/ember.life,1.5)
  var dir=Vector2(cos(ember.a),sin(ember.a)*.6)
  var pos=CENTER+dir*(9+ember.speed*age)
  draw_line(pos-dir*(4+6*alpha),pos,Color(1,.18,.07,.85*alpha),.9,true)

func bake():
 DirAccess.make_dir_recursive_absolute("res://frames")
 var times=bake_times()
 for pass_name in ["floor","air"]:
  layer=pass_name
  for frame in range(times.size()):
   clock=times[frame]
   animate(clock)
   await get_tree().process_frame
   await RenderingServer.frame_post_draw
   var img=get_viewport().get_texture().get_image()
   var err=img.save_png("res://frames/%s_%02d.png" % [pass_name,frame])
   if err!=OK:
    push_error("PNG export failed: %s" % err)
    get_tree().quit(1)
    return
 var meta={"times":times,"frames":times.size(),"cols":8,"life":LIFE,"flags":flags,"anchor":[.5,.5625]}
 var f=FileAccess.open("res://timeline.json",FileAccess.WRITE)
 f.store_string(JSON.stringify(meta,"  "))
 print("BAKE OK: red-black strike, spreading fissures, raised rocks, pulse and dust; %d keyframes x 2 layers" % times.size())
 get_tree().quit()
