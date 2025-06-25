import arcade, arcade.gui, pyglet, json

from game.shader import create_sierpinsky_carpet_shader
from utils.constants import button_style
from utils.preload import button_texture, button_hovered_texture, cursor_texture

class SierpinskyCarpetViewer(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()

        self.pypresence_client = pypresence_client

        with open("settings.json", "r") as file:
            self.settings_dict = json.load(file)

        self.depth = self.settings_dict.get("sierpinsky_depth", 10)
        self.zoom = 1.0
        self.click_center = (self.width / 2, self.height / 2)
        self.has_controller = False
        
    def on_show_view(self):
        super().on_show_view()

        self.shader_program, self.sierpinsky_carpet_image = create_sierpinsky_carpet_shader(self.window.width, self.window.height, self.settings_dict.get("sierpinsky_precision", "Single").lower())

        self.sierpinsky_carpet_sprite = pyglet.sprite.Sprite(img=self.sierpinsky_carpet_image)

        self.create_image()

        self.pypresence_client.update(state='Viewing Sierpinsky Carpet', details=f'Zoom: {self.zoom}\nDepth: {self.depth}', start=self.pypresence_client.start_time)

        self.setup_ui()

        if self.window.get_controllers():
            self.sprite_list = arcade.SpriteList()
            self.cursor_sprite = arcade.Sprite(cursor_texture)
            self.sprite_list.append(self.cursor_sprite)
            self.has_controller = True

    def on_stick_motion(self, controller, name, vector):
        if name == "leftstick":
            self.cursor_sprite.center_x += vector.x * 5
            self.cursor_sprite.center_y += vector.y * 5

    def main_exit(self):
        from menus.main import Main
        self.window.show_view(Main(self.pypresence_client))

    def setup_ui(self):
        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))

        self.info_box = self.anchor.add(arcade.gui.UIBoxLayout(space_between=10, vertical=False), anchor_x="center", anchor_y="top")
        self.zoom_label = self.info_box.add(arcade.gui.UILabel(text=f"Zoom: {self.zoom}", font_name="Roboto", font_size=16))
        self.depth_label = self.info_box.add(arcade.gui.UILabel(text=f"Depth: {self.depth}", font_name="Roboto", font_size=16))

        self.back_button = arcade.gui.UITextureButton(texture=button_texture, texture_hovered=button_hovered_texture, text='<--', style=button_style, width=100, height=50)
        self.back_button.on_click = lambda event: self.main_exit()
        self.anchor.add(self.back_button, anchor_x="left", anchor_y="top", align_x=5, align_y=-5)

    def create_image(self):
        with self.shader_program:
            self.shader_program['u_depth'] = int(self.depth)
            self.shader_program['u_zoom'] = int(self.zoom)
            self.shader_program['u_center'] = self.click_center
            self.shader_program.dispatch(self.sierpinsky_carpet_image.width, self.sierpinsky_carpet_image.height, 1, barrier=pyglet.gl.GL_ALL_BARRIER_BITS)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> bool | None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            zoom = self.settings_dict.get("sierpinsky_zoom_increase", 2)
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            zoom = 1 / self.settings_dict.get("sierpinsky_zoom_increase", 2)
        else:
            return

        self.zoom *= zoom

        self.click_center = (x, y)

        self.zoom_label.text = f"Zoom: {self.zoom}"

        self.create_image()

        self.pypresence_client.update(state='Viewing Sierpinsky Carpet', details=f'Zoom: {self.zoom}\nDepth: {self.depth}', start=self.pypresence_client.start_time)

    def on_button_press(self, controller, name):
        if name == "a":
            self.on_mouse_press(self.cursor_sprite.left, self.cursor_sprite.bottom, arcade.MOUSE_BUTTON_LEFT, 0)

    def on_draw(self):
        self.window.clear()
        self.sierpinsky_carpet_sprite.draw()
        self.ui.draw()
        if self.has_controller:
            self.sprite_list.draw()
