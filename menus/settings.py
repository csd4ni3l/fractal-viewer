import copy, pypresence, json

import arcade, arcade.gui

from utils.constants import button_style, dropdown_style, slider_style, settings, discord_presence_id, settings_start_category
from utils.utils import FakePyPresence
from utils.preload import button_texture, button_hovered_texture

from arcade.gui.experimental.focus import UIFocusGroup

class Settings(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()

        with open("settings.json", "r") as file:
            self.settings_dict = json.load(file)

        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state='In Settings', details='Modifying Settings', start=self.pypresence_client.start_time)

        self.slider_labels = {}
        self.sliders = {}

        self.on_radiobuttons = {}
        self.off_radiobuttons = {}

        self.current_category = settings_start_category

        self.modified_settings = {}

    def create_layouts(self):
        self.anchor = self.add_widget(UIFocusGroup(size_hint=(1, 1)))

        self.box = arcade.gui.UIBoxLayout(space_between=50, align="center", vertical=False)
        self.anchor.add(self.box, anchor_x="center", anchor_y="top", align_x=10, align_y=-75)

        self.top_box = arcade.gui.UIBoxLayout(space_between=self.window.width / 160, vertical=False)
        self.anchor.add(self.top_box, anchor_x="left", anchor_y="top", align_x=10, align_y=-10)

        self.key_layout = self.box.add(arcade.gui.UIBoxLayout(space_between=20, align='left'))
        self.value_layout = self.box.add(arcade.gui.UIBoxLayout(space_between=13, align='left'))

    def on_show_view(self):
        super().on_show_view()

        self.create_layouts()

        self.ui.push_handlers(self) # required for controller stuff

        self.back_button = arcade.gui.UITextureButton(texture=button_texture, texture_hovered=button_hovered_texture, text='<--', style=button_style, width=100, height=50)
        self.back_button.on_click = lambda e: self.main_exit()
        self.top_box.add(self.back_button)

        self.display_categories()

        self.display_category(settings_start_category)

    def display_categories(self):
        for category in settings:
            category_button = arcade.gui.UITextureButton(texture=button_texture, texture_hovered=button_hovered_texture, text=category, style=button_style, width=self.window.width / 13, height=50)

            if not category == "Credits":
                category_button.on_click = lambda e, category=category: self.display_category(category)
            else:
                category_button.on_click = lambda e: self.credits()

            self.top_box.add(category_button)

        self.anchor.detect_focusable_widgets()

    def display_category(self, category):
        if hasattr(self, 'apply_button'):
            self.anchor.remove(self.apply_button)
            del self.apply_button

        if hasattr(self, 'credits_label'):
            self.anchor.remove(self.credits_label)
            del self.credits_label

        self.current_category = category

        self.key_layout.clear()
        self.value_layout.clear()

        for setting in settings[category]:
            label = arcade.gui.UILabel(text=setting, font_name="Roboto", font_size=28, text_color=arcade.color.WHITE )
            self.key_layout.add(label)

            setting_dict = settings[category][setting]

            if setting_dict['type'] == "option":
                dropdown = arcade.gui.UIDropdown(options=setting_dict['options'], width=200, height=50, default=self.settings_dict.get(setting_dict["config_key"], setting_dict["options"][0]), active_style=dropdown_style, dropdown_style=dropdown_style, primary_style=dropdown_style)
                dropdown.on_change = lambda _, setting=setting, dropdown=dropdown: self.update(setting, dropdown.value, "option")
                self.value_layout.add(dropdown)

            elif setting_dict['type'] == "bool":
                button_layout = self.value_layout.add(arcade.gui.arcade.gui.UIBoxLayout(space_between=50, vertical=False))

                on_radiobutton = arcade.gui.UITextureButton(texture=button_texture, texture_hovered=button_hovered_texture, text="ON", style=button_style, width=150, height=50)
                self.on_radiobuttons[setting] = on_radiobutton
                on_radiobutton.on_click = lambda _, setting=setting: self.update(setting, True, "bool")
                button_layout.add(on_radiobutton)

                off_radiobutton = arcade.gui.UITextureButton(texture=button_texture, texture_hovered=button_hovered_texture, text="OFF", style=button_style, width=150, height=50)
                self.off_radiobuttons[setting] = off_radiobutton
                off_radiobutton.on_click = lambda _, setting=setting: self.update(setting, False, "bool")
                button_layout.add(off_radiobutton)

                if self.settings_dict.get(setting_dict["config_key"], setting_dict["default"]):
                    self.set_highlighted_style(on_radiobutton)
                    self.set_normal_style(off_radiobutton)
                else:
                    self.set_highlighted_style(off_radiobutton)
                    self.set_normal_style(on_radiobutton)

            elif setting_dict['type'] == "slider":
                if setting == "FPS Limit":
                    if self.settings_dict.get(setting_dict["config_key"]) == 0:
                        label_text = "FPS Limit: Disabled"
                    else:
                        label_text = f"FPS Limit: {self.settings_dict.get(setting_dict['config_key'], setting_dict['default'])}"
                else:
                    label_text = f"{setting}: {self.settings_dict.get(setting_dict['config_key'], setting_dict['default'])}"

                label.text = label_text

                self.slider_labels[setting] = label

                slider = arcade.gui.UISlider(width=400, height=50, value=self.settings_dict.get(setting_dict["config_key"], setting_dict["default"]), min_value=setting_dict['min'], max_value=setting_dict['max'], step=setting_dict.get("step", 1), style=slider_style)
                slider._render_steps = lambda surface: None
                slider.on_change = lambda event, setting=setting, slider=slider: self.update(setting, slider.value, "slider")

                self.sliders[setting] = slider
                self.value_layout.add(slider)

        self.apply_button = arcade.gui.UITextureButton(texture=button_texture, texture_hovered=button_hovered_texture, text='Apply', style=button_style, width=200, height=100)
        self.apply_button.on_click = lambda event: self.apply_settings()
        self.anchor.add(self.apply_button, anchor_x="right", anchor_y="bottom", align_x=-10, align_y=10)

        self.anchor.detect_focusable_widgets()

    def apply_settings(self):
        for config_key, value in self.modified_settings.items():
            self.settings_dict[config_key] = value

            if self.settings_dict['window_mode'] == "Fullscreen":
                self.window.set_fullscreen(True)
            else:
                self.window.set_fullscreen(False)
                width, height = map(int, self.settings_dict['resolution'].split('x'))
                self.window.set_size(width, height)

            if self.settings_dict['vsync']:
                self.window.set_vsync(True)
                display_mode = self.window.display.get_default_screen().get_mode()
                if display_mode:
                    refresh_rate = display_mode.rate
                else:
                    refresh_rate = 60
                self.window.set_update_rate(1 / refresh_rate)
                self.window.set_draw_rate(1 / refresh_rate)

            elif not self.settings_dict['fps_limit'] == 0:
                self.window.set_vsync(False)
                self.window.set_update_rate(1 / self.settings_dict['fps_limit'])
                self.window.set_draw_rate(1 / self.settings_dict['fps_limit'])

            else:
                self.window.set_vsync(False)
                self.window.set_update_rate(1 / 99999999)
                self.window.set_draw_rate(1 / 99999999)

            if self.settings_dict['discord_rpc']:
                if isinstance(self.pypresence_client, FakePyPresence): # the user has enabled RPC in the settings in this session.
                    start_time = copy.deepcopy(self.pypresence_client.start_time)
                    self.pypresence_client.close()
                    del self.pypresence_client
                    try:
                        self.pypresence_client = pypresence.Presence(discord_presence_id)
                        self.pypresence_client.connect()
                        self.pypresence_client.update(state='In Settings', details='Modifying Settings', start=start_time)
                        self.pypresence_client.start_time = start_time
                    except:
                        self.pypresence_client = FakePyPresence()
                        self.pypresence_client.start_time = start_time
            else:
                if not isinstance(self.pypresence_client, FakePyPresence):
                    start_time = copy.deepcopy(self.pypresence_client.start_time)
                    self.pypresence_client.update()
                    self.pypresence_client.close()
                    del self.pypresence_client
                    self.pypresence_client = FakePyPresence()
                    self.pypresence_client.start_time = start_time

            self.ui_cleanup()

            self.ui = arcade.gui.UIManager()
            self.ui.enable()

            self.create_layouts()

            self.back_button = arcade.gui.UITextureButton(texture=button_texture, texture_hovered=button_hovered_texture, text='<--', style=button_style, width=100, height=50)
            self.back_button.on_click = lambda e: self.main_exit()
            self.top_box.add(self.back_button)

            self.display_categories()

        self.display_category(self.current_category)

        with open("settings.json", "w") as file:
            file.write(json.dumps(self.settings_dict, indent=4))

    def update(self, setting=None, button_state=None, setting_type="bool"):
        config_key = settings[self.current_category][setting]["config_key"]

        if setting_type == "option":
            self.modified_settings[config_key] = button_state

        elif setting_type == "bool":
            self.modified_settings[config_key] = button_state

            if button_state:
                self.set_highlighted_style(self.on_radiobuttons[setting])
                self.set_normal_style(self.off_radiobuttons[setting])
            else:
                self.set_highlighted_style(self.off_radiobuttons[setting])
                self.set_normal_style(self.on_radiobuttons[setting])

        elif setting_type == "slider":
            self.modified_settings[config_key] = button_state
            self.sliders[setting].value = button_state

            if setting == "FPS Limit":
                if button_state == 0:
                    label_text = "FPS Limit: Disabled"
                else:
                    label_text = f"FPS Limit: {str(button_state).rjust(8)}"
            else:
                label_text = f"{setting}: {str(button_state).rjust(8)}"

            self.slider_labels[setting].text = label_text

    def credits(self):
        if hasattr(self, 'apply_button'):
            self.anchor.remove(self.apply_button)
            del self.apply_button

        if hasattr(self, 'credits_label'):
            self.anchor.remove(self.credits_label)
            del self.credits_label

        self.key_layout.clear()
        self.value_layout.clear()

        with open('CREDITS', 'r') as file:
            text = file.read()

        if self.window.width == 3840:
            font_size = 30
        elif self.window.width == 2560:
            font_size = 20
        elif self.window.width == 1920:
            font_size = 17
        elif self.window.width >= 1440:
            font_size = 14
        else:
            font_size = 12

        self.credits_label = arcade.gui.UILabel(text=text, text_color=arcade.color.WHITE, font_name="Roboto", font_size=font_size, align="center", multiline=True)

        self.key_layout.add(self.credits_label)

        self.anchor.detect_focusable_widgets()

    def set_highlighted_style(self, element):
        element.texture = button_hovered_texture
        element.texture_hovered = button_texture

    def set_normal_style(self, element):
        element.texture_hovered = button_hovered_texture
        element.texture = button_texture

    def main_exit(self):
        from menus.main import Main
        self.window.show_view(Main(pypresence_client=self.pypresence_client))

    def ui_cleanup(self):
        self.ui.clear()
        del self.ui
