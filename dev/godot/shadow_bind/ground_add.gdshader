shader_type canvas_item;
render_mode blend_add;
uniform sampler2D noise_tex : repeat_enable,filter_linear;
uniform float clock=0.;
uniform float strength=0.;
uniform bool light_pass=false;
void fragment(){
 vec2 p=(UV-.5)*2.;float r=length(p);float angle=atan(p.y,p.x);
 float n=texture(noise_tex,UV*2.8+vec2(clock*.06,-clock*.035)).r;
 float swirl=texture(noise_tex,vec2(angle/6.283+r*.17-clock*.12,r*.8-clock*.2)).r;
 float ragged=1.-smoothstep(.5+n*.25,.85+n*.15,r);
 float edge=exp(-pow((r-(.5+n*.13))/.1,2.))*smoothstep(.48,.73,swirl);
 float core=(1.-smoothstep(.08,.7,r))*(.25+.5*n);
 if(light_pass)COLOR=vec4(.22,.19,.95,edge*strength*.3);
 else COLOR=vec4(.015,.009,.035,(core+ragged*swirl*.4)*strength*.7);
}
