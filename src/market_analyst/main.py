from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from market_analyst.api.asset_routes import router as asset_router
from market_analyst.api.routes import router
from market_analyst.config import get_settings
from market_analyst.logging import setup_logging


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.log_level)
    app = FastAPI(title=settings.app_name, version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["*"], allow_headers=["*"],
    )
    app.include_router(router)
    return app

app = create_app()
app.include_router(asset_router)
