import arcade.color
from arcade.types import Color
from arcade.gui.widgets.buttons import UITextureButtonStyle, UIFlatButtonStyle
from arcade.gui.widgets.slider import UISliderStyle

menu_background_color = (30, 30, 47)
log_dir = 'logs'
discord_presence_id = 1365949409254441000

initial_real_min = -2.0
initial_real_max = 1.0
initial_imag_min = -1.0
initial_imag_max = 1.0

button_style = {'normal': UITextureButtonStyle(font_name="Protest Strike", font_color=arcade.color.BLACK), 'hover': UITextureButtonStyle(font_name="Protest Strike", font_color=arcade.color.BLACK),
                'press': UITextureButtonStyle(font_name="Protest Strike", font_color=arcade.color.BLACK), 'disabled': UITextureButtonStyle(font_name="Protest Strike", font_color=arcade.color.BLACK)}
big_button_style = {'normal': UITextureButtonStyle(font_name="Protest Strike", font_color=arcade.color.BLACK, font_size=26), 'hover': UITextureButtonStyle(font_name="Protest Strike", font_color=arcade.color.BLACK, font_size=26),
                'press': UITextureButtonStyle(font_name="Protest Strike", font_color=arcade.color.BLACK, font_size=26), 'disabled': UITextureButtonStyle(font_name="Protest Strike", font_color=arcade.color.BLACK, font_size=26)}

dropdown_style = {'normal': UIFlatButtonStyle(font_name="Protest Strike", font_color=arcade.color.BLACK, bg=Color(128, 128, 128)), 'hover': UIFlatButtonStyle(font_name="Protest Strike", font_color=arcade.color.BLACK, bg=Color(49, 154, 54)),
                  'press': UIFlatButtonStyle(font_name="Protest Strike", font_color=arcade.color.BLACK, bg=Color(128, 128, 128)), 'disabled': UIFlatButtonStyle(font_name="Protest Strike", font_color=arcade.color.BLACK, bg=Color(128, 128, 128))}

slider_default_style = UISliderStyle(bg=Color(128, 128, 128), unfilled_track=Color(128, 128, 128), filled_track=Color(49, 154, 54))
slider_hover_style = UISliderStyle(bg=Color(49, 154, 54), unfilled_track=Color(128, 128, 128), filled_track=Color(49, 154, 54))

slider_style = {'normal': slider_default_style, 'hover': slider_hover_style, 'press': slider_hover_style, 'disabled': slider_default_style}

settings = {
    "Mandelbrot": {
        "Float Precision": {"type": "option", "options": ["Single", "Double"], "config_key": "mandelbrot_precision", "default": "Single"},
        "Zoom Increase Per Click": {"type": "slider", "min": 2, "max": 100, "config_key": "mandelbrot_zoom_increase", "default": 2},
        "Max Iterations": {"type": "slider", "min": 100, "max": 10000, "config_key": "mandelbrot_max_iter", "default": 200}
    },
    "Sierpinsky Carpet": {
        "Zoom Increase Per Click": {"type": "slider", "min": 2, "max": 100, "config_key": "sierpinsky_zoom_increase", "default": 2},
        "Depth": {"type": "slider", "min": 2, "max": 10000, "config_key": "sierpinsky_depth", "default": 10}
    },
    "Graphics": {
        "Window Mode": {"type": "option", "options": ["Windowed", "Fullscreen", "Borderless"], "config_key": "window_mode", "default": "Windowed"},
        "Resolution": {"type": "option", "options": ["1366x768", "1440x900", "1600x900", "1920x1080", "2560x1440", "3840x2160"], "config_key": "resolution"},
        "Anti-Aliasing": {"type": "option", "options": ["None", "2x MSAA", "4x MSAA", "8x MSAA", "16x MSAA"], "config_key": "anti_aliasing", "default": "4x MSAA"},
        "VSync": {"type": "bool", "config_key": "vsync", "default": True},
        "FPS Limit": {"type": "slider", "min": 0, "max": 480, "config_key": "fps_limit", "default": 60},
    },
    "Miscellaneous": {
        "Discord RPC": {"type": "bool", "config_key": "discord_rpc", "default": True},
    },
    "Credits": {}
}
settings_start_category = "Mandelbrot"
