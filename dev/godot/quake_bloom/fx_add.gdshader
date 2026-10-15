shader_type canvas_item;
render_mode blend_add;
// Emissive sprite: diagonal reveal (strike direction), noise breakup on the way out, colour cooling.
uniform float reveal = 2.0;
uniform float dissolve = -1.0;
uniform float opacity = 1.0;
uniform float heat = 1.0;      // 1 = white-hot, 0 = deep red ember
uniform float seed = 0.0;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7))+seed*17.0)*43758.5453);}
float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);
 return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}
void fragment(){
 vec4 tex=texture(TEXTURE,UV);
 float along=(UV.x+1.0-UV.y)*0.5;
 float wipe=1.0-smoothstep(reveal-0.06,reveal+0.02,along);
 float hot=smoothstep(reveal-0.12,reveal,along)*wipe; // the leading edge burns brighter
 float n=noise(UV*18.0)*0.65+noise(UV*53.0)*0.35;
 float keep=1.0-smoothstep(n-0.08,n+0.02,dissolve);
 float edge=(1.0-smoothstep(n-0.0,n+0.10,dissolve))*smoothstep(n-0.25,n,dissolve);
 vec3 cool=tex.rgb*mix(vec3(1.0,0.32,0.18),vec3(1.0),heat);
 vec3 col=cool+vec3(1.0,0.75,0.45)*(hot*1.2+edge*0.9);
 float a=tex.a*wipe*keep*opacity;
 COLOR=vec4(col,a);
}
