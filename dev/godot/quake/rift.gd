extends Node2D
## Five advancing ruptures form one vertical attack. Shared quake art/shader.
const LIFE=3.0
var clock=0.0
var layer="all"
var sections=[]
var terrain=load("res://quake.gd")
func _ready():
 get_viewport().transparent_bg=true
 var spike_texture=ImageTexture.create_from_image(Image.load_from_file("res://art/rift_spikes.png"))
 for i in range(5):
  var node=Node2D.new()
  node.set_script(terrain)
  node.export_enabled=false
  add_child(node)
  node.set_process(false)
  node.ridge.texture=spike_texture
  # Origin is the near edge; each rupture advances into the distance.
  node.position=Vector2(200,350-i*70)-node.CENTER*.60
  node.scale=Vector2(.60,.60)
  for rock in node.rocks:rock.size*=1.7
  sections.append(node)
 if "--bake" in OS.get_cmdline_user_args():
  set_process(false)
  call_deferred("bake")
 else:animate(0.0)
func _process(dt):
 clock=fmod(clock+dt,3.7)
 animate(clock)
func animate(t):
 for i in range(sections.size()):
  var node=sections[i]
  var age=t-i*.105
  node.visible=age>=0 and t<LIFE
  if not node.visible:continue
  # Fast emergence, long rock hold, synchronized disappearance with the zone.
  var local_time=age if age<.4 else .4+(t-.4-i*.105)*.36
  if t>2.55:local_time=1.8+(t-2.55)/.45*.60
  node.layer=layer
  node.clock=local_time
  node.animate(local_time)
  # Keep a tall, upward-pointing ridge; the blade and cracks align vertically.
  node.slash.rotation=-PI/4
  node.trail.rotation=-PI/4
  node.cracks.rotation=-PI/4
  node.cracks.scale.x*=.70
  node.cracks.scale.y*=1.30
  node.ridge.scale.x*=1.10
  node.ridge.scale.y*=1.15
  node.ridge.position.y-=10
  var pulse=exp(-pow(fmod(maxf(t,0.0),.5)/.08,2))*maxf(0.0,1-t/3)
  node.cracks.material.set_shader_parameter("pulse",pulse*1.15)
  node.ridge.material.set_shader_parameter("pulse",pulse)
  node.queue_redraw()
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
 print("RIFT BAKE OK: 75 frames x 2 layers")
 get_tree().quit()
