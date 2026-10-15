shader_type canvas_item;
// Matte sprite (dust): soft noise erosion from the outside in, optional warm under-lighting.
uniform float dissolve = -1.0;
uniform float opacity = 1.0;
uniform vec4 tint : source_color = vec4(1.0);
uniform float seed = 0.0;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7))+seed*17.0)*43758.5453);}
float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);
 return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}
void fragment(){
 vec4 tex=texture(TEXTURE,UV);
 float r=length(UV-vec2(0.5))*1.6;
 float n=noise(UV*9.0+seed)*0.6+noise(UV*27.0)*0.4;
 float keep=1.0-smoothstep(n-0.15,n+0.05,dissolve+r*0.35);
 COLOR=vec4(tex.rgb*tint.rgb,tex.a*keep*opacity*tint.a);
}
