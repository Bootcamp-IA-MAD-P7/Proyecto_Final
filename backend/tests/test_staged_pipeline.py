from pathlib import Path

import pytest

from app.contract import ClassMetadata, JobErrorCode, JobStage, Participant, ParticipantRole
from app.inference import (
    EmptyAnalyzer,
    Phrase,
    PipelineError,
    PipelineInput,
    StagedPipeline,
    Turn,
    Word,
)


def metadata(participants: int = 2) -> ClassMetadata:
    return ClassMetadata(
        external_class_id="class-01",
        participant_count=participants,
        participants=[
            Participant(participant_id=f"p{index}", role=ParticipantRole.STUDENT)
            for index in range(1, participants + 1)
        ],
        consent_reference="consent-01",
    )


class RecordingNormalizer:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def load(self) -> None:
        self.calls.append("normalizer.load")

    def close(self) -> None:
        self.calls.append("normalizer.close")

    def normalize(self, audio_path: Path, work_dir: Path) -> Path:
        self.calls.append("normalizer.normalize")
        wav = work_dir / "audio.wav"
        wav.write_bytes(b"wav")
        return wav


class RecordingTranscriber:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def load(self) -> None:
        self.calls.append("transcriber.load")

    def close(self) -> None:
        self.calls.append("transcriber.close")

    def transcribe(self, wav_path: Path) -> list[Phrase]:
        self.calls.append("transcriber.transcribe")
        return [Phrase(words=[Word(text="hola", start_ms=0, end_ms=500)])]


class RecordingDiarizer:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.max_speakers: int | None = None

    def load(self) -> None:
        self.calls.append("diarizer.load")

    def close(self) -> None:
        self.calls.append("diarizer.close")

    def diarize(self, wav_path: Path, max_speakers: int) -> list[Turn]:
        self.calls.append("diarizer.diarize")
        self.max_speakers = max_speakers
        return [Turn(start_ms=0, end_ms=500, speaker_id="voice-a")]


def pipeline() -> tuple[StagedPipeline, RecordingNormalizer, RecordingTranscriber, RecordingDiarizer]:
    normalizer = RecordingNormalizer()
    transcriber = RecordingTranscriber()
    diarizer = RecordingDiarizer()
    return (
        StagedPipeline(normalizer, transcriber, diarizer, EmptyAnalyzer()),
        normalizer,
        transcriber,
        diarizer,
    )


def test_stages_are_reported_in_order_and_adapters_load_and_release(tmp_path: Path) -> None:
    staged, normalizer, transcriber, diarizer = pipeline()
    stages: list[JobStage] = []
    audio = tmp_path / "audio.ogg"
    audio.write_bytes(b"audio")

    output = staged.run(PipelineInput("class-01", metadata(), audio), stages.append)

    assert stages == [
        JobStage.NORMALIZING,
        JobStage.TRANSCRIBING,
        JobStage.DIARIZING,
        JobStage.ANALYZING,
    ]
    assert normalizer.calls == ["normalizer.load", "normalizer.normalize", "normalizer.close"]
    assert transcriber.calls == ["transcriber.load", "transcriber.transcribe", "transcriber.close"]
    assert diarizer.calls == ["diarizer.load", "diarizer.diarize", "diarizer.close"]
    assert diarizer.max_speakers == 2
    assert len(output.transcript.segments) == 1
    assert output.transcript.segments[0].speaker_id == "speaker-1"
    assert output.analysis.general_summary == ""
    assert output.analysis.items == []


def test_participant_count_is_a_maximum_not_an_exact_number(tmp_path: Path) -> None:
    staged, _, _, diarizer = pipeline()
    audio = tmp_path / "audio.ogg"
    audio.write_bytes(b"audio")

    staged.run(PipelineInput("class-01", metadata(participants=3), audio), lambda stage: None)

    assert diarizer.max_speakers == 3


def test_pipeline_error_from_an_adapter_propagates_and_stops_the_stages(tmp_path: Path) -> None:
    staged, _, transcriber, _ = pipeline()

    def unavailable(wav_path: Path) -> list[Phrase]:
        raise PipelineError(JobErrorCode.PROCESSING_UNAVAILABLE, "model missing", retryable=True)

    transcriber.transcribe = unavailable  # type: ignore[method-assign]
    stages: list[JobStage] = []
    audio = tmp_path / "audio.ogg"
    audio.write_bytes(b"audio")

    with pytest.raises(PipelineError) as error:
        staged.run(PipelineInput("class-01", metadata(), audio), stages.append)

    assert error.value.error.code == JobErrorCode.PROCESSING_UNAVAILABLE
    assert error.value.error.retryable is True
    assert stages == [JobStage.NORMALIZING, JobStage.TRANSCRIBING]


def test_unexpected_adapter_error_becomes_a_non_retryable_pipeline_error(tmp_path: Path) -> None:
    staged, normalizer, _, _ = pipeline()

    def broken(audio_path: Path, work_dir: Path) -> Path:
        raise RuntimeError("secret detail")

    normalizer.normalize = broken  # type: ignore[method-assign]
    stages: list[JobStage] = []
    audio = tmp_path / "audio.ogg"
    audio.write_bytes(b"audio")

    with pytest.raises(PipelineError) as error:
        staged.run(PipelineInput("class-01", metadata(), audio), stages.append)

    assert error.value.error.code == JobErrorCode.PROCESSING_FAILED
    assert error.value.error.retryable is False
    assert "secret detail" not in error.value.error.message


def test_pipeline_requires_the_saved_audio(tmp_path: Path) -> None:
    staged, *_ = pipeline()

    with pytest.raises(PipelineError) as error:
        staged.run(PipelineInput("class-01", metadata(), None), lambda stage: None)

    assert error.value.error.code == JobErrorCode.PROCESSING_FAILED
