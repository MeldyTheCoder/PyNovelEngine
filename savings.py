import pickle
import os
import config
from typing import Union, Any


class PathManager:
    def get_dir_name(self, path: Union[str, os.PathLike]):
        return os.path.dirname(path)

    def check_path(self, path: Union[str, os.PathLike]):
        return os.path.exists(path)

    def ensure_path(self, path: Union[str, os.PathLike]):
        dirname = self.get_dir_name(path)
        if not self.check_path(dirname):
            os.makedirs(dirname)
        if not self.check_path(path):
            with open(path, 'w'):
                pass

    def is_directory(self, path: Union[str, os.PathLike]):
        return os.path.isdir(path)

    def read(self, path: Union[str, os.PathLike]):
        if self.check_path(path) and not(self.is_directory(path)):
            with open(path, 'r') as f:
                data = f.read()
            return data
        return None

    def write(self, path: Union[str, os.PathLike], value: Any):
        self.ensure_path(path)
        with open(path, 'w') as f:
            f.write(str(value))




class Saving:
    def __init__(self):
        self.path = config.savings_path
        self.path_manager = PathManager()

    def load(self, key: str = ''):
        data = self.path_manager.read(self.path)
        if not data:
            return {}
        data = pickle.loads(data)
        if not key:
            return data
        return data[key]

    def update(self, key: str, val: Any):
        old_data = self.load()
        old_data[key] = val
        self.save(old_data)

    def save(self, data: dict):
        old_data = self.load()
        old_data.update(data)
        data = pickle.dumps(old_data)
        self.path_manager.write(self.path, data)
