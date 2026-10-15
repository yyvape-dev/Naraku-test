shader_type canvas_item;
render_mode unshaded;
uniform float age=0.;
uniform float opacity=1.;
uniform float consume=0.;
uniform float gust=0.;
uniform float seed=0.;
uniform float cooling=0.;
uniform vec2 root=vec2(.12,.94);
uniform float deform=1.;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}
void vertex(){
 float h=clamp((root.y-UV.y)/root.y,0.,1.);
 float tip=h*h;
 VERTEX.x+=(gust*70.*tip+sin(h*7.-age*16.+seed)*13.*tip)*deform;
 VERTEX.y+=(-gust*16.*tip+sin(UV.x*9.-age*12.)*4.*tip)*deform;
}
void fragment(){
 float h=clamp((root.y-UV.y)/root.y,0.,1.);
 vec2 flow=vec2(-age*(.22+.13*h),age*(.40+.35*h));
 float n=noise(UV*vec2(12.,16.)+flow*8.+seed);
 float fine=noise(UV*vec2(28.,37.)+flow*17.);
 vec2 warp=vec2(sin(UV.y*15.-age*17.+seed),sin(UV.x*14.+age*11.))*(.005+.021*h);
 vec2 uv=UV+warp;
 vec4 c=texture(TEXTURE,clamp(uv,vec2(.001),vec2(.999)));
 float bounds=step(0.,uv.x)*step(uv.x,1.)*step(0.,uv.y)*step(uv.y,1.);
 // Upper flame loses narrow necks first; advected holes consume it instead of
 // preserving a rigid ornamental silhouette until a global fade.
 float fuel=n*.60+fine*.20+(1.-h)*.32;
 float neck=exp(-pow((h-(.53+.05*sin(age*13.)))/.075,2.));
 float sever=neck*smoothstep(.12,.29,age)*.42*deform;
 float burn=1.-smoothstep(fuel-.12,fuel+.12,consume+sever);
 float lum=dot(c.rgb,vec3(.2126,.7152,.0722));
 c.rgb=mix(c.rgb,c.rgb*vec3(.82,.43,.33),cooling);
 c.rgb=mix(c.rgb,vec3(1.,.83,.65),smoothstep(.82,1.,lum)*(1.-cooling)*.06);
 // The contact crop is only a density mask: feather its cut edges.
 float contact=1.-smoothstep(.30,.61,length((UV-.5)*vec2(1.1,1.)));
 c.a*=opacity*burn*bounds*mix(contact,1.,step(.01,deform));
 COLOR=c;
}
