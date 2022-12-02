import os
import pygame.event
import pygame_menu
import pygame_menu.themes
import config
import screen
from types import FunctionType
from screen import Screen
from typing import Union, Callable

pygame.font.init()
pygame.mixer.init()
pygame.display.init()

class BaseMenu(object):
    is_main = False

    def __init__(self, screen: Screen, title: str, main_menu: Union[Callable] = None):
        if main_menu:
            self.main_menu = main_menu
        else:
            self.main_menu = self
        # Sounds paths # # #
        self.selection_sound_path = os.path.join(config.sounds_directory, 'menu', 'selection.ogg')
        self.open_menu_sound_path = os.path.join(config.sounds_directory, 'menu', 'open_menu.ogg')
        self.menu_music_path = os.path.join(config.sounds_directory, 'menu', 'menu_music.mp3')
        # # # # # # # # # #
        self.sound_engine = pygame_menu.sound.Sound()
        self.title = title
        self.screen = screen
        self.main_menu = self
        self.translate_path = []
        self.music_manager = self.screen.music
        self.width = self.screen.resolution[0] // 2
        self.height = self.screen.resolution[1] // 2
        self.background_color = (0, 0, 0, 200)
        self.title_background_color = (0, 0, 0)
        self.title_font_shadow = False
        self.title_font = pygame_menu.font.FONT_FIRACODE_BOLD
        self.widget_margin = (0, 25)
        self.widget_font_color = (255, 255, 255)
        self.widget_shadow_color = (255, 255, 255)
        self.theme = pygame_menu.Theme(background_color=self.background_color,
                                           title_background_color=self.title_background_color,
                                           title_font_shadow=True, widget_font_color=self.widget_font_color, widget_shadow_color=self.widget_shadow_color, title_font=self.title_font, widget_margin=self.widget_margin)

        self.menu = pygame_menu.Menu(self.title, self.width, self.height, theme=self.theme, mouse_motion_selection=True)
        self.initialize_sounds(50)
        data = self.get_data()
        self.set_attrs(data)
        self.format_menu()
        self.music_manager.start(self.menu_music_path)

    def set_main(self, menu):
        self.main_menu = menu

    def get_menu_obj(self):
        self.menu = pygame_menu.Menu(self.title, self.width, self.height, theme=self.theme, mouse_motion_selection=True)
        self.format_menu()
        return self.menu

    def rerender_menu(self):
        self.get_menu_obj()
        self.format_menu()

    def initialize_sounds(self, volume: int = 50):
        if volume > self.music_manager.max_volume or volume < self.music_manager.min_volume:
            volume = 50
        self.sound_engine.set_sound(pygame_menu.sound.SOUND_TYPE_WIDGET_SELECTION, self.selection_sound_path, volume=volume/100)
        self.sound_engine.set_sound(pygame_menu.sound.SOUND_TYPE_OPEN_MENU, self.open_menu_sound_path, volume=volume/100)
        self.sound_engine.set_sound(pygame_menu.sound.SOUND_TYPE_CLOSE_MENU, self.open_menu_sound_path, volume=volume/100)
        self.menu.set_sound(self.sound_engine, recursive=True)

    def format_menu(self):
        print('Noting to add')

    def set_attrs(self, data: dict):
        for key, val in data.items():
            setattr(self, key, val)

    def get_data(self):
        data = {key: val for key, val in self.__dict__.items()}
        new_args = list(set(dir(self.__class__)) - set(dir(BaseMenu)))
        for arg in new_args:
            val = getattr(self.__class__, arg)
            if not isinstance(val, FunctionType):
                data[arg] = val
        return data

    def get_menu(self, menu):
        menu = menu(self.screen, self.title, self.main_menu)
        return menu

    def draw(self, *args):
        if self.menu.is_enabled():
            self.menu.update(pygame.event.get())
            self.menu.draw(self.screen.screen)
        else:
            self.screen.wait(1)

    def get_text(self, *args):
        return self.screen.lang_manager.get_text(*args)

    def get_global(self, key: str):
        return self.screen.lang_manager.get_global(key)


class EpisodeMenu(BaseMenu):
    is_main = False
    translate_path = ['menu', 'episode_menu']

    def set_episode(self, value, difficulty):
        pass


    def format_menu(self):
        episodes = [('Эпизод 1', 1), ('Эпизод 2', 2)]
        self.menu.add.selector(self.get_text(*self.translate_path, "selector_title"), episodes, onchange=self.set_episode, style='fancy', style_fancy_bgcolor=(0, 0, 0, 0), style_fancy_arrow_color=(255, 255, 255), style_fancy_bordercolor=(255, 255, 255))
        self.menu.add.button(self.get_global('back_button'), pygame_menu.events.BACK)

class VolumeSettingsMenu(BaseMenu):
    is_main = False
    translate_path = ['menu', 'audio_settings_menu']

    def on_music_volume_change(self, range_value):
        self.music_manager.set_volume(int(range_value))

    def on_sound_volume_change(self, range_value):
        self.main_menu.initialize_sounds(range_value)

    def format_menu(self):
        self.menu.add.range_slider(self.get_text(*self.translate_path, 'volume_music_selector'), self.music_manager.get_volume()*100, (0, 100), 1,
                              rangeslider_id='music_volume',
                              value_format=lambda x: str(int(x)), onchange=self.on_music_volume_change)
        self.menu.add.range_slider(self.get_text(*self.translate_path, 'volume_sound_selector'), self.music_manager.get_volume() * 100, (0, 100), 1,
                                   rangeslider_id='sound_volume',
                                   value_format=lambda x: str(int(x)), onchange=self.on_sound_volume_change)

        self.menu.add.button(self.get_global('back_button'), pygame_menu.events.BACK)

class LanguageSettingsMenu(BaseMenu):
    is_main = False
    translate_path = ['menu', 'language_settings_menu']

    def on_change(self, selected_item, selected_index):
        self.screen.lang_manager.set_language(selected_index)
        self.main_menu.menu.disable()
        self.main_menu.menu.clear(True)
        self.main_menu.menu.enable()
        self.main_menu.menu.enable()

    def format_menu(self):
        current_lang = self.screen.lang_manager.get_lang_index()
        langs = self.screen.lang_manager.get_langs()
        self.menu.add.dropselect(self.get_text(*self.translate_path, 'dropselect_title'), langs, default=current_lang, onchange=self.on_change)
        self.menu.add.button(self.get_global('back_button'), pygame_menu.events.BACK)

class SettingsMenu(BaseMenu):
    is_main = False
    translate_path = ['menu', 'settings_menu']

    def format_menu(self):
        self.menu.add.button(self.get_text(*self.translate_path, 'audio_button'), self.get_menu(VolumeSettingsMenu).menu)
        self.menu.add.button(self.get_text(*self.translate_path, 'lang_button'), self.get_menu(LanguageSettingsMenu).menu)
        self.menu.add.button(self.get_global('back_button'), pygame_menu.events.BACK)


class MainMenu(BaseMenu):
    is_main = True
    translate_path = ['menu', 'main_menu']

    def format_menu(self):
        self.menu.add.button(self.get_text(*self.translate_path, 'play_button'), self.get_menu(EpisodeMenu).menu)
        self.menu.add.button(self.get_text(*self.translate_path, 'settings_button'), self.get_menu(SettingsMenu).menu)
        self.menu.add.button(self.get_global('exit_button'), pygame_menu.events.EXIT)


