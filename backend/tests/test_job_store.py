"""Behaviour shared by every JobStore: in memory and on PostgreSQL (ADR-0002)."""

from datetime import UTC, datetime, timedelta

import pytest

from app.contract import ClassMetadata, JobError, JobErrorCode, JobStage, JobState, Result
from app.jobs import (
    AudioAsset,
    Idempotency,
    IdempotencyKeyTakenError,
    InMemoryJobStore,
    InvalidJobTransitionError,
    JobNotFoundError,
    JobStore,
    PostgresJobStore,
    Submission,
)
from tests.conftest import load_fixture


@pytest.fixture(params=["memory", "postgres"])
def store(request) -> JobStore:
    counter = iter(range(1, 1000))

    def new_id(prefix: str) -> str:
        return f"{prefix}-{next(counter):02d}"

    if request.param == "memory":
        return InMemoryJobStore(new_id=new_id)
    return PostgresJobStore(request.getfixturevalue("pg"), new_id=new_id)


@pytest.fixture
def metadata() -> ClassMetadata:
    return ClassMetadata.model_validate(load_fixture("valid/class-metadata.json"))


def result_for(class_id: str) -> Result:
    payload = load_fixture("valid/result-draft.json")
    return Result.model_validate({**payload, "class_id": class_id})


def error() -> JobError:
    return JobError(code=JobErrorCode.PROCESSING_FAILED, message="Fallo simulado", retryable=False)


def test_implements_the_interface(store):
    assert isinstance(store, JobStore)


def test_create_class_queues_its_job(store, metadata):
    stored = store.create_class(metadata, submitted_by="demo-teacher")

    assert store.get_class(stored.class_id) == stored
    assert stored.metadata == metadata
    assert stored.submitted_by == "demo-teacher"
    job = store.get_job(stored.job_id)
    assert job.class_id == stored.class_id
    assert (job.state, job.stage, job.attempt, job.error) == (JobState.QUEUED, None, 0, None)
    assert store.get_result(stored.class_id) is None


def test_unknown_ids_return_none(store):
    assert store.get_class("class-99") is None
    assert store.get_job("job-99") is None
    assert store.get_result("class-99") is None


def test_claim_next_takes_the_oldest_job_into_the_first_stage(store, metadata):
    first = store.create_class(metadata, "demo-teacher")
    second = store.create_class(metadata, "demo-teacher")

    claimed = store.claim_next()

    assert claimed.job_id == first.job_id
    assert (claimed.state, claimed.stage, claimed.attempt) == (
        JobState.NORMALIZING,
        JobStage.NORMALIZING,
        1,
    )
    assert store.claim_next().job_id == second.job_id
    assert store.claim_next() is None


def test_advance_moves_through_the_stages(store, metadata):
    job_id = store.create_class(metadata, "demo-teacher").job_id
    store.claim_next()

    assert store.advance(job_id, JobStage.NORMALIZING).stage is JobStage.NORMALIZING
    for stage in (JobStage.TRANSCRIBING, JobStage.DIARIZING, JobStage.ANALYZING):
        job = store.advance(job_id, stage)
        assert (job.state, job.stage) == (JobState(stage.value), stage)
    assert store.get_job(job_id).state is JobState.ANALYZING


def test_advance_cannot_go_back(store, metadata):
    job_id = store.create_class(metadata, "demo-teacher").job_id
    store.claim_next()
    store.advance(job_id, JobStage.DIARIZING)

    with pytest.raises(InvalidJobTransitionError):
        store.advance(job_id, JobStage.TRANSCRIBING)


def test_complete_saves_the_result_and_waits_for_review(store, metadata):
    stored = store.create_class(metadata, "demo-teacher")
    store.claim_next()
    store.advance(stored.job_id, JobStage.ANALYZING)
    result = result_for(stored.class_id)

    job = store.complete(stored.job_id, result)

    assert (job.state, job.stage, job.error) == (JobState.READY_FOR_REVIEW, None, None)
    assert store.get_result(stored.class_id) == result


def test_complete_rejects_a_result_of_another_class(store, metadata):
    stored = store.create_class(metadata, "demo-teacher")
    store.claim_next()

    with pytest.raises(InvalidJobTransitionError):
        store.complete(stored.job_id, result_for("class-other"))
    assert store.get_result(stored.class_id) is None


def test_fail_keeps_the_stage_and_leaves_no_result(store, metadata):
    stored = store.create_class(metadata, "demo-teacher")
    store.claim_next()
    store.advance(stored.job_id, JobStage.TRANSCRIBING)

    job = store.fail(stored.job_id, error())

    assert (job.state, job.stage, job.error) == (JobState.FAILED, JobStage.TRANSCRIBING, error())
    assert store.get_result(stored.class_id) is None


@pytest.mark.parametrize("operation", ["advance", "complete", "fail"])
def test_operations_need_a_job_in_progress(store, metadata, operation):
    stored = store.create_class(metadata, "demo-teacher")
    arguments = {
        "advance": (JobStage.TRANSCRIBING,),
        "complete": (result_for(stored.class_id),),
        "fail": (error(),),
    }[operation]

    with pytest.raises(InvalidJobTransitionError):
        getattr(store, operation)(stored.job_id, *arguments)
    with pytest.raises(JobNotFoundError):
        getattr(store, operation)("job-99", *arguments)


def test_finished_jobs_cannot_change(store, metadata):
    stored = store.create_class(metadata, "demo-teacher")
    store.claim_next()
    store.complete(stored.job_id, result_for(stored.class_id))

    with pytest.raises(InvalidJobTransitionError):
        store.fail(stored.job_id, error())


def test_requeue_in_progress_returns_unfinished_jobs_to_the_queue(store, metadata):
    in_progress = store.create_class(metadata, "demo-teacher")
    finished = store.create_class(metadata, "demo-teacher")
    queued = store.create_class(metadata, "demo-teacher")
    store.claim_next()
    store.claim_next()
    store.advance(in_progress.job_id, JobStage.DIARIZING)
    store.complete(finished.job_id, result_for(finished.class_id))

    assert store.requeue_in_progress() == 1

    job = store.get_job(in_progress.job_id)
    assert (job.state, job.stage, job.attempt) == (JobState.QUEUED, None, 1)
    assert store.get_job(finished.job_id).state is JobState.READY_FOR_REVIEW
    assert store.claim_next().job_id == queued.job_id
    reclaimed = store.claim_next()
    assert (reclaimed.job_id, reclaimed.attempt) == (in_progress.job_id, 2)
    assert store.requeue_in_progress() == 2


# --- Audio and idempotency (add-class-reception) ---------------------------------------------


def audio_asset(audio_id: str = "audio-01") -> AudioAsset:
    received_at = datetime(2026, 11, 25, 12, 0, tzinfo=UTC)
    return AudioAsset(
        audio_id=audio_id,
        storage_key=audio_id,
        format="opus",
        size_bytes=123456,
        duration_seconds=1800.5,
        sha256="a" * 64,
        received_at=received_at,
        expires_at=received_at + timedelta(days=14),
    )


def test_create_class_saves_its_audio(store, metadata):
    stored = store.create_class(metadata, "demo-teacher", audio=audio_asset())

    assert store.get_audio(stored.class_id) == audio_asset()


def test_class_without_audio_has_none(store, metadata):
    stored = store.create_class(metadata, "demo-teacher")

    assert store.get_audio(stored.class_id) is None


def test_submission_is_found_by_its_submitter_and_key(store, metadata):
    stored = store.create_class(
        metadata, "demo-teacher", audio=audio_asset(), idempotency=Idempotency("key-1", "f" * 64)
    )

    found = store.find_submission("demo-teacher", "key-1")

    assert found == Submission(stored.class_id, stored.job_id, "f" * 64)
    assert store.find_submission("other-teacher", "key-1") is None
    assert store.find_submission("demo-teacher", "key-2") is None


def test_a_taken_key_creates_nothing(store, metadata):
    first = store.create_class(metadata, "demo-teacher", idempotency=Idempotency("key-1", "1"))

    with pytest.raises(IdempotencyKeyTakenError):
        store.create_class(
            metadata,
            "demo-teacher",
            audio=audio_asset("audio-02"),
            idempotency=Idempotency("key-1", "2"),
        )

    assert store.claim_next().job_id == first.job_id
    assert store.claim_next() is None


def test_the_same_key_of_another_submitter_is_a_new_class(store, metadata):
    first = store.create_class(metadata, "demo-teacher", idempotency=Idempotency("key-1", "1"))
    second = store.create_class(metadata, "coteach-service", idempotency=Idempotency("key-1", "1"))

    assert first.class_id != second.class_id


def test_classes_without_a_key_never_collide(store, metadata):
    first = store.create_class(metadata, "demo-teacher")
    second = store.create_class(metadata, "demo-teacher")

    assert first.class_id != second.class_id
