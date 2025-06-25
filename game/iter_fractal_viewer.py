import arcade, arcade.gui, pyglet, json

from game.shader import create_iter_calc_shader
from utils.constants import button_style, initial_real_imag
from utils.preload import button_texture, button_hovered_texture, cursor_texture

class IterFractalViewer(arcade.gui.UIView):
    def __init__(self, pypresence_client, fractal_name: str):
        super().__init__()

        self.pypresence_client = pypresence_client
        self.fractal_name = fractal_name

        with open("settings.json", "r") as file:
            self.settings_dict = json.load(file)

        self.escape_radius = int(self.settings_dict.get(f"{self.fractal_name}_escape_radius", 2))
        self.real_min, self.real_max, self.imag_min, self.imag_max = initial_real_imag[fractal_name] if fractal_name != "julia" else (-self.escape_radius, self.escape_radius, -self.escape_radius, self.escape_radius)
        self.max_iter = self.settings_dict.get(f"{self.fractal_name}_max_iter", 200)
        self.zoom = 1.0
        self.zoom_start_position = ()
        self.zoom_rect = None
        self.has_controller = False
        self.dragging_with_controller = False

    def on_show_view(self):
        super().on_show_view()

        self.shader_program, self.fractal_image = create_iter_calc_shader(
            self.fractal_name, 
            self.window.width,
            self.window.height,
            self.settings_dict.get(f"{self.fractal_name}_precision", "Single").lower(),
            int(self.settings_dict.get(f"{self.fractal_name}_n", 2)), # This will work for non-exponentiable fractals as well because they dont have an _n property
            int(self.settings_dict.get(f"{self.fractal_name}_escape_radius", 2)),
            self.settings_dict.get("julia_type", "Classic swirling")
        )

        self.fractal_sprite = pyglet.sprite.Sprite(img=self.fractal_image)

        self.create_image()

        self.pypresence_client.update(state=f'Viewing {self.fractal_name.replace("_", " ").capitalize()}', details=f'Zoom: {self.zoom}\nMax Iterations: {self.max_iter}', start=self.pypresence_client.start_time)

        self.setup_ui()

    def main_exit(self):
        from menus.main import Main
        self.window.show_view(Main(self.pypresence_client))

    def setup_ui(self):
        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))

        self.info_box = self.anchor.add(arcade.gui.UIBoxLayout(space_between=10, vertical=False), anchor_x="center", anchor_y="top")
        self.zoom_label = self.info_box.add(arcade.gui.UILabel(text=f"Zoom: {self.zoom}", font_name="Roboto", font_size=16))
        self.max_iter_label = self.info_box.add(arcade.gui.UILabel(text=f"Max Iterations: {self.max_iter}", font_name="Roboto", font_size=16))

        self.back_button = arcade.gui.UITextureButton(texture=button_texture, texture_hovered=button_hovered_texture, text='<--', style=button_style, width=100, height=50)
        self.back_button.on_click = lambda event: self.main_exit()
        self.anchor.add(self.back_button, anchor_x="left", anchor_y="top", align_x=5, align_y=-5)

        if self.window.get_controllers():
            self.sprite_list = arcade.SpriteList()
            self.cursor_sprite = arcade.Sprite(cursor_texture)
            self.sprite_list.append(self.cursor_sprite)
            self.has_controller = True

    def on_button_press(self, controller, button_name):
        if button_name == "a":
            self.zoom_start_position = self.cursor_sprite.center_x, self.cursor_sprite.center_y
            self.dragging_with_controller = True
        elif button_name == "start":
            self.main_exit()

    def on_button_release(self, controller, button_name):
        if button_name == "a" and self.dragging_with_controller:
            self.dragging_with_controller = False
            self.on_mouse_release(self.cursor_sprite.center_x, self.cursor_sprite.center_y, None, None)

    def on_stick_motion(self, controller, name, vector):
        if name == "leftstick":
            self.cursor_sprite.center_x += vector.x * 5
            self.cursor_sprite.center_y += vector.y * 5
            if self.dragging_with_controller:
                self.on_mouse_drag(self.cursor_sprite.center_x, self.cursor_sprite.center_y, 0, 0, None, None)

    def create_image(self):
        with self.shader_program:
            self.shader_program['u_maxIter'] = int(self.max_iter)
            self.shader_program['u_resolution'] = (self.window.width, self.window.height)
            self.shader_program['u_real_range'] = (self.real_min, self.real_max)
            self.shader_program['u_imag_range'] = (self.imag_min, self.imag_max)
            self.shader_program.dispatch(self.fractal_image.width, self.fractal_image.height, 1, barrier=pyglet.gl.GL_ALL_BARRIER_BITS)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.real_min, self.real_max, self.imag_min, self.imag_max = initial_real_imag[self.fractal_name] if self.fractal_name != "julia" else (-self.escape_radius, self.escape_radius, -self.escape_radius, self.escape_radius)

            self.zoom = 1

            self.zoom_label.text = f"Zoom: {self.zoom:.2f}"

            self.zoom_start_position = None
            self.zoom_rect = None

            self.create_image()

            self.pypresence_client.update(
                state=f'Viewing {self.fractal_name.replace("_", " ").capitalize()}',
                details=f'Zoom: {self.zoom:.2f}\nMax Iterations: {self.max_iter}',
                start=self.pypresence_client.start_time
            )

    def on_mouse_drag(self, x, y, dx, dy, _buttons, _modifiers):
        if not self.zoom_start_position:
            self.zoom_start_position = (x, y)

        x0, y0 = self.zoom_start_position

        width = x - x0
        height = y - y0

        aspect = self.width / self.height

        if abs(width) / abs(height or 1) > aspect:
            adjusted_height = abs(width) / aspect
            height = adjusted_height if height >= 0 else -adjusted_height
        else:
            adjusted_width = abs(height) * aspect
            width = adjusted_width if width >= 0 else -adjusted_width

        x1 = x0 + width
        y1 = y0 + height

        left = min(x0, x1)
        right = max(x0, x1)
        bottom = min(y0, y1)
        top = max(y0, y1)

        self.zoom_rect = arcade.rect.LRBT(left=left, right=right, top=top, bottom=bottom)

    def on_mouse_release(self, x, y, button, modifiers):
        if self.zoom_start_position and self.zoom_rect:
            rect = self.zoom_rect

            center_x = (rect.left + rect.right) / 2
            center_y = (rect.bottom + rect.top) / 2

            center_real = self.real_min + (center_x / self.width) * (self.real_max - self.real_min)
            center_imag = self.imag_min + (center_y / self.height) * (self.imag_max - self.imag_min)

            real_span = (rect.right - rect.left) / self.width * (self.real_max - self.real_min)
            imag_span = (rect.top - rect.bottom) / self.height * (self.imag_max - self.imag_min)

            self.real_min = center_real - real_span / 2
            self.real_max = center_real + real_span / 2
            self.imag_min = center_imag - imag_span / 2
            self.imag_max = center_imag + imag_span / 2

            initial_real_range = initial_real_imag[self.fractal_name][1] - initial_real_imag[self.fractal_name][0]
            new_real_range = self.real_max - self.real_min
            self.zoom = initial_real_range / new_real_range

            self.zoom_label.text = f"Zoom: {self.zoom:.4f}"

            self.zoom_start_position = None
            self.zoom_rect = None

            self.create_image()

            self.pypresence_client.update(
                state=f'Viewing {self.fractal_name.replace("_", " ").capitalize()}',
                details=f'Zoom: {self.zoom:.4f}\nMax Iterations: {self.max_iter}',
                start=self.pypresence_client.start_time
            )

    def on_draw(self):
        self.window.clear()
        self.fractal_sprite.draw()
        self.ui.draw()

        if self.has_controller:
            self.sprite_list.draw()
        
        if self.zoom_rect:
            arcade.draw_rect_outline(self.zoom_rect, color=arcade.color.GRAY)
