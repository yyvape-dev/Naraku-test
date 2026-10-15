shader_type canvas_item;
// 墨絵の滲み：noisy ink blot that bleeds outward, darker at its rim (like ink soaking into paper)
uniform float spread = 0.0;      // 0..1 radius of the blot
uniform float opacity = 1.0;
uniform vec4 ink : source_color = vec4(0.05, 0.015, 0.07, 1.0);
uniform float seed = 0.0;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7))+seed*13.0)*43758.5453);}
float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);
 return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}
float fbm(vec2 p){float v=0.0,a=0.55;for(int i=0;i<4;i++){v+=a*noise(p);p*=2.1;a*=0.5;}return v;}
void fragment(){
 vec2 q=UV-0.5;
 float ang=atan(q.y,q.x);
 float r=length(q)*2.0;
 float edge=spread*(0.78+0.35*fbm(vec2(ang*2.2+seed,spread*1.5)));          // ragged, tendril-like edge
 float inside=1.0-smoothstep(edge-0.03,edge+0.01,r+0.12*fbm(UV*9.0));
 float rim=smoothstep(edge-0.16,edge-0.02,r);                                  // ink pools at the rim
 float grain=0.75+0.25*fbm(UV*22.0);
 float a=inside*(0.45+0.55*rim)*grain*opacity;
 COLOR=vec4(ink.rgb,a*ink.a);
}
