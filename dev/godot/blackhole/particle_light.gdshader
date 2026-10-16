shader_type canvas_item;
render_mode blend_add;
void fragment(){
 // Preserve texture and ParticleProcessMaterial color ramp; only bright cores exceed HDR threshold.
 vec4 tex=COLOR;
 COLOR=vec4(tex.rgb*2.2,tex.a);
}
