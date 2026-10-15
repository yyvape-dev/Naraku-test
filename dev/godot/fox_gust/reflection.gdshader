shader_type canvas_item;
render_mode unshaded;
uniform float age=0.;
uniform float opacity=0.;
void fragment(){
 vec2 p=(UV-.5)*2.;
 vec2 warp=vec2(sin(UV.y*14.-age*5.),sin(UV.x*17.-age*7.))*.025;
 vec4 c=texture(TEXTURE,clamp(UV+warp+vec2(-age*.07,age*.025),vec2(.001),vec2(.999)));
 float lum=dot(c.rgb,vec3(.2126,.7152,.0722));
 float uneven=1.-smoothstep(.50+.08*sin(p.x*9.+age*4.),1.,length(p));
 COLOR=vec4(c.rgb*vec3(1.,.84,.72),opacity*uneven*smoothstep(.025,.46,lum));
}
