import os

import config
import screen
import menu
import alerts
import pygame

from savings import PathManager
from npc import Maksim
from scenes import FadeSceneSingle, FadeEnd

pygame.font.init()
pygame.init()
width = pygame.display.Info().current_w
height = pygame.display.Info().current_h


p = PathManager()
sizes = (width, height)

scr = screen.Screen(sizes, True)

def menu_example():
    menu_obj = menu.MainMenu(scr, config.game_name)
    scr.add_draw_object(menu_obj.draw)
    scr.set_background(os.path.join(config.picture_directory, 'menu.jpg'))

    run = True
    while run:
        scr.draw_screen()

def game_example():
    alert_obj = alerts.DialogManager(scr)
    scr.add_draw_object(alert_obj.draw_dialog)

    img1 = os.path.join(config.picture_directory, 'slide1.png')

    alert_obj.set_image(img1)
    alert_obj.add_text_dialog(Maksim, 'После того как вы нажмете ЛКМ, будет пауза в 3 секунды...')
    alert_obj.add_interval(3)
    alert_obj.add_text_dialog(Maksim, 'А теперь изображение сменилось...')

    img2 = os.path.join(config.picture_directory, 'slide2.png')

    alert_obj.set_image(img2)
    alert_obj.add_text_dialog(Maksim, 'Конец...')
    alert_obj.set_scene(FadeEnd(scr, [img2]))

    run = True
    while run:
        scr.draw_screen()
        for event in pygame.event.get():
            alert_obj.dialog_event_check(event)

# Чтобы посмотреть меню:
menu_example()

# Чтобы посмотреть игровой процесс:
#game_example()

