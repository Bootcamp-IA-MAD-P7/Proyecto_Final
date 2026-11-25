"""Format and duration of an audio file by its content, with ffprobe (add-class-reception).

The file name and the declared Content-Type are never used. Only the demuxers of the admitted
containers are allowed and only local files can be opened, so a crafted file (a playlist, for
example) cannot make ffprobe read other files or the network.
"""

from __future__ import annotations

import json
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

ADMITTED = {
    "ogg": ("opus", frozenset({"opus"})),
    "matroska,webm": ("opus", frozenset({"opus"})),
    "mp3": ("mp3", frozenset({"mp3"})),
    "mov,mp4,m4a,3gp,3g2,mj2": ("aac", frozenset({"aac"})),
}
"""ffprobe format_name -> (format recorded for the audio, codecs admitted in its audio tracks)."""

_DEMUXERS = "ogg,matroska,webm,mp3,mov,mp4,m4a,3gp,3g2,mj2"


class UnreadableAudioError(ValueError):
    """Not audio in an admitted format: unreadable, without audio, with video or another codec."""


@dataclass(frozen=True)
class AudioInfo:
    format: str
    """Codec family of the audio: opus, mp3 or aac."""
    duration_seconds: float


class AudioProbe(Protocol):
    def probe(self, path: Path) -> AudioInfo:
        """Format and duration of the file, or UnreadableAudioError if it is not admitted."""
        ...


class FfprobeAudioProbe:
    def __init__(self, binary: str = "ffprobe", timeout_seconds: float = 60) -> None:
        self._binary = binary
        self._timeout_seconds = timeout_seconds

    def probe(self, path: Path) -> AudioInfo:
        command = [
            self._binary,
            "-v",
            "error",
            "-protocol_whitelist",
            "file",
            "-format_whitelist",
            _DEMUXERS,
            "-print_format",
            "json",
            "-show_entries",
            "format=format_name,duration:stream=codec_type,codec_name,duration"
            ":stream_disposition=attached_pic",
            str(path),
        ]
        try:
            completed = subprocess.run(
                command, capture_output=True, timeout=self._timeout_seconds, check=False
            )
        except subprocess.TimeoutExpired as error:
            raise UnreadableAudioError("ffprobe did not finish") from error
        if completed.returncode != 0:
            raise UnreadableAudioError("ffprobe could not read the file")
        try:
            report = json.loads(completed.stdout)
        except ValueError as error:
            raise UnreadableAudioError("ffprobe answered something that is not JSON") from error
        return audio_info(report)


def audio_info(report: dict[str, Any]) -> AudioInfo:
    """Admitted format and duration from an ffprobe JSON report."""
    container = (report.get("format") or {}).get("format_name")
    if container not in ADMITTED:
        raise UnreadableAudioError("Container not admitted")
    family, codecs = ADMITTED[container]
    streams = report.get("streams") or []
    audio = [stream for stream in streams if stream.get("codec_type") == "audio"]
    video = [
        stream
        for stream in streams
        if stream.get("codec_type") == "video"
        # Cover art of MP3 and M4A files is a picture, not a video.
        and not (stream.get("disposition") or {}).get("attached_pic")
    ]
    if not audio or video:
        raise UnreadableAudioError("Not an audio-only file")
    if any(stream.get("codec_name") not in codecs for stream in audio):
        raise UnreadableAudioError("Codec not admitted")
    durations = [_seconds(report["format"].get("duration"))] + [
        _seconds(stream.get("duration")) for stream in audio
    ]
    known = [duration for duration in durations if duration is not None]
    if not known:
        raise UnreadableAudioError("Unknown duration")
    return AudioInfo(format=family, duration_seconds=known[0])


def _seconds(value: Any) -> float | None:
    try:
        seconds = float(value)
    except (TypeError, ValueError):
        return None
    return seconds if math.isfinite(seconds) and seconds >= 0 else None
