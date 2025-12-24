import sqlite3                  # Библиотека для работы с SQLite базой данных
import json                     # Библиотека для работы с JSON форматом
from datetime import datetime   # Библиотека для работы с датой и временем
import threading                # Библиотека для обеспечения потокобезопасности
import os                       # Библиотека для работы с системными файлами
from pathlib import Path        # Библиотека для работы с путями


class AuthenticationDB:
    """
        Класс для кэширования истории чата в SQLite базе данных.

        Обеспечивает:
        - Потокобезопасное хранение истории сообщений
        - Сохранение метаданных (модель, токены, время)
        - Форматированный вывод истории
        - Очистку истории
    """

    def __init__(self):
        """
            Инициализация системы кэширования.

            Создает:
            - Файл базы данных SQLite
            - Потокобезопасное хранилище соединений
            - Необходимые таблицы в базе данных
        """
        # Имя файла SQLite базы данных
        base = Path(os.getenv("FLET_APP_STORAGE_DATA") or ".")
        self.db_name = str(base / "auth.db")

        # Создание потокобезопасного хранилища соединений
        # Каждый поток будет иметь свое собственное соединение с базой
        self.local = threading.local()

        # Создание необходимых таблиц при инициализации
        self.create_tables()

    def get_connection(self):
        """
            Получение соединения с базой данных для текущего потока.

            Returns:
                sqlite3.Connection: Объект соединения с базой данных

            Note:
                Каждый поток получает свое собственное соединение,
                что обеспечивает потокобезопасность работы с базой.
        """

        # Проверяем, есть ли уже соединение в текущем потоке
        if not hasattr(self.local, 'connection'):
            # Если соединения нет - создаем новое
            self.local.connection = sqlite3.connect(self.db_name)

        # Возвращаем соединение
        return self.local.connection

    def create_tables(self):
        """
            Создание необходимых таблиц в базе данных.

            Создает таблицу messages со следующими полями:
                - id: уникальный идентификатор PIN-кода
                - api_key_hash: API ключ от OpenRouter.ai
                - pin_hash: PIN-код
                - created_at: время создания PIN-кода
                - last_login: время последнего входа
                - is_authenticated: статус регистрации (первый вход/повторный вход)
        """

        # Создаем новое соединение с базой
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # SQL запросы для создания таблиц
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auth_data  (
                id INTEGER PRIMARY KEY AUTOINCREMENT,   -- Уникальный ID для сохранения PIN
                api_key TEXT NOT NULL,             -- API ключ
                pin TEXT NOT NULL,                 --  PIN-код
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP, -- Время создания
                last_login DATETIME,                     -- Время последнего входа
                is_authenticated INTEGER DEFAULT 0       -- Статус регистрации (первый вход/повторный вход)
            )
        ''')

        conn.commit()  # Сохранение изменений в базе
        conn.close()  # Закрытие соединения

    def save_pin(self, api_key, pin):
        """
            Сохранение нового PIN-кода, при первом входе.

            Args:
                api_key: Переданный API-ключ от OpenRouter.ai
                pin: Переданный PIN-код
        """

        # Получение соединения для текущего потока
        conn = self.get_connection()
        cursor = conn.cursor()

        # Вставка новой записи в таблицу auth_data
        cursor.execute('''
                    INSERT INTO auth_data (api_key, pin, created_at, last_login, is_authenticated)
                    VALUES (?, ?, ?, ?, ?)
                ''', (api_key, pin, datetime.now(), datetime.now(), 1))

        # Сохранение изменений
        conn.commit()

    def is_authenticated(self):
        """
            Метод для проверки была ли произведена регистрация.

            Return:
                 True/False - статус первого входа. True - регистрация произведена, False - первый вход.
        """

        # Получение соединения для текущего потока
        conn = self.get_connection()
        cursor = conn.cursor()

        # Получаем значение из БД о входе
        cursor.execute(
            "SELECT is_authenticated FROM auth_data ORDER BY id DESC LIMIT 1"
        )

        # Получение найденной записи
        row = cursor.fetchone()

        # Возвращаем True/False в зависимости от значения регистрации
        return bool(row[0]) if row else False

    def set_authenticated(self, status):
        """
            Метод для смены статуса первого входа.
            Может быть использован для сброса PIN-кода.

            Args:
                status: Статус первого входа, 1/0. 1 - зарегистрирован, 0 - первый вход.
        """

        # Валидация, что переданы верные значения
        if status not in (0, 1):
            # Возвращаем ошибку, если status передан не верно
            return "Error: status must be 0 or 1"

        # Получение соединения для текущего потока
        conn = self.get_connection()
        cursor = conn.cursor()

        # Обновляем поля в БД для сохранения статуса регистрации
        cursor.execute("""
                UPDATE auth_data
                SET is_authenticated = ?
                WHERE id = (
                    SELECT id FROM auth_data ORDER BY id DESC LIMIT 1
                )
            """, (status,))

        # Сохранение изменений
        conn.commit()

    def reset_auth(self):
        """
            Метод для сброса PIN-кода.
            Сбрасывает данные до первоначального входа.
        """

        # Получение соединения для текущего потока
        conn = self.get_connection()
        cursor = conn.cursor()

        # Удаляем данные из БД
        cursor.execute("DELETE FROM auth_data")

        # Сохранение изменений
        conn.commit()

    def verify_pin(self, pin):
        """
            Метод для проверки правильности введенного PIN-кода.

            Args:
                pin: Переданный PIN-код.

            Return:
                bool: True - PIN-код введен верно, False - PIN-код введен не верно.
        """

        # Получение соединения для текущего потока
        conn = self.get_connection()
        cursor = conn.cursor()

        # Получаем PIN-код из БД
        cursor.execute("""
                SELECT id, pin
                FROM auth_data
                ORDER BY id DESC
                LIMIT 1
            """)

        # Получение найденной записи
        row = cursor.fetchone()

        # Если запись не найдена
        if row is None:
            return False  # Возвращаем False

        # Получаем id, сохраненный пароль из БД
        db_id, saved_pin = row

        # Если PIN-код введен не верно
        if str(saved_pin) != str(pin):
            return False  # Возвращаем False

        # Обновляем last_login в БД при успешном входе
        cursor.execute("""
            UPDATE auth_data
            SET last_login = ?
            WHERE id = ?
        """, (datetime.now(), db_id))

        # Сохранение изменений
        conn.commit()

        # Возвращаем True (удачный вход)
        return True

    def get_last_api_key(self):
        """
            Метод для получения последнего введенного API-ключа.
        """

        # Получение соединения для текущего потока
        conn = self.get_connection()
        cursor = conn.cursor()

        # Получение API-ключа из БД
        cursor.execute("SELECT api_key FROM auth_data ORDER BY id DESC LIMIT 1")

        # Получение найденной записи
        row = cursor.fetchone()

        # Возвращаем ключ, либо None при его отсутствии
        return row[0] if row else None

    def __del__(self):
        """
            Деструктор класса.

            Закрывает соединения с базой данных при уничтожении объекта,
            предотвращая утечки ресурсов.
        """
        # Проверка наличия соединения в текущем потоке
        if hasattr(self.local, 'connection'):
            self.local.connection.close()  # Закрытие соединения
