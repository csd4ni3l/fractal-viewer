import pyglet

pyglet.options.debug_gl = False

import logging, datetime, os, json, sys, arcade

from utils.utils import get_closest_resolution, print_debug_info, on_exception
from utils.constants import log_dir, menu_background_color
from menus.main import Main

sys.excepthook = on_exception

pyglet.resource.path.append(os.getcwd())
pyglet.font.add_directory('./assets/fonts')

if not log_dir in os.listdir():
    os.makedirs(log_dir)

while len(os.listdir(log_dir)) >= 5:
    files = [(file, os.path.getctime(os.path.join(log_dir, file))) for file in os.listdir(log_dir)]
    oldest_file = sorted(files, key=lambda x: x[1])[0][0]
    os.remove(os.path.join(log_dir, oldest_file))

timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"debug_{timestamp}.log"
logging.basicConfig(filename=f'{os.path.join(log_dir, log_filename)}', format='%(asctime)s %(name)s %(levelname)s: %(message)s', level=logging.DEBUG)

for logger_name_to_disable in ['arcade', "numba"]:
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

    fullscreen = settings['window_mode'] == 'Fullscreen'
    style = arcade.Window.WINDOW_STYLE_BORDERLESS if settings['window_mode'] == 'borderless' else arcade.Window.WINDOW_STYLE_DEFAULT
    vsync = settings['vsync']
    fps_limit = settings['fps_limit']
else:
    resolution = get_closest_resolution()
    antialiasing = 4
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

window = arcade.Window(width=resolution[0], height=resolution[1], title='Mandelbrot Viewer', samples=antialiasing, antialiasing=antialiasing > 0, fullscreen=fullscreen, vsync=vsync, resizable=False, style=style)

if vsync:
    window.set_vsync(True)
    display_mode = window.display.get_default_screen().get_mode()
    refresh_rate = display_mode.rate
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

logging.debug('Game started.')

arcade.run()

logging.info('Exited with error code 0.')
