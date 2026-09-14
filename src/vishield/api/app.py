"""FastAPI application factory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from vishield import __version__
from vishield.api.errors import register_exception_handlers
from vishield.api.routes import router
from vishield.config import Settings, get_settings
from vishield.domain.safety import ETHICS_BANNER
from vishield.infra.db import Database
from vishield.infra.logging import configure_logging
from vishield.infra.repository import AnalysisRepository
from vishield.services.analyzer import AnalysisService

DESCRIPTION = f"""
**{ETHICS_BANNER}**

Endpoints analyse transcripts or short recordings for social-engineering indicators and
return an explainable risk score with defensive recommendations.
"""


def create_app(settings: Settings | None = None, service: AnalysisService | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if service is not None:
            app.state.service = service
        else:
            repository = AnalysisRepository(Database(settings.database_url))
            app.state.service = AnalysisService(settings, repository=repository)
        yield

    app = FastAPI(
        title="ViShield API",
        version=__version__,
        description=DESCRIPTION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.include_router(router)
    register_exception_handlers(app)
    return app


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run("vishield.api.app:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
