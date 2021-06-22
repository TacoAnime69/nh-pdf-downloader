from sys import platform
import os

if platform == 'win32': import winreg

class PathHandler:
    def __init__(self, folder_path: str, temp_path: str, name: str, id_num: int, config: dict):
        self.path_dir = folder_path
        self.__format = config['type']
        self.bad_chars = ['*', ':', '?', '.', '"', '|', '/', '\\', '<', '>']
        file_name = config["name"].format(Id=id_num, Name=name)
        self.file_name = self.__problem_char_rm(file_name)
        self._final_path = self.__set_path()
        self._temp_path = os.path.join(temp_path, f'temp-{id_num}')

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
        return not os.path.exists(self.final_path)

    @property
    def temp_path(self):
        return self._temp_path

    @property
    def final_path(self):
        return self._final_path

    def rename_path(self, name):
        self.file_name = self.__problem_char_rm(name)
        self._final_path = self.__set_path()

    def __set_path(self):
        if self.__format == 'img': return os.path.join(f'{self.path_dir}', f'{self.file_name}')
        return os.path.join(f'{self.path_dir}', f'{self.file_name}.{self.__format}')

    def __problem_char_rm(self, address: str) -> str:
        """
        Function to remove problematic characters of a path.
        Any characters that causes the "windows can't create this path because it 
        contains illegal characters" should be removed here
        Parameters
        ----------
        address : str
            The path string
        Returns
        -------
        str
            The address with the characters removed
        """
        result = address
        for char in self.bad_chars:
            # go through each character in the set and replace with nothing
            result = result.replace(char, '')
        return result
