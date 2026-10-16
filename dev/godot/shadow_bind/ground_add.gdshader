shader_type canvas_item;
render_mode blend_add;
uniform sampler2D noise_tex : repeat_enable,filter_linear;
uniform float clock=0.;
uniform float strength=0.;
uniform bool light_pass=false;
void fragment(){
 vec2 p=(UV-.5)*2.;float r=length(p);float angle=atan(p.y,p.x);
 float n=texture(noise_tex,UV*2.8+vec2(clock*.06,-clock*.035)).r;
 float haze=texture(noise_tex,UV*4.1-vec2(clock*.05,clock*.08)).r;
 // A soft expanding disc, grounded in dark material; violet light follows its blurred rim.
 float grow=smoothstep(.03,.92,clock);
 float radius=mix(.14,.86,1.-pow(1.-grow,2.));
 float rr=r+(n-.5)*.035;
 float inside=1.-smoothstep(radius-.12,radius+.09,rr);
 float rim=exp(-pow((rr-radius)/.105,2.));
 float dissolve=1.-smoothstep(1.02,1.77,clock);
 float appear=smoothstep(.01,.18,clock);
 float mask=appear*dissolve*(1.-smoothstep(.92,1.,r));
 float varied=.72+.28*haze;
 if(light_pass){
  vec3 tint=mix(vec3(.10,.16,.60),vec3(.36,.10,.55),.5+.5*sin(angle*2.+clock*.7));
  COLOR=vec4(tint,(rim*.48+inside*.13)*varied*mask);
 }else{
  COLOR=vec4(.009,.011,.035,(inside*.46+rim*.08)*varied*mask);
 }
}
