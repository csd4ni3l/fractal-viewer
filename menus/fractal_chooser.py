import arcade, arcade.gui

from utils.constants import button_style, iter_fractals
from utils.preload import button_texture, button_hovered_texture

from arcade.gui.experimental.focus import UIFocusGroup

class FractalChooser(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()

        self.pypresence_client = pypresence_client
        self.iter_fractal_buttons = []

        self.anchor = self.add_widget(UIFocusGroup(size_hint=(1, 1)))

        self.grid = self.add_widget(arcade.gui.UIGridLayout(row_count=4, column_count=3, horizontal_spacing=10, vertical_spacing=10))
        self.anchor.add(self.grid, anchor_x="center", anchor_y="center")

    def on_show_view(self):
        super().on_show_view()

        self.title_label = self.anchor.add(arcade.gui.UILabel(text="Choose a fractal to view.", font_name="Roboto", font_size=32), anchor_x="center", anchor_y="top", align_y=-50)

        self.back_button = arcade.gui.UITextureButton(texture=button_texture, texture_hovered=button_hovered_texture, text='<--', style=button_style, width=100, height=50)
        self.back_button.on_click = lambda event: self.main_exit()
        self.anchor.add(self.back_button, anchor_x="left", anchor_y="top", align_x=5, align_y=-5)

        for n, fractal_name in enumerate(iter_fractals):
            row = n // 3
            col = n % 3
            
            self.iter_fractal_buttons.append(self.grid.add(arcade.gui.UITextureButton(texture=button_texture, texture_hovered=button_hovered_texture, text=fractal_name.replace("_", " ").capitalize(), style=button_style, width=200, height=200), row=row, column=col))
            self.iter_fractal_buttons[-1].on_click = lambda event, fractal_name=fractal_name: self.iter_fractal(fractal_name)

        row = (n + 1) // 3
        col = (n + 1) % 3

        self.sierpinsky_carpet_button = self.grid.add(arcade.gui.UITextureButton(texture=button_texture, texture_hovered=button_hovered_texture, text='Sierpinsky Carpet', style=button_style, width=200, height=200), row=row, column=col)
        self.sierpinsky_carpet_button.on_click = lambda event: self.sierpinsky_carpet()

        self.anchor.detect_focusable_widgets()

    def main_exit(self):
        from menus.main import Main
        self.window.show_view(Main(self.pypresence_client))

    def iter_fractal(self, fractal_name):
        from game.iter_fractal_viewer import IterFractalViewer
        self.window.show_view(IterFractalViewer(self.pypresence_client, fractal_name))

    def sierpinsky_carpet(self):
        from game.sierpinsky_carpet import SierpinskyCarpetViewer
        self.window.show_view(SierpinskyCarpetViewer(self.pypresence_client))