
from mpmath import mp, mpc
from utils.constants import c_for_julia_type
import array, pyglet
from pyglet.gl import GL_TEXTURE_1D, GL_RG32F, GL_NEAREST

def calculate_julia_orbit(z_start, c_constant, max_iterations):
    z = z_start # position
    orbit = [z]
    
    for _ in range(max_iterations):
        z = z*z + c_constant
        orbit.append(z)
            
    return orbit

def calculate_multi_julia_orbit(z_start, c_constant, max_iterations, multi_n):
    z = z_start # position
    orbit = [z]

    for _ in range(max_iterations):
        r = abs(z)
        theta = mp.atan2(z.imag, z.real)
        r_pow = r**multi_n

        z = mpc(r_pow * mp.cos(multi_n * theta), r_pow * mp.sin(multi_n * theta)) + c_constant
        
        orbit.append(z)

    return orbit

def calculate_mandelbrot_orbit(c_val, max_iterations):
    z = mpc(0, 0)
    orbit = [z]
    
    for _ in range(max_iterations):
        z = z*z + c_val
        orbit.append(z)
            
    return orbit

def calculate_multibrot_orbit(c_val, max_iterations, multi_n):
    z = mpc(0, 0)
    orbit = [z]
    
    for _ in range(max_iterations):
        r = abs(z)
        theta = mp.atan2(z.imag, z.real)
        r_n = r ** multi_n
        theta_n = multi_n * theta

        z = mpc(r_n * mp.cos(theta_n), r_n * mp.sin(theta_n)) + c_val
        
        orbit.append(z)
            
    return orbit

def calculate_mandelbar_orbit(c_val, max_iterations):
    z = mpc(0, 0)
    orbit = [z]
    
    for _ in range(max_iterations):
        z = z.conjugate() ** 2 + c_val
        orbit.append(z)

    return orbit

def calculate_multi_mandelbar_orbit(c_val, max_iterations, multi_n):
    z = mpc(0, 0)
    orbit = [z]
    
    for _ in range(max_iterations):
        r = abs(z)
        theta = mp.atan2(-z.imag, z.real)
        r_n = r ** multi_n
        theta_n = multi_n * theta

        z = mpc(r_n * mp.cos(theta_n), r_n * mp.sin(theta_n)) + c_val
        
        orbit.append(z)
            
    return orbit

def calculate_buffalo_fractal_orbit(c_val, max_iterations):
    z = mpc(0, 0)
    orbit = [z]
    
    for _ in range(max_iterations):
        z_squared = z * z
        z_abs = mpc(abs(z_squared.real), abs(z_squared.imag))
        z = z_abs + c_val
        
        orbit.append(z)

    return orbit

def calculate_multi_buffalo_fractal_orbit(c_val, max_iterations, multi_n):
    z = mpc(0, 0)
    orbit = [z]
    
    for _ in range(max_iterations):
        r = abs(z)
        theta = mp.atan2(z.imag, z.real)
        r_n = r ** multi_n
        theta_n = multi_n * theta
        zn_real = r_n * mp.cos(theta_n)
        zn_imag = r_n * mp.sin(theta_n)

        z = mpc(abs(zn_real), abs(zn_imag)) + c_val
        
        orbit.append(z)
            
    return orbit

def calculate_burning_ship_orbit(c_val, max_iterations):
    z = mpc(0, 0)
    orbit = [z]
    
    for _ in range(max_iterations):
        x = z.real
        y = z.imag

        xtemp = x*x - y*y + c_val.real
        ytemp = abs(2 * x * y) + c_val.imag

        z = mpc(xtemp, ytemp)
        orbit.append(z)
            
    return orbit

def calculate_phoenix_fractal_orbit(c_val, max_iterations):
    z = mpc(0, 0)
    z_prev = mpc(0, 0)
    p = 0.56667
    orbit = [z]
    
    for _ in range(max_iterations):
        z_new = z.conjugate() ** 2 + c_val - p * z_prev

        z_prev = z

        z = z_new
        
        orbit.append(z)

    return orbit

def calculate_lambda_fractal_orbit(c_val, max_iterations):
    z = mpc(0.5, 0)
    orbit = [z]
    number_reverse_complex = mpc(1, 1)

    for _ in range(max_iterations):
        one_minus_z = number_reverse_complex - z
        
        temp = z * one_minus_z
        
        z = c_val * temp

        orbit.append(z)
            
    return orbit

def calculate_orbit(fractal_type, position, max_iterations, multi_n=2, julia_type="Classic swirling"):
    if fractal_type == "mandelbrot":
        if int(multi_n) == 2:
            orbit = calculate_mandelbrot_orbit(position, max_iterations)
        else:
            orbit = calculate_multibrot_orbit(position, max_iterations, multi_n)

    elif fractal_type == "mandelbar":
        if int(multi_n) == 2:
            orbit = calculate_mandelbar_orbit(position, max_iterations)
        else:
            orbit = calculate_multi_mandelbar_orbit(position, max_iterations)

    elif fractal_type == "phoenix_fractal":
        orbit = calculate_phoenix_fractal_orbit(position, max_iterations)

    elif fractal_type == "lambda_fractal":
        orbit = calculate_lambda_fractal_orbit(position, max_iterations)

    elif fractal_type == "julia":
        if int(multi_n) == 2:
            orbit = calculate_julia_orbit(position, c_for_julia_type[julia_type], max_iterations)
        else:
            orbit = calculate_multi_julia_orbit(position, c_for_julia_type[julia_type], max_iterations, multi_n)

    elif fractal_type == "buffalo_fractal":
        if int(multi_n) == 2:
            orbit = calculate_buffalo_fractal_orbit(position, max_iterations)
        else:
            orbit = calculate_multi_buffalo_fractal_orbit(position, max_iterations)

    elif fractal_type == "burning_ship":
        orbit = calculate_burning_ship_orbit(position, max_iterations)

    float_array = array.array('f')

    for c_val in orbit:
        float_array.append(float(c_val.real))
        float_array.append(float(c_val.imag))

    orbit_texture = pyglet.image.Texture.create(max_iterations, 1, internalformat=GL_RG32F, target=GL_TEXTURE_1D, min_filter=GL_NEAREST, mag_filter=GL_NEAREST)
    orbit_image_data = pyglet.image.ImageData(max_iterations, 1, "RG", float_array.tobytes())
    orbit_image_data.blit_to_texture(orbit_texture.target, orbit_texture.level, orbit_texture.anchor_x, orbit_texture.anchor_y, 0, None)

    return orbit_texture