from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from project.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


# class TokenData(BaseModel):
#     user_login: Union[str, None] = None
#
#
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)
#
#
# def get_password_hash(password):
#     return pwd_context.hash(password)
#
# async def authenticate_admin(login: str, password: str):
#     # try:
#     #     admin: Admin = await Admin.get_by_login(login=login)
#     # except NoResultFound:
#     #     return False
#     if not verify_password(password, "default"):
#         return False
#     return admin
#
#
# def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.now() + expires_delta
#     else:
#         expire = datetime.now() + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(payload=to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
#     return encoded_jwt
#
#
# async def get_admin(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         user_login: str = payload.get("sub")
#         if user_login is None:
#             raise credentials_exception
#         token_data = TokenData(user_login=user_login)
#     except InvalidTokenError:
#         raise credentials_exception
#     try:
#         admin: Admin = await Admin.get_by_login(login=token_data.user_login)
#     except NoResultFound:
#         raise credentials_exception
#     return admin