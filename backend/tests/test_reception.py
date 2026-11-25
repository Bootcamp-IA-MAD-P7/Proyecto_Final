"""Reception of a class with its audio: specs class-processing and audio-retention."""

import json
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from app.jobs import InMemoryJobStore, PostgresJobStore
from app.main import create_app
from app.settings import Settings
from app.storage import AudioInfo, FfprobeAudioProbe, UnreadableAudioError
from tests.conftest import SETTINGS, FixedProbe, load_fixture
from tests.test_routes import SERVICE, STRANGER, STUDENT, TEACHER, assert_error, submit

METADATA = load_fixture("valid/class-metadata.json")


def audio(content: bytes = b"synthetic class audio", name: str = "class.ogg") -> dict:
    return {"audio": (name, content, "audio/ogg")}


def with_key(key: str, headers: dict = TEACHER) -> dict:
    return {**headers, "Idempotency-Key": key}


def committed(storage) -> list[str]:
    return [stored.key for stored in storage.list() if not stored.temporary]


def assert_nothing_saved(store, storage):
    assert store.claim_next() is None
    assert storage.list() == []


def app_client(store, storage, probe, settings: Settings = SETTINGS, **kwargs) -> TestClient:
    return TestClient(create_app(settings, store=store, storage=storage, probe=probe), **kwargs)


def limited(**limits) -> Settings:
    return Settings(auth_secret=SETTINGS.auth_secret, **limits)


# --- Valid submission ------------------------------------------------------------------------


def test_valid_audio_is_kept_privately_with_the_class_and_its_job(client, store, audio_storage):
    content = b"synthetic class audio"

    response = submit(client, METADATA, files=audio(content), headers=TEACHER)

    assert response.status_code == 202
    body = response.json()
    asset = store.get_audio(body["class_id"])
    assert committed(audio_storage) == [asset.storage_key]
    assert audio_storage.path(asset.storage_key).read_bytes() == content
    assert (asset.format, asset.size_bytes, asset.duration_seconds) == ("opus", len(content), 1800)
    assert asset.storage_key not in response.text
    assert "class.ogg" not in asset.storage_key
    assert store.get_job(body["job_id"]).class_id == body["class_id"]


def test_audio_records_its_reception_and_purge_date(client, store):
    body = submit(client, METADATA, files=audio(), headers=TEACHER).json()

    asset = store.get_audio(body["class_id"])

    assert asset.expires_at - asset.received_at == timedelta(days=14)
    assert asset.received_at.tzinfo is not None
    assert asset.deleted_at is None


def test_retention_comes_from_the_settings(store, audio_storage, probe):
    client = app_client(store, audio_storage, probe, limited(audio_retention_days=0.5))

    body = submit(client, METADATA, files=audio(), headers=TEACHER).json()

    asset = store.get_audio(body["class_id"])
    assert asset.expires_at - asset.received_at == timedelta(hours=12)


# --- Rejected audio --------------------------------------------------------------------------


def test_audio_above_the_maximum_size_is_rejected(store, audio_storage, probe):
    client = app_client(store, audio_storage, probe, limited(upload_max_bytes=10))

    response = submit(client, METADATA, files=audio(b"x" * 11), headers=TEACHER)

    assert_error(response, 413, "audio_too_large")
    assert_nothing_saved(store, audio_storage)


def test_audio_of_exactly_the_maximum_size_is_accepted(store, audio_storage, probe):
    client = app_client(store, audio_storage, probe, limited(upload_max_bytes=10))

    assert submit(client, METADATA, files=audio(b"x" * 10), headers=TEACHER).status_code == 202


def test_content_that_is_not_admitted_audio_is_rejected_whatever_its_name(store, audio_storage):
    client = app_client(store, audio_storage, FixedProbe(UnreadableAudioError("not audio")))

    response = submit(client, METADATA, files=audio(b"text", "class.mp3"), headers=TEACHER)

    assert_error(response, 415, "unsupported_audio")
    assert_nothing_saved(store, audio_storage)


@pytest.mark.parametrize("seconds", [59, 7201])
def test_audio_outside_the_duration_limits_is_rejected(store, audio_storage, seconds):
    client = app_client(store, audio_storage, FixedProbe(AudioInfo("opus", seconds)))

    response = submit(client, METADATA, files=audio(), headers=TEACHER)

    assert_error(response, 422, "invalid_audio_duration")
    assert_nothing_saved(store, audio_storage)


# --- Order of the errors (contract) ----------------------------------------------------------


def test_forbidden_comes_before_invalid_metadata(client, store, audio_storage):
    metadata = {**METADATA, "consent_reference": ""}

    assert_error(submit(client, metadata, files=audio(), headers=STUDENT), 403, "forbidden")
    assert_nothing_saved(store, audio_storage)


def test_invalid_metadata_comes_before_the_audio_errors(store, audio_storage):
    probe = FixedProbe(UnreadableAudioError("not audio"))
    client = app_client(store, audio_storage, probe, limited(upload_max_bytes=1))
    metadata = {**METADATA, "consent_reference": ""}

    response = submit(client, metadata, files=audio(b"too large"), headers=TEACHER)

    assert_error(response, 422, "invalid_consent_reference")
    assert_nothing_saved(store, audio_storage)


def test_size_comes_before_format(store, audio_storage):
    probe = FixedProbe(UnreadableAudioError("not audio"))
    client = app_client(store, audio_storage, probe, limited(upload_max_bytes=1))

    assert_error(submit(client, METADATA, files=audio(), headers=TEACHER), 413, "audio_too_large")


@pytest.mark.parametrize(
    ("probe", "status", "code"),
    [
        (FixedProbe(UnreadableAudioError("not audio")), 415, "unsupported_audio"),
        (FixedProbe(AudioInfo("opus", 1)), 422, "invalid_audio_duration"),
    ],
)
def test_audio_errors_come_before_the_idempotency_conflict(
    store, audio_storage, probe, status, code
):
    accepting = app_client(store, audio_storage, FixedProbe())
    submit(accepting, METADATA, files=audio(b"first"), headers=with_key("key-1"))
    client = app_client(store, audio_storage, probe)

    response = submit(client, METADATA, files=audio(b"second"), headers=with_key("key-1"))

    assert_error(response, status, code)
    assert len(committed(audio_storage)) == 1


# --- Idempotency (class-processing, «Recepción idempotente») ---------------------------------


def test_identical_resubmission_returns_the_same_class(client, store, audio_storage):
    first = submit(client, METADATA, files=audio(), headers=with_key("key-1"))
    second = submit(client, METADATA, files=audio(), headers=with_key("key-1"))

    assert first.status_code == second.status_code == 202
    assert second.json() == first.json()
    assert len(committed(audio_storage)) == 1
    assert store.claim_next() is not None
    assert store.claim_next() is None


def test_resubmission_reports_the_current_state_of_the_job(client, store):
    first = submit(client, METADATA, files=audio(), headers=with_key("key-1")).json()
    store.claim_next()

    second = submit(client, METADATA, files=audio(), headers=with_key("key-1")).json()

    assert (second["class_id"], second["job_id"]) == (first["class_id"], first["job_id"])
    assert second["state"] == "normalizing"


@pytest.mark.parametrize(
    ("content", "metadata"),
    [
        (b"other audio", METADATA),
        (b"synthetic class audio", {**METADATA, "external_class_id": "other-class"}),
    ],
    ids=["other-audio", "other-metadata"],
)
def test_same_key_with_other_content_is_a_conflict(client, store, audio_storage, content, metadata):
    submit(client, METADATA, files=audio(), headers=with_key("key-1"))
    store.claim_next()

    response = submit(client, metadata, files=audio(content), headers=with_key("key-1"))

    assert_error(response, 409, "idempotency_conflict")
    assert len(audio_storage.list()) == 1
    assert store.claim_next() is None


def test_metadata_is_compared_once_normalized(client):
    first = submit(client, METADATA, files=audio(), headers=with_key("key-1")).json()
    reordered = json.dumps(dict(reversed(list(METADATA.items()))), indent=2)

    second = submit(client, reordered, files=audio(), headers=with_key("key-1"))

    assert second.status_code == 202
    assert second.json()["class_id"] == first["class_id"]


def test_the_key_of_another_submitter_is_a_new_class(client, store):
    teacher = submit(client, METADATA, files=audio(), headers=with_key("key-1")).json()

    stranger = submit(client, METADATA, files=audio(), headers=with_key("key-1", STRANGER))
    service = submit(client, METADATA, files=audio(), headers=with_key("key-1", SERVICE))

    ids = {teacher["class_id"], stranger.json()["class_id"], service.json()["class_id"]}
    assert len(ids) == 3


def test_without_the_header_every_submission_is_new(client, audio_storage):
    first = submit(client, METADATA, files=audio(), headers=TEACHER).json()
    second = submit(client, METADATA, files=audio(), headers=TEACHER).json()

    assert first["class_id"] != second["class_id"]
    assert len(committed(audio_storage)) == 2


class RacingStore(InMemoryJobStore):
    """Another request with the same key commits between our lookup and our insert."""

    def __init__(self) -> None:
        super().__init__()
        self.hide_next_lookup = False

    def find_submission(self, submitted_by, idempotency_key):
        if self.hide_next_lookup:
            self.hide_next_lookup = False
            return None
        return super().find_submission(submitted_by, idempotency_key)


def test_a_concurrent_identical_submission_returns_the_winner(audio_storage, probe):
    store = RacingStore()
    client = app_client(store, audio_storage, probe)
    winner = submit(client, METADATA, files=audio(), headers=with_key("key-1")).json()
    store.hide_next_lookup = True

    loser = submit(client, METADATA, files=audio(), headers=with_key("key-1"))

    assert loser.status_code == 202
    assert loser.json() == winner
    assert len(audio_storage.list()) == 1


def test_a_concurrent_submission_with_other_content_is_a_conflict(audio_storage, probe):
    store = RacingStore()
    client = app_client(store, audio_storage, probe)
    submit(client, METADATA, files=audio(), headers=with_key("key-1"))
    store.hide_next_lookup = True

    response = submit(client, METADATA, files=audio(b"other"), headers=with_key("key-1"))

    assert_error(response, 409, "idempotency_conflict")
    assert len(audio_storage.list()) == 1


# --- Failures after the audio is stored ------------------------------------------------------


class FailingStore(InMemoryJobStore):
    def create_class(self, *args, **kwargs):
        raise RuntimeError("database lost")


def test_the_audio_is_removed_if_the_transaction_fails(audio_storage, probe):
    store = FailingStore()
    client = app_client(store, audio_storage, probe, raise_server_exceptions=False)

    response = submit(client, METADATA, files=audio(), headers=TEACHER)

    assert_error(response, 500, "internal_error")
    assert audio_storage.list() == []


def test_postgres_keeps_class_audio_and_job_together(pg, audio_storage, probe):
    store = PostgresJobStore(pg)
    client = app_client(store, audio_storage, probe)

    first = submit(client, METADATA, files=audio(), headers=with_key("key-1")).json()
    again = submit(client, METADATA, files=audio(), headers=with_key("key-1")).json()
    other = submit(client, METADATA, files=audio(b"other"), headers=with_key("key-1"))

    assert again == first
    assert_error(other, 409, "idempotency_conflict")
    assert committed(audio_storage) == [store.get_audio(first["class_id"]).storage_key]


# --- With the real ffprobe and synthetic audio -----------------------------------------------


@pytest.fixture
def ffprobe_client(store, audio_storage) -> TestClient:
    settings = limited(upload_min_seconds=1, upload_max_seconds=5)
    return app_client(store, audio_storage, FfprobeAudioProbe(), settings)


@pytest.mark.parametrize(("kind", "family"), [("ogg", "opus"), ("mp3", "mp3"), ("m4a", "aac")])
def test_real_audio_is_accepted(ffprobe_client, store, synthetic_audio, kind, family):
    path = synthetic_audio(kind, 2)

    response = submit(
        ffprobe_client, METADATA, files={"audio": ("a.bin", path.read_bytes())}, headers=TEACHER
    )

    assert response.status_code == 202
    assert store.get_audio(response.json()["class_id"]).format == family


def test_real_audio_in_another_format_is_unsupported(
    ffprobe_client, store, audio_storage, synthetic_audio
):
    content = synthetic_audio("wav", 2).read_bytes()

    response = submit(ffprobe_client, METADATA, files=audio(content, "class.mp3"), headers=TEACHER)

    assert_error(response, 415, "unsupported_audio")
    assert_nothing_saved(store, audio_storage)


def test_real_audio_too_long_is_rejected(ffprobe_client, store, audio_storage, synthetic_audio):
    content = synthetic_audio("ogg", 6).read_bytes()

    response = submit(ffprobe_client, METADATA, files=audio(content), headers=TEACHER)

    assert_error(response, 422, "invalid_audio_duration")
    assert_nothing_saved(store, audio_storage)
