shader_type canvas_item;
render_mode unshaded;
uniform float age=0.0;
uniform float opacity=1.0;
uniform float spread=1.2;
uniform float erosion=-.2;
uniform float cooling=0.0;
uniform float thermal=1.0;
uniform float seed=0.0;
uniform float flow=1.0;
uniform vec2 origin=vec2(.59,.80);
uniform vec4 tint:source_color=vec4(1.0);
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}
void fragment(){
 vec2 uv=UV,radial=uv-origin;
 float n=noise(uv*11.0+vec2(-age*3.7,age*4.8)+seed);
 vec2 curl=vec2(sin(uv.y*17.0-age*11.0+seed),sin(uv.x*13.0+age*9.0));
 vec2 drift=(curl*.009+normalize(radial+vec2(.0001))*n*.009)*flow;
 vec4 c=texture(TEXTURE,clamp(uv+drift,vec2(.001),vec2(.999)));
 float distance_along=length(radial*vec2(1.0,1.25));
 float leading=1.0-smoothstep(spread-.10,spread+.045,distance_along);
 float dissolve=1.0-smoothstep(n-.16,n+.16,erosion);
 float lum=dot(c.rgb,vec3(.2126,.7152,.0722));
 vec3 cooled=mix(c.rgb,vec3(lum)*vec3(1.16,.66,.42),cooling*.24*thermal);
 float hot=smoothstep(.4,.9,lum)*(1.0-cooling)*thermal;
 c.rgb=mix(cooled,vec3(1,.91,.77),hot*.08)*mix(.98,1.02,n)*tint.rgb;
 c.rgb*=mix(1.04,.87,cooling*thermal);
 c.a*=opacity*leading*dissolve*tint.a;
 COLOR=c;
}
