"""FastAPI application of the api component."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Engine

from app.api.auth import dev_router
from app.api.errors import REQUEST_ID_HEADER, install_error_handling
from app.api.routes import operation_router, router
from app.api.upload_limits import UploadSizeLimitMiddleware
from app.contract import CONTRACT_VERSION
from app.db import make_engine
from app.jobs import JobStore, PostgresJobStore
from app.settings import Settings
from app.storage import AudioProbe, AudioStorage, DiskAudioStorage, FfprobeAudioProbe

DESCRIPTION = """\
Contract between the CoTeach AI service and its consumers (the web and CoTeach).
Rules that this document does not tell, such as authentication, visibility and compatibility,
are in docs/CONTRACTS/coteach-ai-api.md.
"""


def create_app(
    settings: Settings | None = None,
    store: JobStore | None = None,
    engine: Engine | None = None,
    storage: AudioStorage | None = None,
    probe: AudioProbe | None = None,
) -> FastAPI:
    """Build the api. Without a store or an engine they come from DATABASE_URL, if set.

    The audio goes to AUDIO_STORAGE_DIR and is checked with ffprobe unless a storage or a probe
    is given.
    """
    settings = settings or Settings.from_env()
    if engine is None and settings.database_url:
        engine = make_engine(settings.database_url)
    if store is None and engine is not None:
        store = PostgresJobStore(engine)

    app = FastAPI(title="CoTeach AI API", version=CONTRACT_VERSION, description=DESCRIPTION)
    app.state.settings = settings
    app.state.engine = engine
    app.state.store = store
    app.state.storage = storage or DiskAudioStorage(settings.audio_storage_dir)
    app.state.probe = probe or FfprobeAudioProbe()
    install_error_handling(app)
    app.add_middleware(UploadSizeLimitMiddleware, settings=settings)
    if settings.frontend_origin:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[settings.frontend_origin],
            allow_methods=["GET", "POST", "PATCH"],
            allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
            expose_headers=[REQUEST_ID_HEADER],
        )
    app.include_router(operation_router)
    app.include_router(router)
    if settings.auth_dev_issuer:
        app.include_router(dev_router)
    return app


app = create_app()
