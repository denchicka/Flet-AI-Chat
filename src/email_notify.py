# Импорт необходимых библиотек
from email.message import EmailMessage # Модуль для работы с почтой
from logger import AppLogger           # Импорт собственного логгера для отслеживания работы
import smtplib                         # Библиотека для подключения к SMTP серверу для отправки письма (email)


class EmailNotificationSender:

    def __init__(self):
        """
        Инициализация отправки уведомлений по почте.

        Настраивает:
            - Систему логирования
            - SMTP-сервер
            - Логин для входа на почту
            - Пароль для отправки уведомления
        """
        # Инициализация логгера для отслеживания работы клиента
        self.logger = AppLogger()

        # Логирование успешной инициализации SMTP-серера
        self.logger.info("EmailNotificationSender initialized successfully")

    def send_notification(self, email_to: str, text: str, login: str, password: str, mail_domain: str = "yandex.ru"):
        """
        Метод для отправки уведомления на почту.

        Args:
            email_to: Адрес получателя
            text: Текст уведомления
            login: Логин для авторизации в почте
            password: Пароль для авторизации в IMAP
            mail_domain: Домен для отправки уведомления. По умолчанию: yandex.ru

        Raises:
            SMTPAuthenticationError: Не правильный логин/пароль в .env файле
        """

        # Проверка, что пользователь передал логин и пароль
        if not login or not password:
            # Логируем не переданные данные
            self.logger.error("Email or password missing")

            # Возвращаем текст ошибки
            return "Не настроена почта отправителя (в Настройках)"

        try:
            # Задаем заголовки, чтобы письмо не попало в спам
            message = EmailMessage()
            message["From"] = f"{login}@{mail_domain}" # От кого письмо
            message["To"] = email_to                             # Кому отправлять письмо
            message["Subject"] = "Уведомление"                   # Заголовок письма
            message.set_content(text, charset="utf-8")           # Тело письма (текст)

            # Подключаемся к SMTP-серверу, указывая хост и порт
            # Если в домене есть упоминание про yandex
            if "yandex" in mail_domain:
                smtp_server = "smtp.yandex.ru" # Устанавливаем сервер как smtp.yandex.ru
            else:
                smtp_server = "smtp.gmail.com" # Иначе используем smtp.gmail.com

            with smtplib.SMTP_SSL(smtp_server, 465) as server:
                server.login(login, password) # Логин и пароль для входа
                server.send_message(message) # Отправка сообщения

            # Логируем удачную отправку сообщения через почту
            self.logger.info(f"Уведомление отправлено на почту {email_to}")

        except smtplib.SMTPAuthenticationError:
            # Логируем ошибку аутентификации
            self.logger.error("SMTP аутентификация не удалась. Проверьте пароли приложений в почте.")
            # Возвращаем ошибку
            return "Не удалось авторизоваться по введенному логину и паролю. Проверьте пароли приложений на почте"
        except Exception as e:
            # Логируем ошибку при отправке email
            self.logger.error(f"Ошибка при отправке email: {e}")
            # Возвращаем ошибку
            return f"Ошибка при отправке email {e}"
