import logging

from telegram.telegram_client import TelegramAccount

logging.basicConfig(level=logging.DEBUG)


if __name__ == "__main__":
    account = TelegramAccount(session_path="client_session")
    account.create_session()