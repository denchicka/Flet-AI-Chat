# Импорт необходимых библиотек и модулей
import sys                # Библиотека для работы с системой
from pathlib import Path  # Библиотека для работы с системными путями
import os                 # Библиотека для работы с системными файлами
import flet as ft         # Фреймворк для создания кроссплатформенных приложений с современным UI

# Получаем абсолютный путь к папке, где лежит main.py (это папка src)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Добавляем этот путь в системные пути Python, если его там нет
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


async def main(page: ft.Page):
    """Точка входа в приложение/окна авторизации"""

    try:
        from auth_window import AuthenticationWindow # Окно авторизации
    except ImportError as e:
        # Если вдруг ошибка, выведем ее на экран телефона, чтобы видеть причину
        page.add(ft.Text(f"Критическая ошибка запуска:\n{e}", color="red", size=20))
        return

    try:
        auth = AuthenticationWindow()  # Создание экземпляра окна авторизации
        auth.show(page)                # Отображение окна авторизации
    except Exception as e:
        page.add(ft.Text(f"Ошибка в приложении:\n{e}", color="red"))


if __name__ == "__main__":
    ft.app(target=main)  # Запуск если файл запущен напрямую
