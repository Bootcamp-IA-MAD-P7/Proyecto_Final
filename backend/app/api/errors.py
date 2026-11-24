"""Every error of the API leaves with the contract envelope (ErrorResponse) and a request_id."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.contract import DEFAULT_MESSAGES, RETRYABLE_CODES, ErrorCode, metadata_error_code

REQUEST_ID_HEADER = "X-Request-ID"
NOT_IMPLEMENTED = "not_implemented"
"""Code of the 501 answered by routes not built yet. Temporary, so not part of the contract."""


class ApiError(Exception):
    """An error answered with the contract envelope."""

    def __init__(
        self,
        status_code: int,
        code: ErrorCode | str,
        message: str | None = None,
        retryable: bool | None = None,
    ) -> None:
        super().__init__(code)
        self.status_code = status_code
        self.code = str(code)
        known = ErrorCode(code) if code in ErrorCode.__members__.values() else None
        self.message = message or (DEFAULT_MESSAGES[known] if known else "Error")
        self.retryable = retryable if retryable is not None else known in RETRYABLE_CODES


def not_implemented() -> ApiError:
    return ApiError(501, NOT_IMPLEMENTED, "Operación todavía no disponible", retryable=False)


def error_response(request: Request, error: ApiError) -> JSONResponse:
    body = {
        "error": {"code": error.code, "message": error.message, "retryable": error.retryable},
        "request_id": request_id(request),
    }
    return JSONResponse(
        body, status_code=error.status_code, headers={REQUEST_ID_HEADER: body["request_id"]}
    )


def request_id(request: Request) -> str:
    if not getattr(request.state, "request_id", None):
        request.state.request_id = new_request_id()
    return request.state.request_id


def new_request_id() -> str:
    return f"request-{uuid4().hex}"


_STATUS_CODES = {
    401: ErrorCode.UNAUTHENTICATED,
    403: ErrorCode.FORBIDDEN,
    404: ErrorCode.RESOURCE_NOT_AVAILABLE,
    503: ErrorCode.SERVICE_UNAVAILABLE,
}


def is_path_error(errors: list[dict[str, Any]]) -> bool:
    """An identifier in the URL that cannot exist: answered like an unknown resource (404)."""
    return any(error["loc"][:1] == ("path",) for error in errors)


def validation_error_code(errors: list[dict[str, Any]]) -> ErrorCode:
    """Contract code of a request validation error (422)."""
    metadata_errors = [
        {**error, "loc": tuple(error["loc"][2:])}
        for error in errors
        if tuple(error["loc"][:2]) == ("body", "metadata")
    ]
    if metadata_errors:
        return metadata_error_code(metadata_errors)
    if any(tuple(error["loc"][:2]) == ("body", "changes") for error in errors):
        return ErrorCode.INVALID_REVIEW_CHANGES
    return ErrorCode.INVALID_REQUEST


def install_error_handling(app: FastAPI) -> None:
    @app.middleware("http")
    async def assign_request_id(request: Request, call_next):
        request_id(request)
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request.state.request_id
        return response

    @app.exception_handler(ApiError)
    async def handle_api_error(request: Request, exc: ApiError) -> JSONResponse:
        return error_response(request, exc)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        # Details are left out on purpose: they could echo personal data from the request.
        errors = [{**error, "loc": tuple(error["loc"])} for error in exc.errors()]
        if is_path_error(errors):
            return error_response(request, ApiError(404, ErrorCode.RESOURCE_NOT_AVAILABLE))
        return error_response(request, ApiError(422, validation_error_code(errors)))

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        fallback = (
            ErrorCode.SERVICE_UNAVAILABLE if exc.status_code >= 500 else ErrorCode.INVALID_REQUEST
        )
        code = _STATUS_CODES.get(exc.status_code, fallback)
        response = error_response(request, ApiError(exc.status_code, code))
        if exc.headers:
            response.headers.update(exc.headers)
        return response

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        # Logged by the server; the client only gets the envelope, never the trace.
        return error_response(request, ApiError(500, ErrorCode.INTERNAL_ERROR))
