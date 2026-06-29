from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.core.di import get_container
from src.core.exceptions import register_exception_handlers
from src.core.logging import configure_logging, get_logger
from src.core.middleware import RequestIdMiddleware
from src.infrastructure.observability import configure_tracing
from src.modules.drivepass.documents.infrastructure.bindings import register_document_bindings
from src.modules.identity.infrastructure.bindings import register_identity_bindings
from src.modules.intelligence.infrastructure.bindings import register_intelligence_bindings
from src.presentation.api.v1 import api_v1_router

settings = get_settings()
configure_logging(settings)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    logger.info("startup", environment=settings.environment)
    yield
    logger.info("shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        docs_url=f"{settings.api_v1_prefix}/docs",
        lifespan=lifespan,
    )

    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    configure_tracing(app, settings)
    register_identity_bindings(get_container(), settings)
    register_document_bindings(get_container(), settings)
    register_intelligence_bindings(get_container(), settings)

    app.include_router(api_v1_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
