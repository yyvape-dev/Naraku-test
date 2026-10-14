shader_type canvas_item;
uniform int mode = 0;
uniform vec4 tint = vec4(1.0);
uniform float reveal = 1.0;
uniform float dissolve = -0.2;
uniform float opacity = 1.0;
uniform float pulse = 0.0;
uniform float seed = 0.0;
uniform float red_tone = 0.0;
uniform int mask_frame = 0;
uniform sampler2D dust_mask : filter_linear, repeat_disable;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7))+seed)*43758.5453);}
float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}
void fragment(){
 vec4 tex=texture(TEXTURE,UV);
 float progress=(UV.x+1.0-UV.y)*0.5;
 if(mode==1){progress=length((UV-vec2(.5))*vec2(1.0,1.0))*1.43;}
 if(mode==2){progress=1.0-UV.y;}
 float wipe=1.0-smoothstep(reveal-0.05,reveal+0.05,progress);
 float n=noise(UV*21.0)*0.7+noise(UV*61.0)*0.3;
 float breakup=1.0-smoothstep(n-0.07,n+0.07,dissolve);
 float mask=1.0;
 if(mode==3){
  vec2 tile=vec2(float(mask_frame%8),float(mask_frame/8));
  vec2 uv=(clamp(UV,vec2(.01),vec2(.99))+tile)/8.0;
  vec2 step_uv=vec2(.0008);
  mask=texture(dust_mask,uv).a*.4;
  mask+=texture(dust_mask,uv+vec2(step_uv.x,0)).a*.15;
  mask+=texture(dust_mask,uv-vec2(step_uv.x,0)).a*.15;
  mask+=texture(dust_mask,uv+vec2(0,step_uv.y)).a*.15;
  mask+=texture(dust_mask,uv-vec2(0,step_uv.y)).a*.15;
 }
 vec3 color=tex.rgb;
 float warm=max(0.0,color.r-color.b*.85);
 float hot=smoothstep(.87,1.0,min(color.r,color.g));
 color=mix(color,mix(vec3(color.r*.85,color.g*.16,color.b*.16),color,hot),red_tone);
 if(mode==1||mode==2){
  float crack=max(0.0,tex.r-max(tex.g,tex.b)*1.12);
  float front=exp(-pow((progress-reveal)/.055,2.0));
  float fissure_mask=smoothstep(.08,.35,crack);
  color*=mix(1.0,.28+clamp(pulse,0.0,1.2)*.90,fissure_mask);
  color+=vec3(1.0,.055,.015)*crack*(pulse*.50+front*.75);
 }
 COLOR=vec4(color,tex.a*wipe*breakup*opacity*mask)*tint;
}
