"""Routes of the contract v0.1 under /v1.

They declare inputs, outputs and errors of the contract and answer from the JobStore. Access to
each class is resolved on the server (spec api-access). Review and approval answer the contract
examples without saving anything until E5.
"""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path as FilePath
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, Form, Header, Path, Request, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import Json

from app.api.access import can_see, can_submit, teaches
from app.api.auth import CurrentPrincipal, get_principal
from app.api.errors import ApiError
from app.auth.principal import Principal
from app.contract import (
    ApprovalResponse,
    ApproveRequest,
    ClassAccepted,
    ClassMetadata,
    DependencyStatus,
    ErrorCode,
    ErrorResponse,
    Health,
    Identifier,
    Job,
    JobState,
    PublicationStatus,
    Readiness,
    Result,
    ReviewRequest,
)
from app.db import database_available
from app.jobs import JobStore, StoredClass

EXAMPLES = FilePath(__file__).resolve().parents[1] / "contract" / "examples"


def get_store(request: Request) -> JobStore:
    store = request.app.state.store
    if store is None:
        raise ApiError(503, ErrorCode.SERVICE_UNAVAILABLE)
    return store


Store = Annotated[JobStore, Depends(get_store)]

router = APIRouter(prefix="/v1", dependencies=[Depends(get_principal)])
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
        "`idempotency_conflict` when the Idempotency-Key was used with other content; 413 "
        "`audio_too_large` above the configured size; 415 `unsupported_audio` when the content "
        "is not Opus, MP3 or AAC audio; 422 `invalid_participants`, `invalid_consent_reference` "
        "or `invalid_request` for the metadata, and `invalid_audio_duration` when the audio is "
        "shorter or longer than the configured limits."
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
    *,
    principal: CurrentPrincipal,
    store: Store,
) -> ClassAccepted:
    # The audio is received and validated in E2; the walking skeleton does not keep it.
    if not can_submit(principal):
        raise ApiError(403, ErrorCode.FORBIDDEN)
    stored = store.create_class(metadata, submitted_by=principal.subject)
    return ClassAccepted(class_id=stored.class_id, job_id=stored.job_id, state=JobState.QUEUED)


@router.get(
    "/jobs/{job_id}",
    operation_id="getJob",
    response_model=Job,
    summary="State and stage of a processing job",
    responses=_errors(),
)
def get_job(job_id: JobId, principal: CurrentPrincipal, store: Store) -> Job:
    job = store.get_job(job_id)
    if job is None:
        raise _not_available()
    _visible_class(store, principal, job.class_id)
    return job


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
def get_class_result(class_id: ClassId, principal: CurrentPrincipal, store: Store) -> Result:
    stored = _visible_class(store, principal, class_id)
    result = store.get_result(class_id)
    if not teaches(principal, stored):
        # Students only see the published version; a draft does not exist for them.
        if result is None or result.publication.status != PublicationStatus.PUBLISHED:
            raise _not_available()
        return result
    if result is None:
        raise ApiError(409, ErrorCode.RESULT_NOT_READY)
    return result


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
def review_class_result(
    class_id: ClassId, request: ReviewRequest, principal: CurrentPrincipal, store: Store
) -> Result:
    _reviewable_class(store, principal, class_id)
    return Result.model_validate({**_example("result-reviewed.json"), "class_id": class_id})


@router.post(
    "/classes/{class_id}/approve",
    operation_id="approveClassResult",
    response_model=ApprovalResponse,
    summary="Approve and publish a version of the result",
    description="409 `result_version_conflict` when expected_result_version is stale.",
    responses=_errors(403, 409),
)
def approve_class_result(
    class_id: ClassId, request: ApproveRequest, principal: CurrentPrincipal, store: Store
) -> ApprovalResponse:
    _reviewable_class(store, principal, class_id)
    example = _example("approval-response.json")
    return ApprovalResponse.model_validate({**example, "class_id": class_id})


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
def get_readiness(request: Request) -> JSONResponse:
    ok = database_available(request.app.state.engine)
    body = Readiness(
        status="ready" if ok else "unavailable",
        dependencies={"database": DependencyStatus.OK if ok else DependencyStatus.UNAVAILABLE},
    )
    return JSONResponse(body.model_dump(mode="json"), status_code=200 if ok else 503)


def _not_available() -> ApiError:
    return ApiError(404, ErrorCode.RESOURCE_NOT_AVAILABLE)


def _visible_class(store: JobStore, principal: Principal, class_id: str) -> StoredClass:
    """The class if the caller can see it; unknown and foreign classes answer the same 404."""
    stored = store.get_class(class_id)
    if stored is None or not can_see(principal, stored):
        raise _not_available()
    return stored


def _reviewable_class(store: JobStore, principal: Principal, class_id: str) -> StoredClass:
    stored = _visible_class(store, principal, class_id)
    if not teaches(principal, stored):
        raise ApiError(403, ErrorCode.FORBIDDEN)
    if store.get_result(class_id) is None:
        raise ApiError(409, ErrorCode.RESULT_NOT_READY)
    return stored


@cache
def _example(name: str) -> dict[str, Any]:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))
