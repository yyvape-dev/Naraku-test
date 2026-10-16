"""RIFE v4.6 midpoint-only atlases; original 30fps atlases remain untouched.
Environment: RIFE_BIN, RIFE_MODEL, and a Vulkan driver (e.g. VK_DRIVER_FILES).
RIFE -n 192 maps frame i to source i/2; last frame is held, not looped.
"""
from pathlib import Path
from PIL import Image
import numpy as np,os,subprocess,time,json,hashlib,sys
root=Path(__file__).resolve().parent;assets=root.parents[1]/'assets';work=root/'rife-work';work.mkdir(exist_ok=True)
binary=os.environ.get('RIFE_BIN','/tmp/naraku-rife/rife-ncnn-vulkan');model=os.environ.get('RIFE_MODEL','/tmp/naraku-rife/rife-v4.6')
report={'sourceFrames':96,'originalFps':30,'playbackFrames':192,'playbackFps':60,'life':3.2,'midpoints':95,'lastFrame':'hold','cols':12,'rows':8,'model':'rife-v4.6 (20221029)','layers':{}}
for layer in ['floor','air']:
 if '--air-only' in sys.argv and layer=='floor':
  report['layers'][layer]=json.loads((root/'rife.json').read_text())['layers'][layer]
  continue
 start=time.perf_counter();source=Image.open(assets/f'vfx_blackhole_{layer}.webp').convert('RGBA');tile=source.width//12;original=[]
 for kind in ['color','alpha']:
  (work/f'{layer}-{kind}').mkdir(exist_ok=True);(work/f'{layer}-{kind}-out').mkdir(exist_ok=True)
 for i in range(96):
  im=source.crop((i%12*tile,i//12*tile,(i%12+1)*tile,(i//12+1)*tile));original.append(im)
  a=np.asarray(im,dtype=np.float32);rgb=np.rint(a[:,:,:3]*a[:,:,3:4]/255).astype('uint8')
  Image.fromarray(rgb).save(work/f'{layer}-color/{i:04}.png');im.getchannel('A').convert('RGB').save(work/f'{layer}-alpha/{i:04}.png')
 for kind in ['color','alpha']:
  output=work/f'{layer}-{kind}-out'
  # Directory mode reuses the model and Vulkan context for all 95 pairs.
  args=[binary,'-m',model,'-g','0','-j','1:1:1','-i',str(work/f'{layer}-{kind}'),'-o',str(output),'-n','192','-f','%04d.png']
  with (work/f'{layer}-{kind}.log').open('w') as log:
   result=subprocess.run(args,stdout=log,stderr=log,timeout=900)
  if result.returncode:raise RuntimeError(f'{layer}/{kind} failed, see {log.name}')
  print(layer,kind,'done',round(time.perf_counter()-start,2),flush=True)
 atlas=Image.new('RGBA',source.size)
 for i in range(96):
  if i==95:im=original[-1]
  else:
   # Filenames start at 1; 2,4,...,190 are the temporal midpoints.
   rgb=np.asarray(Image.open(work/f'{layer}-color-out/{i*2+2:04}.png').convert('RGB'),dtype=np.float32)
   alpha=np.asarray(Image.open(work/f'{layer}-alpha-out/{i*2+2:04}.png').convert('L'),dtype=np.float32)
   straight=np.clip(rgb*255/np.maximum(alpha[:,:,None],1),0,255)
   rgba=np.concatenate([straight,alpha[:,:,None]],axis=2);rgba[alpha<2]=0
   # Source padding is transparent; retain zero outermost pixels after inference.
   rgba[0,:,:]=0;rgba[-1,:,:]=0;rgba[:,0,:]=0;rgba[:,-1,:]=0
   im=Image.fromarray(np.rint(rgba).astype('uint8'))
  atlas.paste(im,(i%12*tile,i//12*tile))
 path=assets/f'vfx_blackhole_{layer}_mid.webp';atlas.save(path,quality=94,method=6)
 report['layers'][layer]={'tile':tile,'bytes':path.stat().st_size,'decodedBytes':atlas.width*atlas.height*4,'seconds':round(time.perf_counter()-start,2),'sourceSha256':hashlib.sha256((assets/f'vfx_blackhole_{layer}.webp').read_bytes()).hexdigest()}
 print(layer,'packed',report['layers'][layer],flush=True)
(root/'rife.json').write_text(json.dumps(report,indent=2)+'\n')
