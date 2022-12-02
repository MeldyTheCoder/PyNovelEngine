import json
import os
import random
import re
import time

import bs4
import pygame
import math
import pygame_menu
import config

from _thread import start_new_thread
from typing import Union, Callable, Any, Optional




class Screen:
    def __init__(self, resolution: tuple[int], fullscreen: bool = True):
        self.resolution = resolution
        self.fullscreen = fullscreen
        self.music = Music()
        self.lang_manager = LanguageManager('en')
        if self.fullscreen:
            self.screen = pygame.display.set_mode(self.resolution, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.resolution)
        self.background_image = None
        self.image_rect = (0, 0)
        self.draw_objects = []
        self.render_offset = [0, 0]
        self.fade = False
        self.shake = False
        self.fps = 60
        self.fade_surface = pygame.Surface(self.resolution)
        self.fade_rect = (0, 0)
        self.fade_alpha = 0

    def set_background(self, img: Union[str, os.PathLike, pygame.Surface]):
        if isinstance(img, pygame.Surface):
            self.background_image = pygame.transform.scale(img, self.resolution)

        elif isinstance(img, os.PathLike) or isinstance(img, str):
            self.background_image = pygame.transform.scale(pygame.image.load(img), self.resolution)

    def add_draw_object(self, object: Callable):
        if not object in self.draw_objects:
            self.draw_objects.append(object)

    def remove_draw_object(self, index: int):
        try:
            self.draw_objects.pop(index)
        except:
            pass

    def get_fade_surface(self):
        self.fade_surface = pygame.Surface(self.resolution)
        return self.fade_surface, self.fade_rect

    def get_background(self):
        return self.background_image

    def wait(self, seconds: int):
        pygame.time.wait(seconds*1000)


    def set_resolution(self, width: int, height: int):
        self.width = width
        self.height = height
        self.get_fade_surface()
        self.screen = pygame.display.set_mode((self.width, self.height))

    def get_img_size(self):
        if self.background_image:
            return self.background_image.get_rect()
        return (0, 0)

    def shake_screen(self, timer: int = 3):
        self.shake = True
        def proc():
            if self.shake:
                self.render_offset = [0, 0]
                time_start = pygame.time.get_ticks()
                while (pygame.time.get_ticks() - time_start) <= timer*1000:
                    self.render_offset[0] = random.randint(0, 4)
                    self.render_offset[1] = random.randint(0, 4)
                self.shake = False
        start_new_thread(proc, ())


    def fade_animation_screen(self, time_fade: int = 5, on_fade: Callable = None):
        self.fade = True
        def proc():
            fade_start_time = pygame.time.get_ticks()
            fade_time = time_fade*1000
            self.fade = True
            self.fade_alpha = 0
            while self.fade_alpha < 300:
                self.fade_alpha += 3
                pygame.time.wait(1)
            try:
                if on_fade:
                    on_fade()
            except:
                pass
            while pygame.time.get_ticks() - fade_start_time < fade_time:
                pass
            while self.fade_alpha > 0:
                self.fade_alpha -= 3
                pygame.time.wait(1)
            self.fade = False

        start_new_thread(proc, ())

    def unfade_screen(self, time: int = 5):

        max_alpha = 300
        def proc():
            self.fade_alpha = max_alpha
            while self.fade_alpha > 0:
                self.fade_alpha -= 3
                pygame.time.wait(15)

            self.fade = False
        start_new_thread(proc, ())

    def fade_screen(self, time: int = 5):
        max_alpha = 300
        def proc():
            self.fade_alpha = 0
            while self.fade_alpha < max_alpha:
                self.fade_alpha += 3
                pygame.time.wait(15)
            self.fade = True
        start_new_thread(proc, ())

    def wait_for_fade(self):
        while not(self.fade):
            pygame.time.wait(10)

    def wait_for_unfade(self):
        while self.fade:
            pygame.time.wait(10)

    def convert_render_offset(self, rect: tuple[int]):
        return (rect[0] + self.render_offset[0], rect[1] + self.render_offset[1])

    def draw_text(self, text: str, font: pygame.font, rect: tuple[int] = (0, 0), color: tuple[int] = (0, 255, 0), time: int = 0):
        textobj = font.render(text, True, color)
        textrect = textobj.get_rect(center=rect)
        self.screen.blit(textobj, textrect)

    def draw_screen(self):
        self.screen.fill((0, 0, 0))

        if self.background_image:
            if self.shake:
                rect = (self.image_rect[0] + self.render_offset[0], self.image_rect[1] + self.render_offset[1])
            else:
                rect = self.image_rect
            self.screen.blit(self.background_image, rect)

        for obj in self.draw_objects:
            obj(self.render_offset)

        #if self.fade:
        self.fade_surface.fill((0, 0, 0))
        self.fade_surface.set_alpha(self.fade_alpha)
        self.screen.blit(self.fade_surface, self.fade_rect)
        pygame.display.flip()


class Music:
    def __init__(self):
        self.max_volume = 100
        self.min_volume = 0
        pygame.mixer.init()

    def start(self, music: Union[str, os.PathLike], loop: int = -1, volume: int = 50):
        if volume > self.max_volume or volume < self.min_volume:
            volume = 50
        pygame.mixer.init()
        pygame.mixer.music.load(music)
        pygame.mixer.music.play(loop)
        pygame.mixer.music.set_volume(volume/100)

    def pause(self):
        pygame.mixer.music.pause()

    def unpause(self):
        pygame.mixer.music.unpause()

    def set_volume(self, volume: int):
        if volume > self.max_volume or volume < self.min_volume:
            volume = 50
        pygame.mixer.music.set_volume(volume/100)

    def get_volume(self):
        return pygame.mixer.music.get_volume()

class MenuSoundManager:
    def __init__(self):
        self.volume = 0
        self.engine = pygame_menu.Sound()



class LanguageManager:
    def __init__(self, pre_lang: str = 'en'):
        self.language_path = config.language_directory
        self.curr_language = pre_lang
        self.default_lang = 'en'
        self.root_tag = 'root'
        self.menu_path = []
        self.reader = bs4.BeautifulSoup(self.__read(self.curr_language), features='xml')

    def set_language(self, lang: str):
        self.curr_language = lang

    def __get_lang_path(self, lang: str = ''):
        if not lang:
            lang = self.curr_language
        path = os.path.join(self.language_path, f'{lang}.xml')
        if not os.path.exists(path):
            print('err')
            lang = 'ru'
            return self.__get_lang_path(lang)
        return path

    def __read(self, lang: str = ''):
        if not lang:
            lang = self.curr_language
        path = self.__get_lang_path(lang)
        with open(path, 'r', encoding='utf-8') as f:
            data = f.read()
        return data

    def get_global(self, var: str, lang: str = '') -> str:
        if not lang:
            lang = self.curr_language
        return self.get_text(lang, 'globals', var)

    def get_lang_index(self, lang: str = ''):
        if not lang:
            lang = self.curr_language
        data = self.get_langs()
        for index, d in enumerate(data):
            if d[1] == lang:
                return index

    def get_langs(self):
        lang_files = list(os.walk(self.language_path))[0][2]
        langs = [i.split('.')[0] for i in lang_files]
        info = [(self.get_info('name', lang), self.get_info('code', lang)) for lang in langs]
        return info



    def get_info(self, key: str, lang: str = ''):
        if not lang:
            lang = self.curr_language
        return self.get_text(lang, 'info', key)

    def get_text(self, lang: str = '', *args) -> str:
        if not lang:
            lang = self.curr_language
        args = list(args)
        #if self.menu_path:
            #args = self.menu_path + args
        args.insert(0, self.root_tag)
        data = self.reader
        for arg in args:
            data = data.find(arg)
        return data.get_text()
