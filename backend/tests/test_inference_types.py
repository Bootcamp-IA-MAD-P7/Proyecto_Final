from pathlib import Path

import pytest

from app.contract import Analysis, Transcript
from app.inference import (
    Analyzer,
    Diarizer,
    EmptyAnalyzer,
    Normalizer,
    Phrase,
    Transcriber,
    Turn,
    Word,
)


def test_word_and_turn_require_positive_intervals() -> None:
    with pytest.raises(ValueError):
        Word(text="hola", start_ms=10, end_ms=10)
    with pytest.raises(ValueError):
        Turn(start_ms=20, end_ms=19, speaker_id="voice-a")


def test_phrase_requires_ordered_words_and_exposes_its_interval_and_text() -> None:
    words = [
        Word(text="hola", start_ms=0, end_ms=100),
        Word(text="mundo", start_ms=100, end_ms=200),
    ]
    phrase = Phrase(words=words)

    assert phrase.start_ms == 0
    assert phrase.end_ms == 200
    assert phrase.text == "hola mundo"
    with pytest.raises(ValueError):
        Phrase(words=list(reversed(words)))
    with pytest.raises(ValueError):
        Phrase(words=[])


def test_empty_analyzer_returns_an_empty_contract_analysis() -> None:
    analyzer = EmptyAnalyzer()
    analysis = analyzer.analyze(Transcript(speakers=[], segments=[]))

    assert analyzer.load() is None
    assert isinstance(analyzer, Analyzer)
    assert analysis == Analysis(general_summary="", items=[])
    assert analyzer.close() is None


def test_adapter_protocols_are_runtime_checkable() -> None:
    class FakeNormalizer:
        def load(self) -> None:
            pass

        def close(self) -> None:
            pass

        def normalize(self, audio_path: Path, work_dir: Path) -> Path:
            return audio_path

    class FakeTranscriber:
        def load(self) -> None:
            pass

        def close(self) -> None:
            pass

        def transcribe(self, wav_path: Path) -> list[Phrase]:
            return []

    class FakeDiarizer:
        def load(self) -> None:
            pass

        def close(self) -> None:
            pass

        def diarize(self, wav_path: Path, max_speakers: int) -> list[Turn]:
            return []

    assert isinstance(FakeNormalizer(), Normalizer)
    assert isinstance(FakeTranscriber(), Transcriber)
    assert isinstance(FakeDiarizer(), Diarizer)
