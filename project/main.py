from fastapi import FastAPI
from app.api import users, admins

app = FastAPI()
app.include_router(router=users.router)
app.include_router(router=admins.router)
