import os
import pygame


pygame.font.init()

#############################################################
# Диалоговые окна #
###################

# Имя игры
game_name = 'Game 1'

# путь к папке проекта
working_directory = os.path.dirname(os.path.abspath(__file__))

# путь к папке со шрифтами
fonts_directory = os.path.join(working_directory, 'fonts')

# шрифт текста в диалогах
default_dialog_font_text = pygame.font.Font(os.path.join(fonts_directory, 'font2.ttf'), 25)

# шрифт текста имени персонажа
default_dialog_font_name = pygame.font.SysFont('Arial', 18)

# цвет текста диалога
default_dialog_color = (227, 242, 19)

# интервал между переключениями диалогов
default_dialog_cooldown = 1000


dialog_close_callback = lambda event: (event.type == pygame.MOUSEBUTTONDOWN) and (event.button == 1)

# максимальная прозрачность диалога
dialog_max_alpha = 250

# ширина окна диалога
dialog_padding_width = lambda width: width - 40*2

# длина окна диалога
dialog_padding_height = lambda height: height//5

# координата размещения окна диалога по X
dialog_place_x = lambda x: x // 2

# координата размещения окна диалога по Y
dialog_place_y = lambda y: y - (y // 5)

# координата размещения текста в окне диалога по X
dialog_padding_text_x = lambda x: 30

# координата размещения текста в окне диалога по Y
dialog_padding_text_y = lambda y: 30

# координата размещения текста в окне диалога по X
dialog_padding_name_x = lambda x: 10

# координата размещения текста в окне диалога по Y
dialog_padding_name_y = lambda y: 0

# вертикальный отступ между строчками в диалоговом окне
dialog_text_padding = lambda p: p + 5

menu_width_padding = lambda p: 20

menu_height_padding = lambda p: 10

########################################################
# Сохранения #
##############


# путь к фото-файлам
picture_directory = os.path.join(working_directory, 'pictures')

# путь к аудио-файлам
sounds_directory = os.path.join(working_directory, 'sounds')

# папка с переводами
language_directory = os.path.join(working_directory, 'languages')

# путь к файлу сохранений
savings_path = os.path.join(working_directory, 'savedata', 'saving.data')
