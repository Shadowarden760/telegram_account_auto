import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    DEBUG: bool = True
    ADMIN_LOGIN = os.getenv("ADMIN_LOGIN", "default")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "default")
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()