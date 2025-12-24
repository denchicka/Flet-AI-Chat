import flet as ft  # Импортируем фреймворк Flet для создания пользовательского интерфейса

class AppStyles:
    """
        Класс для централизованного хранения всех стилей приложения.

        Содержит константы и конфигурации для всех визуальных элементов интерфейса:
            - Настройки страницы
            - Стили компонентов чата
            - Настройки кнопок
            - Параметры полей ввода
            - Конфигурации layout элементов
    """

    # Основные настройки страницы приложения
    PAGE_SETTINGS = {
        "title": "AI Chat",                                    # Заголовок окна приложения
        "vertical_alignment": ft.MainAxisAlignment.CENTER,     # Вертикальное выравнивание содержимого по центру
        "horizontal_alignment": ft.CrossAxisAlignment.CENTER,  # Горизонтальное выравнивание содержимого по центру
        "padding": ft.padding.only(top=60, left=20, right=20, bottom=20), # Отступы от краев окна
        "bgcolor": ft.Colors.GREY_900,                        # Темно-серый цвет фона для темной темы
        "theme_mode": ft.ThemeMode.DARK,                      # Использование темной темы оформления
    }

    # Настройки области истории чата
    CHAT_HISTORY = {
        "expand": True,       # Разрешаем расширение на все доступное пространство
        "spacing": 10,        # Отступ между сообщениями в пикселях
        "height": 400,        # Фиксированная высота области чата
        "auto_scroll": True,  # Автоматическая прокрутка к новым сообщениям
        "padding": 20,        # Внутренние отступы области чата
    }

    # Настройки поля ввода сообщений
    MESSAGE_INPUT = {
        "height": 50,                        # Высота поля ввода в пикселях
        "multiline": False,                  # Запрет многострочного ввода
        "text_size": 16,                     # Размер шрифта текста
        "color": ft.Colors.WHITE,            # Цвет вводимого текста
        "bgcolor": ft.Colors.GREY_800,       # Цвет фона поля ввода
        "border_color": ft.Colors.BLUE_400,  # Цвет границы поля
        "cursor_color": ft.Colors.WHITE,     # Цвет курсора ввода
        "content_padding": 5,                # Внутренние отступы текста
        "border_radius": 8,                  # Радиус скругления углов
        "hint_text": "Введите сообщение здесь...",  # Текст-подсказка в пустом поле
        "shift_enter": True,                 # Включение отправки по Shift+Enter
    }

    # Настройки кнопки отправки сообщения
    SEND_BUTTON = {
        "text": "Отправка",                  # Текст на кнопке
        "icon": ft.Icons.SEND,               # Иконка отправки сообщения
        "style": ft.ButtonStyle(             # Стиль оформления кнопки
            color=ft.Colors.WHITE,           # Цвет текста кнопки
            bgcolor=ft.Colors.BLUE_700,      # Цвет фона кнопки
            padding=10,                      # Внутренние отступы
        ),
        "tooltip": "Отправить сообщение",    # Всплывающая подсказка при наведении
        "height": 40,                        # Высота кнопки
        "width": 130,                        # Ширина кнопки
    }

    # Настройки кнопки сохранения диалога
    SAVE_BUTTON = {
        "text": "Сохранить",                 # Текст на кнопке
        "icon": ft.Icons.SAVE,               # Иконка сохранения
        "style": ft.ButtonStyle(             # Стиль оформления кнопки
            color=ft.Colors.WHITE,           # Цвет текста
            bgcolor=ft.Colors.BLUE_700,      # Цвет фона
            padding=10,                      # Внутренние отступы
        ),
        "tooltip": "Сохранить диалог в файл", # Всплывающая подсказка
        "width": 130,                        # Ширина кнопки
        "height": 40,                        # Высота кнопки
    }

    # Настройки кнопки очистки истории
    CLEAR_BUTTON = {
        "text": "Очистить",                  # Текст на кнопке
        "icon": ft.Icons.DELETE,             # Иконка удаления
        "style": ft.ButtonStyle(             # Стиль оформления кнопки
            color=ft.Colors.WHITE,           # Цвет текста
            bgcolor=ft.Colors.RED_700,       # Красный цвет фона для предупреждения
            padding=10,                      # Внутренние отступы
        ),
        "tooltip": "Очистить историю чата",   # Всплывающая подсказка
        "width": 130,                        # Ширина кнопки
        "height": 40,                        # Высота кнопки
    }

    # Настройки кнопки показа аналитики
    ANALYTICS_BUTTON = {
        "text": "Аналитика",                 # Текст на кнопке
        "icon": ft.Icons.ANALYTICS,          # Иконка аналитики
        "style": ft.ButtonStyle(             # Стиль оформления кнопки
            color=ft.Colors.WHITE,           # Цвет текста
            bgcolor=ft.Colors.GREEN_700,     # Зеленый цвет фона
            padding=10,                      # Внутренние отступы
        ),
        "tooltip": "Показать аналитику",     # Всплывающая подсказка
        "width": 130,                        # Ширина кнопки
        "height": 40,                        # Высота кнопки
    }

    # Настройки кнопки настроек (шестеренки)
    SETTINGS_BUTTON = {
        "icon": ft.Icons.SETTINGS,          # Иконка кнопки
        "icon_color": ft.Colors.GREY_400,   # Цвет кнопки
        "tooltip": "Настройки почты",       # Всплывающая подсказка
    }

    # Поле ввода токена Telegram
    TELEGRAM_INPUT = {
        "label": "Telegram Bot Token",      # Заголовок поля
        "password": True,                   # Скрывать ли вводимый текст
        "can_reveal_password": True,        # Можно ли посмотреть введенный текст
        "width": 400,                       # Ширина поля
        "border_color": ft.Colors.BLUE_400, # Цвет обводки
        "bgcolor": ft.Colors.GREY_800,      # Цвет заднего фона
        "color": ft.Colors.WHITE,           # Цвет вводимого текста
    }

    # Поле ввода получателя (email или ID)
    RECIPIENT_INPUT = {
        "label": "Получатель уведомлений",  # Заголовок поля
        "width": 400,                       # Ширина поля
        "border_color": ft.Colors.BLUE_400, # Цвет обводки
        "bgcolor": ft.Colors.GREY_800,      # Цвет заднего фона
        "color": ft.Colors.WHITE,           # Цвет вводимого текста
    }

    # Поля внутри диалогового окна настроек (Login/Password)
    SETTINGS_INPUT_FIELD = {
        "width": 300,                       # Ширина поля
        "border_color": ft.Colors.GREY_600, # Цвет обводки
        "bgcolor": ft.Colors.GREY_800,      # Цвет заднего фона
        "color": ft.Colors.WHITE,           # Цвет вводимого текста
        "text_size": 14,                    # Размер шрифта
    }

    # Контейнер содержимого диалога настроек
    SETTINGS_DIALOG_COLUMN = {
        "height": 200,                      # Высота окна
        "tight": True,                      # Настройка "растягивания"
        "spacing": 20,                      # Отступы
        "alignment": ft.MainAxisAlignment.CENTER, # Позиционирование
    }

    # Настройки строки с полем ввода и кнопкой отправки
    INPUT_ROW = {
        "spacing": 10,                                    # Отступ между элементами
        "alignment": ft.MainAxisAlignment.SPACE_BETWEEN,  # Распределение пространства между элементами
        "width": 920,                                    # Общая ширина строки
    }

    # Настройки строки с кнопками управления
    CONTROL_BUTTONS_ROW = {
        "spacing": 10,                             # Отступ между кнопками
        "alignment": ft.MainAxisAlignment.CENTER,  # Выравнивание кнопок по центру
    }

    # Настройки колонки с элементами управления
    CONTROLS_COLUMN = {
        "spacing": 20,                                    # Отступ между элементами
        "horizontal_alignment": ft.CrossAxisAlignment.CENTER,  # Выравнивание по центру по горизонтали
    }

    # Настройки главной колонки приложения
    MAIN_COLUMN = {
        "expand": True,                                   # Разрешение расширения
        "spacing": 20,                                    # Отступ между элементами
        "alignment": ft.MainAxisAlignment.CENTER,         # Вертикальное выравнивание по центру
        "horizontal_alignment": ft.CrossAxisAlignment.CENTER,  # Горизонтальное выравнивание по центру
    }

    # Настройки поля поиска модели
    MODEL_SEARCH_FIELD = {
        "width": 400,                        # Ширина поля в пикселях
        "border_radius": 8,                  # Радиус скругления углов
        "bgcolor": ft.Colors.GREY_900,       # Цвет фона поля
        "border_color": ft.Colors.GREY_700,  # Цвет границы в обычном состоянии
        "color": ft.Colors.WHITE,            # Цвет текста
        "content_padding": 10,               # Внутренние отступы
        "cursor_color": ft.Colors.WHITE,     # Цвет курсора
        "focused_border_color": ft.Colors.BLUE_400,  # Цвет границы при фокусе
        "focused_bgcolor": ft.Colors.GREY_800,      # Цвет фона при фокусе
        "hint_style": ft.TextStyle(          # Стиль текста-подсказки
            color=ft.Colors.GREY_400,        # Цвет текста-подсказки
            size=14,                         # Размер шрифта подсказки
        ),
        "prefix_icon": ft.Icons.SEARCH,      # Иконка поиска слева от поля
        "height": 45,                        # Высота поля
    }

    # Настройки выпадающего списка выбора модели
    MODEL_DROPDOWN = {
        "width": 400,                        # Ширина списка
        "height": 45,                        # Высота в закрытом состоянии
        "border_radius": 8,                  # Радиус скругления углов
        "bgcolor": ft.Colors.GREY_900,       # Цвет фона
        "border_color": ft.Colors.GREY_700,  # Цвет границы
        "color": ft.Colors.WHITE,            # Цвет текста
        "content_padding": 10,               # Внутренние отступы
        "focused_border_color": ft.Colors.BLUE_400,  # Цвет границы при фокусе
        "focused_bgcolor": ft.Colors.GREY_800,      # Цвет фона при фокусе
    }

    # Настройки колонки с элементами выбора модели
    MODEL_SELECTION_COLUMN = {
        "spacing": 10,                                    # Отступ между элементами
        "horizontal_alignment": ft.CrossAxisAlignment.CENTER,  # Выравнивание по центру
        "width": 400,                                    # Ширина колонки
    }

    # Настройки колонки с элементами выбора формата отправки уведомлений
    NOTIFICATION_SELECTION_COLUMN = {
        "spacing": 10,  # Отступ между элементами
        "horizontal_alignment": ft.CrossAxisAlignment.CENTER,  # Выравнивание по центру
        "width": 400,  # Ширина колонки
    }

    # Настройки текста отображения баланса
    BALANCE_TEXT = {
        "size": 16,                          # Размер шрифта
        "color": ft.Colors.GREEN_400,        # Зеленый цвет для позитивного восприятия
        "weight": ft.FontWeight.BOLD,        # Жирное начертание для акцента
    }

    # Настройки контейнера для отображения баланса
    BALANCE_CONTAINER = {
        "padding": 10,                       # Внутренние отступы
        "bgcolor": ft.Colors.GREY_900,       # Цвет фона
        "border_radius": 8,                  # Радиус скругления углов
        "border": ft.border.all(1, ft.Colors.GREY_700),  # Тонкая серая граница
    }

    # Заголовки экранов (Авторизация, Введите PIN)
    HEADER_TEXT = {
        "size": 22,                     # Размер текста
        "weight": ft.FontWeight.BOLD,   # Жирность текста
        "color": ft.Colors.WHITE,       # Цвет текста
        "text_align": ft.TextAlign.CENTER, # Положение текста
    }

    # Стиль поля после генерации PIN-кода
    PIN_DISPLAY_MODE = {
        "multiline": True,      # Включаем многострочность
        "height": 80,           # Увеличиваем высоту
        "read_only": True,      # Запрещаем редактирование
        "text_align": ft.TextAlign.CENTER,  # Центрируем текст
        "width": 600,           # Увеличиваем ширину
        "password": False,      # Отключаем скрытие символов
        "error_text": None,     # Убираем текст ошибки, если он был
    }

    # Поле ввода PIN-кода
    PIN_INPUT = {
        "hint_text": "Введите PIN", # Подсказка для текста
        "password": True,           # Тип поля (прячем вводимый текст)
        "width": 200,               # Ширина поля
        "text_align": ft.TextAlign.CENTER,  # Положение текста
        "border_color": ft.Colors.BLUE_400, # Цвет обводки
        "bgcolor": ft.Colors.GREY_800,      # Цвет заднего фона
    }


    # Настройки ряда "Поле ввода + Кнопка настроек"
    RECIPIENT_ROW = {
        "width": 400,  # Ширина ряда
        "spacing": 5,  # Отступ между полем и кнопкой
        "vertical_alignment": ft.CrossAxisAlignment.CENTER,  # Выравнивание по центру
    }

    # Кнопка логов
    LOGS_BUTTON = {
        "text": "Логи",                    # Текст кнопки
        "icon": ft.Icons.TEXT_SNIPPET,     # Иконка кнопки
        "style": ft.ButtonStyle(
            color=ft.Colors.WHITE,         # Цвет текста
            bgcolor=ft.Colors.ORANGE_700,  # Цвет заднего фона
            padding=10,                    # Внутренние отступы
        ),
        "tooltip": "Посмотреть системные логи", # Подсказка при наведении
        "width": 130,                           # Ширина кнопки
        "height": 40,                           # Высота кнопки
    }

    # Стиль текста внутри окна логов
    LOG_TEXT_STYLE = {
        "font_family": "monospace",   # Шрифт
        "size": 12,                   # Размер шрифта
        "color": ft.Colors.GREEN_300, # Цвет текста
        "selectable": True,           # Чтобы можно было скопировать ошибку
    }

    # Настройки контейнера внутри диалогового окна логов
    LOG_DIALOG_CONTAINER = {
        "width": 600,   # Ширина окна
        "height": 400,  # Высота окна
        "padding": 10,  # Внутренний отступ
    }

    # Стиль заголовка диалога
    DIALOG_TITLE = {
        "weight": ft.FontWeight.BOLD,
        "size": 20,
    }

    @staticmethod
    def set_window_size(page: ft.Page):
        """
            Установка адаптивного размера окна под устройство.

            Args:
                page (ft.Page): Объект страницы приложения
        """

        # Проверяем платформу
        if page.platform not in [ft.PagePlatform.ANDROID, ft.PagePlatform.IOS]:
            page.window.width = 1000      # Ширина окна
            page.window.height = 900      # Высота окна
            page.window.min_width = 600   # Минимальная ширина окна
            page.window.min_height = 600  # Минимальная высота окна
            page.window.resizable = True  # Разрешаем пользователю растягивать окно
            page.window.center()          # Центрируем окно на мониторе
