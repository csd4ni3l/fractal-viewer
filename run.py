import pyglet

pyglet.options['shadow_window'] = False  # Fix double window issue on Wayland
pyglet.options.debug_gl = False

import logging, datetime, os, json, sys, arcade, platform

# Set up paths BEFORE importing modules that load assets
script_dir = os.path.dirname(os.path.abspath(__file__))
pyglet.resource.path.append(script_dir)
pyglet.font.add_directory(os.path.join(script_dir, 'assets', 'fonts'))

import mpmath
mpmath.dps = 1000

from utils.utils import get_closest_resolution, print_debug_info, on_exception
from utils.constants import log_dir, menu_background_color
from menus.main import Main
from arcade.experimental.controller_window import ControllerWindow

sys.excepthook = on_exception

pyglet.resource.path.append(os.getcwd())
pyglet.font.add_directory('./assets/fonts')

__builtins__.print = lambda *args, **kwargs: logging.debug(" ".join(map(str, args)))

if not log_dir in os.listdir():
    os.makedirs(log_dir)

while len(os.listdir(log_dir)) >= 5:
    files = [(file, os.path.getctime(os.path.join(log_dir, file))) for file in os.listdir(log_dir)]
    oldest_file = sorted(files, key=lambda x: x[1])[0][0]
    os.remove(os.path.join(log_dir, oldest_file))

timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"debug_{timestamp}.log"
logging.basicConfig(filename=f'{os.path.join(log_dir, log_filename)}', format='%(asctime)s %(name)s %(levelname)s: %(message)s', level=logging.DEBUG)

for logger_name_to_disable in ['arcade']:
    logging.getLogger(logger_name_to_disable).propagate = False
    logging.getLogger(logger_name_to_disable).disabled = True

if os.path.exists('settings.json'):
    with open('settings.json', 'r') as settings_file:
        settings = json.load(settings_file)

    resolution = list(map(int, settings['resolution'].split('x')))

    if not settings.get("anti_aliasing", "4x MSAA") == "None":
        antialiasing = int(settings.get("anti_aliasing", "4x MSAA").split('x')[0])
    else:
        antialiasing = 0

    # Wayland workaround (can be overridden with environment variable)
    if (platform.system() == "Linux" and
        os.environ.get("WAYLAND_DISPLAY") and
        not os.environ.get("ARCADE_FORCE_MSAA")):
        logging.info("Wayland detected - disabling MSAA (set ARCADE_FORCE_MSAA=1 to override)")
        antialiasing = 0

    fullscreen = settings['window_mode'] == 'Fullscreen'
    style = arcade.Window.WINDOW_STYLE_BORDERLESS if settings['window_mode'] == 'borderless' else arcade.Window.WINDOW_STYLE_DEFAULT
    vsync = settings['vsync']
    fps_limit = settings['fps_limit']
else:
    resolution = get_closest_resolution()
    antialiasing = 4

    # Wayland workaround (can be overridden with environment variable)
    if (platform.system() == "Linux" and
        os.environ.get("WAYLAND_DISPLAY") and
        not os.environ.get("ARCADE_FORCE_MSAA")):
        logging.info("Wayland detected - disabling MSAA (set ARCADE_FORCE_MSAA=1 to override)")
        antialiasing = 0

    fullscreen = False
    style = arcade.Window.WINDOW_STYLE_DEFAULT
    vsync = True
    fps_limit = 0

    settings = {
        "resolution": f"{resolution[0]}x{resolution[1]}",
        "antialiasing": "4x MSAA",
        "window_mode": "Windowed",
        "vsync": True,
        "fps_limit": 60,
        "discord_rpc": True
    }

    with open("settings.json", "w") as file:
        file.write(json.dumps(settings))

try:
    window = ControllerWindow(width=resolution[0], height=resolution[1], title='FractalViewer', samples=antialiasing, antialiasing=antialiasing > 0, fullscreen=fullscreen, vsync=vsync, resizable=False, style=style, visible=False)
except (FileNotFoundError, PermissionError) as e:
    logging.warning(f"Controller support unavailable: {e}. Falling back to regular window.")
    window = arcade.Window(width=resolution[0], height=resolution[1], title='FractalViewer', samples=antialiasing, antialiasing=antialiasing > 0, fullscreen=fullscreen, vsync=vsync, resizable=False, style=style, visible=False)

if vsync:
    window.set_vsync(True)
    display_mode = window.display.get_default_screen().get_mode()
    if display_mode:
        refresh_rate = display_mode.rate
    else:
        refresh_rate = 60
    window.set_update_rate(1 / refresh_rate)
    window.set_draw_rate(1 / refresh_rate)
elif not fps_limit == 0:
    window.set_update_rate(1 / fps_limit)
    window.set_draw_rate(1 / fps_limit)
else:
    window.set_update_rate(1 / 99999999)
    window.set_draw_rate(1 / 99999999)

arcade.set_background_color(menu_background_color)

print_debug_info()
main = Main()

window.show_view(main)

# Make window visible after all setup is complete (helps prevent double window on Wayland)
window.set_visible(True)

logging.debug('Game started.')

arcade.run()

logging.info('Exited with error code 0.')
