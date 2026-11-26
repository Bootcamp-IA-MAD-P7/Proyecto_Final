"""Early multipart reception limits of POST /v1/classes (Issue #54)."""

import asyncio
import json

import pytest

from app.api.upload_limits import MULTIPART_OVERHEAD_BYTES, UploadSizeLimitMiddleware
from app.main import create_app
from app.settings import Settings
from tests.conftest import SETTINGS
from tests.test_routes import STUDENT, TEACHER, assert_error


def _scope(headers: dict[str, str]) -> dict:
    return {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/v1/classes",
        "raw_path": b"/v1/classes",
        "query_string": b"",
        "headers": [(name.lower().encode(), value.encode()) for name, value in headers.items()],
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
        "root_path": "",
    }


def _call(app, headers: dict[str, str], messages: list[dict]) -> tuple[list[dict], int]:
    sent: list[dict] = []
    received = 0

    async def receive():
        nonlocal received
        received += 1
        return messages.pop(0)

    async def send(message):
        sent.append(message)

    asyncio.run(app(_scope(headers), receive, send))
    return sent, received


def _status(sent: list[dict]) -> int:
    return next(message["status"] for message in sent if message["type"] == "http.response.start")


def _error_code(sent: list[dict]) -> str:
    body = b"".join(
        message.get("body", b"") for message in sent if message["type"] == "http.response.body"
    )
    return json.loads(body)["error"]["code"]


def _over_limit_headers(*, content_length: int | None = None, headers: dict | None = None) -> dict:
    result = {
        **TEACHER,
        "Content-Type": "multipart/form-data; boundary=upload-boundary",
        **(headers or {}),
    }
    if content_length is not None:
        result["Content-Length"] = str(content_length)
    return result


LIMITED_SETTINGS = Settings(auth_secret=SETTINGS.auth_secret, upload_max_bytes=10)


@pytest.fixture
def limited_app(store, audio_storage, probe):
    return create_app(LIMITED_SETTINGS, store=store, storage=audio_storage, probe=probe)


def test_content_length_above_the_multipart_limit_is_rejected_before_receiving_the_body(
    limited_app, store, audio_storage
):
    max_request = LIMITED_SETTINGS.upload_max_bytes + MULTIPART_OVERHEAD_BYTES

    sent, received = _call(
        limited_app,
        _over_limit_headers(content_length=max_request + 1),
        [{"type": "http.request", "body": b"", "more_body": False}],
    )

    assert (_status(sent), _error_code(sent), received) == (413, "audio_too_large", 0)
    assert store.claim_next() is None
    assert audio_storage.list() == []


def test_body_without_content_length_is_stopped_at_the_multipart_limit(limited_app):
    body = b"x" * (LIMITED_SETTINGS.upload_max_bytes + MULTIPART_OVERHEAD_BYTES + 1)

    sent, received = _call(
        limited_app,
        _over_limit_headers(),
        [
            {"type": "http.request", "body": body, "more_body": True},
            {"type": "http.request", "body": b"must not be consumed", "more_body": False},
        ],
    )

    assert (_status(sent), _error_code(sent), received) == (413, "audio_too_large", 1)


def test_content_length_smaller_than_the_received_body_is_stopped(limited_app):
    body = b"x" * (LIMITED_SETTINGS.upload_max_bytes + MULTIPART_OVERHEAD_BYTES + 1)

    sent, received = _call(
        limited_app,
        _over_limit_headers(content_length=1),
        [{"type": "http.request", "body": body, "more_body": False}],
    )

    assert (_status(sent), _error_code(sent), received) == (413, "audio_too_large", 1)


def test_multipart_margin_is_accepted_without_changing_the_audio_limit():
    received: list[bytes] = []

    async def next_app(scope, receive, send):
        message = await receive()
        received.append(message["body"])
        await send({"type": "http.response.start", "status": 204, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    middleware = UploadSizeLimitMiddleware(next_app, LIMITED_SETTINGS)
    maximum = LIMITED_SETTINGS.upload_max_bytes + MULTIPART_OVERHEAD_BYTES
    sent, calls = _call(
        middleware,
        _over_limit_headers(content_length=maximum),
        [{"type": "http.request", "body": b"x" * maximum, "more_body": False}],
    )

    assert _status(sent) == 204
    assert calls == 1
    assert len(received[0]) == maximum


def test_oversized_upload_preserves_authentication_and_authorization_priority(limited_app):
    max_request = LIMITED_SETTINGS.upload_max_bytes + MULTIPART_OVERHEAD_BYTES + 1

    unauthenticated, unauthenticated_reads = _call(
        limited_app,
        {"Content-Length": str(max_request)},
        [{"type": "http.request", "body": b"", "more_body": False}],
    )
    forbidden, forbidden_reads = _call(
        limited_app,
        _over_limit_headers(content_length=max_request, headers=STUDENT),
        [{"type": "http.request", "body": b"", "more_body": False}],
    )

    assert (_status(unauthenticated), _error_code(unauthenticated), unauthenticated_reads) == (
        401,
        "unauthenticated",
        0,
    )
    assert (_status(forbidden), _error_code(forbidden), forbidden_reads) == (403, "forbidden", 0)


def test_existing_multipart_submission_still_reports_contract_errors(client):
    response = client.post("/v1/classes", headers=TEACHER, data={"metadata": "not json"})

    assert_error(response, 422, "invalid_request")
