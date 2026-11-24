"""Routes of the contract v0.1 with the in-memory store: specs api-access and class-processing."""

import json

import pytest
from fastapi.testclient import TestClient

from app.contract import (
    ApprovalResponse,
    ErrorResponse,
    Health,
    Job,
    JobError,
    JobErrorCode,
    JobStage,
    Publication,
    PublicationMode,
    PublicationStatus,
    Result,
)
from app.main import create_app
from app.settings import Settings
from tests.conftest import SETTINGS, auth, load_fixture, token

AUDIO = {"audio": ("synthetic-class.mp3", b"synthetic", "audio/mpeg")}
TEACHER = auth("demo-teacher", "teacher")
STUDENT = auth("demo-student", "student")
STRANGER = auth("other-teacher", "teacher")
SERVICE = auth("coteach-service", "service")


def submit(client, metadata, files=AUDIO, headers=None):
    data = {"metadata": metadata if isinstance(metadata, str) else json.dumps(metadata)}
    return client.post("/v1/classes", files=files, data=data, headers=headers)


def assert_error(response, status: int, code: str, retryable: bool = False):
    assert response.status_code == status
    body = response.json()
    ErrorResponse.model_validate(body)
    assert body["error"]["code"] == code
    assert body["error"]["retryable"] is retryable
    assert body["error"]["message"]
    assert body["request_id"] == response.headers["X-Request-ID"]
    return body


def submitted(client, headers=TEACHER) -> dict:
    response = submit(client, load_fixture("valid/class-metadata.json"), headers=headers)
    assert response.status_code == 202
    return response.json()


def finish(store, class_id: str, published: bool = False) -> Result:
    job = store.claim_next()
    result = Result.model_validate(
        {**load_fixture("valid/result-draft.json"), "class_id": class_id}
    )
    if published:
        result = result.model_copy(
            update={
                "publication": Publication(
                    status=PublicationStatus.PUBLISHED,
                    result_version=1,
                    published_at="2026-12-10T12:00:00Z",
                    mode=PublicationMode.TEACHER_APPROVED,
                )
            }
        )
    store.complete(job.job_id, result)
    return result


# --- Submission (class-processing) -----------------------------------------------------------


def test_valid_submission_creates_a_queued_job(client, store):
    response = submit(
        client,
        load_fixture("valid/class-metadata.json"),
        headers={**TEACHER, "Idempotency-Key": "demo-upload-01"},
    )

    assert response.status_code == 202
    body = response.json()
    assert body["state"] == "queued"
    assert store.get_job(body["job_id"]).class_id == body["class_id"]
    assert store.get_class(body["class_id"]).submitted_by == "demo-teacher"


def test_service_credential_can_submit(client):
    assert submitted(client, SERVICE)["state"] == "queued"


def test_student_cannot_submit_even_with_a_teacher_role_in_the_body(client, store):
    metadata = load_fixture("valid/class-metadata.json")
    metadata["participants"][1]["role"] = "teacher"

    assert_error(submit(client, metadata, headers=STUDENT), 403, "forbidden")
    assert store.claim_next() is None


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
def test_invalid_metadata_answers_the_contract_code(client, store, name):
    fixture = load_fixture(f"invalid/{name}.json")

    response = submit(client, fixture["payload"], headers=TEACHER)

    body = assert_error(response, 422, fixture["metadata_error_code"])
    assert "Docente de prueba" not in json.dumps(body)
    assert store.claim_next() is None


def test_submission_without_audio_is_an_invalid_request(client, store):
    response = submit(
        client, load_fixture("valid/class-metadata.json"), files=None, headers=TEACHER
    )

    assert_error(response, 422, "invalid_request")
    assert store.claim_next() is None


def test_metadata_that_is_not_json_is_an_invalid_request(client):
    assert_error(submit(client, "{not json", headers=TEACHER), 422, "invalid_request")


# --- Authentication (api-access) -------------------------------------------------------------


@pytest.mark.parametrize(
    ("method", "path", "fixture"),
    [
        ("get", "/v1/jobs/job-demo-01", None),
        ("get", "/v1/classes/class-demo-01/result", None),
        ("patch", "/v1/classes/class-demo-01/review", "valid/review-request.json"),
        ("post", "/v1/classes/class-demo-01/approve", "valid/approve-request.json"),
    ],
)
def test_requests_without_token_are_unauthenticated(client, method, path, fixture):
    body = load_fixture(fixture) if fixture else None

    assert_error(client.request(method, path, json=body), 401, "unauthenticated")


def test_submission_without_token_is_unauthenticated(client, store):
    assert_error(submit(client, load_fixture("valid/class-metadata.json")), 401, "unauthenticated")
    assert store.claim_next() is None


@pytest.mark.parametrize(
    "bad_token",
    [
        token("demo-teacher", "teacher", ttl_seconds=-10),
        token("demo-teacher", "teacher", Settings(auth_secret="another-secret-of-enough-length-x")),
        token(
            "demo-teacher", "teacher", Settings(auth_secret=SETTINGS.auth_secret, auth_audience="x")
        ),
        "not-a-token",
    ],
    ids=["expired", "other-key", "other-audience", "malformed"],
)
def test_invalid_tokens_get_no_class_data(client, bad_token):
    accepted = submitted(client)
    headers = {"Authorization": f"Bearer {bad_token}"}

    response = client.get(f"/v1/jobs/{accepted['job_id']}", headers=headers)

    assert_error(response, 401, "unauthenticated")
    assert accepted["class_id"] not in response.text


@pytest.mark.parametrize("secret", [None, "short-secret"], ids=["missing", "too-short"])
def test_without_a_valid_auth_secret_every_token_is_rejected(store, secret):
    client = TestClient(create_app(Settings(auth_secret=secret), store=store))

    assert_error(client.get("/v1/jobs/job-demo-01", headers=TEACHER), 401, "unauthenticated")


# --- Access to each class (api-access) -------------------------------------------------------


def test_teacher_of_the_class_sees_its_job(client):
    accepted = submitted(client)

    response = client.get(f"/v1/jobs/{accepted['job_id']}", headers=TEACHER)

    assert response.status_code == 200
    job = Job.model_validate(response.json())
    assert (job.state, job.stage, job.class_id) == ("queued", None, accepted["class_id"])


def test_participant_student_sees_the_job_in_progress(client, store):
    accepted = submitted(client)
    store.claim_next()
    store.advance(accepted["job_id"], JobStage.TRANSCRIBING)

    body = client.get(f"/v1/jobs/{accepted['job_id']}", headers=STUDENT).json()

    assert (body["state"], body["stage"], body["attempt"]) == ("transcribing", "transcribing", 1)


@pytest.mark.parametrize(
    "path", ["/v1/jobs/{job_id}", "/v1/classes/{class_id}/result"], ids=["job", "result"]
)
def test_strangers_get_the_same_404_as_unknown_ids(client, store, path):
    accepted = submitted(client)
    finish(store, accepted["class_id"])

    foreign = client.get(path.format(**accepted), headers=STRANGER)
    unknown = client.get(path.format(job_id="job-x", class_id="class-x"), headers=STRANGER)

    assert_error(foreign, 404, "resource_not_available")
    assert_error(unknown, 404, "resource_not_available")
    assert accepted["class_id"] not in foreign.text


def test_failed_job_is_read_with_its_error(client, store):
    accepted = submitted(client)
    store.claim_next()
    error = JobError(code=JobErrorCode.PROCESSING_FAILED, message="Fallo", retryable=False)
    store.fail(accepted["job_id"], error)

    body = client.get(f"/v1/jobs/{accepted['job_id']}", headers=TEACHER).json()

    assert body["state"] == "failed"
    assert body["error"]["code"] == "processing_failed"
    path = f"/v1/classes/{accepted['class_id']}/result"
    assert_error(client.get(path, headers=TEACHER), 409, "result_not_ready")


# --- Results (class-processing, api-access) --------------------------------------------------


def test_result_not_ready_yet(client):
    accepted = submitted(client)

    response = client.get(f"/v1/classes/{accepted['class_id']}/result", headers=TEACHER)

    assert_error(response, 409, "result_not_ready")


def test_teacher_reads_the_draft_result(client, store):
    accepted = submitted(client)
    result = finish(store, accepted["class_id"])

    response = client.get(f"/v1/classes/{accepted['class_id']}/result", headers=TEACHER)

    assert response.status_code == 200
    body = Result.model_validate(response.json())
    assert body == result
    assert (body.schema_version, body.result_version) == ("0.1.0", 1)


def test_class_submitted_by_the_service_is_read_by_its_teacher_only(client, store):
    accepted = submitted(client, SERVICE)
    finish(store, accepted["class_id"])
    path = f"/v1/classes/{accepted['class_id']}"
    approve = load_fixture("valid/approve-request.json")

    assert client.get(f"{path}/result", headers=TEACHER).status_code == 200
    assert_error(client.get(f"{path}/result", headers=SERVICE), 404, "resource_not_available")
    assert_error(client.post(f"{path}/approve", json=approve, headers=SERVICE), 403, "forbidden")


def test_student_participant_does_not_see_an_unpublished_result(client, store):
    accepted = submitted(client)
    finish(store, accepted["class_id"])

    response = client.get(f"/v1/classes/{accepted['class_id']}/result", headers=STUDENT)

    assert_error(response, 404, "resource_not_available")
    assert "segments" not in response.text


def test_student_with_a_teacher_entry_does_not_get_teacher_rights(client, store):
    metadata = load_fixture("valid/class-metadata.json")
    metadata["participants"][1]["role"] = "teacher"
    accepted = submit(client, metadata, headers=TEACHER).json()
    finish(store, accepted["class_id"])

    response = client.get(f"/v1/classes/{accepted['class_id']}/result", headers=STUDENT)

    assert_error(response, 404, "resource_not_available")


def test_student_sees_a_published_result(client, store):
    accepted = submitted(client)
    finish(store, accepted["class_id"], published=True)

    response = client.get(f"/v1/classes/{accepted['class_id']}/result", headers=STUDENT)

    assert response.status_code == 200


# --- Review and approval: contract examples without saving (E5) ------------------------------


def test_review_answers_the_example_without_saving(client, store):
    accepted = submitted(client)
    draft = finish(store, accepted["class_id"])
    path = f"/v1/classes/{accepted['class_id']}/review"

    response = client.patch(path, json=load_fixture("valid/review-request.json"), headers=TEACHER)

    assert response.status_code == 200
    reviewed = Result.model_validate(response.json())
    assert (reviewed.class_id, reviewed.result_version) == (accepted["class_id"], 2)
    assert store.get_result(accepted["class_id"]) == draft


def test_approve_answers_the_example_without_saving(client, store):
    accepted = submitted(client)
    draft = finish(store, accepted["class_id"])
    path = f"/v1/classes/{accepted['class_id']}/approve"

    response = client.post(path, json=load_fixture("valid/approve-request.json"), headers=TEACHER)

    assert response.status_code == 200
    approval = ApprovalResponse.model_validate(response.json())
    assert approval.class_id == accepted["class_id"]
    assert store.get_result(accepted["class_id"]) == draft


@pytest.mark.parametrize(
    ("action", "method", "fixture"),
    [("review", "patch", "review-request"), ("approve", "post", "approve-request")],
)
def test_review_and_approval_need_a_teacher_and_a_result(client, store, action, method, fixture):
    accepted = submitted(client)
    path = f"/v1/classes/{accepted['class_id']}/{action}"
    body = load_fixture(f"valid/{fixture}.json")

    assert_error(client.request(method, path, json=body, headers=TEACHER), 409, "result_not_ready")
    finish(store, accepted["class_id"])
    assert_error(client.request(method, path, json=body, headers=STUDENT), 403, "forbidden")
    assert_error(
        client.request(method, path, json=body, headers=STRANGER), 404, "resource_not_available"
    )


def test_examples_served_by_the_api_are_the_contract_fixtures():
    from app.api.routes import _example

    assert _example("result-reviewed.json") == load_fixture("valid/result-reviewed.json")
    assert _example("approval-response.json") == load_fixture("valid/approval-response.json")


def test_invalid_review_changes(client):
    response = client.patch(
        "/v1/classes/class-demo-01/review",
        json={"expected_result_version": 1, "changes": {}},
        headers=TEACHER,
    )

    assert_error(response, 422, "invalid_review_changes")


# --- Errors and operation ---------------------------------------------------------------------


def test_unknown_route_uses_the_error_envelope(client):
    assert_error(client.get("/v1/unknown", headers=TEACHER), 404, "resource_not_available")


@pytest.mark.parametrize("path", ["/v1/jobs/bad%20id", "/v1/jobs/" + "a" * 200])
def test_malformed_ids_answer_like_unknown_resources(client, path):
    assert_error(client.get(path, headers=TEACHER), 404, "resource_not_available")


def test_unexpected_errors_use_the_envelope_without_details():
    app = create_app(SETTINGS)

    @app.get("/boom")
    def boom():
        raise RuntimeError("secret detail")

    response = TestClient(app, raise_server_exceptions=False).get("/boom")

    body = assert_error(response, 500, "internal_error")
    assert "secret" not in json.dumps(body)


def test_health_answers_without_credential_or_database(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert Health.model_validate(response.json()).status == "ok"


def test_ready_without_a_configured_database_is_unavailable(client):
    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "dependencies": {"database": "unavailable"}}


def test_without_a_database_the_v1_routes_are_unavailable():
    client = TestClient(create_app(SETTINGS))

    assert_error(
        client.get("/v1/jobs/job-demo-01", headers=TEACHER), 503, "service_unavailable", True
    )


# --- CORS -------------------------------------------------------------------------------------


def test_cors_allows_only_the_frontend_origin(store):
    settings = Settings(auth_secret=SETTINGS.auth_secret, frontend_origin="http://localhost:5173")
    client = TestClient(create_app(settings, store=store))
    preflight = {"Access-Control-Request-Method": "GET"}

    allowed = client.options("/v1/jobs/x", headers={"Origin": "http://localhost:5173", **preflight})
    denied = client.options("/v1/jobs/x", headers={"Origin": "http://evil.test", **preflight})

    assert allowed.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "access-control-allow-origin" not in denied.headers
