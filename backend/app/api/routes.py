"""Routes of the contract v0.1 under /v1.

They declare inputs, outputs and errors of the contract. Until section 2 of add-walking-skeleton
gives them behaviour, every route validates its input and answers 501.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, Form, Header, Path, UploadFile, status
from fastapi.security import HTTPBearer
from pydantic import Json

from app.api.errors import not_implemented
from app.contract import (
    ApprovalResponse,
    ApproveRequest,
    ClassAccepted,
    ClassMetadata,
    ErrorResponse,
    Health,
    Identifier,
    Job,
    Readiness,
    Result,
    ReviewRequest,
)

bearer = HTTPBearer(
    auto_error=False,
    scheme_name="bearerToken",
    description="Signed token of the identity issuer. The role comes from it, never from the body.",
)
"""Declares the credential in the contract. Section 2 validates it (spec api-access)."""

router = APIRouter(prefix="/v1", dependencies=[Depends(bearer)])
operation_router = APIRouter(tags=["operation"])
"""Health and readiness: no credential and no class data (spec service-operation)."""

ClassId = Annotated[Identifier, Path(description="Unknown or malformed ids answer 404")]
JobId = Annotated[Identifier, Path(description="Unknown or malformed ids answer 404")]


def _errors(*statuses: int) -> dict[int | str, dict[str, Any]]:
    descriptions = {
        401: "Missing, expired or invalid credential (`unauthenticated`)",
        403: "Operation not allowed on a class the caller can see (`forbidden`)",
        404: "Unknown resource or one the caller cannot see (`resource_not_available`)",
        409: "Conflict with the current state",
        413: "Audio larger than allowed (`audio_too_large`)",
        415: "Audio format not supported (`unsupported_audio`)",
        422: "Invalid request",
        500: "Unexpected error (`internal_error`)",
        503: "Transient unavailability (`service_unavailable`, retryable)",
    }
    common = (401, 403, 404, 422, 500, 503)
    return {
        code: {"model": ErrorResponse, "description": descriptions[code]}
        for code in sorted({*common, *statuses})
    }


@router.post(
    "/classes",
    operation_id="submitClass",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ClassAccepted,
    summary="Submit the audio and metadata of a class",
    description=(
        "Creates the class and its processing job and answers without waiting for the "
        "processing. Allowed to a teacher or to the CoTeach service credential. 409 "
        "`idempotency_conflict` when the Idempotency-Key was used with other content; 422 "
        "`invalid_participants`, `invalid_consent_reference` or `invalid_request`."
    ),
    responses=_errors(403, 409, 413, 415),
)
def submit_class(
    audio: Annotated[UploadFile, File(description="Audio of the class")],
    metadata: Annotated[Json[ClassMetadata], Form(description="ClassMetadata serialized as JSON")],
    idempotency_key: Annotated[
        str | None,
        Header(
            alias="Idempotency-Key",
            min_length=1,
            max_length=128,
            description="Same key and content return the same class; same key, other content: 409",
        ),
    ] = None,
) -> ClassAccepted:
    raise not_implemented()


@router.get(
    "/jobs/{job_id}",
    operation_id="getJob",
    response_model=Job,
    summary="State and stage of a processing job",
    responses=_errors(),
)
def get_job(job_id: JobId) -> Job:
    raise not_implemented()


@router.get(
    "/classes/{class_id}/result",
    operation_id="getClassResult",
    response_model=Result,
    summary="Result of a class visible to the caller",
    description=(
        "Teachers of the class see the draft; students only the published version. 409 "
        "`result_not_ready` while the job has not finished."
    ),
    responses=_errors(409),
)
def get_class_result(class_id: ClassId) -> Result:
    raise not_implemented()


@router.patch(
    "/classes/{class_id}/review",
    operation_id="reviewClassResult",
    response_model=Result,
    summary="Correct the result and create a new version",
    description=(
        "Each section sent replaces that whole section; absent ones are kept. 409 "
        "`result_version_conflict` when expected_result_version is stale; 422 "
        "`invalid_review_changes` for an invalid change or reference."
    ),
    responses=_errors(403, 409),
)
def review_class_result(class_id: ClassId, request: ReviewRequest) -> Result:
    raise not_implemented()


@router.post(
    "/classes/{class_id}/approve",
    operation_id="approveClassResult",
    response_model=ApprovalResponse,
    summary="Approve and publish a version of the result",
    description="409 `result_version_conflict` when expected_result_version is stale.",
    responses=_errors(403, 409),
)
def approve_class_result(class_id: ClassId, request: ApproveRequest) -> ApprovalResponse:
    raise not_implemented()


@operation_router.get(
    "/health",
    operation_id="getHealth",
    response_model=Health,
    summary="The api process is alive",
    description="Answers 200 while the process runs, even if a dependency is down.",
)
def get_health() -> Health:
    return Health(status="ok")


@operation_router.get(
    "/ready",
    operation_id="getReadiness",
    response_model=Readiness,
    summary="The dependencies of the api are available",
    description=(
        "503 with the same body when a dependency, such as the database, is not available. "
        "Never includes credentials or connection strings."
    ),
    responses={503: {"model": Readiness, "description": "A dependency is not available"}},
)
def get_readiness() -> Readiness:
    raise not_implemented()
