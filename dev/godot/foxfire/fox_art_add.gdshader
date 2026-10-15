shader_type canvas_item;
render_mode blend_add;
// One keyframe of the user's art. Two variants share this code: fox_art.gdshader (normal blend, the art's
// true colours incl. black ink) and fox_art_add.gdshader (additive copy that feeds the bloom).
// burn   : centre-out reveal with a noisy front (the next frame "blooms" into place)
// dissolve: noisy erosion from the outside in (the previous frame burns away)
// ywipe  : top-down reveal (the pillar of light falling)
uniform float burn = 2.0;
uniform float dissolve = -1.0;
uniform float ywipe = 2.0;
uniform float opacity = 1.0;
uniform float seed = 0.0;
uniform vec2 pivot = vec2(0.5, 0.736);
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7))+seed*17.0)*43758.5453);}
float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);
 return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}
void fragment(){
 vec4 tex=COLOR;   // texture × modulate (reading TEXTURE directly would drop self_modulate)
 float r=length((UV-pivot)*vec2(1.0,1.15))*1.9;
 float n=noise(UV*14.0)*0.6+noise(UV*41.0)*0.4;
 float shown=1.0-smoothstep(burn-0.06,burn+0.02,r*0.75+n*0.35);
 float gone=1.0-smoothstep(dissolve-0.05,dissolve+0.05,n*0.7+(1.0-r)*0.3);
 float wipe=1.0-smoothstep(ywipe-0.04,ywipe+0.01,UV.y);
 float a=tex.a*shown*(1.0-gone)*wipe*opacity;
 COLOR=vec4(tex.rgb,a);
}
