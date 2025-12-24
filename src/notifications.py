from email_notify import EmailNotificationSender # Модуль с логикой для отправки уведомления через почту
from telegram import TelegramNotificationSender  # Модуль с логикой для отправки уведомления через telegram


class NotificationService:

    def __init__(self):
        """
        Конструктор системы уведомлений.

        Инициализирует каналы для отправки уведомлений.
        """

        # Атрибут для отправки сообщения по Email
        self.email_sender = EmailNotificationSender()

        # Атрибут для отправки уведомления через Telegram
        self.telegram_sender = TelegramNotificationSender()

    async def send_notification(self, channel: str, recipient: str, message: str, token: str = None, email_login: str = None, email_pass: str = None):
        """
        Метод для отправки уведомления по переданному каналу.

        Args:
            channel: Канал для отправки уведомления.
            recipient: Получатель уведомления
            message: Сообщение уведомления
            token: Токен для отправки уведомления через telegram-бота. По умолчанию: None
            email_login: Логин для авторизации в почте. По умолчанию: None
            email_pass: Пароль для авторизации в IMAP. По умолчанию: None
        """

        if channel == "email":
            # Валидация почты
            if recipient.count("@") == 0:
                raise ValueError("Проверьте валидность введенной почты")

            # email - синхронная отправка
            self.email_sender.send_notification(
                email_to=recipient, # Получатель
                text=message,       # Текст уведомления
                login=email_login,  # Логин почты
                password=email_pass # Пароль для авторизации IMAP
            )

        elif channel == "telegram":
            # Валидация Telegram ID
            if not recipient.isdigit():
                raise ValueError("Telegram chat_id должен быть числом")

            # telegram - асинхронна отправка
            await self.telegram_sender.send_notification(
                target_chat_id=int(recipient), # Получатель
                message=message,               # Текст уведомления
                token=token                    # Токен telegram-бота
            )

        else:
            raise ValueError(f"Unsupported notification channel: {channel}")
