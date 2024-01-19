import pygame
import pygame_gui

from Utils import DataBase


class Text(pygame.font.Font):
    '''Класс для отображения текста на экране

     Аргументы инициализации:
         *text — Текст, который вы хотите отобразить: str
         *code_name — специальное имя для текстового объекта для идентификации: str
         *settings - Dict с настройками из настроек класса: dict
         *position - Положение текста на экране [x, y]: список
         *font_size — Размер шрифта: int
         *font_path — Путь к файлу шрифта: str
         *font_name - Имя шрифта в базе данных (если нет пути): str

     Методы:
         *draw - Нарисовать себя на экране
         *get_font — Загрузить шрифт из базы данных.
         *get_text — Загрузить визуализированный текст
    '''
    __slots__ = ['settings', 'rendered_text', 'code_name']

    def __init__(self, text: str, code_name: str, settings: dict, position=None,
                 font_size=50, font_path=None, font_name=None):
        self.settings = settings
        self.code_name = code_name
        if font_path is None:
            if font_name is None:
                font_name = 'christmas'
            font_path = self.get_font(font_name)
        super().__init__(font_path, font_size)
        self.rendered_text = self.get_text(text, position)

    def get_font(self, font_name: str) -> str:
        db_path = f'{self.settings["path"]}/assets/database/'
        database = DataBase(db_path)
        database.get_skins()
        font_path = f"{self.settings['path']}/{database.get_font(font_name)}"
        return font_path

    def get_text(
            self, text: str,
            position: list = None) -> (pygame.font.Font.render, (int, int)):
        rendered_text = self.render(text, True, (255, 255, 255))
        if position == None:
            text_x = self.settings['window_size'][0] // 2 -\
                rendered_text.get_width() // 2
            text_y = 20
        else:
            text_x, text_y = position[0], position[1]
        return rendered_text, (text_x, text_y)

    def draw(self, screen) -> None:
        screen.blit(*self.rendered_text)


class Message(pygame_gui.windows.UIMessageWindow):
    '''Класс базового сообщения (окно сообщения)

     Аргументы инициализации:
         *text — Текст сообщения: ул.
         *code_name — специальное имя для поля сообщения для идентификации: str
         *manager — менеджер pygame_gui: pygame_gui.UIManager
         *position - Положение окна сообщения на экране [x, y]: список
         *size - Размер окна сообщения [ш, в]: список
         *title — заголовок окна сообщения: str

     Методы:
         *is_alive — Проверить, живо ли окно
    '''
    __slots__ = ['code_name']

    def __init__(self, text: str, code_name: str, manager: pygame_gui.UIManager,
                 position: list, size: list, title: str):
        rect = pygame.Rect((*position,), (*size,))
        super().__init__(rect=rect, window_title=title, html_message=text,
                         manager=manager)
        self.dismiss_button.text = 'Ok'
        self.dismiss_button.rebuild()
        self.code_name = code_name

    def is_alive(self) -> bool:
        if self.dismiss_button.pressed or self.close_window_button.pressed:
            return False
        return True


class Label(pygame_gui.elements.UIButton):
    '''Базовый класс меток

     Аргументы инициализации:
         *text — Текст метки: str
         *code_name — специальное имя для метки для идентификации: str
         *manager — менеджер pygame_gui: pygame_gui.UIManager
         *position — Положение метки на экране [x, y]: список
         *size - Размер этикетки [ш, в]: список

     Методы:
         *connect_to_button — соединяет метку с кнопкой.
         *move — просто пометить кнопку в выбранной позиции: нет.
    '''
    __slots__ = ['code_name']

    def __init__(self, text: str, code_name: str, manager: pygame_gui.UIManager,
                 position: list, size: list):
        label_rect = pygame.Rect((*position,), (*size,))
        super().__init__(label_rect, text, manager)
        self.code_name = code_name

    def move(self, position: list) -> None:
        self.rect.x = position[0]
        self.rect.y = position[1]

    def connect_to_button(self, button: pygame_gui.elements.UIButton,
                          window_size: list, label_w: int) -> None:
        label_x = button.rect.x + 46
        label_y = window_size[1] - 55
        label_w = label_w - button.rect.w - 5
        label_h = button.rect.h
        label_rect = pygame.Rect((label_x, label_y), (label_w, label_h))
        self.rect = label_rect
        main_color = self.colours['normal_bg']
        for theme in self.colours:
            if 'text' not in theme:
                self.colours[theme] = main_color
        self.rebuild()


class Button(pygame_gui.elements.UIButton):
    '''Базовый класс кнопки

     Аргументы инициализации:
         *text — Текст кнопки: str
         *code_name - Специальное имя для кнопки для идентификации: str
         *manager — менеджер pygame_gui: pygame_gui.UIManager
         *position - Положение кнопки на экране [x, y]: список
         *size - Размер кнопки [ш, в]: список

     Методы:
         *load_icon — Загрузите изображение и обрежьте его до стандартных размеров: pygame.Surface.
         *set_icon — Установить значок для кнопки: нет.
         *get_rect — Получить прямоугольник кнопки с координатами x, y, w и h: pygame.Rect
         *move — просто переместить кнопку в выбранное положение: нет.
         *is_pressed — Проверить, нажата кнопка или нет: bool
    '''
    __slots__ = ['code_name']

    def __init__(self, text: str, code_name: str, manager: pygame_gui.UIManager,
                 position: list, size: list = [50, 50]):
        relative_rect = self.get_rect((*position,), (*size,))
        super().__init__(relative_rect=relative_rect, text=text,
                         manager=manager)
        self.code_name = code_name

    def load_icon(self, icon_path) -> pygame.Surface:
        return pygame.transform.scale(pygame.image.load(icon_path), [50, 50])

    def set_icon(self, icon_path, is_pressed_version=True) -> None:
        icon_extension = '.' + icon_path.split('.')[-1]
        icon = self.load_icon(icon_path)
        if is_pressed_version:
            hovered_icon_path = '.'.join(icon_path.split(icon_extension)[:-1]) +\
                '_pressed' + icon_extension
            hovered_icon = self.load_icon(hovered_icon_path)
            self.hovered_image = hovered_icon
        self.normal_image = self.selected_image = icon
        self.rebuild()

    def get_rect(self, position: list, size: list) -> pygame.Rect:
        label_rect = pygame.Rect((*position,), (*size,))
        return label_rect

    def move(self, position: list) -> None:
        self.rect.x = position[0]
        self.rect.y = position[1]

    def is_pressed(self, event: pygame.event) -> bool:
        if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self:
                return True
        return False
