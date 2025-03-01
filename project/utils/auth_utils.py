from datetime import timedelta, datetime
from typing import Union

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel

from config import get_settings
from database.database import AsyncMongoClient
from database.models import UserDbModel

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


class TokenData(BaseModel):
    user_login: Union[str, None] = None


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

async def authenticate_user(login: str, password: str) -> Union[UserDbModel, None]:
    try:
        db = AsyncMongoClient()
        user: Union[UserDbModel, None] = await db.get_user_by_login(username=login)
        if user and user.active and verify_password(password, user.user_hashed_password):
            return user
        else:
            return None
    except Exception:
        return None


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(payload=to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_user(token: str = Depends(oauth2_scheme)) -> Union[UserDbModel, None]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_login: str = payload.get("sub")
        if user_login is None:
            raise credentials_exception
        token_data = TokenData(user_login=user_login)
        db = AsyncMongoClient()
        user: Union[UserDbModel, None] = await db.get_user_by_login(username=token_data.user_login)
        if user:
            return user
        else:
            raise credentials_exception
    except Exception:
        raise credentials_exception
