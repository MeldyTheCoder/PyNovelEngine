import json
import random
import re
import time
import math
import pygame
import os
import time

import npc
import scenes
import config

from npc import NPCObject
from screen import Screen
from _thread import start_new_thread
from typing import Union

class BasicAlert(object):
    def __init__(self, screen: Screen, player: NPCObject, text: str):
        self.surf = screen.screen
        self.screen = screen
        self.player = player
        self.player_name = self.player.name
        self.player_font = config.default_dialog_font_name
        self.text = text
        self.color = (0, 0, 255)
        self.text_color = self.player.text_color
        self.close_callback = config.dialog_close_callback
        self.blank_width = config.dialog_padding_width(self.surf.get_width())
        self.blank_height = config.dialog_padding_height(self.surf.get_height())
        self.font = config.default_dialog_font_text
        self.blank_x = config.dialog_place_x(self.surf.get_width())
        self.blank_y = config.dialog_place_y(self.surf.get_height())
        self.blank = pygame.transform.scale(pygame.image.load(os.path.join(config.working_directory, 'pictures', 'blank.png')), (self.blank_width, self.blank_height))
        self.blank = pygame.Surface((self.blank_width, self.blank_height))
        self.blank_rect = self.blank.get_rect(center=(self.blank_x, self.blank_y))
        self.blank.set_alpha(0)
        self.show = True
        self.hide = False
        self.close_without_anim = True
        self.alpha_step = 10
        self.text_alpha = 0
        self.start_time = pygame.time.get_ticks()

    def animation_show(self):
        def proc():
            if not(self.hide):
                for i in range(0, config.dialog_max_alpha, self.alpha_step):
                    self.blank.set_alpha(i)
                    pygame.time.wait(20)
                for i in range(0, 255, self.alpha_step):
                    self.text_alpha = i
                    pygame.time.wait(100)
        start_new_thread(proc, ())


    def animation_hide(self):
        def proc():
            if self.hide:
                for i in reversed(range(0, config.dialog_max_alpha, self.alpha_step)):
                    self.blank.set_alpha(i)
                    pygame.time.wait(15)
                self.text_alpha = 0
        start_new_thread(proc, ())

    def animation_close(self):
        def proc():
            if self.hide:
                for i in reversed(range(0, config.dialog_max_alpha, self.alpha_step)):
                    self.blank.set_alpha(i)
                    pygame.time.wait(15)
                self.text_alpha = 0
                self.show = False
        start_new_thread(proc, ())


    def cooldown_timer(self):
        return bool(pygame.time.get_ticks() - self.start_time >= config.default_dialog_cooldown)

    def update_timer(self):
        self.start_time = pygame.time.get_ticks()

    def event_check(self, event: pygame.event):
        if self.show and self.cooldown_timer():
            if self.close_callback(event) and self.hide:
                self.show_dialog()
            elif self.close_callback(event) and not(self.hide):
                self.close_dialog()
            self.update_timer()

    def text_splitlines(self, text: str, pos: tuple[int], font: pygame.font):
        render_list = []
        words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
        space = font.size(' ')[0]  # The width of a space.
        max_width, max_height = self.blank.get_size()
        x, y = pos
        for line in words:
            for word in line:
                word_surface = font.render(word, 0, self.text_color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width:
                    x = pos[0]  # Reset the x.
                    y += word_height  # Start on new row.
                render_list.append((word_surface, (x, y)))
                x += word_width + space
            x = pos[0]  # Reset the x.
            y += word_height  # Start on new row.
        return render_list

    def draw_text(self, isPlayerLabel: bool = False):
        if isPlayerLabel:
            text = self.player_name
            rect = (config.dialog_padding_name_x(self.blank_width), config.dialog_padding_name_y(self.blank_height))
            font = config.default_dialog_font_name
        else:
            text = self.text
            rect = (config.dialog_padding_text_x(self.blank_width), config.dialog_padding_text_y(self.blank_height))
            font = config.default_dialog_font_text

        text_rects = self.text_splitlines(text, rect, font)
        for rect_text in text_rects:
            rect_text[0].set_alpha(self.text_alpha)
            yield rect_text

    def draw(self, render_offset: list[int] = [0, 0]):
        if self.show:
            for render_player, rect_player in self.draw_text(True):
                rect = self.screen.convert_render_offset(rect_player)
                self.blank.blit(render_player, rect_player)
            for render_text, rect_text in self.draw_text(False):
                #rect = self.screen.convert_render_offset(rect_text)
                self.blank.blit(render_text, rect_text)
            blank_rect = self.screen.convert_render_offset(self.blank_rect)
            self.surf.blit(self.blank, blank_rect)

    def close_dialog(self):
        self.hide = True
        if self.close_without_anim:
            self.show = False
        else:
            self.animation_close()

    def hide_dialog(self):
        self.hide = True
        self.animation_hide()

    def show_dialog(self):
        self.hide = False
        self.animation_show()

class DialogManager:
    def __init__(self, screen: Screen):
        self.alerts = []
        self.intervals = {}
        self.current_dialog = None
        self.surf = screen.screen
        self.screen = screen
        self.photos = {}
        self.scenes = {}
        self.current_scene = None
        self.end = False
        self.timer = pygame.time.get_ticks()
        self.dialog_times = {}
        self.dialog_checker()

    def add_text_dialog(self, player: npc.NPCObject, text: str):
        dialog = BasicAlert(self.screen, player, text)
        self.alerts.append(dialog)

    def wait_until_dialog_lapse(self, index: int = -1):
        try:
            if index != -1:
                dialog = self.alerts[index]
            else:
                dialog = self.alerts[-1]

            if dialog:
                while dialog.show:
                    pass
        except:
            pass

    def set_image(self, image: Union[str, os.PathLike, pygame.Surface]):
        if not self.alerts:
            self.photos['0'] = image
            return
        last_alert = self.alerts[-1]
        index = self.alerts.index(last_alert)
        self.photos[str(index)] = image

    def set_scene(self, scene: scenes.BasicScene):
        if not self.alerts:
            self.scenes['0'] = scene
            return
        last_alert = self.alerts[-1]
        index = self.alerts.index(last_alert)
        scene.dialog_manager = self
        self.scenes[str(index)] = scene

    def get_image(self, index: int):
        try:
            return self.photos[str(index)]
        except:
            return None

    def get_scene(self, index: int):
        try:
            return self.scenes[str(index)]
        except:
            return None

    def has_scene(self, index: int):
        return bool(self.get_scene(index))

    def has_image(self, index: int):
        return bool(self.get_image(index))

    def dialog_checker(self):
        def proc():
            while not(self.end):
                if not self.current_dialog and not self.alerts:
                    continue

                elif not self.current_dialog and self.alerts:
                    self.current_dialog = self.alerts[0]
                    if self.has_scene(0):
                        self.current_scene = self.get_scene(0)
                        self.current_scene.animate()
                    elif self.has_image(0):
                        self.screen.set_background(self.get_image(0))
                    self.current_dialog.show_dialog()

                elif self.current_dialog and self.current_dialog.show == False:
                    try:
                        ind_old = self.alerts.index(self.current_dialog)
                        self.add_to_timer(ind_old)
                        ind = ind_old + 1

                        if self.has_dialog(ind):
                            if self.has_interval(ind_old):
                                self.wait(self.get_interval(ind_old))

                            self.current_dialog = self.alerts[ind]
                            if self.has_scene(ind):
                                self.current_scene = self.get_scene(ind)
                                self.current_scene.animate()
                            elif self.has_image(ind):
                                self.screen.set_background(self.get_image(ind))
                            self.current_dialog.show_dialog()
                        else:
                            self.end = True
                            self.current_dialog = None
                            break
                        #self.alerts.pop(ind)
                    except Exception as e:
                        raise
        start_new_thread(proc, ())

    def has_interval(self, alert_index: int):
        try:
            return bool(self.get_interval(alert_index))
        except:
            return False

    def get_interval(self, alert_index: int):
        try:
            return self.intervals[str(alert_index)]
        except:
            return 0

    def has_dialog(self, ind: int):
        try:
            d = self.alerts[ind]
            return True
        except:
            return False

    def wait(self, time_sleep: int):
        return pygame.time.wait(time_sleep)

    def add_to_timer(self, index: int):
        self.dialog_times[str(index)] = pygame.time.get_ticks()

    def get_timer(self, index: int):
        try:
            return self.dialog_times[str(index)]
        except:
            return 0

    def check_timer(self, index: int, time: int):
        timer = self.get_timer(index)
        return (pygame.time.get_ticks() - timer) >= time



    def add_interval(self, time: int):
        try:
            last_alert = self.alerts[-1]
            last_alert.close_without_anim = False
            alert_index = self.alerts.index(last_alert)
            self.intervals[str(alert_index)] = time*1000
        except:
            pass

    def dialog_event_check(self, event: pygame.event):
        if self.current_dialog and self.current_dialog.show:
            self.current_dialog.event_check(event)

    def draw_dialog(self, render_offset: list[int] = [0, 0]):
        if self.current_scene:
            self.current_scene.draw()
        if self.current_dialog and self.current_dialog.show:
            self.current_dialog.draw(render_offset)


