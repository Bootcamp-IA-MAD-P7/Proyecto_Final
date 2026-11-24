"""JobStore on PostgreSQL (ADR-0002): short transactions and claims with FOR UPDATE SKIP LOCKED."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from sqlalchemy import Connection, Engine, Row, func, insert, select, update

from app.contract import (
    ClassMetadata,
    Job,
    JobError,
    JobStage,
    JobState,
    Participant,
    Result,
)
from app.db.tables import classes, jobs, participants, results
from app.jobs.store import (
    IN_PROGRESS_STATES,
    STAGE_ORDER,
    InvalidJobTransitionError,
    JobNotFoundError,
    StoredClass,
    new_id,
)

_IN_PROGRESS = [state.value for state in IN_PROGRESS_STATES]


class PostgresJobStore:
    """JobStore shared by the api and the worker through PostgreSQL."""

    def __init__(self, engine: Engine, new_id: Callable[[str], str] = new_id) -> None:
        self._engine = engine
        self._new_id = new_id

    def create_class(self, metadata: ClassMetadata, submitted_by: str) -> StoredClass:
        stored = StoredClass(
            class_id=self._new_id("class"),
            job_id=self._new_id("job"),
            metadata=metadata,
            submitted_by=submitted_by,
        )
        with self._engine.begin() as connection:
            connection.execute(
                insert(classes).values(
                    class_id=stored.class_id,
                    external_class_id=metadata.external_class_id,
                    participant_count=metadata.participant_count,
                    consent_reference=metadata.consent_reference,
                    submitted_by=submitted_by,
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
        return stored

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

    def claim_next(self) -> Job | None:
        first = STAGE_ORDER[0]
        with self._engine.begin() as connection:
            job_id = connection.execute(
                select(jobs.c.job_id)
                .where(jobs.c.state == JobState.QUEUED.value)
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
            return self._save(
                connection,
                job_id,
                state=JobState.FAILED.value,
                error_code=error.code.value,
                error_message=error.message,
                error_retryable=error.retryable,
            )

    def requeue_in_progress(self) -> int:
        with self._engine.begin() as connection:
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


def _no_error() -> dict[str, None]:
    return {"error_code": None, "error_message": None, "error_retryable": None}


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
