"""JobStore: classes and their processing jobs, shared by the api and the worker.

Internal interface (design of add-walking-skeleton): section 1 brings the in-memory
implementation for tests, section 2 the PostgreSQL one (ADR-0002).

Lifecycle of a job, with a single worker:

    queued --claim_next--> normalizing --advance--> transcribing --> diarizing --> analyzing
    <stage> --complete--> ready_for_review       <stage> --fail--> failed
    <stage> --requeue_in_progress (worker start)--> queued
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from app.contract import ClassMetadata, Job, JobError, JobStage, JobState, Result

IN_PROGRESS_STATES = frozenset(JobState(stage.value) for stage in JobStage)
"""States of a job that a worker is processing: one per stage."""


@dataclass(frozen=True)
class StoredClass:
    """A submitted class, with what the api needs to resolve who can see it (spec api-access)."""

    class_id: str
    job_id: str
    metadata: ClassMetadata
    submitted_by: str
    """Subject of the token that submitted the class: a teacher or the CoTeach service."""


class JobNotFoundError(LookupError):
    """No job with that job_id."""


class InvalidJobTransitionError(ValueError):
    """The job is not in a state that allows the operation."""


@runtime_checkable
class JobStore(Protocol):
    def create_class(self, metadata: ClassMetadata, submitted_by: str) -> StoredClass:
        """Create the class and its job in `queued`, in a single step."""
        ...

    def get_class(self, class_id: str) -> StoredClass | None: ...

    def get_job(self, job_id: str) -> Job | None: ...

    def get_result(self, class_id: str) -> Result | None:
        """The result saved by the worker, or None while there is none."""
        ...

    def claim_next(self) -> Job | None:
        """Take the oldest queued job: it moves to the first stage and its attempt grows by one."""
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

    def requeue_in_progress(self) -> int:
        """Return every job left in progress to `queued` and count them. Run at worker start."""
        ...
