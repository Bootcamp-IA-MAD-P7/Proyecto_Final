import pytest

from app.settings import Settings


def test_background_settings_come_from_the_environment():
    settings = Settings.from_env(
        {
            "REVIEW_PERIOD_HOURS": "48",
            "FAKE_STAGE_SECONDS": "0.5",
            "WORKER_POLL_SECONDS": "3",
            "MAINTENANCE_INTERVAL_SECONDS": "10",
        }
    )

    assert settings.review_period_hours == 48
    assert settings.fake_stage_seconds == 0.5
    assert settings.worker_poll_seconds == 3
    assert settings.maintenance_interval_seconds == 10


def test_background_settings_have_defaults():
    settings = Settings.from_env({})

    assert settings.review_period_hours == 24
    assert settings.maintenance_interval_seconds == 60


def test_a_negative_interval_is_refused():
    with pytest.raises(ValueError, match="MAINTENANCE_INTERVAL_SECONDS"):
        Settings.from_env({"MAINTENANCE_INTERVAL_SECONDS": "-1"})


@pytest.mark.parametrize("value", ["0", "nan", "inf", "soon"])
def test_an_interval_must_be_a_finite_number_above_zero(value):
    with pytest.raises(ValueError, match="WORKER_POLL_SECONDS"):
        Settings.from_env({"WORKER_POLL_SECONDS": value})


def test_the_simulated_pipeline_can_skip_the_wait():
    assert Settings.from_env({"FAKE_STAGE_SECONDS": "0"}).fake_stage_seconds == 0


def test_upload_limits_and_retention_have_the_contract_defaults():
    settings = Settings.from_env({})

    assert settings.upload_max_bytes == 150 * 1024 * 1024
    assert (settings.upload_min_seconds, settings.upload_max_seconds) == (60, 7200)
    assert settings.audio_retention_days == 14
    assert settings.audio_storage_dir == "data/audio"
    assert settings.work_dir == "data/work"


def test_upload_limits_and_retention_come_from_the_environment():
    settings = Settings.from_env(
        {
            "UPLOAD_MAX_BYTES": "1048576",
            "UPLOAD_MIN_SECONDS": "1",
            "UPLOAD_MAX_SECONDS": "5",
            "AUDIO_RETENTION_DAYS": "0.01",
            "AUDIO_STORAGE_DIR": "/var/lib/coteach/audio",
            "WORK_DIR": "/var/lib/coteach/work",
        }
    )

    assert settings.upload_max_bytes == 1048576
    assert (settings.upload_min_seconds, settings.upload_max_seconds) == (1, 5)
    assert settings.audio_retention_days == 0.01
    assert settings.audio_storage_dir == "/var/lib/coteach/audio"
    assert settings.work_dir == "/var/lib/coteach/work"


def test_the_minimum_duration_cannot_exceed_the_maximum():
    with pytest.raises(ValueError, match="UPLOAD_MIN_SECONDS"):
        Settings.from_env({"UPLOAD_MIN_SECONDS": "120", "UPLOAD_MAX_SECONDS": "60"})


@pytest.mark.parametrize("name", ["UPLOAD_MAX_BYTES", "AUDIO_RETENTION_DAYS"])
def test_size_and_retention_must_be_above_zero(name):
    with pytest.raises(ValueError, match=name):
        Settings.from_env({name: "0"})


@pytest.mark.parametrize("value", ["0.5", "1e6", "-1"])
def test_the_maximum_size_is_a_whole_number_of_bytes(value):
    with pytest.raises(ValueError, match="UPLOAD_MAX_BYTES"):
        Settings.from_env({"UPLOAD_MAX_BYTES": value})
