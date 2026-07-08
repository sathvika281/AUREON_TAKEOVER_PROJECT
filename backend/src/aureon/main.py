from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aureon.api.router import api_router
from aureon.api.v1 import health
from aureon.core.config import get_settings
from aureon.core.exceptions import register_exception_handlers
from aureon.core.logging import configure_logging

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    configure_logging(settings)
    logger.info("aureon.startup", environment=settings.environment)
    yield
    logger.info("aureon.shutdown")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title="Aureon API", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(health.router)
    app.include_router(api_router)

    return app


app = create_app()
