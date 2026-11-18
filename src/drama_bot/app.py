"""FastAPI composition, with no network or database side effects on import."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from drama_bot.config import Settings
from drama_bot.core.api import build_router
from drama_bot.runtime import local_identity, service_for


def create_app(settings=None) -> FastAPI:
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app):
        service = service_for(settings)
        app.state.service = service
        app.include_router(build_router(service, settings, local_identity(settings)))
        try:
            yield
        finally:
            service.engine.dispose()

    app = FastAPI(title="Feishu Drama MVP", version="0.1.0", lifespan=lifespan)

    @app.get("/healthz")
    def health() -> dict[str, str]:
        return {"status": "ok", "generation_quality": "unverified"}

    @app.get("/readyz")
    def ready():
        with app.state.service.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"database": "ok", "generation_quality": "unverified"}

    return app


app = create_app()
