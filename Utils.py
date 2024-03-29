from configparser import ConfigParser, SectionProxy
from locale import getdefaultlocale
from os.path import abspath, dirname
from sqlite3 import connect

import pygame


class DataBase:
    '''Класс для работы с базами данных sqlite3.

     Аргументы инициализации:
         *db_folder_path - Путь к папке с базами данных относительно C://: str

     Методы:
         *execute — выполнить запрос sqlite3.
         *get_text — Получить dict с текстом на выбранном языке (если он поддерживается)
         *get_sounds — Получить список звуков с кортежами (путь и сам звук pygame)
         *get_font — Возвращает шрифт с выбранным именем.
         *get_skins — Возвращает dict со всеми скинами и их вариациями.
    '''
    __slots__ = ['sound_db_path', 'selected_db_path', 'font_db_path',
                 'text_db_path', 'skins_db_path']

    def __init__(self, db_folder_path: str):
        self.sound_db_path: str = f'{db_folder_path}/sounds.db'
        self.font_db_path: str = f'{db_folder_path}/fonts.db'
        self.text_db_path: str = f'{db_folder_path}/text.db'
        self.skins_db_path: str = f'{db_folder_path}/skins.db'
        self.selected_db_path = self.sound_db_path

    def execute(self, command: str) -> str:
        with connect(self.selected_db_path) as database:
            cur = database.cursor()
            result: str = cur.execute(command).fetchall()
        return result

    def get_text(self) -> dict:
        self.selected_db_path = self.text_db_path
        if None in getdefaultlocale():
            lang = 'en'
        else:
            lang = getdefaultlocale()[0].split('_')[0].lower().strip()
        if lang not in ['ru', 'tr', 'en', 'az']:
            lang = 'en'
        result = self.execute(f'SELECT *\nFROM {lang}')[0]
        decryptor = {0: 'play', 1: 'shop', 2: 'faq', 3: 'settings',
                     4: 'faq_text', 5: 'skin_blocked', 6: 'ordinary_level_tip',
                     7: 'build_level_tip'}
        return {decryptor[index]: title for index, title in enumerate(result)}

    def get_skins(self) -> dict:
        decryptor = {0: 'folder_path', 1: 'jump', 2: 'sit', 3: 'stand'}
        self.selected_db_path: str = self.skins_db_path
        result: list = self.execute(f'SELECT *\nFROM skins')
        return {sprite[0]: {decryptor[index]: sprite_path
                            for index, sprite_path in enumerate(sprite[1:])}
                for sprite in result}

    def get_sounds(self) -> list([tuple, tuple, tuple, ...]):
        self.selected_db_path = self.sound_db_path
        return self.execute('SELECT *\nFROM sounds')

    def get_font(self, name) -> str:
        self.selected_db_path = self.font_db_path
        result = self.execute(
            f'SELECT path\nFROM fonts\nWHERE name = "{name}"')
        return result[0][0]


class Settings:
    '''Класс, который может анализировать и сохранять настройки из файла настроек (расширение: .ini)

     Аргументы инициализации:
         *settings_file_name - Путь к файлу настроек: str

     Методы:
         *all_settings — Разобрать все настройки и вернуть их.
         *save - Записать в настройки заданный словарь
    '''
    __slots__ = ['settings_path', 'settings_parser', 'settings']

    def __init__(self, settings_file_name: str):
        self.settings_path: str = f'./{settings_file_name}'
        self.settings_parser: ConfigParser = ConfigParser()
        self.settings = self.all_settings()

    def all_settings(self) -> dict:
        self.settings_parser.read(self.settings_path, encoding='utf-8')
        dirty_settings: SectionProxy = self.settings_parser[
            'ChristmasAdventures']
        fps = int(dirty_settings['fps'])
        skin: str = dirty_settings['skin']
        window_size = list(
            map(int, dirty_settings['window_size'].split('x')))
        path: str = dirname(abspath(__file__))
        gravity = float(dirty_settings['gravity'])
        step = int(dirty_settings['step'])
        jump_power = int(dirty_settings['jump_power'])
        number_of_games = int(dirty_settings['number_of_games'])
        return {'fps': fps, 'path': path,
                'window_size': window_size,
                'skin': skin, 'gravity': gravity,
                'step': step, 'jump_power': jump_power,
                'number_of_games': number_of_games, 'file': 'settings.ini',
                'visited_github': int(dirty_settings['visited_github'])}

    def save(self, new_settings: dict) -> None:
        for key in new_settings:
            self.settings_parser.set(
                'ChristmasAdventures', key, new_settings[key])
        with open(self.settings_path, 'w', encoding='utf-8') as settings_file:
            self.settings_parser.write(settings_file)


class Sounds:
    '''Класс для работы с базами данных sqlite3.

     Аргументы инициализации:
         *database — База данных звуков пути: str

     Методы:
         *get_sounds — Возвращает диктовку со всеми звуками из базы данных.
         *play — Воспроизвести звук по имени определенное количество раз.
         *stop — остановить воспроизведение выбранного звука.
         *stop_all — остановить ВСЕ звуки.

    '''
    __slots__ = ['database', 'sounds']

    def __init__(self, database):
        self.database = DataBase(database)
        self.sounds = self.get_sounds()
        self.sounds['step']['sound'].set_volume(0.5)

    def get_sounds(self) -> dict:
        sounds = self.database.get_sounds()
        return {name: {'path': path,
                       'sound': pygame.mixer.Sound(path)}
                for (name, path) in sounds}

    def play(self, name, loops=0) -> None:
        self.stop(name)
        self.sounds[name]['sound'].play(loops)

    def stop(self, name) -> None:
        self.sounds[name]['sound'].stop()

    def stop_all(self) -> None:
        for name in self.sounds:
            self.sounds[name]['sound'].stop()
