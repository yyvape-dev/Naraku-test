shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_opaque, shadows_disabled;
uniform sampler2D art:source_color,filter_linear;
uniform float opening=0.0;
uniform float growth=1.0;
uniform float petal_length=1.8;
uniform float width=.55;
uniform float angle=0.0;
uniform float twist=.15;
uniform float age=0.0;
uniform float opacity=1.0;
uniform float erosion=-.2;
uniform float reflection=0.0;
uniform float detached=0.0;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}
void vertex(){
 if(detached<.5){
  float v=UV.y,u=UV.x*2.0-1.0;
  float pitch=(.10+opening*1.12)*v;
  float d=petal_length*v*growth;
  float r=.13+d*sin(pitch);
  float y=d*cos(pitch)+twist*pow(v,4.)*.35;
  float a=angle+twist*v*.35;
  float lateral=u*width*(.35+.65*sin(v*3.141593));
  VERTEX=vec3(cos(a)*r-sin(a)*lateral,y,sin(a)*r+cos(a)*lateral);
  NORMAL=normalize(vec3(-cos(pitch)*cos(a),sin(pitch),-cos(pitch)*sin(a)));
  if(reflection>.5){VERTEX.y=-VERTEX.y*.20-.025;VERTEX.x+=sin(v*17.+age*7.)*.04;}
 }
}
void fragment(){
 vec2 uv=vec2(UV.x,1.-UV.y);
 float n=noise(uv*10.+vec2(-age*2.,age*4.)+angle);
 vec2 flow=vec2(sin(uv.y*18.-age*8.),sin(uv.x*12.+age*6.))*.003;
 vec4 c=texture(art,clamp(uv+flow,vec2(.001),vec2(.999)));
 float fade=1.-smoothstep(n-.18,n+.18,erosion);
 float facing=mix(.86,1.15,abs(dot(normalize(NORMAL),normalize(vec3(.3,.8,.5)))));
 vec3 color=c.rgb*facing*mix(1.22,.94,smoothstep(.25,.85,age));
 color=mix(color,vec3(dot(color,vec3(.2126,.7152,.0722)))*vec3(1.22,.37,.39),clamp(age-.35,0.,.5)*.28);
 if(reflection>.5)color*=vec3(.80,.30,.35);
 ALBEDO=color;ALPHA=c.a*opacity*fade;
}
