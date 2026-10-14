shader_type canvas_item;
uniform float reveal = 1.0;
uniform float dissolve = 0.0;
uniform float opacity = 1.0;
uniform float seed = 0.0;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7))+seed)*43758.5453);}
float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}
void fragment(){
 vec4 tex=texture(TEXTURE,UV);
 float along=(UV.x+1.0-UV.y)*0.5;
 float wipe=1.0-smoothstep(reveal-0.045,reveal+0.045,along);
 float n=noise(UV*25.0)*0.7+noise(UV*67.0)*0.3;
 float breakup=1.0-smoothstep(n-0.07,n+0.07,dissolve);
 COLOR=vec4(tex.rgb,tex.a*wipe*breakup*opacity);
}
