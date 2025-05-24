import pyglet
mandelbrot_compute_source = """#version 430 core

uniform int u_maxIter;
uniform vec2 u_resolution;
uniform vec2 u_real_range;
uniform vec2 u_imag_range;

layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
layout(location = 0, rgba32f) uniform image2D img_output;

int mandelbrot({vec2type} c, int maxIter) {
    {vec2type} z = {vec2type}(0.0, 0.0);
    for (int n = 0; n < maxIter; n++) {
        if (dot(z, z) > 4.0) {
            return n;
        }
        z = {vec2type}(
            z.x * z.x - z.y * z.y + c.x,
            2.0 * z.x * z.y + c.y
        );
    }
    return maxIter;
}

{vec2type} map_pixel({floattype} x, {floattype} y, {vec2type} resolution, {vec2type} real_range, {vec2type} imag_range) {
    {floattype} real = real_range.x + (x / resolution.x) * (real_range.y - real_range.x);
    {floattype} imag = imag_range.x + (y / resolution.y) * (imag_range.y - imag_range.x);
    return {vec2type}(real, imag);
}

void main() {
    ivec2 texel_coord = ivec2(gl_GlobalInvocationID.xy);
    {vec2type} c = map_pixel({floattype}(texel_coord.x), {floattype}(texel_coord.y), u_resolution, u_real_range, u_imag_range);
    int iters = mandelbrot(c, u_maxIter);

    vec4 value = vec4(0.0, 0.0, 0.0, 1.0);

    if (iters != u_maxIter) {
        float t = float(iters) / float(u_maxIter);
        float pow_amount = 0.7;
        t = pow(t, pow_amount);

        value.r = 9.0 * (1.0 - t) * t * t * t;
        value.g = 15.0 * (1.0 - t) * (1.0 - t) * t * t;
        value.b = 8.5 * (1.0 - t) * (1.0 - t) * (1.0 - t) * t;
    }

    imageStore(img_output, texel_coord, value);
}
"""

sierpinsky_carpet_compute_source = """#version 430 core

uniform int u_depth;
uniform int u_zoom;
layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
layout(location = 0, rgba32f) uniform image2D img_output;

void main() {
    ivec2 coord = ivec2(gl_GlobalInvocationID.xy);
    bool isHole = false;

    for (int i = 0; i < u_depth; ++i) {
        if (coord.x % 3 == 1 && coord.y % 3 == 1) {
            isHole = true;
            break;
        }
        coord /= 3;
    }

    vec4 color = isHole ? vec4(0, 0, 0, 1) : vec4(1, 1, 1, 1);
    imageStore(img_output, ivec2(gl_GlobalInvocationID.xy), color);
}

"""

def create_sierpinsky_carpet_shader(width, height, precision="single"):
    shader_source = sierpinsky_carpet_compute_source

    shader_program = pyglet.graphics.shader.ComputeShaderProgram(shader_source)

    sierpinsky_carpet_image = pyglet.image.Texture.create(width, height, internalformat=pyglet.gl.GL_RGBA32F)

    uniform_location = shader_program['img_output']
    sierpinsky_carpet_image.bind_image_texture(unit=uniform_location)

    return shader_program, sierpinsky_carpet_image

def create_mandelbrot_shader(width, height, precision="single"):
    shader_source = mandelbrot_compute_source

    if precision == "single":
        shader_source = shader_source.replace("{vec2type}", "vec2").replace("{floattype}", "float")
    elif precision == "double":
        shader_source = shader_source.replace("{vec2type}", "dvec2").replace("{floattype}", "double")
    else:
        raise TypeError("Invalid Precision")

    shader_program = pyglet.graphics.shader.ComputeShaderProgram(shader_source)

    mandelbrot_image = pyglet.image.Texture.create(width, height, internalformat=pyglet.gl.GL_RGBA32F)

    uniform_location = shader_program['img_output']
    mandelbrot_image.bind_image_texture(unit=uniform_location)

    return shader_program, mandelbrot_image
