shader_type canvas_item;
uniform sampler2D noise_tex : repeat_enable,filter_linear;
uniform float clock = 0.0;
uniform float opacity = 1.0;
uniform float reveal = 1.0;
uniform float erode = 0.0;
uniform bool light_pass = false;
void fragment(){
 vec2 q=UV-vec2(.5,.8134);
 // A travelling twist follows the ribbons upward; the contact point stays put.
 float h=clamp(-q.y,0.,.8);
 float wave=sin(h*17.-clock*9.)*.018*h;
 vec2 p=UV*vec2(2.8,3.1)+vec2(clock*.11,-clock*.45);
 vec2 n=vec2(texture(noise_tex,p).r,texture(noise_tex,p+vec2(.41,.23)).r)-.5;
 vec2 uv=UV+vec2(wave,n.y*.007)*smoothstep(.01,.22,h)+n*.012*smoothstep(.05,.3,length(q));
 vec4 tex=texture(TEXTURE,clamp(uv,vec2(.001),vec2(.999)));
 float grain=texture(noise_tex,UV*3.7+vec2(clock*.045,-clock*.13)).r;
 float rising=smoothstep(1.-reveal-.06,1.-reveal+.06,UV.y+grain*.1);
 float broken=1.-smoothstep(1.-erode-.1,1.-erode+.1,grain*.65+(1.-UV.y)*.35);
 float a=tex.a*opacity*rising*broken;
 if(light_pass){
  float hot=smoothstep(.55,.95,max(tex.r,max(tex.g,tex.b)));
  float stream=smoothstep(.58,.78,texture(noise_tex,vec2(UV.x*5.+clock*.3,UV.y*2.-clock*.8)).r);
  float pulse=exp(-pow((clock-.32)/.10,2.))+.65*exp(-pow((clock-.78)/.14,2.));
  COLOR=vec4(tex.rgb*8.0,a*hot*(.12+.04*stream)*(1.+.16*pulse));
 }else{
  // Preserve blue, violet and the nearly black material of the supplied art.
  COLOR=vec4(tex.rgb,a);
 }
}
