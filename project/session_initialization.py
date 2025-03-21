import logging

from telegram.telegram_client import TelegramAccount

logging.basicConfig(level=logging.DEBUG)


if __name__ == "__main__":
    account = TelegramAccount(session_file_name="client_session", app_id=0, app_hash="")
    account.create_session()