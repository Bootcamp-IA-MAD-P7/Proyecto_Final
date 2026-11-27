"""JobStore: classes and their processing jobs, shared by the api and the worker.

Internal interface (design of add-walking-skeleton): section 1 brings the in-memory
implementation for tests, section 2 the PostgreSQL one (ADR-0002).

Lifecycle of a job, with a single worker:

    queued --claim_next--> normalizing --advance--> transcribing --> diarizing --> analyzing
    <stage> --complete--> ready_for_review       <stage> --fail--> failed
    <stage> --retry_later--> retry_wait --claim_next (once next_attempt_at passes)--> normalizing
    <stage> --requeue_in_progress (worker start)--> queued, or failed with no attempts left
    queued | <stage> | retry_wait --expire_jobs--> expired
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable
from uuid import uuid4

from app.contract import ClassMetadata, Job, JobError, JobErrorCode, JobStage, JobState, Result

IN_PROGRESS_STATES = frozenset(JobState(stage.value) for stage in JobStage)
"""States of a job that a worker is processing: one per stage."""

UNFINISHED_STATES = IN_PROGRESS_STATES | {JobState.QUEUED, JobState.RETRY_WAIT}
"""States of a job that can still be expired (audio-retention)."""

STAGE_ORDER = list(JobStage)

FAILED_MESSAGE = "No se ha podido procesar la clase."
"""Message of a contract error that must not reveal anything of the class."""

EXHAUSTED_ERROR = JobError(
    code=JobErrorCode.PROCESSING_FAILED, message=FAILED_MESSAGE, retryable=False
)
"""Error of a job left in progress after its last attempt, such as one that kills the worker."""


def new_id(prefix: str) -> str:
    """Opaque identifier of a class or a job."""
    return f"{prefix}-{uuid4().hex}"


@dataclass(frozen=True)
class StoredClass:
    """A submitted class, with what the api needs to resolve who can see it (spec api-access)."""

    class_id: str
    job_id: str
    metadata: ClassMetadata
    submitted_by: str
    """Subject of the token that submitted the class: a teacher or the CoTeach service."""


@dataclass(frozen=True)
class AudioAsset:
    """The audio of a class in the private storage (ADR-0004). Never sent to a client."""

    audio_id: str
    storage_key: str
    """Opaque name of the file in the AudioStorage."""
    format: str
    size_bytes: int
    duration_seconds: float
    sha256: str
    received_at: datetime
    expires_at: datetime
    """Purge date: received_at plus AUDIO_RETENTION_DAYS (spec audio-retention)."""
    deleted_at: datetime | None = None


@dataclass(frozen=True)
class Idempotency:
    """Idempotency-Key of a submission and the fingerprint of its audio and metadata."""

    key: str
    fingerprint: str


@dataclass(frozen=True)
class Submission:
    """A class found by the Idempotency-Key of whoever submitted it."""

    class_id: str
    job_id: str
    fingerprint: str


class IdempotencyKeyTakenError(Exception):
    """Another submission saved the same submitted_by and Idempotency-Key first."""


class JobNotFoundError(LookupError):
    """No job with that job_id."""


class InvalidJobTransitionError(ValueError):
    """The job is not in a state that allows the operation."""


@runtime_checkable
class JobStore(Protocol):
    def create_class(
        self,
        metadata: ClassMetadata,
        submitted_by: str,
        audio: AudioAsset | None = None,
        idempotency: Idempotency | None = None,
    ) -> StoredClass:
        """Create the class, its audio and its job in `queued`, in a single transaction.

        Raises IdempotencyKeyTakenError, creating nothing, when `submitted_by` already used the
        key of `idempotency`.
        """
        ...

    def find_submission(self, submitted_by: str, idempotency_key: str) -> Submission | None:
        """The class created by `submitted_by` with that Idempotency-Key, if any."""
        ...

    def get_audio(self, class_id: str) -> AudioAsset | None: ...

    def get_class(self, class_id: str) -> StoredClass | None: ...

    def get_job(self, job_id: str) -> Job | None: ...

    def get_result(self, class_id: str) -> Result | None:
        """The result saved by the worker, or None while there is none."""
        ...

    def claim_next(self, now: datetime | None = None) -> Job | None:
        """Take the oldest job ready to run: it moves to the first stage and its attempt grows.

        A job is ready when it is `queued`, or in `retry_wait` and its next attempt is due by
        `now` (the current time when omitted). They are taken in order of arrival to the queue.
        """
        ...

    def advance(self, job_id: str, stage: JobStage) -> Job:
        """Move a job in progress to a later stage; its current stage changes nothing."""
        ...

    def complete(self, job_id: str, result: Result) -> Job:
        """Save the result of a job in progress and move it to `ready_for_review`."""
        ...

    def fail(self, job_id: str, error: JobError) -> Job:
        """Move a job in progress to `failed`, keeping its stage and without a result."""
        ...

    def retry_later(self, job_id: str, error: JobError, next_attempt_at: datetime) -> Job:
        """Move a job in progress to `retry_wait`, keeping its stage, until `next_attempt_at`."""
        ...

    def requeue_in_progress(self, max_attempts: int | None = None) -> int:
        """Return every job left in progress to `queued` and count them. Run at worker start.

        With `max_attempts`, a job that already used them all moves to `failed` with
        EXHAUSTED_ERROR instead, so a job that kills the worker cannot block the queue.
        """
        ...

    def expire_jobs(self, now: datetime) -> int:
        """Mark unfinished jobs whose audio expired by `now` as `expired`; count them.

        Expiry depends on the recorded `expires_at`, not on whether the file still exists.
        Finished jobs keep their result.
        """
        ...

    def audios_to_purge(self, now: datetime) -> list[AudioAsset]:
        """Expired audio not yet marked as deleted, still to be removed from the storage."""
        ...

    def mark_audio_purged(self, audio_id: str, when: datetime) -> None:
        """Record the physical deletion of an audio, so a failed delete can be retried."""
        ...

    def stored_audio_keys(self) -> set[str]:
        """Opaque keys of the audio registered here, to spot orphan files in the storage."""
        ...
