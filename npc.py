import os
from types import FunctionType
import config
import os
from typing import Union

class NPCObject(object):
    def __init__(self, name: str = '???', text_color: tuple[int] = (206, 209, 207), photo_path: Union[str, os.PathLike] = os.path.join(config.picture_directory, 'npc')):
        self.text_color = text_color
        self.name = name
        self.photo_path = photo_path
        data = self.get_data()
        self.set_attrs(data)

    def set_attrs(self, data: dict):
        for key, val in data.items():
            setattr(self, key, val)

    def get_data(self):
        data = {key: val for key, val in self.__dict__.items()}
        new_args = list(set(dir(self.__class__)) - set(dir(NPCObject)))
        for arg in new_args:
            val = getattr(self.__class__, arg)
            if not isinstance(val, FunctionType):
                data[arg] = val
        return data

class Maksim(NPCObject):
    name = 'Максим'
    full_name = 'Максим Максимов'
    text_color = (192, 84, 219)
    photo_path = os.path.join(config.picture_directory, 'maksim')
