import arcade, arcade.gui

from utils.constants import button_style
from utils.preload import button_texture, button_hovered_texture

class FractalChooser(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()

        self.pypresence_client = pypresence_client

    def on_show_view(self):
        super().on_show_view()

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))

        self.grid = self.add_widget(arcade.gui.UIGridLayout(row_count=3, column_count=3, horizontal_spacing=10, vertical_spacing=10))
        self.anchor.add(self.grid, anchor_x="center", anchor_y="center")

        self.title_label = self.anchor.add(arcade.gui.UILabel(text="Choose a fractal to view.", font_name="Protest Strike", font_size=32), anchor_x="center", anchor_y="top", align_y=-50)

        self.back_button = arcade.gui.UITextureButton(texture=button_texture, texture_hovered=button_hovered_texture, text='<--', style=button_style, width=100, height=50)
        self.back_button.on_click = lambda event: self.main_exit()
        self.anchor.add(self.back_button, anchor_x="left", anchor_y="top", align_x=5, align_y=-5)

        self.mandelbrot_button = self.grid.add(arcade.gui.UITextureButton(texture=button_texture, texture_hovered=button_hovered_texture, text='Mandelbrot', style=button_style, width=200, height=200), row=0, column=0)
        self.mandelbrot_button.on_click = lambda event: self.mandelbrot()

        self.sierpinsky_carpet_button = self.grid.add(arcade.gui.UITextureButton(texture=button_texture, texture_hovered=button_hovered_texture, text='Sierpinsky Carpet', style=button_style, width=200, height=200), row=0, column=1)
        self.sierpinsky_carpet_button.on_click = lambda event: self.sierpinsky_carpet()

    def main_exit(self):
        from menus.main import Main
        self.window.show_view(Main(self.pypresence_client))

    def mandelbrot(self):
        from game.mandelbrot import MandelbrotViewer
        self.window.show_view(MandelbrotViewer(self.pypresence_client))

    def sierpinsky_carpet(self):
        from game.sierpinsky_carpet import SierpinskyCarpetViewer
        self.window.show_view(SierpinskyCarpetViewer(self.pypresence_client))
