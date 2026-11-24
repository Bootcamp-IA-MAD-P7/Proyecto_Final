"""Pydantic models of the CoTeach AI API contract.

These models and the routes that declare them are the source of truth of the contract;
`openapi.json` is exported from them (docs/CONTRACTS/coteach-ai-api.md).
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Self

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    NonNegativeInt,
    PositiveInt,
    StringConstraints,
    model_validator,
)
from pydantic_core import PydanticCustomError

CONTRACT_VERSION = "0.1.0"
"""Version of the API contract. Also the `schema_version` of the results it produces."""

Identifier = Annotated[
    str,
    StringConstraints(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$"),
]
"""Opaque identifier: letters, digits and `._:-`, starting with a letter or a digit."""

ConsentReference = Annotated[
    str,
    StringConstraints(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$"),
]
"""Reference to the consent evidence kept by CoTeach. Its shape is checked, not its existence."""

NonEmptyText = Annotated[str, StringConstraints(min_length=1)]


class ContractModel(BaseModel):
    """Base of every contract object: unknown fields are rejected."""

    model_config = ConfigDict(extra="forbid")


# --- Reception --------------------------------------------------------------------------------


class ParticipantRole(StrEnum):
    TEACHER = "teacher"
    STUDENT = "student"


class Participant(ContractModel):
    participant_id: Identifier
    role: ParticipantRole
    display_name: Annotated[str, StringConstraints(min_length=1, max_length=200)] | None = None


class ClassMetadata(ContractModel):
    """Metadata sent with the audio of a class (`metadata` part of POST /v1/classes)."""

    external_class_id: Identifier
    participant_count: PositiveInt
    participants: Annotated[list[Participant], Field(min_length=1)]
    consent_reference: ConsentReference

    @model_validator(mode="after")
    def check_participants(self) -> Self:
        ids = [participant.participant_id for participant in self.participants]
        if len(set(ids)) != len(ids):
            raise PydanticCustomError(
                "invalid_participants", "Participants must have distinct participant_id values"
            )
        if self.participant_count != len(self.participants):
            raise PydanticCustomError(
                "invalid_participants", "participant_count must match the participants list"
            )
        return self


# --- Jobs -------------------------------------------------------------------------------------


class JobState(StrEnum):
    QUEUED = "queued"
    NORMALIZING = "normalizing"
    TRANSCRIBING = "transcribing"
    DIARIZING = "diarizing"
    ANALYZING = "analyzing"
    READY_FOR_REVIEW = "ready_for_review"
    FAILED = "failed"
    RETRY_WAIT = "retry_wait"
    PUBLISHED = "published"
    EXPIRED = "expired"


class JobStage(StrEnum):
    """Processing stages, in order. A job in progress has the state of its current stage."""

    NORMALIZING = "normalizing"
    TRANSCRIBING = "transcribing"
    DIARIZING = "diarizing"
    ANALYZING = "analyzing"


class JobErrorCode(StrEnum):
    PROCESSING_UNAVAILABLE = "processing_unavailable"
    PROCESSING_FAILED = "processing_failed"
    INVALID_AUDIO = "invalid_audio"


class JobError(ContractModel):
    code: JobErrorCode
    message: NonEmptyText
    retryable: bool


class ClassAccepted(ContractModel):
    """Response 202 of POST /v1/classes."""

    class_id: Identifier
    job_id: Identifier
    state: JobState


class Job(ContractModel):
    job_id: Identifier
    class_id: Identifier
    state: JobState
    stage: JobStage | None
    attempt: NonNegativeInt
    error: JobError | None


# --- Result -----------------------------------------------------------------------------------


class Speaker(ContractModel):
    speaker_id: Identifier
    participant_id: Identifier | None


class Segment(ContractModel):
    segment_id: Identifier
    start_ms: NonNegativeInt
    end_ms: NonNegativeInt
    speaker_id: Identifier
    text: str

    @model_validator(mode="after")
    def check_interval(self) -> Self:
        if self.end_ms <= self.start_ms:
            raise PydanticCustomError("invalid_interval", "end_ms must be greater than start_ms")
        return self


class Transcript(ContractModel):
    speakers: list[Speaker]
    segments: list[Segment]

    @model_validator(mode="after")
    def check_references(self) -> Self:
        speaker_ids = [speaker.speaker_id for speaker in self.speakers]
        if len(set(speaker_ids)) != len(speaker_ids):
            raise PydanticCustomError("duplicate_id", "speaker_id values must be distinct")
        segment_ids = [segment.segment_id for segment in self.segments]
        if len(set(segment_ids)) != len(segment_ids):
            raise PydanticCustomError("duplicate_id", "segment_id values must be distinct")
        known = set(speaker_ids)
        if any(segment.speaker_id not in known for segment in self.segments):
            raise PydanticCustomError(
                "unknown_speaker", "Every segment must reference a declared speaker_id"
            )
        return self


class AnalysisCategory(StrEnum):
    VOCABULARY = "vocabulary"
    GRAMMAR = "grammar"
    ERRORS_CORRECTIONS = "errors_corrections"
    REINFORCED_SUCCESSES = "reinforced_successes"
    KEY_CONCEPTS = "key_concepts"
    RESOLVED_QUESTIONS = "resolved_questions"


class AnalysisItem(ContractModel):
    item_id: Identifier
    category: AnalysisCategory
    content: NonEmptyText


class Analysis(ContractModel):
    general_summary: str
    items: list[AnalysisItem]

    @model_validator(mode="after")
    def check_items(self) -> Self:
        item_ids = [item.item_id for item in self.items]
        if len(set(item_ids)) != len(item_ids):
            raise PydanticCustomError("duplicate_id", "item_id values must be distinct")
        return self


class ReviewStatus(StrEnum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"


class Review(ContractModel):
    status: ReviewStatus
    review_due_at: AwareDatetime


class PublicationStatus(StrEnum):
    UNPUBLISHED = "unpublished"
    PUBLISHED = "published"


class PublicationMode(StrEnum):
    TEACHER_APPROVED = "teacher_approved"
    AUTOMATIC = "automatic"


class Publication(ContractModel):
    status: PublicationStatus
    result_version: PositiveInt | None
    published_at: AwareDatetime | None
    mode: PublicationMode | None

    @model_validator(mode="after")
    def check_status(self) -> Self:
        details = (self.result_version, self.published_at, self.mode)
        if self.status is PublicationStatus.PUBLISHED and any(value is None for value in details):
            raise PydanticCustomError(
                "invalid_publication",
                "A published result needs result_version, published_at and mode",
            )
        if self.status is PublicationStatus.UNPUBLISHED and any(
            value is not None for value in details
        ):
            raise PydanticCustomError(
                "invalid_publication",
                "An unpublished result has no result_version, published_at or mode",
            )
        return self


class Result(ContractModel):
    """Structured result of a class: transcript and analysis kept in separate sections."""

    schema_version: Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")]
    class_id: Identifier
    result_version: PositiveInt
    transcript: Transcript
    analysis: Analysis
    review: Review
    publication: Publication


# --- Review and approval ----------------------------------------------------------------------


class SpeakerAssignment(ContractModel):
    """Assigns a session speaker to a participant of the class, or removes the assignment."""

    speaker_id: Identifier
    participant_id: Identifier | None


class ReviewChanges(ContractModel):
    """Corrected sections. Each section sent replaces the whole section; absent ones are kept."""

    transcript: Transcript | None = None
    analysis: Analysis | None = None
    speaker_assignments: list[SpeakerAssignment] | None = None

    @model_validator(mode="after")
    def check_not_empty(self) -> Self:
        if self.transcript is None and self.analysis is None and self.speaker_assignments is None:
            raise PydanticCustomError("empty_changes", "At least one section must be changed")
        return self


class ReviewRequest(ContractModel):
    expected_result_version: PositiveInt
    changes: ReviewChanges


class ApproveRequest(ContractModel):
    expected_result_version: PositiveInt


class ApprovalResponse(ContractModel):
    class_id: Identifier
    publication: Publication
