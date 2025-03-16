from datetime import timedelta
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from api.auth_utils import authenticate_user, create_access_token
from database.models import UserDbModel
from config import get_settings

settings = get_settings()

router = APIRouter()

@router.post("/login", name="login", tags=["default"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user: Union[UserDbModel, None] = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}