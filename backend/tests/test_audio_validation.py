"""Validation of the received audio: size, format by its content and duration (class-processing)."""

import io

import pytest

from app.storage import (
    AudioInfo,
    AudioLimits,
    AudioTooLargeError,
    DiskAudioStorage,
    FfprobeAudioProbe,
    InvalidAudioDurationError,
    UnreadableAudioError,
    UnsupportedAudioError,
    receive_audio,
)
from app.storage.probe import audio_info
from tests.conftest import FixedProbe

LIMITS = AudioLimits(max_bytes=1024 * 1024, min_seconds=1, max_seconds=5)


@pytest.fixture
def storage(tmp_path) -> DiskAudioStorage:
    return DiskAudioStorage(tmp_path / "audio")


def receive(storage, content: bytes, probe=None, limits=LIMITS):
    probe = probe or FixedProbe(AudioInfo("opus", 2))
    return receive_audio(io.BytesIO(content), storage, probe, limits, chunk_size=4)


# --- Size, format and duration, with a fixed probe ---------------------------------------------


def test_valid_audio_stays_as_a_temporary_file_with_its_size_and_hash(storage):
    received = receive(storage, b"0123456789")

    assert received.size_bytes == 10
    assert received.sha256 == "84d89877f0d4041efb6bf91a16f0248f2fd573e6af05c19f96bedb9f882f7882"
    assert storage.path(received.temporary_key).read_bytes() == b"0123456789"
    assert (received.format, received.duration_seconds) == ("opus", 2)


def test_size_above_the_maximum_stops_the_copy_and_leaves_no_file(storage):
    class Unbounded(io.RawIOBase):
        reads = 0

        def read(self, size=-1):
            self.reads += 1
            return b"x" * size

    source = Unbounded()
    limits = AudioLimits(max_bytes=10, min_seconds=1, max_seconds=5)

    with pytest.raises(AudioTooLargeError):
        receive_audio(source, storage, FixedProbe(AudioInfo("opus", 2)), limits, chunk_size=4)

    assert source.reads == 3
    assert storage.list() == []


def test_size_equal_to_the_maximum_is_accepted(storage):
    limits = AudioLimits(max_bytes=10, min_seconds=1, max_seconds=5)

    assert receive(storage, b"x" * 10, limits=limits).size_bytes == 10


def test_unreadable_audio_is_unsupported_and_leaves_no_file(storage):
    with pytest.raises(UnsupportedAudioError):
        receive(storage, b"not audio", FixedProbe(UnreadableAudioError("unreadable")))

    assert storage.list() == []


@pytest.mark.parametrize("seconds", [0.5, 5.5])
def test_duration_outside_the_limits_leaves_no_file(storage, seconds):
    with pytest.raises(InvalidAudioDurationError):
        receive(storage, b"audio", FixedProbe(AudioInfo("opus", seconds)))

    assert storage.list() == []


@pytest.mark.parametrize("seconds", [1, 5])
def test_duration_on_the_limits_is_accepted(storage, seconds):
    assert receive(storage, b"audio", FixedProbe(AudioInfo("mp3", seconds))).duration_seconds == (
        seconds
    )


# --- Reports of ffprobe -----------------------------------------------------------------------


def report(container: str, *streams: dict, duration: str | None = "60.0") -> dict:
    return {"format": {"format_name": container, "duration": duration}, "streams": list(streams)}


AUDIO = {"codec_type": "audio", "codec_name": "opus"}


@pytest.mark.parametrize(
    ("container", "codec", "family"),
    [
        ("ogg", "opus", "opus"),
        ("matroska,webm", "opus", "opus"),
        ("mp3", "mp3", "mp3"),
        ("mov,mp4,m4a,3gp,3g2,mj2", "aac", "aac"),
    ],
)
def test_admitted_formats(container, codec, family):
    info = audio_info(report(container, {"codec_type": "audio", "codec_name": codec}))

    assert info == AudioInfo(family, 60.0)


def test_cover_art_is_not_a_video():
    cover = {"codec_type": "video", "codec_name": "mjpeg", "disposition": {"attached_pic": 1}}

    assert audio_info(
        report("mp3", {"codec_type": "audio", "codec_name": "mp3"}, cover)
    ).format == ("mp3")


@pytest.mark.parametrize(
    "bad",
    [
        report("wav", {"codec_type": "audio", "codec_name": "pcm_s16le"}),
        report("ogg", {"codec_type": "audio", "codec_name": "vorbis"}),
        report("ogg"),
        report("matroska,webm", AUDIO, {"codec_type": "video", "codec_name": "vp8"}),
        report("ogg", AUDIO, duration=None),
        report("ogg", AUDIO, duration="N/A"),
        {},
    ],
)
def test_reports_that_are_not_admitted_audio(bad):
    with pytest.raises(UnreadableAudioError):
        audio_info(bad)


def test_duration_falls_back_to_the_audio_track():
    stream = {**AUDIO, "duration": "90.5"}

    assert audio_info(report("ogg", stream, duration=None)).duration_seconds == 90.5


# --- Real ffprobe on synthetic audio ------------------------------------------------------------


@pytest.mark.parametrize(
    ("kind", "family"), [("ogg", "opus"), ("webm", "opus"), ("mp3", "mp3"), ("m4a", "aac")]
)
def test_ffprobe_admits_the_contract_formats(synthetic_audio, kind, family):
    info = FfprobeAudioProbe().probe(synthetic_audio(kind, 2))

    assert info.format == family
    assert info.duration_seconds == pytest.approx(2, abs=0.2)


@pytest.mark.parametrize(("kind", "video"), [("wav", False), ("flac", False), ("mp4", True)])
def test_ffprobe_rejects_other_formats_and_video(synthetic_audio, kind, video):
    with pytest.raises(UnreadableAudioError):
        FfprobeAudioProbe().probe(synthetic_audio(kind, 2, video=video))


def test_ffprobe_rejects_content_that_is_not_audio(synthetic_audio, tmp_path):
    fake = tmp_path / "class.mp3"
    fake.write_bytes(b"ID3 this is text with an audio name" * 100)

    with pytest.raises(UnreadableAudioError):
        FfprobeAudioProbe().probe(fake)


def test_ffprobe_does_not_follow_playlists(synthetic_audio, tmp_path):
    target = synthetic_audio("mp3", 2)
    playlist = tmp_path / "class.mp3"
    playlist.write_text(f"#EXTM3U\n#EXTINF:2,\nfile:{target}\n#EXT-X-ENDLIST\n")

    with pytest.raises(UnreadableAudioError):
        FfprobeAudioProbe().probe(playlist)
