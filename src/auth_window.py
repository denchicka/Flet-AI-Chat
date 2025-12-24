# Импорт необходимых библиотек и модулей
import random                                   # Библиотека для генерации случайного PIN-кода
import flet as ft                               # Фреймворк для создания пользовательского интерфейса
from styles import AppStyles                    # Импорт стилей приложения
from auth_db import AuthenticationDB            # Импорт класса для доступа к базе данных для авторизации
from chat_app import ChatApp                    # Импорт основного класса с окном приложения (чат)
from openrouter import OpenRouterClient         # Импорт класса для работы с API OpenRouter.ai
from logger import AppLogger                    # Импорт класса для логов

class AuthenticationWindow:
    """
        Класс для авторизации в приложении.
        Управляет логикой авторизации в приложении, включая UI и взаимодействие с API, базой данных.
    """
    def __init__(self):
        """
            Инициализация основных компонентов окна авторизации:
                - API клиент для связи с языковой моделью
                - Система логирования для отслеживания работы
                - База данных для сохранения статуса регистрации

            Создает базу данных, при инициализации.
        """

        # Инициализация основных компонентов
        self.logger = AppLogger()  # Инициализация системы логирования
        self.db = AuthenticationDB()  # Инициализация базы данных

        # Создание БД
        self.db.create_tables()

    def show(self, page: ft.Page):
        """
            Метод для отображения и настройки окон.

            Args:
                page: Переданное окно, для отображения элементов интерфейса.
        """

        # Создаем атрибут для дальнейшего доступа к окну
        self.page = page

        # Очищаем окно от всех элементов
        page.clean()

        # Применение базовых настроек страницы из конфигурации стилей
        for key, value in AppStyles.PAGE_SETTINGS.items():
            setattr(page, key, value)

        # Меняем размер окна
        AppStyles.set_window_size(page)

        # Проверка первого входа
        if not self.db.is_authenticated():
            self.show_auth_screen(page) # Отображаем страницу первого входа
        else:
            self.show_pin_screen()      # Если пользователь зарегистрирован - отображаем окно ввода PIN-кода

    def show_auth_screen(self, page: ft.Page):
        """
            Основная функция инициализации интерфейса приложения.
            Создает все элементы UI и настраивает их взаимодействие.

            Args:
                page (ft.Page): Объект страницы Flet для размещения элементов интерфейса
        """

        # Очистка окна от всех элементов
        page.clean()


        def login_click(e):
            """
                Функция для авторизации в приложении.
                Срабатывает при клике кнопки "Войти". Проверяет введенный пользователем API ключ.
                При удачной проверке ключа и баланса генерирует PIN-код для дальнейшего входа.
            """

            # Получение введенного API-ключа OpenRouter.ai
            key = self.openrouter_keyfield.value.strip()

            # Если ключ не введен
            if not key:
                self.logger.error("Не введен API ключ OpenRouter.")         # Логируем ошибку
                self.openrouter_keyfield.error_text = "Введите API ключ"    # Выводим ошибку под полем ввода ключа
                error_text.visible = False                                  # Прячем текст ошибки
                page.update()   # Обновляем окно
                return          # Выходим из функции
            else:
                self.openrouter_keyfield.error_text = "" # Если ключ введен - убираем ошибку

            # Получаем баланс через API
            try:
                client = OpenRouterClient(api_key=key)
                balance = client.get_balance()
            except Exception as e:
                self.logger.error(f"Ошибка проверки ключа: {e}")
                error_text.value = "Неверный API ключ"
                error_text.visible = True
                page.update()
                return

            # Проверка валидности баланса
            if not str(balance).startswith("$"): # Если баланс не начинается с $ (например: $0.00)
                self.logger.error("Ошибка при получении баланса.") # Логируем ошибку
                error_text.value = balance  # Выводим ошибку в поле для ошибки
                error_text.visible = True   # Отображаем ошибку
                page.update()               # Обновляем окно
                return                      # Выходим из функции

            # Проверка баланса
            if float(balance[1:]) < 0: # Если баланс отрицательный
                self.logger.error("Баланс отрицательный. Дальнейший вход не возможен.") # Логируем ошибку
                error_text.value = "Баланс отрицательный. Дальнейший вход не возможен."  # Меняем значение ошибки
                error_text.visible = True   # Выводим ошибку
                page.update()               # Обновляем окно
                return                      # Выходим из функции

            # Логируем удачный вход
            self.logger.info("Удачный вход. Генерация 4-ех значного PIN.")

            # Генерируем PIN-код
            pin = self.generate_pin()

            # Сохраняем API-ключ и PIN-код в БД
            self.db.save_pin(
                api_key=key, # API-ключ
                pin=pin      # Сгенерированный PIN-код
            )

            # Отображаем кнопку для входа в чат
            enter_button.visible = True

            # Прячем кнопку входа и поле для ошибки
            login_button.visible = False
            error_text.visible = False

            # Обновляем окно
            page.update()

        async def enter_chat_click(e):
            """
            Функция для перехода в основной чат приложения.
            """

            # Логируем удачную регистрацию
            self.logger.info("Регистрация завершена, вход в чат.")

            # Меняем статус первого входа, для дальнейшей авторизации по PIN-коду
            self.db.set_authenticated(1)

            # Очищаем окно
            page.clean()

            # Получаем API-ключ из БД
            api_key = self.db.get_last_api_key()

            if not api_key:
                # если БД пустая - вернуть на регистрацию
                self.show_auth_screen(self.page)
                return

            # Создаем экземпляр основного класса ChatApp
            chat = ChatApp(api_key=api_key)

            # Переходим в основное окно приложения (чат)
            await chat.main(self.page)

        # Инициализация окна ввода ключа
        self.openrouter_keyfield = ft.TextField(
            hint_text="Введите ключ OpenRouter",  # Текст-подсказка в поле поиска
            password=True,                  # Устанавливаем тип поля, как пароль, чтобы прятать API-ключ
            **AppStyles.MODEL_SEARCH_FIELD  # Применение стилей из конфигурации
        )

        # Кнопка входа
        login_button = ft.ElevatedButton(
            "Войти",              # Текст кнопки
            on_click=login_click, # Функция, выполняющаяся при клике по кнопке
            visible=True          # Изначально отображаем в окне
        )

        # Поле для вывода ошибки
        error_text = ft.Text(
            value="",            # Изначальное значение пустота, так как ошибок не было
            color=ft.Colors.RED, # Устанавливаем красный цвет для текста ошибки
            visible=False        # Изначально прячем текст ошибки, так как ее не было
        )

        # Кнопка для перехода в основное приложение
        enter_button = ft.ElevatedButton(
            "Перейти в чат",        # Текст кнопки
            on_click=enter_chat_click,   # Функция, выполняющаяся при клике по кнопке
            visible=False                # Изначально прячем кнопку
        )

        # Добавляем элементы в окно авторизации
        page.add(
            ft.Column(
                [
                    ft.Text("Авторизация", **AppStyles.HEADER_TEXT), # Текст окна
                    self.openrouter_keyfield, # Поле для ввода ключа
                    login_button,             # Кнопка для регистрации
                    enter_button,             # Кнопка перехода в основное приложение (чат)
                    error_text                # Текст с ошибкой
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

    def show_pin_screen(self):
        """
            Метод для показа окна с PIN-кодом.
            Содержит функции:
                pin_login: для проверки введенного PIN-кода;
                reset_pin: для сброса PIN-кода.
        """

        # Поле для ввода PIN-кода
        pin_field = ft.TextField(
            **AppStyles.PIN_INPUT # Устанавливаем стили
        )

        async def pin_login(e):
            """
                Функция для проверки введенного PIN-кода.
                Переходит в основное приложение (чат), если PIN-код введен верно.
                Выводит ошибку, если PIN-код введен не верно.
            """

            # Получаем значение введенного PIN-кода пользователем
            pin = pin_field.value.strip()

            # Проверяем введенный PIN-код и значение хранящаяся в БД
            if self.db.verify_pin(pin):
                # Логируем верно введенный PIN-код
                self.logger.info("PIN-код введен верно.")

                # Очищаем окно
                self.page.clean()

                # Получаем API-ключ из БД
                api_key = self.db.get_last_api_key()
                if not api_key:
                    # Если БД пустая - вернуть на регистрацию
                    self.show_auth_screen(self.page)
                    return

                # Создаем экземпляр основного класса ChatApp
                chat = ChatApp(api_key=api_key)

                # Переходим в основное окно приложения (чат)
                await chat.main(self.page)
            else: # Иначе, если PIN-код введен не верно
                self.logger.error("PIN-код введен не верно.") # Логируем ошибку, что PIN-код введен не верно
                pin_field.error_text = "Неверный PIN"  # Выводим ошибку о не верном PIN-коде пользователю
                self.page.update()                     # Обновляем окно

        def reset_pin(e):
            """
                Функция для сброса PIN-кода.
            """

            # Логируем информацию, что пользователь сбросил PIN-код
            self.logger.info("Пользователь сбросил PIN-код.")

            # Вызываем метод из БД для удаления данных
            self.db.reset_auth()

            # Показываем окно регистрации, для ввода API-ключа от OpenRouter.ai
            self.show_auth_screen(self.page)

        # Добавляем элементы в окно
        self.page.add(
            ft.Column(
                [
                    ft.Text("Введите PIN", size=22), # Текст "Введите PIN"
                    pin_field,                             # Поле для ввода PIN-кода
                    ft.ElevatedButton("Войти", on_click=pin_login), # Кнопка для смены окна на ChatApp
                    ft.ElevatedButton("Сбросить PIN-код", on_click=reset_pin), # Кнопка для сброса PIN-кода
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )

    def generate_pin(self):
        """
            Метод для генерации 4-ех значного PIN-кода.

            Return:
                pin: Сгенерированный 4-ех значный PIN-код.
        """

        # Генерация 4-ех значного пин
        pin = "".join(map(str, random.sample(range(10), 4)))

        # Применение стилей
        for key, value in AppStyles.PIN_DISPLAY_MODE.items():
            setattr(self.openrouter_keyfield, key, value)

        # Заменяем значение в поле для ввода API-ключа от OpenRouter.ai
        self.openrouter_keyfield.value = f"Ваш PIN: {pin}.\nСохраните его, для дальнейшего входа"


        # Возвращаем сгенерированный PIN-код
        return pin