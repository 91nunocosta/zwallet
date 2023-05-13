from fastapi import FastAPI

from .auth.router import router as users_router
from .settings import Settings
from .wallets.router import router as wallets_router


def create_api() -> FastAPI:
    Settings()  # type: ignore
    api = FastAPI()
    api.include_router(users_router)
    api.include_router(wallets_router)
    return api
