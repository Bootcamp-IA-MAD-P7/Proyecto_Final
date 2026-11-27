"""JobStore on PostgreSQL (ADR-0002): short transactions and claims with FOR UPDATE SKIP LOCKED."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any

from sqlalchemy import Connection, Engine, Row, and_, func, insert, or_, select, update
from sqlalchemy.exc import IntegrityError

from app.contract import (
    ClassMetadata,
    Job,
    JobError,
    JobStage,
    JobState,
    Participant,
    Result,
)
from app.db.tables import audio_assets, classes, jobs, participants, results
from app.jobs.store import (
    EXHAUSTED_ERROR,
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

_IN_PROGRESS = [state.value for state in IN_PROGRESS_STATES]
_UNFINISHED = [state.value for state in UNFINISHED_STATES]


class PostgresJobStore:
    """JobStore shared by the api and the worker through PostgreSQL."""

    def __init__(self, engine: Engine, new_id: Callable[[str], str] = new_id) -> None:
        self._engine = engine
        self._new_id = new_id

    def create_class(
        self,
        metadata: ClassMetadata,
        submitted_by: str,
        audio: AudioAsset | None = None,
        idempotency: Idempotency | None = None,
    ) -> StoredClass:
        stored = StoredClass(
            class_id=self._new_id("class"),
            job_id=self._new_id("job"),
            metadata=metadata,
            submitted_by=submitted_by,
        )
        try:
            with self._engine.begin() as connection:
                self._insert_class(connection, stored, audio, idempotency)
        except IntegrityError as error:
            constraint = getattr(getattr(error.orig, "diag", None), "constraint_name", None)
            if idempotency is not None and constraint == "classes_idempotency_key":
                raise IdempotencyKeyTakenError(idempotency.key) from error
            raise
        return stored

    def _insert_class(
        self,
        connection: Connection,
        stored: StoredClass,
        audio: AudioAsset | None,
        idempotency: Idempotency | None,
    ) -> None:
        metadata = stored.metadata
        connection.execute(
            insert(classes).values(
                class_id=stored.class_id,
                external_class_id=metadata.external_class_id,
                participant_count=metadata.participant_count,
                consent_reference=metadata.consent_reference,
                submitted_by=stored.submitted_by,
                idempotency_key=idempotency.key if idempotency else None,
                request_fingerprint=idempotency.fingerprint if idempotency else None,
            )
        )
        if audio is not None:
            connection.execute(
                insert(audio_assets).values(
                    audio_id=audio.audio_id,
                    class_id=stored.class_id,
                    storage_key=audio.storage_key,
                    format=audio.format,
                    size_bytes=audio.size_bytes,
                    duration_seconds=audio.duration_seconds,
                    sha256=audio.sha256,
                    received_at=audio.received_at,
                    expires_at=audio.expires_at,
                    deleted_at=audio.deleted_at,
                )
            )
        connection.execute(
            insert(participants),
            [
                {
                    "class_id": stored.class_id,
                    "participant_id": participant.participant_id,
                    "position": position,
                    "role": participant.role.value,
                    "display_name": participant.display_name,
                }
                for position, participant in enumerate(metadata.participants)
            ],
        )
        connection.execute(
            insert(jobs).values(
                job_id=stored.job_id,
                class_id=stored.class_id,
                state=JobState.QUEUED.value,
                attempt=0,
            )
        )

    def find_submission(self, submitted_by: str, idempotency_key: str) -> Submission | None:
        with self._engine.connect() as connection:
            row = connection.execute(
                select(classes.c.class_id, jobs.c.job_id, classes.c.request_fingerprint)
                .join(jobs, jobs.c.class_id == classes.c.class_id)
                .where(
                    classes.c.submitted_by == submitted_by,
                    classes.c.idempotency_key == idempotency_key,
                )
            ).first()
        return Submission(row.class_id, row.job_id, row.request_fingerprint) if row else None

    def get_audio(self, class_id: str) -> AudioAsset | None:
        with self._engine.connect() as connection:
            row = connection.execute(
                select(audio_assets).where(audio_assets.c.class_id == class_id)
            ).first()
        return _audio(row) if row is not None else None

    def get_class(self, class_id: str) -> StoredClass | None:
        with self._engine.connect() as connection:
            row = connection.execute(
                select(classes, jobs.c.job_id)
                .join(jobs, jobs.c.class_id == classes.c.class_id)
                .where(classes.c.class_id == class_id)
            ).first()
            if row is None:
                return None
            people = connection.execute(
                select(participants)
                .where(participants.c.class_id == class_id)
                .order_by(participants.c.position)
            ).all()
        metadata = ClassMetadata(
            external_class_id=row.external_class_id,
            participant_count=row.participant_count,
            participants=[
                Participant(
                    participant_id=person.participant_id,
                    role=person.role,
                    display_name=person.display_name,
                )
                for person in people
            ],
            consent_reference=row.consent_reference,
        )
        return StoredClass(
            class_id=row.class_id,
            job_id=row.job_id,
            metadata=metadata,
            submitted_by=row.submitted_by,
        )

    def get_job(self, job_id: str) -> Job | None:
        with self._engine.connect() as connection:
            row = connection.execute(select(jobs).where(jobs.c.job_id == job_id)).first()
        return _job(row) if row else None

    def get_result(self, class_id: str) -> Result | None:
        with self._engine.connect() as connection:
            body = connection.execute(
                select(results.c.body).where(results.c.class_id == class_id)
            ).scalar_one_or_none()
        return Result.model_validate(body) if body is not None else None

    def claim_next(self, now: datetime | None = None) -> Job | None:
        first = STAGE_ORDER[0]
        due = func.now() if now is None else now
        with self._engine.begin() as connection:
            job_id = connection.execute(
                select(jobs.c.job_id)
                .where(
                    or_(
                        jobs.c.state == JobState.QUEUED.value,
                        and_(
                            jobs.c.state == JobState.RETRY_WAIT.value,
                            jobs.c.next_attempt_at <= due,
                        ),
                    )
                )
                .order_by(jobs.c.queued_at, jobs.c.job_id)
                .limit(1)
                .with_for_update(skip_locked=True)
            ).scalar_one_or_none()
            if job_id is None:
                return None
            return self._save(
                connection,
                job_id,
                state=first.value,
                stage=first.value,
                attempt=jobs.c.attempt + 1,
                next_attempt_at=None,
                **_no_error(),
            )

    def advance(self, job_id: str, stage: JobStage) -> Job:
        with self._engine.begin() as connection:
            job = self._in_progress(connection, job_id)
            if stage == job.stage:
                return job
            if STAGE_ORDER.index(stage) < STAGE_ORDER.index(job.stage):
                raise InvalidJobTransitionError(f"{job_id} is already past {stage}")
            return self._save(connection, job_id, state=stage.value, stage=stage.value)

    def complete(self, job_id: str, result: Result) -> Job:
        with self._engine.begin() as connection:
            job = self._in_progress(connection, job_id)
            if result.class_id != job.class_id:
                raise InvalidJobTransitionError(
                    f"The result belongs to another class than {job_id}"
                )
            connection.execute(
                insert(results).values(
                    class_id=job.class_id,
                    result_version=result.result_version,
                    body=result.model_dump(mode="json"),
                )
            )
            return self._save(connection, job_id, state=JobState.READY_FOR_REVIEW.value, stage=None)

    def fail(self, job_id: str, error: JobError) -> Job:
        with self._engine.begin() as connection:
            self._in_progress(connection, job_id)
            return self._save(connection, job_id, state=JobState.FAILED.value, **_error(error))

    def retry_later(self, job_id: str, error: JobError, next_attempt_at: datetime) -> Job:
        # queued_at does not change: once due, the job keeps its place in the queue.
        with self._engine.begin() as connection:
            self._in_progress(connection, job_id)
            return self._save(
                connection,
                job_id,
                state=JobState.RETRY_WAIT.value,
                next_attempt_at=next_attempt_at,
                **_error(error),
            )

    def requeue_in_progress(self, max_attempts: int | None = None) -> int:
        with self._engine.begin() as connection:
            if max_attempts is not None:
                connection.execute(
                    update(jobs)
                    .where(jobs.c.state.in_(_IN_PROGRESS), jobs.c.attempt >= max_attempts)
                    .values(
                        state=JobState.FAILED.value,
                        updated_at=func.now(),
                        **_error(EXHAUSTED_ERROR),
                    )
                )
            moved = connection.execute(
                update(jobs)
                .where(jobs.c.state.in_(_IN_PROGRESS))
                .values(
                    state=JobState.QUEUED.value,
                    stage=None,
                    queued_at=func.now(),
                    updated_at=func.now(),
                )
            )
            return moved.rowcount

    def expire_jobs(self, now: datetime) -> int:
        with self._engine.begin() as connection:
            expired = connection.execute(
                update(jobs)
                .where(jobs.c.state.in_(_UNFINISHED))
                .where(
                    jobs.c.class_id.in_(
                        select(audio_assets.c.class_id).where(audio_assets.c.expires_at <= now)
                    )
                )
                .values(
                    state=JobState.EXPIRED.value,
                    stage=None,
                    next_attempt_at=None,
                    updated_at=now,
                )
            )
            return expired.rowcount

    def audios_to_purge(self, now: datetime) -> list[AudioAsset]:
        with self._engine.connect() as connection:
            rows = connection.execute(
                select(audio_assets)
                .where(audio_assets.c.expires_at <= now, audio_assets.c.deleted_at.is_(None))
                .order_by(audio_assets.c.audio_id)
            ).all()
        return [_audio(row) for row in rows]

    def mark_audio_purged(self, audio_id: str, when: datetime) -> None:
        with self._engine.begin() as connection:
            connection.execute(
                update(audio_assets)
                .where(audio_assets.c.audio_id == audio_id, audio_assets.c.deleted_at.is_(None))
                .values(deleted_at=when)
            )

    def stored_audio_keys(self) -> set[str]:
        with self._engine.connect() as connection:
            return set(connection.execute(select(audio_assets.c.storage_key)).scalars())

    def _in_progress(self, connection: Connection, job_id: str) -> Job:
        row = connection.execute(
            select(jobs).where(jobs.c.job_id == job_id).with_for_update()
        ).first()
        if row is None:
            raise JobNotFoundError(job_id)
        job = _job(row)
        if job.state not in IN_PROGRESS_STATES:
            raise InvalidJobTransitionError(f"{job_id} is not in progress: {job.state}")
        return job

    def _save(self, connection: Connection, job_id: str, **changes: Any) -> Job:
        row = connection.execute(
            update(jobs)
            .where(jobs.c.job_id == job_id)
            .values(**changes, updated_at=func.now())
            .returning(*jobs.c)
        ).one()
        return _job(row)


def _error(error: JobError) -> dict[str, Any]:
    return {
        "error_code": error.code.value,
        "error_message": error.message,
        "error_retryable": error.retryable,
    }


def _no_error() -> dict[str, None]:
    return {"error_code": None, "error_message": None, "error_retryable": None}


def _audio(row: Row) -> AudioAsset:
    return AudioAsset(
        audio_id=row.audio_id,
        storage_key=row.storage_key,
        format=row.format,
        size_bytes=row.size_bytes,
        duration_seconds=row.duration_seconds,
        sha256=row.sha256,
        received_at=row.received_at,
        expires_at=row.expires_at,
        deleted_at=row.deleted_at,
    )


def _job(row: Row) -> Job:
    error = (
        JobError(code=row.error_code, message=row.error_message, retryable=row.error_retryable)
        if row.error_code
        else None
    )
    return Job(
        job_id=row.job_id,
        class_id=row.class_id,
        state=row.state,
        stage=row.stage,
        attempt=row.attempt,
        error=error,
    )
