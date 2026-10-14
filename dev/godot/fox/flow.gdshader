shader_type canvas_item;
render_mode unshaded;
uniform float age = 0.0;
uniform float opacity = 1.0;
uniform float reveal = 1.0;
uniform float erosion = 0.0;
uniform float flow = 1.0;
uniform float seed = 0.0;
uniform vec4 tint : source_color = vec4(1.0);
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}
void fragment(){
 vec2 uv=UV;
 float n=noise(uv*13.0+vec2(-age*8.0,age*5.0)+seed);
 vec2 drift=vec2(sin(uv.y*21.0-age*18.0+seed),sin(uv.x*17.0+age*13.0))*0.018*flow;
 vec4 c=texture(TEXTURE,clamp(uv+drift,vec2(.001),vec2(.999)));
 float distance_along=(uv.x+1.0-uv.y)*0.5;
 float leading=1.0-smoothstep(reveal-.12,reveal+.07,distance_along);
 float dissolve=1.0-smoothstep(n-.12,n+.12,erosion);
 // Local advection only: no global sine brightness pulse.
 c.rgb*=mix(.88,1.18,n)*tint.rgb;
 c.a*=opacity*leading*dissolve*tint.a;
 COLOR=c;
}
