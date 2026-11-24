"""Error envelope of the CoTeach AI API contract."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from enum import StrEnum
from typing import Any

from pydantic import Field

from app.contract.models import ContractModel, Identifier, NonEmptyText


class ErrorCode(StrEnum):
    UNAUTHENTICATED = "unauthenticated"
    FORBIDDEN = "forbidden"
    RESOURCE_NOT_AVAILABLE = "resource_not_available"
    INVALID_REQUEST = "invalid_request"
    INVALID_PARTICIPANTS = "invalid_participants"
    INVALID_CONSENT_REFERENCE = "invalid_consent_reference"
    INVALID_REVIEW_CHANGES = "invalid_review_changes"
    IDEMPOTENCY_CONFLICT = "idempotency_conflict"
    RESULT_NOT_READY = "result_not_ready"
    RESULT_VERSION_CONFLICT = "result_version_conflict"
    AUDIO_TOO_LARGE = "audio_too_large"
    UNSUPPORTED_AUDIO = "unsupported_audio"
    SERVICE_UNAVAILABLE = "service_unavailable"


DEFAULT_MESSAGES: dict[ErrorCode, str] = {
    ErrorCode.UNAUTHENTICATED: "Se requiere autenticación válida",
    ErrorCode.FORBIDDEN: "No tienes permiso para esta operación",
    ErrorCode.RESOURCE_NOT_AVAILABLE: "El recurso no está disponible",
    ErrorCode.INVALID_REQUEST: "La petición no es válida",
    ErrorCode.INVALID_PARTICIPANTS: "Los participantes no son válidos",
    ErrorCode.INVALID_CONSENT_REFERENCE: "Se requiere una referencia de consentimiento válida",
    ErrorCode.INVALID_REVIEW_CHANGES: "Los cambios de la revisión no son válidos",
    ErrorCode.IDEMPOTENCY_CONFLICT: "La clave de idempotencia ya se usó con otro contenido",
    ErrorCode.RESULT_NOT_READY: "El resultado todavía no está listo",
    ErrorCode.RESULT_VERSION_CONFLICT: "La versión del resultado ha cambiado",
    ErrorCode.AUDIO_TOO_LARGE: "El audio supera el tamaño permitido",
    ErrorCode.UNSUPPORTED_AUDIO: "El formato del audio no está admitido",
    ErrorCode.SERVICE_UNAVAILABLE: "Servicio temporalmente no disponible",
}
"""Safe default message of each code: never traces, tokens, audio or personal data."""

RETRYABLE_CODES = frozenset({ErrorCode.SERVICE_UNAVAILABLE})
"""Only transient errors can be retried as they are."""


class ErrorDetail(ContractModel):
    code: ErrorCode
    message: NonEmptyText
    retryable: bool


class ErrorResponse(ContractModel):
    """Body of every error response."""

    error: ErrorDetail
    request_id: Identifier = Field(description="Identifier of the request, for support")


_PARTICIPANT_FIELDS = frozenset({"participants", "participant_count"})


def metadata_error_code(errors: Iterable[Mapping[str, Any]]) -> ErrorCode:
    """Contract error code for validation errors of ClassMetadata.

    `errors` are Pydantic error dicts whose `loc` is relative to the metadata object.
    A consent problem wins over a participants problem, and both over any other field.
    """
    errors = list(errors)
    if any(_first(error["loc"]) == "consent_reference" for error in errors):
        return ErrorCode.INVALID_CONSENT_REFERENCE
    if any(
        error["type"] == "invalid_participants" or _first(error["loc"]) in _PARTICIPANT_FIELDS
        for error in errors
    ):
        return ErrorCode.INVALID_PARTICIPANTS
    return ErrorCode.INVALID_REQUEST


def _first(loc: tuple[Any, ...] | list[Any]) -> Any:
    return loc[0] if loc else None
