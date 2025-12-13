import pyglet

from utils.constants import c_for_julia_type
from game.preturbation import calculate_orbit
from mpmath import mpc

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
    vec4 value = vec4(1.0, 0.0, 0.0, 1.0);
    if (iters != u_maxIter) {{
        float t = float(iters) / float(u_maxIter) + 0.5;
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

uniform vec2 u_center;
uniform sampler2D orbit;
uniform bool usepreturbation;

layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
layout(location = 0, rgba32f) uniform image2D img_output;

{coloring_func}
{iter_calc_func}

int calculate_iters({vec2type} pos) {{
    int fractal_type = {fractal_type};
    {vec2type} z = {initial_z};
    {vec2type} c = {initial_c};

    if (fractal_type != 0) {{
        return int(fractal_iteration(z, c).x);
    }}

    int iters = 0;
    float R = {escape_radius};

    if (!usepreturbation) {{
        while (dot(z, z) < R * R && iters < u_maxIter) {{
            z = fractal_iteration(z, c);
            iters++;
        }}

        return iters;
    }}

    {vec2type} delta = c - u_center;
    {vec2type} eps = {vec2type}(0.0);
    {vec2type} zn = {vec2type}(0, 0);

    while (dot(zn, zn) < R * R && iters < u_maxIter) {{
        vec2 Z = texelFetch(orbit, ivec2(iters, 0), 0).xy;
        {vec2type} eps_sq = {vec2type}(eps.x * eps.x - eps.y * eps.y, 2.0 * eps.x * eps.y);
        {vec2type} term1 = {vec2type}(2.0 * Z.x * eps.x - 2.0 * Z.y * eps.y, 2.0 * Z.x * eps.y + 2.0 * Z.y * eps.x);
        eps = term1 + eps_sq + delta;
        zn = Z + eps;

        iters++;
    }}

    return iters;
}}

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

normal_julia_calc = """
{vec2type} fractal_iteration ({vec2type} z, {vec2type} c) {{
    int n = {multi_n};
    {floattype} xtemp = z.x * z.x - z.y * z.y;
    return {vec2type}(xtemp + c.x, 2 * z.x * z.y + c.y);
}}
"""

multi_julia_calc = """
{vec2type} fractal_iteration ({vec2type} z, {vec2type} c) {{
    {floattype} n = {floattype}({multi_n});
    {floattype} r = length(z);
    {floattype} theta = atan(z.y, z.x);
    {floattype} r_pow = pow(r, n);

    return {vec2type}(r_pow * cos(n * theta), r_pow * sin(n * theta)) + c;
}}
"""

mandelbrot_calc = """
{vec2type} fractal_iteration ({vec2type} z, {vec2type} c) {{
    return {vec2type}(
        z.x * z.x - z.y * z.y + c.x,
        2.0 * z.x * z.y + c.y
    );
}}
"""

multibrot_calc = """
{vec2type} fractal_iteration ({vec2type} z, {vec2type} c) {{
    {floattype} n = {multi_n};
    {floattype} r = length(z);
    {floattype} theta = atan(z.y, z.x);

    {floattype} r_n = pow(r, n);
    {floattype} theta_n = n * theta;

    return r_n * {vec2type}(cos(theta_n), sin(theta_n)) + c;
}} 
"""

mandelbar_calc = """
{vec2type} fractal_iteration ({vec2type} z, {vec2type} c) {{
    return {vec2type}(
        z.x * z.x - z.y * z.y + c.x,
        -2.0 * z.x * z.y + c.y
    );
}}
"""

multi_mandelbar_calc = """
{vec2type} fractal_iteration ({vec2type} z, {vec2type} c) {{
    {floattype} n = {multi_n};
    {floattype} r = length(z);
    {floattype} theta = atan(-z.y, z.x);

    {floattype} r_n = pow(r, n);
    {floattype} theta_n = n * theta;

    return r_n * {vec2type}(cos(theta_n), sin(theta_n)) + c;
}}
"""

buffalo_fractal_calc = """
{vec2type} fractal_iteration ({vec2type} z, {vec2type} c) {{
    {floattype} z_squared_real = z.x * z.x - z.y * z.y;
    {floattype} z_squared_imag = 2.0 * z.x * z.y;
    return {vec2type}(abs(z_squared_real) + c.x, abs(z_squared_imag) + c.y);
}}
"""

multi_buffalo_fractal_calc = """
{vec2type} fractal_iteration ({vec2type} z, {vec2type} c) {{
    {floattype} n = {floattype}({multi_n});
    {floattype} r = length(z);
    {floattype} theta = atan(z.y, z.x);
    {floattype} r_n = pow(r, n);
    {floattype} theta_n = n * theta;
    {floattype} zn_real = r_n * cos(theta_n);
    {floattype} zn_imag = r_n * sin(theta_n);
    return {vec2type}(abs(zn_real) + c.x, abs(zn_imag) + c.y);
}}
"""

burning_ship_calc = """
{vec2type} fractal_iteration ({vec2type} z, {vec2type} c) {{
    {floattype} xtemp = z.x * z.x - z.y * z.y + c.x;
    return {vec2type}(xtemp, abs(2.0 * z.x * z.y) + c.y);
}}
"""

phoenix_fractal_calc = """{vec2type} fractal_iteration({vec2type} unused, {vec2type} c) {{
    int iters = 0;
    {vec2type} z = {vec2type}(0.0, 0.0);
    {vec2type} z_prev = {vec2type}(0.0, 0.0);
    {floattype} p = 0.56667;
    {floattype} R = {escape_radius};

    while (dot(z, z) < R * R && iters < u_maxIter) {{
        {vec2type} z_new = {vec2type}(
            z.x * z.x - z.y * z.y + c.x - p * z_prev.x,
            2.0 * z.x * z.y + c.y - p * z_prev.y
        );

        z_prev = z;
        z = z_new;
        iters++;
    }}

    return {vec2type}(iters, 0);
}}
"""

lambda_fractal_calc = """
{vec2type} fractal_iteration ({vec2type} z, {vec2type} c) {{
    if (z.x == 0) {{
        z.x = 0.5;
    }}

    {vec2type} one_minus_z = {vec2type}(1.0, 1.0) - z;

    {vec2type} temp = {vec2type}(
        z.x * one_minus_z.x - z.y * one_minus_z.y,
        z.x * one_minus_z.y + z.y * one_minus_z.x
    );

    return {vec2type}(
        c.x * temp.x - c.y * temp.y,
        c.x * temp.y + c.y * temp.x
    );
}} 
"""


newton_fractal_calc = """{vec2type} cmul({vec2type} a, {vec2type} b) {{
    return {vec2type}(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x);
}}

{vec2type} cdiv({vec2type} a, {vec2type} b) {{
    float denom = b.x * b.x + b.y * b.y;
    return {vec2type}((a.x * b.x + a.y * b.y) / denom, (a.y * b.x - a.x * b.y) / denom);
}}

{vec2type} cpow({vec2type} z, int power) {{
    {vec2type} result = {vec2type}(1.0, 0.0);
    for (int i = 0; i < power; ++i) {{
        result = cmul(result, z);
    }}
    return result;
}}

{vec2type} func({vec2type} z) {{
    return cpow(z, 3) - {vec2type}(1.0, 0.0);
}}

{vec2type} derivative({vec2type} z) {{
    return 3.0 * cmul(z, z);
}}

{vec2type} fractal_iteration({vec2type} c, {vec2type} z) {{
    float tolerance = 0.000001;
    {vec2type} roots[3] = {vec2type}[](
        {vec2type}(1, 0),
        {vec2type}(-0.5, 0.866025404),
        {vec2type}(-0.5, -0.866025404)
    );

    for (int iters = 0; iters < u_maxIter; iters++) {{
        z -= cdiv(func(z), derivative(z));

        for (int i = 0; i < 3; i++) {{
            {vec2type} difference = z - roots[i];
            if (abs(difference.x) < tolerance && abs(difference.y) < tolerance) {{
                return {vec2type}(i, 0);
            }}
        }}
    }}

    return {vec2type}(-1, 0);
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

def create_iter_calc_shader(fractal_type, width, height, precision="single", multi_n=2, escape_radius=2, julia_type="Classic swirling", use_preturbation=False, preturbation_center=mpc(0, 0), max_iters=0):
    shader_source = iter_fractal_template

    replacements = {
        "multi_n": str(multi_n),
        "escape_radius": str(escape_radius),
        "vec2type": "dvec2" if int(multi_n) == 2 and precision == "double" else "vec2",
        "floattype": "double" if int(multi_n) == 2 and precision == "double" else "float"
    }

    replacements["coloring_func"] = fire_coloring.format_map(replacements)
    replacements["fractal_type"] = 0

    if fractal_type == "julia":
        replacements["initial_z"] = "pos"
        replacements["initial_c"] = f"{replacements['vec2type']}{c_for_julia_type[julia_type]}" # this works because if its vec2, it would be vec2(..., ...) for example.
    else:
        replacements["initial_z"] = "vec2(0.0)"
        replacements["initial_c"] = "pos"

    if fractal_type == "mandelbrot":
        if int(multi_n) == 2:
            replacements["iter_calc_func"] = mandelbrot_calc.format_map(replacements)
        else:
            replacements["iter_calc_func"] = multibrot_calc.format_map(replacements)

    elif fractal_type == "mandelbar":
        if int(multi_n) == 2:
            replacements["iter_calc_func"] = mandelbar_calc.format_map(replacements)
        else:
            replacements["iter_calc_func"] = multi_mandelbar_calc.format_map(replacements)

    elif fractal_type == "phoenix_fractal":
        replacements["iter_calc_func"] = phoenix_fractal_calc.format_map(replacements)
        replacements["fractal_type"] = 1

    elif fractal_type == "lambda_fractal":
        replacements["iter_calc_func"] = lambda_fractal_calc.format_map(replacements)

    elif fractal_type == "julia":
        if int(multi_n) == 2:
            replacements["iter_calc_func"] = normal_julia_calc.format_map(replacements)
        else:
            replacements["iter_calc_func"] = multi_julia_calc.format_map(replacements)

    elif fractal_type == "buffalo_fractal":
        replacements["coloring_func"] = fire_coloring.format_map(replacements)
        if int(multi_n) == 2:
            replacements["iter_calc_func"] = buffalo_fractal_calc.format_map(replacements)
        else:
            replacements["iter_calc_func"] = multi_buffalo_fractal_calc.format_map(replacements)

    elif fractal_type == "burning_ship":
        replacements["coloring_func"] = fire_coloring.format_map(replacements)
        replacements["iter_calc_func"] = burning_ship_calc.format_map(replacements)

    elif fractal_type == "newton_fractal":
        replacements["coloring_func"] = newton_coloring.format_map(replacements)
        replacements["iter_calc_func"] = newton_fractal_calc.format_map(replacements)
        replacements["fractal_type"] = 2

    shader_source = shader_source.format_map(replacements)

    shader_program = pyglet.graphics.shader.ComputeShaderProgram(shader_source)

    fractal_image = pyglet.image.Texture.create(width, height, internalformat=pyglet.gl.GL_RGBA32F)

    fractal_image.bind_image_texture(unit=shader_program['img_output'])

    if use_preturbation:
        orbit_image = calculate_orbit(fractal_type, preturbation_center, max_iters, multi_n, julia_type)
        orbit_image.bind_image_texture(unit=shader_program['orbit'])

    return shader_program, fractal_image
