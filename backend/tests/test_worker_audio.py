from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from app.contract import ClassMetadata, JobErrorCode, JobState
from app.inference import FakePipeline, PipelineError, PipelineOutput
from app.jobs import AudioAsset, InMemoryJobStore
from app.worker import Worker
from tests.conftest import load_fixture

NOW = datetime(2026, 11, 26, 10, tzinfo=UTC)


@pytest.fixture
def metadata() -> ClassMetadata:
    return ClassMetadata.model_validate(load_fixture("valid/class-metadata.json"))


class PathRecordingPipeline(FakePipeline):
    def __init__(self) -> None:
        super().__init__()
        self.paths: list[Path | None] = []
        self.contents: list[bytes | None] = []

    def run(self, job_input, on_stage) -> PipelineOutput:
        self.paths.append(job_input.audio_path)
        self.contents.append(
            job_input.audio_path.read_bytes() if job_input.audio_path is not None else None
        )
        return super().run(job_input, on_stage)


class FailingPipeline(FakePipeline):
    def run(self, job_input, on_stage) -> PipelineOutput:
        raise PipelineError(JobErrorCode.PROCESSING_UNAVAILABLE, "model missing", retryable=True)


def audio_asset(key: str = "audio-01") -> AudioAsset:
    return AudioAsset(
        audio_id="audio-01",
        storage_key=key,
        format="opus",
        size_bytes=5,
        duration_seconds=61,
        sha256="a" * 64,
        received_at=NOW,
        expires_at=NOW + timedelta(days=14),
    )


def worker(
    store: InMemoryJobStore,
    pipeline,
    work_dir: Path | None = None,
    audio_storage=None,
) -> Worker:
    return Worker(
        store,
        pipeline,
        timedelta(hours=24),
        clock=lambda: NOW,
        audio_storage=audio_storage,
        work_dir=work_dir,
    )


def test_worker_passes_a_private_work_copy_of_the_saved_audio(metadata, audio_storage, tmp_path):
    key = audio_storage.commit(audio_storage.write_temporary([b"audio"]), "audio-01")
    store = InMemoryJobStore()
    stored = store.create_class(metadata, "demo-teacher", audio=audio_asset(key))
    pipeline = PathRecordingPipeline()

    done = worker(store, pipeline, tmp_path / "work", audio_storage).run_once()

    assert done.state == JobState.READY_FOR_REVIEW
    assert pipeline.paths == [tmp_path / "work" / stored.job_id / key]
    assert pipeline.contents == [b"audio"]
    assert audio_storage.path(key).read_bytes() == b"audio"
    assert not (tmp_path / "work" / stored.job_id).exists()


def test_work_copy_is_removed_when_the_attempt_ends(metadata, audio_storage, tmp_path):
    key = audio_storage.commit(audio_storage.write_temporary([b"audio"]), "audio-01")
    store = InMemoryJobStore()
    stored = store.create_class(metadata, "demo-teacher", audio=audio_asset(key))
    work_dir = tmp_path / "work"

    worker(store, PathRecordingPipeline(), work_dir, audio_storage).run_once()

    assert not (work_dir / stored.job_id).exists()
    assert work_dir.is_dir()


def test_work_copy_is_removed_after_a_pipeline_failure(metadata, audio_storage, tmp_path):
    key = audio_storage.commit(audio_storage.write_temporary([b"audio"]), "audio-01")
    store = InMemoryJobStore()
    stored = store.create_class(metadata, "demo-teacher", audio=audio_asset(key))
    work_dir = tmp_path / "work"

    done = worker(store, FailingPipeline(), work_dir, audio_storage).run_once()

    assert done.state == JobState.RETRY_WAIT  # a failed attempt, retried later from the start
    assert not (work_dir / stored.job_id).exists()


def test_missing_audio_file_fails_the_job_without_a_result(metadata, audio_storage, tmp_path):
    store = InMemoryJobStore()
    store.create_class(metadata, "demo-teacher", audio=audio_asset("missing"))
    pipeline = PathRecordingPipeline()

    done = worker(store, pipeline, tmp_path / "work", audio_storage).run_once()

    assert done.state == JobState.FAILED
    assert done.error is not None
    assert done.error.code == JobErrorCode.PROCESSING_FAILED
    assert pipeline.paths == []


def test_worker_cleans_work_copies_left_by_a_crashed_worker(metadata, tmp_path):
    work_dir = tmp_path / "work"
    stale = work_dir / "job-old"
    stale.mkdir(parents=True)
    (stale / "audio.wav").write_bytes(b"old")
    store = InMemoryJobStore()

    worker(store, FakePipeline(), work_dir).start()

    assert list(work_dir.iterdir()) == []


def test_worker_without_audio_keeps_the_legacy_fake_pipeline(metadata, tmp_path):
    store = InMemoryJobStore()
    store.create_class(metadata, "demo-teacher")
    pipeline = PathRecordingPipeline()

    done = worker(store, pipeline, tmp_path / "work").run_once()

    assert done.state == JobState.READY_FOR_REVIEW
    assert pipeline.paths == [None]
