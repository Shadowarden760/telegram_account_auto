import asyncio

import uvicorn
from fastapi import FastAPI

from api import users, admins
from config import get_settings
from database.database import AsyncMongoClient

settings = get_settings()

app = FastAPI()
app.include_router(router=users.router)
app.include_router(router=admins.router)


async def main():
    db = AsyncMongoClient()
    await db.create_admin()
    if settings.DEBUG:
        uvicorn.run(app="main:app", reload=True, proxy_headers=True, host="0.0.0.0", port=8000)
    else:
        uvicorn.run(app="main:app", proxy_headers=True, host="0.0.0.0", port=8000, workers=4)



if __name__ == "__main__":
    asyncio.run(main())
