import os                               # Библиотека для работы с операционной системой и переменными окружения
from logger import AppLogger            # Импорт собственного логгера для отслеживания работы
from aiogram import Bot                 # Библиотека для отправки Telegram сообщения
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError  # Библиотека для работы с исключениями

class TelegramNotificationSender:

    def __init__(self):
        """
        Инициализация отправки уведомлений в Telegram.

        Настраивает:
            - Систему логирования
            - Инициализация бота

        Raises:
            ValueError: Если забыли передать BOT_TOKEN в .env
        """
        # Инициализация логгера для отслеживания работы клиента
        self.logger = AppLogger()

        # Логирование успешной инициализации бота
        self.logger.info("TelegramNotificationSender initialized successfully")

    async def send_notification(self, target_chat_id: int, message: str, token: str):
        """
        Метод для отправки уведомления в Telegram чат.

        Args:
            target_chat_id: ID чата для отправки уведомления
            message: Текст уведомления для отправки
            token: Переданный токен, для инициализации бота

        Raises:
            TelegramBadRequest: Не верный ID пользователя
            TelegramForbiddenError: Пользователь не написал боту, чтобы получать уведомления
        """

        # Проверка наличия токена
        if not token:
            # Логирование критической ошибки
            self.logger.error("Missing Telegram configuration")
            # Возвращаем ошибку
            raise ValueError("Missing Telegram configuration")

        # Инициализация объекта бота
        bot = None

        try:
            # Создаем бота с переданным токеном
            bot = Bot(token=token)

            # Пробуем отправить уведомление через Telegram
            await bot.send_message(
                chat_id=target_chat_id,  # CHAT_ID получателя
                text=message  # Сообщение уведомления
            )

            # Логируем удачную отправку сообщения через Telegram
            self.logger.info(f"Уведомление отправлено на Telegram пользователю с ID: {target_chat_id}")

        except TelegramBadRequest:
            # Логируем ошибку отправки уведомления, если пользователь не верно указал ID
            self.logger.error(f"Chat {target_chat_id} not found")
            return f"Чат с ID пользователя: {target_chat_id} не найден. Возможно вы не верно указали ID."  # Возвращаем ошибку
        except TelegramForbiddenError:
            # Логируем ошибку отправки уведомления, если пользователь не написал боту
            self.logger.warning(f"Bot cannot send message to user {target_chat_id}")
            return f"Бот не может отправить уведомление пользователю с ID: {target_chat_id}"  # Возвращаем ошибку
        except Exception as e:
            # Логируем ошибку отправки уведомления через Telegram
            self.logger.error(f"Отправка уведомления не удалась. Ошибка: {e}.")
            return f"Ошибка при отправке уведомления: {e}"  # Возвращаем ошибку
        finally:
            # Закрываем сессию бота
            if bot:
                await bot.session.close()
