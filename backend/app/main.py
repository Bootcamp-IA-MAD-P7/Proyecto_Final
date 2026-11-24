"""FastAPI application of the api component."""

from __future__ import annotations

from fastapi import FastAPI

from app.api.errors import install_error_handling
from app.api.routes import operation_router, router
from app.contract import CONTRACT_VERSION

DESCRIPTION = """\
Contract between the CoTeach AI service and its consumers (the web and CoTeach).
Rules that this document does not tell, such as authentication, visibility and compatibility,
are in docs/CONTRACTS/coteach-ai-api.md.
"""


def create_app() -> FastAPI:
    app = FastAPI(title="CoTeach AI API", version=CONTRACT_VERSION, description=DESCRIPTION)
    install_error_handling(app)
    app.include_router(operation_router)
    app.include_router(router)
    return app


app = create_app()
