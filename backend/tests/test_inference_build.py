"""The worker's pipeline according to INFERENCE_PIPELINE, and the startup log of its models."""

import json
import logging

import pytest

import app.worker.__main__ as worker_main
from app.contract import JobStage
from app.inference import FakePipeline, StagedPipeline, diarization, transcription
from app.inference.build import build_pipeline, stage_models
from app.logs import JsonFormatter
from app.settings import Settings


def test_models_is_the_default_pipeline():
    assert Settings.from_env({}).inference_pipeline == "models"


def test_the_pipeline_is_chosen_with_inference_pipeline():
    assert Settings.from_env({"INFERENCE_PIPELINE": " Fake "}).inference_pipeline == "fake"


def test_an_unknown_pipeline_is_refused():
    with pytest.raises(ValueError, match="INFERENCE_PIPELINE"):
        Settings.from_env({"INFERENCE_PIPELINE": "gpu"})


def test_models_builds_the_staged_pipeline_without_loading_anything(tmp_path):
    # MODELS_DIR is empty: building must not fail, the stage fails later with a retry.
    settings = Settings(models_dir=str(tmp_path / "models"))

    assert isinstance(build_pipeline(settings), StagedPipeline)


def test_fake_keeps_the_synthetic_pipeline():
    assert isinstance(build_pipeline(Settings(inference_pipeline="fake")), FakePipeline)


def test_each_stage_names_its_model_revision_and_device():
    models = {item.stage: item for item in stage_models(Settings())}

    assert list(models) == list(JobStage)
    assert models[JobStage.TRANSCRIBING].model == transcription.MODEL_ID
    assert models[JobStage.TRANSCRIBING].revision == transcription.MODEL_REVISION
    assert models[JobStage.TRANSCRIBING].device == "cpu"
    assert models[JobStage.TRANSCRIBING].compute_type == "int8"
    assert models[JobStage.DIARIZING].model == diarization.MODEL_ID
    assert models[JobStage.DIARIZING].revision == diarization.MODEL_REVISION


def test_the_worker_logs_the_model_of_each_stage(caplog: pytest.LogCaptureFixture):
    caplog.set_level(logging.INFO, logger="app.worker")

    worker_main.log_stage_models(Settings(asr_device="cpu"))

    entries = [json.loads(JsonFormatter("worker").format(r)) for r in caplog.records]
    assert [entry["stage"] for entry in entries] == [stage.value for stage in JobStage]
    transcribing = entries[1]
    assert transcribing["event"] == "stage model"
    assert transcribing["pipeline"] == "models"
    assert transcribing["model"] == transcription.MODEL_ID
    assert transcribing["revision"] == transcription.MODEL_REVISION
    assert transcribing["device"] == "cpu"
