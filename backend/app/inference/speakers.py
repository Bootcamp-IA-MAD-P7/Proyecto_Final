"""Pure combination of transcribed words and diarization turns into a contract transcript."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import pairwise

from app.contract import Segment, Speaker, Transcript
from app.inference.types import Phrase, Turn, Word

NEAREST_TURN_MS = 1000
NO_TURNS_VOICE = "only-voice"


@dataclass(frozen=True)
class _Piece:
    voice: str
    start_ms: int
    end_ms: int
    text: str


def _overlap(word: Word, turn: Turn) -> int:
    return max(0, min(word.end_ms, turn.end_ms) - max(word.start_ms, turn.start_ms))


def _distance(word: Word, turn: Turn) -> int:
    return max(0, turn.start_ms - word.end_ms, word.start_ms - turn.end_ms)


def _voice_for(word: Word, turns: list[Turn], previous: str | None) -> str:
    if not turns:
        return NO_TURNS_VOICE

    overlapping = [
        (_overlap(word, turn), index, turn.speaker_id) for index, turn in enumerate(turns)
    ]
    best_overlap = max(overlapping, default=None)
    if best_overlap is not None and best_overlap[0] > 0:
        return best_overlap[2]

    nearby = [
        (_distance(word, turn), index, turn.speaker_id)
        for index, turn in enumerate(turns)
        if _distance(word, turn) < NEAREST_TURN_MS
    ]
    if nearby:
        return min(nearby)[2]
    if previous is not None:
        return previous

    # The first word of a phrase far from every turn still belongs to a detected voice.
    return min((_distance(word, turn), index, turn.speaker_id) for index, turn in enumerate(turns))[
        2
    ]


def _pieces(phrase: Phrase, turns: list[Turn]) -> list[_Piece]:
    pieces: list[_Piece] = []
    previous: str | None = None
    for word in phrase.words:
        voice = _voice_for(word, turns, previous)
        previous = voice
        if pieces and pieces[-1].voice == voice:
            last = pieces[-1]
            pieces[-1] = _Piece(voice, last.start_ms, word.end_ms, f"{last.text} {word.text}")
        else:
            pieces.append(_Piece(voice, word.start_ms, word.end_ms, word.text))
    return pieces


def assign_speakers(phrases: list[Phrase], turns: list[Turn]) -> Transcript:
    """Build the contract transcript from phrases and exclusive speaker turns.

    Voices are declared in the order of their first segment and are never associated to a
    participant (RD-04). Simultaneous text is attributed to the dominant voice, not marked.
    """
    pieces = sorted(
        (piece for phrase in phrases for piece in _pieces(phrase, turns)),
        key=lambda piece: (piece.start_ms, piece.end_ms),
    )

    if any(current.start_ms < previous.end_ms for previous, current in pairwise(pieces)):
        raise ValueError("phrases must not overlap in time")

    voices: dict[str, str] = {}
    speakers: list[Speaker] = []
    segments: list[Segment] = []
    for index, piece in enumerate(pieces, start=1):
        if piece.voice not in voices:
            speaker_id = f"speaker-{len(voices) + 1}"
            voices[piece.voice] = speaker_id
            speakers.append(Speaker(speaker_id=speaker_id, participant_id=None))
        segments.append(
            Segment(
                segment_id=f"segment-{index}",
                start_ms=piece.start_ms,
                end_ms=piece.end_ms,
                speaker_id=voices[piece.voice],
                text=piece.text,
            )
        )
    return Transcript(speakers=speakers, segments=segments)
