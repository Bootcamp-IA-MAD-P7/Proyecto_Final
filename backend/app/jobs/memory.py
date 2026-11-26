"""In-memory JobStore, for tests and for working without a database."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from datetime import datetime
from threading import Lock

from app.contract import ClassMetadata, Job, JobError, JobStage, JobState, Result
from app.jobs.store import (
    IN_PROGRESS_STATES,
    STAGE_ORDER,
    UNFINISHED_STATES,
    AudioAsset,
    Idempotency,
    IdempotencyKeyTakenError,
    InvalidJobTransitionError,
    JobNotFoundError,
    StoredClass,
    Submission,
    new_id,
)


class InMemoryJobStore:
    """JobStore kept in a process. Safe to share between threads; nothing survives a restart."""

    def __init__(self, new_id: Callable[[str], str] = new_id) -> None:
        self._new_id = new_id
        self._lock = Lock()
        self._classes: dict[str, StoredClass] = {}
        self._jobs: dict[str, Job] = {}
        self._queue: list[str] = []
        self._results: dict[str, Result] = {}
        self._audio: dict[str, AudioAsset] = {}
        self._submissions: dict[tuple[str, str], Submission] = {}

    def create_class(
        self,
        metadata: ClassMetadata,
        submitted_by: str,
        audio: AudioAsset | None = None,
        idempotency: Idempotency | None = None,
    ) -> StoredClass:
        with self._lock:
            if idempotency and (submitted_by, idempotency.key) in self._submissions:
                raise IdempotencyKeyTakenError(idempotency.key)
            stored = StoredClass(
                class_id=self._new_id("class"),
                job_id=self._new_id("job"),
                metadata=metadata,
                submitted_by=submitted_by,
            )
            self._classes[stored.class_id] = stored
            self._jobs[stored.job_id] = Job(
                job_id=stored.job_id,
                class_id=stored.class_id,
                state=JobState.QUEUED,
                stage=None,
                attempt=0,
                error=None,
            )
            self._queue.append(stored.job_id)
            if audio is not None:
                self._audio[stored.class_id] = audio
            if idempotency is not None:
                self._submissions[(submitted_by, idempotency.key)] = Submission(
                    stored.class_id, stored.job_id, idempotency.fingerprint
                )
            return stored

    def find_submission(self, submitted_by: str, idempotency_key: str) -> Submission | None:
        with self._lock:
            return self._submissions.get((submitted_by, idempotency_key))

    def get_audio(self, class_id: str) -> AudioAsset | None:
        with self._lock:
            return self._audio.get(class_id)

    def get_class(self, class_id: str) -> StoredClass | None:
        with self._lock:
            return self._classes.get(class_id)

    def get_job(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def get_result(self, class_id: str) -> Result | None:
        with self._lock:
            return self._results.get(class_id)

    def claim_next(self) -> Job | None:
        with self._lock:
            while self._queue:
                job = self._jobs[self._queue.pop(0)]
                if job.state is not JobState.QUEUED:
                    continue
                first = STAGE_ORDER[0]
                return self._save(
                    job,
                    state=JobState(first.value),
                    stage=first,
                    attempt=job.attempt + 1,
                    error=None,
                )
            return None

    def advance(self, job_id: str, stage: JobStage) -> Job:
        with self._lock:
            job = self._in_progress(job_id)
            if stage == job.stage:
                return job
            if STAGE_ORDER.index(stage) < STAGE_ORDER.index(job.stage):
                raise InvalidJobTransitionError(f"{job_id} is already past {stage}")
            return self._save(job, state=JobState(stage.value), stage=stage)

    def complete(self, job_id: str, result: Result) -> Job:
        with self._lock:
            job = self._in_progress(job_id)
            if result.class_id != job.class_id:
                raise InvalidJobTransitionError(
                    f"The result belongs to another class than {job_id}"
                )
            self._results[job.class_id] = result
            return self._save(job, state=JobState.READY_FOR_REVIEW, stage=None)

    def fail(self, job_id: str, error: JobError) -> Job:
        with self._lock:
            job = self._in_progress(job_id)
            return self._save(job, state=JobState.FAILED, error=error)

    def requeue_in_progress(self) -> int:
        with self._lock:
            jobs = [job for job in self._jobs.values() if job.state in IN_PROGRESS_STATES]
            for job in jobs:
                self._save(job, state=JobState.QUEUED, stage=None)
                self._queue.append(job.job_id)
            return len(jobs)

    def expire_jobs(self, now: datetime) -> int:
        with self._lock:
            expired = 0
            for job in self._jobs.values():
                audio = self._audio.get(job.class_id)
                if job.state not in UNFINISHED_STATES or audio is None or audio.expires_at > now:
                    continue
                self._save(job, state=JobState.EXPIRED, stage=None)
                if job.job_id in self._queue:
                    self._queue.remove(job.job_id)
                expired += 1
            return expired

    def audios_to_purge(self, now: datetime) -> list[AudioAsset]:
        with self._lock:
            pending = (
                audio
                for audio in self._audio.values()
                if audio.expires_at <= now and audio.deleted_at is None
            )
            return sorted(pending, key=lambda audio: audio.audio_id)

    def mark_audio_purged(self, audio_id: str, when: datetime) -> None:
        with self._lock:
            for class_id, audio in self._audio.items():
                if audio.audio_id == audio_id:
                    self._audio[class_id] = replace(audio, deleted_at=when)
                    return

    def stored_audio_keys(self) -> set[str]:
        with self._lock:
            return {audio.storage_key for audio in self._audio.values()}

    def _in_progress(self, job_id: str) -> Job:
        job = self._jobs.get(job_id)
        if job is None:
            raise JobNotFoundError(job_id)
        if job.state not in IN_PROGRESS_STATES:
            raise InvalidJobTransitionError(f"{job_id} is not in progress: {job.state}")
        return job

    def _save(self, job: Job, **changes: object) -> Job:
        updated = job.model_copy(update=changes)
        self._jobs[job.job_id] = updated
        return updated
