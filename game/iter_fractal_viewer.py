import arcade, arcade.gui, pyglet, json

from game.shader import create_iter_calc_shader
from utils.constants import button_style, initial_real_imag
from utils.preload import button_texture, button_hovered_texture

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

    def zoom_at(self, center_x, center_y, zoom_factor):
        center_real = self.real_min + (center_x / self.width) * (self.real_max - self.real_min)
        center_imag = self.imag_min + (center_y / self.height) * (self.imag_max - self.imag_min)

        new_real_range = (self.real_max - self.real_min) / zoom_factor
        new_imag_range = (self.imag_max - self.imag_min) / zoom_factor

        self.real_min = center_real - new_real_range / 2
        self.real_max = center_real + new_real_range / 2
        self.imag_min = center_imag - new_imag_range / 2
        self.imag_max = center_imag + new_imag_range / 2

    def create_image(self):
        with self.shader_program:
            self.shader_program['u_maxIter'] = int(self.max_iter)
            self.shader_program['u_resolution'] = (self.window.width, self.window.height)
            self.shader_program['u_real_range'] = (self.real_min, self.real_max)
            self.shader_program['u_imag_range'] = (self.imag_min, self.imag_max)
            self.shader_program.dispatch(self.fractal_image.width, self.fractal_image.height, 1, barrier=pyglet.gl.GL_ALL_BARRIER_BITS)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> bool | None:
        super().on_mouse_press(x, y, button, modifiers)

        if button == arcade.MOUSE_BUTTON_LEFT:
            zoom = self.settings_dict.get(f"{self.fractal_name}_zoom_increase", 2)
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            zoom = 1 / self.settings_dict.get(f"{self.fractal_name}_zoom_increase", 2)
        else:
            return

        self.zoom *= zoom

        self.zoom_label.text = f"Zoom: {self.zoom}"

        self.zoom_at(self.window.mouse.data["x"], self.window.mouse.data["y"], zoom)
        self.create_image()

        self.pypresence_client.update(state=f'Viewing {self.fractal_name.replace("_", " ").capitalize()}', details=f'Zoom: {self.zoom}\nMax Iterations: {self.max_iter}', start=self.pypresence_client.start_time)

    def on_draw(self):
        self.window.clear()
        self.fractal_sprite.draw()
        self.ui.draw()
