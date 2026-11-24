from app.contract import Analysis, ClassMetadata, JobErrorCode, JobStage, Transcript
from app.inference import InferencePipeline, PipelineError, PipelineInput, PipelineOutput
from tests.conftest import load_fixture


class StubPipeline:
    """Minimal implementation: proves that the interface can be implemented as declared."""

    def run(self, job_input: PipelineInput, on_stage) -> PipelineOutput:
        result = load_fixture("valid/result-draft.json")
        for stage in JobStage:
            on_stage(stage)
        return PipelineOutput(
            transcript=Transcript.model_validate(result["transcript"]),
            analysis=Analysis.model_validate(result["analysis"]),
        )


def test_a_pipeline_reports_every_stage_in_order():
    pipeline = StubPipeline()
    stages = []
    metadata = ClassMetadata.model_validate(load_fixture("valid/class-metadata.json"))

    output = pipeline.run(PipelineInput("class-demo-01", metadata, None), stages.append)

    assert isinstance(pipeline, InferencePipeline)
    assert stages == list(JobStage)
    assert output.analysis.items[0].category == "vocabulary"


def test_pipeline_error_carries_a_contract_error():
    error = PipelineError(JobErrorCode.PROCESSING_UNAVAILABLE, "No disponible", retryable=True)

    assert error.error.code is JobErrorCode.PROCESSING_UNAVAILABLE
    assert error.error.retryable is True
