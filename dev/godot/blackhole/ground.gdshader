shader_type canvas_item;
uniform sampler2D noise_tex:repeat_enable,filter_linear;
uniform float clock=0.;
uniform float strength=0.;
uniform bool light_pass=false;
void fragment(){
 vec2 q=(UV-.5)*2.;float r=length(q);float a=atan(q.y,q.x);
 float n=texture(noise_tex,vec2(a/6.283+r*.5-clock*.10,r*1.8-clock*.12)).r;
 float disk=(1.-smoothstep(.35,.96,r))*strength;
 float edge=exp(-pow((r-(.48+.12*sin(a*3.+r*9.-clock)))/.15,2.));
 if(light_pass){COLOR=vec4(.47,.12,.94,disk*edge*(.07+n*.08));}
 else{COLOR=vec4(.025,.006,.05,disk*(.45+n*.20));}
}
