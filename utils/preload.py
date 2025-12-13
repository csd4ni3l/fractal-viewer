import arcade.gui, arcade, os

# Get the directory where this module is located
_module_dir = os.path.dirname(os.path.abspath(__file__))
_assets_dir = os.path.join(os.path.dirname(_module_dir), 'assets')

button_texture = arcade.gui.NinePatchTexture(64 // 4, 64 // 4, 64 // 4, 64 // 4, arcade.load_texture(os.path.join(_assets_dir, 'graphics', 'button.png')))
button_hovered_texture = arcade.gui.NinePatchTexture(64 // 4, 64 // 4, 64 // 4, 64 // 4, arcade.load_texture(os.path.join(_assets_dir, 'graphics', 'button_hovered.png')))
cursor_texture = arcade.load_texture(os.path.join(_assets_dir, "graphics", "cursor.png"))