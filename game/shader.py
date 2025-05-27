import pyglet
from utils.constants import c_for_julia_type

newton_coloring = """vec4 getColor(int color_number) {{
    vec4 value = vec4(0.0, 0.0, 0.0, 1.0);
    if (color_number == 0) {{
        value.r = 1.0;
    }}
    else if (color_number == 1) {{
        value.g = 1.0;
    }}
    else if (color_number == 2) {{
        value.b = 1.0;
    }}

    return value;
}}
"""

polynomial_coloring = """vec4 getColor(int iters) {{
    vec4 value = vec4(0.0, 0.0, 0.0, 1.0);
    if (iters != u_maxIter) {{
        float t = float(iters) / float(u_maxIter);
        value.r = 9.0 * (1.0 - t) * t * t * t;
        value.g = 15.0 * (1.0 - t) * (1.0 - t) * t * t;
        value.b = 8.5 * (1.0 - t) * (1.0 - t) * (1.0 - t) * t;
    }}
    return value;
}}
"""

fire_coloring = """vec4 getColor(int iters) {{
    vec4 value = vec4(0.0, 0.0, 0.0, 1.0);
    if (iters != u_maxIter) {{
        float t = float(iters) / float(u_maxIter);
        value.r = 3.0 * t;
        value.g = 2.0 * t * t;
        value.b = t * t * t;
    }}
    return value;
}}
"""

iter_fractal_template = """#version 430 core
uniform int u_maxIter;
uniform vec2 u_resolution;
uniform vec2 u_real_range;
uniform vec2 u_imag_range;
layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
layout(location = 0, rgba32f) uniform image2D img_output;

{coloring_func}
{iter_calc_func}

{vec2type} map_pixel({floattype} x, {floattype} y, {vec2type} resolution, {vec2type} real_range, {vec2type} imag_range) {{
    {floattype} real = real_range.x + (x / resolution.x) * (real_range.y - real_range.x);
    {floattype} imag = imag_range.x + (y / resolution.y) * (imag_range.y - imag_range.x);
    return {vec2type}(real, imag);
}}

void main() {{
    ivec2 texel_coord = ivec2(gl_GlobalInvocationID.xy);
    {vec2type} pos = map_pixel({floattype}(texel_coord.x), {floattype}(texel_coord.y), u_resolution, u_real_range, u_imag_range);
    int iters = calculate_iters(pos);
    vec4 value = getColor(iters);
    imageStore(img_output, texel_coord, value);
}}
"""

sierpinsky_carpet_compute_source = """#version 430 core
uniform int u_depth;
uniform int u_zoom;
uniform vec2 u_center;
layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
layout(location = 0, rgba32f) uniform image2D img_output;
void main() {{
    {vec2type} centered = {vec2type}(gl_GlobalInvocationID.xy) - u_center;
    {vec2type} zoomed = centered / u_zoom;
    {vec2type} final_coord = zoomed + u_center;
    ivec2 coord = ivec2(final_coord);
    bool isHole = false;
    for (int i = 0; i < u_depth; ++i) {{
        if (coord.x % 3 == 1 && coord.y % 3 == 1) {{
            isHole = true;
            break;
        }}
        coord /= 3;
    }}
    vec4 color = isHole ? vec4(0, 0, 0, 1) : vec4(1, 1, 1, 1);
    imageStore(img_output, ivec2(gl_GlobalInvocationID.xy), color);
}}
"""

normal_julia_calc = """int calculate_iters({vec2type} z) {{
    int iters = 0;
    float R = {escape_radius};
    int n = {multi_n};
    {vec2type} c = {vec2type}{julia_c};
    while (dot(z, z) < R * R && iters < u_maxIter){{
        {floattype} xtemp = z.x * z.x - z.y * z.y;
        z.y = 2 * z.x * z.y + c.y;
        z.x = xtemp + c.x;
        iters++;
    }}
    return iters;
}}
"""

multi_julia_calc = """int calculate_iters(float z) {{
    int iters = 0;
    float R = {escape_radius};
    float n = float({multi_n});
    float c = float({julia_c});

    while (dot(z, z) < R * R && iters < u_maxIter) {{
        float r = length(z);
        float theta = atan(z.y, z.x);
        float r_pow = pow(r, n);

        z = vec2(r_pow * cos(n * theta), r_pow * sin(n * theta)) + c;

        iters++;
    }}

    return iters;
}}
"""

mandelbrot_calc = """int calculate_iters({vec2type} c) {{
    int iters = 0;
    {vec2type} z = {vec2type}(0.0, 0.0);
    float R = {escape_radius};

    while (dot(z, z) < R * R && iters < u_maxIter) {{
        z = {vec2type}(
            z.x * z.x - z.y * z.y + c.x,
            2.0 * z.x * z.y + c.y
        );

        iters++;
    }}

    return iters;
}}
"""

multibrot_calc = """int calculate_iters(vec2 c) {{
    int iters = 0;
    vec2 z = vec2(0.0);
    float n = {multi_n};
    float R = {escape_radius};

    while (dot(z, z) < R * R && iters < u_maxIter) {{
        float r = length(z);
        float theta = atan(z.y, z.x);

        float r_n = pow(r, n);
        float theta_n = n * theta;

        z = r_n * vec2(cos(theta_n), sin(theta_n)) + c;

        iters++;
    }}

    return iters;
}}
"""

burning_ship_calc = """int calculate_iters({vec2type} c) {{
    int iters = 0;
    {vec2type} z = {vec2type}(0.0, 0.0);
    float R = {escape_radius};

    while (dot(z, z) < R * R && iters < u_maxIter) {{
        {floattype} xtemp = z.x * z.x - z.y * z.y + c.x;
        z.y = abs(2.0 * z.x * z.y) + c.y;
        z.x = xtemp;

        iters++;
    }}

    return iters;
}}
"""

newton_fractal_calc = """vec2 cmul(vec2 a, vec2 b) {{
    return vec2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x);
}}

vec2 cdiv(vec2 a, vec2 b) {{
    float denom = b.x * b.x + b.y * b.y;
    return vec2((a.x * b.x + a.y * b.y) / denom, (a.y * b.x - a.x * b.y) / denom);
}}

vec2 cpow(vec2 z, int power) {{
    vec2 result = vec2(1.0, 0.0);
    for (int i = 0; i < power; ++i) {{
        result = cmul(result, z);
    }}
    return result;
}}

vec2 func(vec2 z) {{
    return cpow(z, 3) - vec2(1.0, 0.0);
}}

vec2 derivative(vec2 z) {{
    return 3.0 * cmul(z, z);
}}

int calculate_iters(vec2 z) {{
    float tolerance = 0.000001;
    vec2 roots[3] = vec2[](
        vec2(1, 0),
        vec2(-0.5, 0.866025404),
        vec2(-0.5, -0.866025404)
    );

    for (int iters = 0; iters < u_maxIter; iters++) {{
        z -= cdiv(func(z), derivative(z));

        for (int i = 0; i < 3; i++) {{
            vec2 difference = z - roots[i];
            if (abs(difference.x) < tolerance && abs(difference.y) < tolerance) {{
                return i;
            }}
        }}
    }}

    return -1;
}}
"""

def create_sierpinsky_carpet_shader(width, height, precision="single"):
    shader_source = sierpinsky_carpet_compute_source

    replacements = {
        "vec2type": "dvec2" if precision == "double" else "vec2",
        "floattype": "double" if precision == "double" else "float"
    }

    shader_source = shader_source.format_map(replacements)

    shader_program = pyglet.graphics.shader.ComputeShaderProgram(shader_source)

    sierpinsky_carpet_image = pyglet.image.Texture.create(width, height, internalformat=pyglet.gl.GL_RGBA32F)

    uniform_location = shader_program['img_output']
    sierpinsky_carpet_image.bind_image_texture(unit=uniform_location)

    return shader_program, sierpinsky_carpet_image

def create_iter_calc_shader(fractal_type, width, height, precision="single", multi_n=2, escape_radius=2, julia_type="Classic swirling"):
    shader_source = iter_fractal_template

    replacements = {
        "multi_n": str(multi_n),
        "julia_c": str(c_for_julia_type[julia_type]),
        "escape_radius": str(escape_radius),
        "vec2type": "dvec2" if int(multi_n) == 2 and precision == "double" else "vec2",
        "floattype": "double" if int(multi_n) == 2 and precision == "double" else "float"
    }

    replacements["coloring_func"] = polynomial_coloring.format_map(replacements)

    if fractal_type == "mandelbrot":
        if int(multi_n) == 2:
            replacements["iter_calc_func"] = mandelbrot_calc.format_map(replacements)
        else:
            replacements["iter_calc_func"] = multibrot_calc.format_map(replacements)

    elif fractal_type == "julia":
        if int(multi_n) == 2:
            replacements["iter_calc_func"] = normal_julia_calc.format_map(replacements)
        else:
            replacements["iter_calc_func"] = multi_julia_calc.format_map(replacements)

    elif fractal_type == "burning_ship":
        replacements["coloring_func"] = fire_coloring.format_map(replacements)
        replacements["iter_calc_func"] = burning_ship_calc.format_map(replacements)

    elif fractal_type == "newton_fractal":
        replacements["coloring_func"] = newton_coloring.format_map(replacements)
        replacements["iter_calc_func"] = newton_fractal_calc.format_map(replacements)

    shader_source = shader_source.format_map(replacements)

    shader_program = pyglet.graphics.shader.ComputeShaderProgram(shader_source)

    julia_image = pyglet.image.Texture.create(width, height, internalformat=pyglet.gl.GL_RGBA32F)

    uniform_location = shader_program['img_output']
    julia_image.bind_image_texture(unit=uniform_location)

    return shader_program, julia_image
