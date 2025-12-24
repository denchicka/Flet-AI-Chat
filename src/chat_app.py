# Импорт необходимых библиотек и модулей
import flet as ft                             # Фреймворк для создания кроссплатформенных приложений с современным UI
from openrouter import OpenRouterClient       # Клиент для взаимодействия с AI API через OpenRouter
from styles import AppStyles                  # Модуль с настройками стилей интерфейса
from components import MessageBubble, ModelSelector, NotificationSelector # Компоненты пользовательского интерфейса
from cache import ChatCache                   # Модуль для кэширования истории чата
from logger import AppLogger                  # Модуль для логирования работы приложения
from analytics import Analytics               # Модуль для сбора и анализа статистики использования
from monitor import PerformanceMonitor        # Модуль для мониторинга производительности
from notifications import NotificationService # Модуль для отправки уведомлений
import asyncio                                # Библиотека для асинхронного программирования
import time                                   # Библиотека для работы с временными метками
import json                                   # Библиотека для работы с JSON-данными
from datetime import datetime                 # Класс для работы с датой и временем
import os                                     # Библиотека для работы с операционной системой
from pathlib import Path                      # Библиотека для работы с путями
import asyncio                                # Библиотека для асинхронных запросов


class ChatApp:
    """
        Основной класс приложения чата.
        Управляет всей логикой работы приложения, включая UI и взаимодействие с API.
    """

    def __init__(self, api_key):
        """
            Инициализация основных компонентов приложения:
                - API клиент для связи с языковой моделью
                - Система кэширования для сохранения истории
                - Система логирования для отслеживания работы
                - Система аналитики для сбора статистики
                - Система мониторинга для отслеживания производительности
                - Система уведомлений для отправки на почту
                - Система уведомлений для отправки в Telegram

            Args:
                api_key: Переданный API ключ от OpenRouter.ai
        """

        # Инициализация основных компонентов
        self.api_client = OpenRouterClient(api_key=api_key)  # Создание клиента для работы с AI API
        self.cache = ChatCache()  # Инициализация системы кэширования
        self.logger = AppLogger()  # Инициализация системы логирования
        self.analytics = Analytics(self.cache)  # Инициализация системы аналитики с передачей кэша
        self.monitor = PerformanceMonitor()  # Инициализация системы мониторинга
        self.notification_service = NotificationService()  # Инициализация системы отправки уведомлений

        # Создание компонента для отображения баланса API
        self.balance_text = ft.Text(
            "Баланс: Загрузка...",  # Начальный текст до загрузки реального баланса
            **AppStyles.BALANCE_TEXT  # Применение стилей из конфигурации
        )
        self.update_balance()  # Первичное обновление баланса

        # Получаем путь для android
        storage_path = os.getenv("FLET_APP_STORAGE_DATA")

        # Если storage_path не пуст (android)
        if storage_path:
            base_dir = Path(storage_path) # Используем storage_path
        else: # Если не android
            base_dir =  Path(".") # Используем текущую папку

        # Создание директории для экспорта истории чата
        self.exports_dir = base_dir / "exports"
        self.exports_dir.mkdir(parents=True, exist_ok=True)


    def load_chat_history(self):
        """
            Загрузка истории чата из кэша и отображение её в интерфейсе.
            Сообщения добавляются в обратном порядке для правильной хронологии.
        """

        try:
            history = self.cache.get_chat_history()  # Получение истории из кэша
            for msg in reversed(history):  # Перебор сообщений в обратном порядке
                # Распаковка данных сообщения в отдельные переменные
                _, model, user_message, ai_response, timestamp, tokens = msg
                # Добавление пары сообщений (пользователь + AI) в интерфейс
                self.chat_history.controls.extend([
                    MessageBubble(  # Создание пузырька сообщения пользователя
                        message=user_message,
                        is_user=True
                    ),
                    MessageBubble(  # Создание пузырька ответа AI
                        message=ai_response,
                        is_user=False
                    )
                ])
        except Exception as e:
            # Логирование ошибки при загрузке истории
            self.logger.error(f"Ошибка загрузки истории чата: {e}")

    def update_balance(self):
        """
            Обновление отображения баланса API в интерфейсе.
            При успешном получении баланса показывает его зеленым цветом,
            при ошибке - красным с текстом 'н/д' (не доступен).
        """

        try:
            balance = self.api_client.get_balance()  # Запрос баланса через API
            self.balance_text.value = f"Баланс: {balance}"  # Обновление текста с балансом
            self.balance_text.color = ft.Colors.GREEN_400  # Установка зеленого цвета для успешного получения
        except Exception as e:
            # Обработка ошибки получения баланса
            self.balance_text.value = "Баланс: н/д"  # Установка текста ошибки
            self.balance_text.color = ft.Colors.RED_400  # Установка красного цвета для ошибки
            self.logger.error(f"Ошибка обновления баланса: {e}")

    async def main(self, page: ft.Page):
        """
            Основная функция инициализации интерфейса приложения.
            Создает все элементы UI и настраивает их взаимодействие.

            Args:
                page (ft.Page): Объект страницы Flet для размещения элементов интерфейса
        """

        # Применение базовых настроек страницы из конфигурации стилей
        for key, value in AppStyles.PAGE_SETTINGS.items():
            setattr(page, key, value)

        AppStyles.set_window_size(page)  # Установка размеров окна приложения

        # Инициализация выпадающего списка для выбора модели AI
        models = self.api_client.available_models
        self.model_dropdown = ModelSelector(models)
        self.model_dropdown.value = models[0] if models else None

        await asyncio.sleep(0.2) # Прогрузка интерфейса

        # Пытаемся достать данные из памяти телефона для авторизации в почте
        try:
            saved_email_login = await page.client_storage.get_async("email_login") or "" # Получаем логин для почты
            saved_email_pass = await page.client_storage.get_async("email_pass") or ""   # Получаем пароль для IMAP
        except Exception as e:
            # Если возникла непредвиденная ошибка
            self.logger.error(f"Ошибка загрузки настроек: {e}") # Логируем ошибку
            saved_email_login = "" # Выставляем пустое значение
            saved_email_pass = ""  # Выставляем пустое значение

        # Инициализация поля для ввода токена telegram-бота
        self.telegram_token_input = ft.TextField(
            visible=False,              # Скрываем поле по умолчанию
            **AppStyles.TELEGRAM_INPUT  # Применяем стили
        )

        # Создание поля для ввода логина почты
        self.settings_login_field = ft.TextField(
            label="Yandex Login (без @yandex.ru)",  # Подпись поля
            value=saved_email_login,                # Значение поля
            **AppStyles.SETTINGS_INPUT_FIELD        # Применяем стиль
        )

        # Создание поля для ввода IMAP пароля
        self.settings_pass_field = ft.TextField(
            label="Пароль приложения",  # Подпись поля
            password=True,              # Устанавливаем тип поля, как пароль, чтобы спрятать вводимый пароль
            value=saved_email_pass,     # Значение поля
            can_reveal_password=True,   # Можно посмотреть вводимый пароль
            **AppStyles.SETTINGS_INPUT_FIELD  # Применяем стиль
        )


        def open_settings(e):
            """
                Функция для открытия окна настроек.
                Содержит функции для сохранения логина и пароля от почты.
            """

            async def save_settings(e):
                """
                    Функция для сохранения настроек (логин и пароль) от почты.
                """

                # Сохраняем в память телефона
                await page.client_storage.set_async("email_login", self.settings_login_field.value) # Сохранение логина
                await page.client_storage.set_async("email_pass", self.settings_pass_field.value)   # Сохранения пароля

                page.close(dialog)         # Закрытие диалогового окна
                page.snack_bar = ft.SnackBar(ft.Text("Настройки сохранены!")) # Сохраняем результат
                page.snack_bar.open = True # Отображаем результат для пользователя
                page.update()              # Обновляем окно
                self.logger.info("Пользователь сохранил логин и пароль для почты.") # Логируем изменения

            def close_settings(e):
                """
                    Функция для закрытия окна настроек.
                """

                page.close(dialog) # Закрываем диалоговое окно

            # Создаем диалоговое окно для настроек
            dialog = ft.AlertDialog(
                title=ft.Text("Настройки почты"), # Заголовок диалогового окна
                content=ft.Column([               # Содержимое
                    ft.Text("Введите данные для отправки уведомлений (Yandex):"), # Поле с текстом
                    self.settings_login_field,    # Поле для ввода логина
                    self.settings_pass_field      # Поле для ввода IMAP пароля
                ],
                **AppStyles.SETTINGS_DIALOG_COLUMN # Применяем стиль для колонки
                ),
                actions=[    # Доступные действия
                    ft.TextButton("Отмена", on_click=close_settings),   # Кнопка "Отмена" для закрытия окна
                    ft.TextButton("Сохранить", on_click=save_settings), # Кнопка "Сохранить" для сохранения настроек
                ],
            )

            # Отображаем диалоговое окно в основном окне
            page.open(dialog)

        def on_notification_change(e):
            """
                Функция для отображения поля ввода токена в telegram.
                Включает поле для ввода токена, если для уведомлений выбран Telegram.
            """

            # Проверяем выбранное значение в выпадающем списке для уведомлений
            # Если выбранное значение - telegram
            if self.notification_dropdown.value == "telegram":
                self.telegram_token_input.visible = True  # Включаем поле
                self.notification_target.label = "Получатель уведомлений (ID telegram)" # Меняем текст
                settings_button.visible = False           # Прячем кнопку настроек
            else: # В любом другом случае
                self.telegram_token_input.visible = False # Отключаем поле
                self.notification_target.label = "Получатель уведомлений (email)" # Меняем текст
                settings_button.visible = True            # Показываем кнопку настроек

            # Обновляем окно
            page.update()


        # Инициализация выпадаещего списка для выбора формата отправки уведомлений
        notifications = self.api_client.available_notifications
        self.notification_dropdown = NotificationSelector(notifications)
        self.notification_dropdown.on_change = on_notification_change

        # Определяем, выбрана ли почта по умолчанию
        is_email_default = self.notification_dropdown.value == "email"

        # Создаем кнопку для настроек логина и пароля почты
        settings_button = ft.IconButton(
            on_click=open_settings,      # Вызываемая функция, при нажатии на кнопку
            visible=is_email_default,    # Показываем, если email выбран по умолчанию
            **AppStyles.SETTINGS_BUTTON  # Применяем стиль
        )

        # Если есть значения в notifications
        if notifications:
            self.notification_dropdown.value = notifications[0] if notifications else None # Выбор значения по умолчанию
            # Если выбранное значение telegram
            if self.notification_dropdown.value == "telegram":
                self.telegram_token_input.visible = True   # Отображаем поле для ввода токена
            # Иначе если выбранное значение email
            elif self.notification_dropdown.value == "email":
                self.telegram_token_input.visible = False  # Прячем поле для ввода токена

        def show_logs_click(e):
            """
                Функция для открытия диалогового окна с содержимым последнего лог-файла.
            """
            log_content = "Логи не найдены."

            try:
                # Задаем путь к папке logs
                logs_dir = "logs"

                # Если папка существует
                if os.path.exists(logs_dir):
                    # Получаем список всех файлов в папке
                    files = [os.path.join(logs_dir, f) for f in os.listdir(logs_dir) if f.endswith('.log')]

                    if files:
                        # Находим последний файл по дате изменения
                        latest_file = max(files, key=os.path.getctime)

                        # Читаем содержимое (последние 100 строк, чтобы не зависло)
                        with open(latest_file, 'r', encoding='utf-8') as f:
                            lines = f.readlines() # Читаем содержимое
                            # Берем последние 200 строк
                            log_content = "".join(lines[-200:])

                        # Добавляем заголовок с именем файла
                        log_content = f"--- Файл: {latest_file} ---\n\n{log_content}"

            except Exception as err:
                # Если возникло исключение
                log_content = f"Ошибка чтения логов: {err}"


            def close_logs(e):
                """
                    Функция закрытия окна логов.
                """

                page.close(log_dialog)


            def copy_logs(e):
                """
                    Функция копирования логов в буфер обмена.
                """

                page.set_clipboard(log_content)
                page.snack_bar = ft.SnackBar(ft.Text("Логи скопированы!"))
                page.snack_bar.open = True
                page.update()

            # Создаем диалог
            log_dialog = ft.AlertDialog(
                title=ft.Text("Системные логи", **AppStyles.DIALOG_TITLE),
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(log_content, **AppStyles.LOG_TEXT_STYLE)
                        ],
                        scroll=ft.ScrollMode.AUTO,   # Включаем прокрутку
                    ),
                    **AppStyles.LOG_DIALOG_CONTAINER # Применяем стили
                ),
                actions=[
                    ft.TextButton("Копировать", on_click=copy_logs),
                    ft.TextButton("Закрыть", on_click=close_logs),
                ],
            )

            page.open(log_dialog)

        async def send_message_click(e):
            """
                Асинхронная функция отправки сообщения.
            """

            if not self.message_input.value:
                return

            try:
                # Визуальная индикация процесса
                self.message_input.border_color = ft.Colors.BLUE_400
                page.update()

                # Сохранение данных сообщения
                start_time = time.time()
                user_message = self.message_input.value
                self.message_input.value = ""
                page.update()

                # Добавление сообщения пользователя
                self.chat_history.controls.append(
                    MessageBubble(message=user_message, is_user=True)
                )

                # Индикатор загрузки
                loading = ft.ProgressRing()
                self.chat_history.controls.append(loading)
                page.update()

                # Асинхронная отправка запроса
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.api_client.send_message(
                        user_message,
                        self.model_dropdown.value
                    )
                )

                # Удаление индикатора загрузки
                self.chat_history.controls.remove(loading)

                # Обработка ответа
                if "error" in response:
                    # Если возникла ошибка запоминаем ее
                    response_text = f"Ошибка: {response['error']}"

                    # Сбрасываем использованные токены
                    tokens_used = 0

                    # Логируем ошибку
                    self.logger.error(f"Ошибка API: {response['error']}")
                else:
                    # Получение ответа
                    response_text = response["choices"][0]["message"]["content"]

                    # Удаление пробела, если он идет первым
                    if response_text.startswith(" "):
                        response_text = response_text[1:]

                    # Получаем использованное количество токенов
                    tokens_used = response.get("usage", {}).get("total_tokens", 0)

                    if self.notification_dropdown and self.notification_target.value:

                        # Получаем текущий логин и пароль для авторизации на SMTP-сервере
                        current_login = await page.client_storage.get_async("email_login")
                        current_pass = await page.client_storage.get_async("email_pass")

                        # Получаем telegram токен
                        tg_token = self.telegram_token_input.value

                        # Отправка уведомления по выбранному каналу
                        await self.notification_service.send_notification(
                            channel=self.notification_dropdown.value,  # Канал для отправки уведомления
                            recipient=self.notification_target.value,  # Получатель
                            message=response_text,                     # Текст для отправки
                            token=tg_token,                            # Телеграм токен для отправки через telegram-бота
                            email_login=current_login,                 # Логин для авторизации в почте
                            email_pass=current_pass                    # Пароль для авторизации в почте
                        )

                # Сохранение в кэш
                self.cache.save_message(
                    model=self.model_dropdown.value,
                    user_message=user_message,
                    ai_response=response_text,
                    tokens_used=tokens_used
                )

                # Добавление ответа в чат
                self.chat_history.controls.append(
                    MessageBubble(message=response_text, is_user=False)
                )

                # Обновление аналитики
                response_time = time.time() - start_time
                self.analytics.track_message(
                    model=self.model_dropdown.value,
                    message_length=len(user_message),
                    response_time=response_time,
                    tokens_used=tokens_used
                )

                # Логирование метрик
                self.monitor.log_metrics(self.logger)
                page.update()

            except Exception as e:
                self.logger.error(f"Ошибка отправки сообщения: {e}")
                self.message_input.border_color = ft.Colors.RED_500

                # Показ уведомления об ошибке
                snack = ft.SnackBar(
                    content=ft.Text(
                        str(e),
                        color=ft.Colors.RED_500,
                        weight=ft.FontWeight.BOLD
                    ),
                    bgcolor=ft.Colors.GREY_900,
                    duration=5000,
                )
                page.overlay.append(snack)
                snack.open = True
                page.update()

        def show_error_snack(page, message: str):
            """
                Функция для уведомления об ошибке.

                Args:
                    page: Переданная страница
                    message: Сообщение об ошибке
            """

            snack = ft.SnackBar(  # Создание уведомления
                content=ft.Text(
                    message,
                    color=ft.Colors.RED_500
                ),
                bgcolor=ft.Colors.GREY_900,
                duration=5000,
            )
            page.overlay.append(snack)  # Добавление уведомления
            snack.open = True  # Открытие уведомления
            page.update()  # Обновление страницы

        async def show_analytics(e):
            """
                Функция показа статистики использования.
            """

            stats = self.analytics.get_statistics()  # Получение статистики

            # Создание диалога статистики
            dialog = ft.AlertDialog(
                title=ft.Text("Аналитика"),
                content=ft.Column([
                    ft.Text(f"Всего сообщений: {stats['total_messages']}"),
                    ft.Text(f"Всего токенов: {stats['total_tokens']}"),
                    ft.Text(f"Среднее токенов/сообщение: {stats['tokens_per_message']:.2f}"),
                    ft.Text(f"Сообщений в минуту: {stats['messages_per_minute']:.2f}")
                ]),
                actions=[
                    ft.TextButton("Закрыть", on_click=lambda e: close_dialog(dialog)),
                ],
            )

            page.overlay.append(dialog)  # Добавление диалога
            dialog.open = True  # Открытие диалога
            page.update()  # Обновление страницы

        async def clear_history(e):
            """
                Функция для очистки истории чата.
            """

            try:
                self.logger.info("Пользователь очистил историю чата.") # Логируем очистку
                self.cache.clear_history()  # Очистка кэша
                self.analytics.clear_data()  # Очистка аналитики
                self.chat_history.controls.clear()  # Очистка истории чата

            except Exception as e:
                self.logger.error(f"Ошибка очистки истории: {e}")
                show_error_snack(page, f"Ошибка очистки истории: {str(e)}")

        async def confirm_clear_history(e):
            """
                Функция для подтверждения очистки истории.
            """

            def close_dlg(e):  # Функция закрытия диалога
                close_dialog(dialog)

            async def clear_confirmed(e):  # Функция подтверждения очистки
                await clear_history(e)
                close_dialog(dialog)

            # Создание диалога подтверждения
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Подтверждение удаления"),
                content=ft.Text("Вы уверены? Это действие нельзя отменить!"),
                actions=[
                    ft.TextButton("Отмена", on_click=close_dlg),
                    ft.TextButton("Очистить", on_click=clear_confirmed),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            page.overlay.append(dialog)
            dialog.open = True
            page.update()

        def close_dialog(dialog):
            """
                Функция закрытия диалогового окна.

                Args:
                    dialog: Диалоговое окно
            """

            dialog.open = False  # Закрытие диалога
            page.update()  # Обновление страницы

            if dialog in page.overlay:  # Удаление из overlay
                page.overlay.remove(dialog)



        async def save_dialog(e):
            """
                Функция сохранения истории диалога в JSON файл.
            """

            try:
                # Получение истории из кэша
                history = self.cache.get_chat_history()

                # Форматирование данных для сохранения
                dialog_data = []
                for msg in history:
                    dialog_data.append({
                        "timestamp": msg[4],
                        "model": msg[1],
                        "user_message": msg[2],
                        "ai_response": msg[3],
                        "tokens_used": msg[5]
                    })

                # Создание имени файла
                filename = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                filepath = self.exports_dir / filename

                # Сохранение в JSON
                filepath.write_text(
                    json.dumps(dialog_data, ensure_ascii=False, indent=2, default=str),
                    encoding="utf-8"
                )

                # Создание диалога успешного сохранения
                dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Диалог сохранен"),
                    content=ft.Column([
                        ft.Text("Путь сохранения:"),
                        ft.Text(str(filepath), selectable=True, weight=ft.FontWeight.BOLD),
                    ]),
                    actions=[
                        ft.TextButton("OK", on_click=lambda e: close_dialog(dialog)),
                    ],
                )

                page.overlay.append(dialog)
                dialog.open = True
                page.update()

            except Exception as e:
                self.logger.error(f"Ошибка сохранения: {e}")
                show_error_snack(page, f"Ошибка сохранения: {str(e)}")

        # Создание компонентов интерфейса
        self.message_input = ft.TextField(expand=True, **AppStyles.MESSAGE_INPUT)  # Поле ввода
        self.chat_history = ft.ListView(**AppStyles.CHAT_HISTORY)     # История чата
        self.notification_target = ft.TextField(expand=True, **AppStyles.RECIPIENT_INPUT)  # Поле для ввода получателя

        recipient_row = ft.Row(
            controls=[
                self.notification_target,  # Поле ввода получателя
                settings_button,           # Кнопка настроек для почты
            ],
            **AppStyles.RECIPIENT_ROW      # Применение стилей
        )

        # Загрузка существующей истории
        self.load_chat_history()

        # Создание кнопок управления
        save_button = ft.ElevatedButton(
            on_click=save_dialog,  # Привязка функции сохранения
            **AppStyles.SAVE_BUTTON  # Применение стилей
        )

        clear_button = ft.ElevatedButton(
            on_click=confirm_clear_history,  # Привязка функции очистки
            **AppStyles.CLEAR_BUTTON  # Применение стилей
        )

        send_button = ft.ElevatedButton(
            on_click=send_message_click,  # Привязка функции отправки
            **AppStyles.SEND_BUTTON  # Применение стилей
        )

        analytics_button = ft.ElevatedButton(
            on_click=show_analytics,  # Привязка функции аналитики
            **AppStyles.ANALYTICS_BUTTON  # Применение стилей
        )

        # Создание кнопки логов
        logs_button = ft.ElevatedButton(
            on_click=show_logs_click,
            **AppStyles.LOGS_BUTTON
        )

        # Создание layout компонентов

        # Создание ряда кнопок управления
        control_buttons = ft.Row(
            controls=[  # Размещение кнопок в ряд
                save_button,
                analytics_button,
                clear_button,
                logs_button
            ],
            wrap=True, # Перенос кнопок
            **AppStyles.CONTROL_BUTTONS_ROW  # Применение стилей к ряду
        )

        # Создание строки ввода с кнопкой отправки
        input_row = ft.Row(
            controls=[  # Размещение элементов ввода
                self.message_input,
                send_button
            ],
            **AppStyles.INPUT_ROW  # Применение стилей к строке ввода
        )

        # Создание колонки для элементов управления
        controls_column = ft.Column(
            controls=[  # Размещение элементов управления
                input_row,
                control_buttons,
            ],
            **AppStyles.CONTROLS_COLUMN  # Применение стилей к колонке
        )

        # Создание контейнера для баланса
        balance_container = ft.Container(
            content=self.balance_text,  # Размещение текста баланса
            **AppStyles.BALANCE_CONTAINER  # Применение стилей к контейнеру
        )

        # Создание колонки выбора модели
        model_selection = ft.Column(
            controls=[  # Размещение элементов выбора модели
                self.model_dropdown.search_field,
                self.model_dropdown
            ],
            **AppStyles.MODEL_SELECTION_COLUMN  # Применение стилей к колонке
        )

        # Создание колонки выбора формата отправки уведомлений
        notification_selection = ft.Column(
            controls=[  # Размещение элементов выбора формата уведомлений
                self.notification_dropdown,
                ft.Container(
                    content=self.telegram_token_input,
                    margin=ft.margin.only(top=10)  # Отступ сверху 10 пикселей
                ),
                ft.Container(
                    content=recipient_row,
                    margin=ft.margin.only(top=10)  # Отступ сверху 10 пикселей
                ),
                balance_container
            ],
            **AppStyles.MODEL_SELECTION_COLUMN  # Применение стилей к колонке
        )

        # Создание основной колонки приложения
        self.main_column = ft.Column(
            controls=[  # Размещение основных элементов
                ft.Container(
                    content=model_selection,
                    margin=ft.margin.only(top=10)  # Отступ сверху 10 пикселей
                ),
                notification_selection,
                self.chat_history,
                controls_column
            ],
            **AppStyles.MAIN_COLUMN  # Применение стилей к главной колонке
        )

        # Добавление основной колонки на страницу
        page.add(self.main_column)

        # Запуск монитора
        self.monitor.get_metrics()

        # Логирование запуска
        self.logger.info("Приложение запущено")