"""Early body limit for class submissions, before multipart parsing allocates the upload."""

from __future__ import annotations

from contextlib import suppress

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.api.access import can_submit
from app.api.auth import principal_from_authorization
from app.api.errors import ApiError, error_response
from app.contract import ErrorCode
from app.settings import Settings

MULTIPART_OVERHEAD_BYTES = 64 * 1024
"""Room for multipart boundaries and the JSON metadata, not additional audio bytes."""


class RequestBodyTooLarge(HTTPException):
    """The raw multipart request crossed its bounded reception limit."""

    def __init__(self) -> None:
        super().__init__(status_code=413)


class UploadSizeLimitMiddleware:
    """Reject oversized authenticated class uploads without reading their remaining body.

    The multipart envelope has bounded room beyond ``UPLOAD_MAX_BYTES``. The exact audio limit
    remains enforced by ``receive_audio`` once the ``audio`` part is streamed to private storage.
    """

    def __init__(self, app: ASGIApp, settings: Settings) -> None:
        self.app = app
        self.settings = settings
        self.max_request_bytes = settings.upload_max_bytes + MULTIPART_OVERHEAD_BYTES

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["method"] != "POST" or scope["path"] != "/v1/classes":
            await self.app(scope, receive, send)
            return

        error = self._authorization_error(scope)
        if error is not None:
            await _send_error(scope, receive, send, error)
            return
        if _content_length(scope) > self.max_request_bytes:
            await _send_error(scope, receive, send, ApiError(413, ErrorCode.AUDIO_TOO_LARGE))
            return

        received = 0
        body_limit_exceeded = False
        response_messages: list[Message] = []

        async def limited_receive() -> Message:
            nonlocal body_limit_exceeded, received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_request_bytes:
                    body_limit_exceeded = True
                    raise RequestBodyTooLarge()
            return message

        async def buffer_response(message: Message) -> None:
            response_messages.append(message)

        with suppress(RequestBodyTooLarge):
            # The multipart parser usually catches this exception and prepares a 400. When it
            # does not, the resulting contract response is still the same 413 below.
            await self.app(scope, limited_receive, buffer_response)
        if body_limit_exceeded:
            await _send_error(scope, receive, send, ApiError(413, ErrorCode.AUDIO_TOO_LARGE))
            return
        for message in response_messages:
            await send(message)

    def _authorization_error(self, scope: Scope) -> ApiError | None:
        headers = scope.get("headers", [])
        authorization = next(
            (
                value.decode("latin-1")
                for name, value in headers
                if name.lower() == b"authorization"
            ),
            None,
        )
        try:
            principal = principal_from_authorization(self.settings, authorization)
        except ApiError as error:
            return error
        if not can_submit(principal):
            return ApiError(403, ErrorCode.FORBIDDEN)
        return None


def _content_length(scope: Scope) -> int:
    raw = next(
        (value for name, value in scope.get("headers", []) if name.lower() == b"content-length"),
        None,
    )
    try:
        return int(raw) if raw is not None else 0
    except ValueError:
        return 0


async def _send_error(scope: Scope, receive: Receive, send: Send, error: ApiError) -> None:
    request = Request(scope, receive=receive)
    response: JSONResponse = error_response(request, error)
    await response(scope, receive, send)
