import os

import config
import pygame

from typing import Union
from screen import Screen
from _thread import start_new_thread

class BasicScene(object):
    def __init__(self, screen: Screen, images: list[pygame.Surface], rect: tuple[int] = (0, 0), **kwargz):
        self.draw_args = {}
        self.screen = screen
        self.rect = rect
        self.images = images
        self.current_image = None
        self.started = True
        self.end = False
        self.dialog_manager = None
        self.current_alpha = 300
        self.max_alpha = 300
        self.alpha_step = 10
        self.fade = False
        self.add_screen_image()

    def fade_image(self, ind: int = 0):
        if ind:
            current_image = self.get_image(ind)
        else:
            if self.current_image:
                current_image = self.current_image
            else:
                current_image = self.images[0]
        self.fade = True
        for i in reversed(range(0, self.max_alpha, self.alpha_step)):
            current_image.set_alpha(i)

    def unfade_image(self, ind: int = 0):
        if ind:
            current_image = self.get_image(ind)
        else:
            if self.current_image:
                current_image = self.current_image
            else:
                current_image = self.images[0]

        self.fade = False
        for i in range(0, self.max_alpha, self.alpha_step):
            current_image.set_alpha(i)

    def add_screen_image(self):
        if self.screen.background_image:
            self.images.append(self.screen.background_image)

    def wait_until_fade(self):
        while not(self.fade):
            pygame.time.wait(10)

    def wait_until_unfade(self):
        while self.fade:
            pygame.time.wait(10)

    def animate(self):
        next_image = self.get_next_image()
        if next_image:
            self.screen.set_background(next_image)

    def has_next_image(self):
        return bool(self.get_next_image())

    def set_image(self, ind: int = 0):
        try:
            image = self.get_image(ind)
            if image:
                self.current_image = image
        except:
            pass

    def has_previous_image(self):
        return bool(self.get_previous_image())

    def get_image(self, ind: int = 0):
        try:
            return self.images[ind]
        except:
            return None

    def get_next_image(self):
        try:
            if self.current_image and self.images:
                return self.images[self.images.index(self.current_image)+1]
            elif self.images:
                return self.images[0]
            elif not self.images and self.current_image:
                return None
        except:
            return None

    def get_previous_image(self):
        try:
            if self.current_image and self.images:
                return self.images[self.images.index(self.current_image) - 1]
            elif self.images:
                return self.images[0]
            elif not self.images and self.current_image:
                return None
        except:
            return None

    def draw(self):
        if self.current_image:
            rect = self.screen.convert_render_offset(self.rect)
            self.screen.screen.blit(self.current_image, rect)


class FadeSceneSingle(BasicScene):
    def animate(self):
        def proc():
            next_image = self.get_next_image()
            if next_image:
                next_image = self.images.index(next_image)
                self.fade_image()
                self.wait_until_fade()
                self.set_image()
                self.unfade_image(next_image)
        start_new_thread(proc, ())


class FadeEnd(BasicScene):
    def animate(self):
        def proc():
            if self.dialog_manager:
                print('dialog manager init')
                self.dialog_manager.wait_until_dialog_lapse()
            pygame.time.wait(1000)
            self.screen.fade_screen()
            self.wait_until_fade()
        start_new_thread(proc, ())


class FadeTextUnfade(BasicScene):
    "args: text, font, color, rect"
    def animate(self):
        def proc():
            if self.dialog_manager:
                self.dialog_manager.wait_until_dialog_lapse()
            pygame.time.wait(1000)
            self.screen.fade_screen()
            self.wait_until_fade()
            self.screen.unfade_screen()

        start_new_thread(proc, ())
