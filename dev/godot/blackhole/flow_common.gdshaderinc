uniform sampler2D noise_tex : repeat_enable,filter_linear;
uniform float clock=0.;
uniform float opacity=1.;
uniform float reveal=1.;
uniform float erode=0.;
uniform bool light_pass=false;
void fragment(){
 vec2 q=UV-.5;float r=length(q);
 float n=texture(noise_tex,q*3.+vec2(clock*.15,-clock*.19)).r;
 // Differential angular advection: core and outer arms travel at different speeds.
 float ang=clock*(.22+.60*exp(-r*7.))+sin(r*27.-clock*4.)*.025+n*.04;
 float ca=cos(ang),sa=sin(ang);
 vec2 uv=mat2(vec2(ca,sa),vec2(-sa,ca))*q+.5;
 uv+=normalize(q+vec2(.0001))*sin(r*35.-clock*5.)*.004;
 vec4 tex=texture(TEXTURE,clamp(uv,vec2(.001),vec2(.999)));
 float grain=texture(noise_tex,UV*4.+vec2(clock*.09,-clock*.12)).r;
 float a=tex.a*opacity*(1.-smoothstep(.42,.49,r));
 a*=1.-smoothstep(1.-erode-.08,1.-erode+.08,grain);
 if(light_pass){
  float hot=smoothstep(.64,.96,max(tex.r,max(tex.g,tex.b)));
  COLOR=vec4(tex.rgb*vec3(1.0,.78,1.1)*7.0,a*hot*.16*(1.+.22*exp(-pow((clock-2.4)/.09,2.))));
 }else{COLOR=vec4(tex.rgb,a);}
}
