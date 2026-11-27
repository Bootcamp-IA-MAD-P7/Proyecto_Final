"""Types and adapter interfaces for the staged inference pipeline.

Word and turn timestamps are milliseconds from the start of the original recording.
Normalization changes sample rate and channels, never the timeline (design.md, E3).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

from app.contract import Analysis, Transcript


@dataclass(frozen=True)
class Word:
    text: str
    start_ms: int
    end_ms: int

    def __post_init__(self) -> None:
        if not self.text:
            raise ValueError("word text must not be empty")
        if self.end_ms <= self.start_ms:
            raise ValueError("word end must be after its start")


@dataclass(frozen=True)
class Phrase:
    words: list[Word]

    def __post_init__(self) -> None:
        if not self.words:
            raise ValueError("phrase must have at least one word")
        if any(
            current.end_ms > following.start_ms
            for current, following in zip(self.words, self.words[1:])
        ):
            raise ValueError("phrase words must be ordered and not overlap")

    @property
    def start_ms(self) -> int:
        return self.words[0].start_ms

    @property
    def end_ms(self) -> int:
        return self.words[-1].end_ms

    @property
    def text(self) -> str:
        return " ".join(word.text for word in self.words)


@dataclass(frozen=True)
class Turn:
    start_ms: int
    end_ms: int
    speaker_id: str

    def __post_init__(self) -> None:
        if self.end_ms <= self.start_ms:
            raise ValueError("turn end must be after its start")
        if not self.speaker_id:
            raise ValueError("turn speaker must not be empty")


@runtime_checkable
class ModelAdapter(Protocol):
    """An adapter loads its model at the start of its stage and releases it at the end."""

    def load(self) -> None: ...

    def close(self) -> None: ...


@runtime_checkable
class Normalizer(ModelAdapter, Protocol):
    def normalize(self, audio_path: Path, work_dir: Path) -> Path: ...


@runtime_checkable
class Transcriber(ModelAdapter, Protocol):
    def transcribe(self, wav_path: Path) -> list[Phrase]: ...


@runtime_checkable
class Diarizer(ModelAdapter, Protocol):
    def diarize(self, wav_path: Path, max_speakers: int) -> list[Turn]: ...


@runtime_checkable
class Analyzer(ModelAdapter, Protocol):
    def analyze(self, transcript: Transcript) -> Analysis: ...
