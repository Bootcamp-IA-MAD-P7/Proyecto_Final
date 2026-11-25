"""Private storage and validation of the class audio (design of add-class-reception)."""

from app.storage.disk import (
    TEMPORARY_PREFIX,
    AudioStorage,
    DiskAudioStorage,
    InvalidStorageKeyError,
    StoredFile,
)
from app.storage.probe import AudioInfo, AudioProbe, FfprobeAudioProbe, UnreadableAudioError
from app.storage.reception import (
    AudioLimits,
    AudioTooLargeError,
    InvalidAudioDurationError,
    ReceivedAudio,
    UnsupportedAudioError,
    receive_audio,
)

__all__ = [
    "TEMPORARY_PREFIX",
    "AudioInfo",
    "AudioLimits",
    "AudioProbe",
    "AudioStorage",
    "AudioTooLargeError",
    "DiskAudioStorage",
    "FfprobeAudioProbe",
    "InvalidAudioDurationError",
    "InvalidStorageKeyError",
    "ReceivedAudio",
    "StoredFile",
    "UnreadableAudioError",
    "UnsupportedAudioError",
    "receive_audio",
]
