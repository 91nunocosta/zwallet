from fastapi import FastAPI

from .auth.router import router as users_router
from .settings import Settings


def create_api() -> FastAPI:
    Settings()  # type: ignore
    api = FastAPI()
    api.include_router(users_router)
    return api
