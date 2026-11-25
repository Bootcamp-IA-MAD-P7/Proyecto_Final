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
