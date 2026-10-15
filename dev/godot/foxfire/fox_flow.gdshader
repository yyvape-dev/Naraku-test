shader_type canvas_item;
// v2: one keyframe of the user's art, made to MOVE. A seamless noise texture scrolls upward and warps the
// art's UVs (flames lick upward, petals ripple); the heart stays steady, the outer petals move most.
// burn = centre-out reveal, dissolve = outside-in erosion, ywipe = top-down reveal (falling pillar).
uniform sampler2D flow_tex : repeat_enable, filter_linear;
uniform float flow_t = 0.0;        // seconds; drives the scroll
uniform float flow_amt = 0.022;    // UV warp strength at the rim
uniform float burn = 2.0;
uniform float dissolve = -1.0;
uniform float ywipe = 2.0;
uniform float gain = 1.0;          // brightness (modulate is not used: we sample TEXTURE ourselves)
uniform float opacity = 1.0;
uniform float sat = 1.2;           // saturation lift toward the purple / pink motif
uniform vec2 pivot = vec2(0.5, 0.736);
void fragment(){
 float r=length((UV-pivot)*vec2(1.0,1.15))*1.9;
 float rim=smoothstep(0.08,0.75,r);
 // the noise is greyscale: sample it twice at offsets for independent x / y warp
 vec2 p1=UV*vec2(1.6,1.1)+vec2(0.0, flow_t*0.55), p2=UV*vec2(3.1,2.4)+vec2(flow_t*0.12, flow_t*1.1);
 vec2 w=vec2(texture(flow_tex,p1).r, texture(flow_tex,p1+vec2(0.37,0.71)).r)-0.5;
 vec2 w2=vec2(texture(flow_tex,p2).r, texture(flow_tex,p2+vec2(0.53,0.19)).r)-0.5;
 vec2 uv=UV+(w*0.75+w2*0.35)*flow_amt*rim+vec2(0.0, flow_amt*0.35*rim);
 vec4 tex=texture(TEXTURE, uv);
 float g0=dot(tex.rgb,vec3(0.3,0.55,0.15));
 tex.rgb=clamp(mix(vec3(g0),tex.rgb,sat),0.0,1.0);
 float n=texture(flow_tex, UV*2.3).b;
 float shown=1.0-smoothstep(burn-0.06,burn+0.02,r*0.75+n*0.35);
 float gone=1.0-smoothstep(dissolve-0.05,dissolve+0.05,n*0.7+(1.0-r)*0.3);
 float wipe=1.0-smoothstep(ywipe-0.04,ywipe+0.01,UV.y);
 float a=tex.a*shown*(1.0-gone)*wipe*opacity;
#ifdef LIGHT_PASS
 // only the hottest cores feed the bloom (keeps the purple and pink saturated), plus light flowing tip-ward
 float l=dot(tex.rgb,vec3(0.3,0.55,0.15));
 float hot=smoothstep(0.55,0.92,l);
 float stream=smoothstep(0.62,0.9,texture(flow_tex, UV*vec2(2.0,1.3)+vec2(0.0, flow_t*1.6)).g)*rim;
 COLOR=vec4(tex.rgb*gain, a*(hot+stream*0.6*smoothstep(0.3,0.7,l)));
#else
 COLOR=vec4(tex.rgb*gain, a);
#endif
}
