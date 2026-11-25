"""The synthetic examples of add-walking-skeleton, as fixtures validated against the models."""

import pytest
from pydantic import BaseModel, ValidationError

from app import contract
from app.contract import ClassMetadata, ErrorCode, metadata_error_code
from tests.conftest import FIXTURES, load_fixture

VALID = {
    "class-metadata.json": contract.ClassMetadata,
    "class-accepted.json": contract.ClassAccepted,
    "job-analyzing.json": contract.Job,
    "job-retry-wait.json": contract.Job,
    "result-draft.json": contract.Result,
    "review-request.json": contract.ReviewRequest,
    "result-reviewed.json": contract.Result,
    "approve-request.json": contract.ApproveRequest,
    "approval-response.json": contract.ApprovalResponse,
    "error-result-version-conflict.json": contract.ErrorResponse,
    "error-invalid-participants.json": contract.ErrorResponse,
    "error-unauthenticated.json": contract.ErrorResponse,
    "error-invalid-consent-reference.json": contract.ErrorResponse,
    "error-audio-too-large.json": contract.ErrorResponse,
    "error-unsupported-audio.json": contract.ErrorResponse,
    "error-invalid-audio-duration.json": contract.ErrorResponse,
}
INVALID = sorted(path.name for path in (FIXTURES / "invalid").glob("*.json"))


def test_every_valid_fixture_has_a_model():
    assert sorted(path.name for path in (FIXTURES / "valid").glob("*.json")) == sorted(VALID)


@pytest.mark.parametrize(("name", "model"), VALID.items())
def test_valid_fixture(name: str, model: type[BaseModel]):
    payload = load_fixture(f"valid/{name}")
    parsed = model.model_validate(payload)
    assert parsed.model_dump(mode="json", exclude_unset=True) == payload


@pytest.mark.parametrize("name", INVALID)
def test_invalid_fixture(name: str):
    fixture = load_fixture(f"invalid/{name}")
    model: type[BaseModel] = getattr(contract, fixture["model"])
    with pytest.raises(ValidationError) as raised:
        model.model_validate(fixture["payload"])
    if "metadata_error_code" in fixture:
        expected = ErrorCode(fixture["metadata_error_code"])
        assert metadata_error_code(raised.value.errors()) is expected


def test_reviewed_result_applies_the_review_request():
    draft = contract.Result.model_validate(load_fixture("valid/result-draft.json"))
    request = contract.ReviewRequest.model_validate(load_fixture("valid/review-request.json"))
    reviewed = contract.Result.model_validate(load_fixture("valid/result-reviewed.json"))
    assert request.expected_result_version == draft.result_version
    assert reviewed.result_version == draft.result_version + 1
    assert reviewed.analysis == request.changes.analysis
    assert reviewed.transcript == draft.transcript


def test_metadata_without_problems_on_participants_or_consent_is_an_invalid_request():
    with pytest.raises(ValidationError) as raised:
        ClassMetadata.model_validate({})
    assert metadata_error_code(raised.value.errors()) is ErrorCode.INVALID_CONSENT_REFERENCE
    errors = [{"type": "string_too_long", "loc": ("external_class_id",)}]
    assert metadata_error_code(errors) is ErrorCode.INVALID_REQUEST


def test_readiness_names_dependencies_only():
    ready = contract.Readiness.model_validate({"status": "ready", "dependencies": {"db": "ok"}})
    assert ready.dependencies["db"] is contract.DependencyStatus.OK
    with pytest.raises(ValidationError):
        contract.Readiness.model_validate(
            {"status": "unavailable", "dependencies": {"postgresql://user:pw@db": "unavailable"}}
        )
