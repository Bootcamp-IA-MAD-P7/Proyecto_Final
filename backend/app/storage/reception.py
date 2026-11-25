"""Reception of the audio of a class: size, format and duration, in the order of the contract.

The audio is copied to a temporary file of the storage in chunks, counting bytes and computing
its sha256, and the copy stops as soon as it goes over the maximum size. Then ffprobe checks the
format and the duration. Any rejected audio leaves no file behind.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterator
from dataclasses import dataclass
from typing import BinaryIO

from app.storage.disk import AudioStorage
from app.storage.probe import AudioProbe, UnreadableAudioError


class AudioTooLargeError(ValueError):
    """Above the maximum size (413 audio_too_large)."""


class UnsupportedAudioError(ValueError):
    """Not audio in an admitted format, by its content (415 unsupported_audio)."""


class InvalidAudioDurationError(ValueError):
    """Shorter or longer than the configured limits (422 invalid_audio_duration)."""


@dataclass(frozen=True)
class AudioLimits:
    max_bytes: int
    min_seconds: float
    max_seconds: float


@dataclass(frozen=True)
class ReceivedAudio:
    temporary_key: str
    """Temporary file of the storage: commit it or delete it."""
    format: str
    size_bytes: int
    duration_seconds: float
    sha256: str


def receive_audio(
    source: BinaryIO,
    storage: AudioStorage,
    probe: AudioProbe,
    limits: AudioLimits,
    chunk_size: int = 1024 * 1024,
) -> ReceivedAudio:
    """Copy and validate the audio. On any error the temporary file is already removed."""
    digest = hashlib.sha256()
    size = 0

    def chunks() -> Iterator[bytes]:
        nonlocal size
        while chunk := source.read(chunk_size):
            size += len(chunk)
            if size > limits.max_bytes:
                raise AudioTooLargeError("The audio is larger than the maximum size")
            digest.update(chunk)
            yield chunk

    key = storage.write_temporary(chunks())
    try:
        try:
            info = probe.probe(storage.path(key))
        except UnreadableAudioError as error:
            raise UnsupportedAudioError(str(error)) from error
        if not limits.min_seconds <= info.duration_seconds <= limits.max_seconds:
            raise InvalidAudioDurationError("The duration is outside the limits")
    except BaseException:
        storage.delete(key)
        raise
    return ReceivedAudio(
        temporary_key=key,
        format=info.format,
        size_bytes=size,
        duration_seconds=info.duration_seconds,
        sha256=digest.hexdigest(),
    )
