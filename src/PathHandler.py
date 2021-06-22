from sys import platform
from os import path
import re

if platform == 'win32': import winreg

class PathHandler:
    #bad_chars = ('*', ':', '?', '.', '"', '|', '/', '\\', '<', '>')
    bad_chars = re.compile(r'[*:?."|/\\<>]') # Put bad characters inside the square brackets
    def __init__(self, folder_path: str, temp_path: str, name: str, id_num: int, config: dict):
        self.path_dir = folder_path
        self.__format = config['type']
        file_name = config["name"].format(Id=id_num, Name=name)
        self.file_name = PathHandler.bad_chars.sub('', file_name)
        self._final_path = self.__set_path()
        self._temp_path = path.join(temp_path, f'temp-{id_num}')

    @property
    def valid(self):
        # This reg key if set to 1 removes the char limit for path
        long_paths_enabled = platform == 'win32' \
                             and winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                                                    r'SYSTEM\CurrentControlSet\Control\FileSystem'),
                                                     'LongPathsEnabled')[0] == 1
        return long_paths_enabled or (len(self.final_path) < 200)

    @property
    def unique(self):
        return not path.exists(self.final_path)

    @property
    def temp_path(self):
        return self._temp_path

    @property
    def final_path(self):
        return self._final_path

    def rename_path(self, name):
        self.file_name = PathHandler.bad_chars.sub('', name)
        self._final_path = self.__set_path()

    def __set_path(self):
        if self.__format == 'img': return path.join(f'{self.path_dir}', f'{self.file_name}')
        return path.join(f'{self.path_dir}', f'{self.file_name}.{self.__format}')
