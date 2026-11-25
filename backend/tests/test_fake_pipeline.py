from app.contract import ClassMetadata, JobStage
from app.inference import FakePipeline, InferencePipeline, PipelineInput
from app.inference.fake import SYNTHETIC_RESULT
from tests.conftest import load_fixture


def run(pipeline: FakePipeline, stages: list[JobStage]):
    metadata = ClassMetadata.model_validate(load_fixture("valid/class-metadata.json"))
    return pipeline.run(PipelineInput("class-01", metadata, None), stages.append)


def test_goes_through_every_stage_and_returns_the_synthetic_example():
    stages: list[JobStage] = []
    draft = load_fixture("valid/result-draft.json")

    output = run(FakePipeline(), stages)

    assert isinstance(FakePipeline(), InferencePipeline)
    assert stages == list(JobStage)
    assert output.transcript.model_dump(mode="json", exclude_unset=True) == draft["transcript"]
    assert output.analysis.model_dump(mode="json", exclude_unset=True) == draft["analysis"]


def test_waits_the_configured_seconds_in_each_stage():
    waits: list[float] = []

    run(FakePipeline(stage_seconds=0.5, sleep=waits.append), [])

    assert waits == [0.5] * len(JobStage)


def test_the_example_shipped_with_the_app_is_the_contract_fixture():
    import json

    shipped = json.loads(SYNTHETIC_RESULT.read_text(encoding="utf-8"))
    assert shipped == load_fixture("valid/result-draft.json")
