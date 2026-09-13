from fastapi import FastAPI

from api.routes import chat, figma, health
from config.settings import settings

app = FastAPI(title=settings.app_name)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(figma.router)
