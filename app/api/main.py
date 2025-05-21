from fastapi import APIRouter

from app.api.routes import chat, cities, health, users

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(users.router)
api_router.include_router(cities.router)
api_router.include_router(chat.router)
