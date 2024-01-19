'''Этот модуль содержит все игровые ошибки'''


class SpriteError(Exception):
    '''Не могу найти ошибку файла спрайта'''
    __slots__ = ['text']

    def __init__(self):
        super().__init__()
        self.text = 'Не удаётся найти файл спрайта'
