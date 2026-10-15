shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_opaque, shadows_disabled;
uniform sampler2D surface_art:source_color,repeat_enable,filter_linear;
uniform float age=0.0;
uniform float opacity=1.0;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}
void vertex(){
 float r=length(VERTEX.xz);
 VERTEX.y+=sin(r*13.-age*8.+sin(VERTEX.x*6.)*.5)*.025*(1.-smoothstep(.8,1.7,r));
}
void fragment(){
 vec2 p=(UV-.5)*2.;float r=length(p);
 float n=noise(p*3.+vec2(-age*.33,age*.21));
 vec2 warp=vec2(sin(p.y*9.-age*2.),sin(p.x*7.+age*1.6))*.018;
 vec4 a=texture(surface_art,UV+warp+vec2(age*.025,-age*.017));
 vec4 b=texture(surface_art,UV*1.37+warp*.6+vec2(-age*.019,age*.012));
 vec3 color=mix(a.rgb,b.rgb,.23)*vec3(1.17,1.05,1.08);
 float lum=dot(color,vec3(.2126,.7152,.0722));
 float rim=1.-smoothstep(.72+n*.025,.99,r);
 ALBEDO=color;
 ALPHA=rim*opacity*(.20+smoothstep(.025,.4,lum)*.65);
}
