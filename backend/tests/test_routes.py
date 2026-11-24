"""Routes of the contract v0.1: they validate their input and, until section 2, answer 501."""

import json

import pytest
from fastapi.testclient import TestClient

from app.contract import ErrorResponse, Health
from app.main import create_app
from tests.conftest import load_fixture

AUDIO = {"audio": ("synthetic-class.mp3", b"synthetic", "audio/mpeg")}


def submit(client, metadata, files=AUDIO, headers=None):
    data = {"metadata": metadata if isinstance(metadata, str) else json.dumps(metadata)}
    return client.post("/v1/classes", files=files, data=data, headers=headers)


def assert_error(response, status: int, code: str, retryable: bool = False):
    assert response.status_code == status
    body = response.json()
    if code != "not_implemented":
        ErrorResponse.model_validate(body)
    assert body["error"]["code"] == code
    assert body["error"]["retryable"] is retryable
    assert body["error"]["message"]
    assert body["request_id"] == response.headers["X-Request-ID"]
    return body


def test_valid_submission_reaches_the_route_stub(client):
    response = submit(
        client,
        load_fixture("valid/class-metadata.json"),
        headers={"Idempotency-Key": "demo-upload-01"},
    )

    assert_error(response, 501, "not_implemented")


@pytest.mark.parametrize(
    "name",
    [
        "class-metadata-duplicate-participants",
        "class-metadata-count-mismatch",
        "class-metadata-missing-consent",
        "class-metadata-blank-consent",
        "class-metadata-missing-external-id",
    ],
)
def test_invalid_metadata_answers_the_contract_code(client, name):
    fixture = load_fixture(f"invalid/{name}.json")

    response = submit(client, fixture["payload"])

    body = assert_error(response, 422, fixture["metadata_error_code"])
    assert "Docente de prueba" not in json.dumps(body)


def test_submission_without_audio_is_an_invalid_request(client):
    response = submit(client, load_fixture("valid/class-metadata.json"), files=None)

    assert_error(response, 422, "invalid_request")


def test_metadata_that_is_not_json_is_an_invalid_request(client):
    assert_error(submit(client, "{not json"), 422, "invalid_request")


@pytest.mark.parametrize(
    ("method", "path", "fixture"),
    [
        ("get", "/v1/jobs/job-demo-01", None),
        ("get", "/v1/classes/class-demo-01/result", None),
        ("patch", "/v1/classes/class-demo-01/review", "valid/review-request.json"),
        ("post", "/v1/classes/class-demo-01/approve", "valid/approve-request.json"),
    ],
)
def test_routes_are_declared_but_not_implemented_yet(client, method, path, fixture):
    body = load_fixture(fixture) if fixture else None

    response = client.request(method, path, json=body)

    assert_error(response, 501, "not_implemented")


def test_invalid_review_changes(client):
    response = client.patch(
        "/v1/classes/class-demo-01/review",
        json={"expected_result_version": 1, "changes": {}},
    )

    assert_error(response, 422, "invalid_review_changes")


def test_unknown_route_uses_the_error_envelope(client):
    assert_error(client.get("/v1/unknown"), 404, "resource_not_available")


@pytest.mark.parametrize("path", ["/v1/jobs/bad%20id", "/v1/jobs/" + "a" * 200])
def test_malformed_ids_answer_like_unknown_resources(client, path):
    assert_error(client.get(path), 404, "resource_not_available")


def test_unexpected_errors_use_the_envelope_without_details():
    app = create_app()

    @app.get("/boom")
    def boom():
        raise RuntimeError("secret detail")

    response = TestClient(app, raise_server_exceptions=False).get("/boom")

    body = assert_error(response, 500, "internal_error")
    assert "secret" not in json.dumps(body)


def test_health_answers_without_credential(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert Health.model_validate(response.json()).status == "ok"


def test_readiness_is_declared_but_not_implemented_yet(client):
    assert_error(client.get("/ready"), 501, "not_implemented")
