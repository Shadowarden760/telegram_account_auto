import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    DEBUG: bool = True
    ADMIN_LOGIN: str = os.getenv("ADMIN_LOGIN", "default")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "default")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    TELEGRAM_API_ID: int = os.getenv("TELEGRAM_API_ID")
    TELEGRAM_API_HASH: str = os.getenv("TELEGRAM_API_HASH")
    TELEGRAM_SESSION_PATH: str = str(Path("./sessions/client_session").absolute())

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
