from app.inference import Phrase, Turn, Word, assign_speakers
from app.contract import Transcript


def phrase(*words: tuple[str, int, int]) -> Phrase:
    return Phrase(words=[Word(text=text, start_ms=start, end_ms=end) for text, start, end in words])


def transcript(*phrases: Phrase, turns: list[Turn]) -> Transcript:
    return assign_speakers(list(phrases), turns)


def test_two_speakers_taking_turns() -> None:
    result = transcript(
        phrase(("uno", 0, 500), ("dos", 500, 1000)),
        phrase(("tres", 1500, 2000)),
        turns=[Turn(0, 1000, "voice-a"), Turn(1500, 2000, "voice-b")],
    )

    assert [speaker.speaker_id for speaker in result.speakers] == ["speaker-1", "speaker-2"]
    assert [segment.speaker_id for segment in result.segments] == ["speaker-1", "speaker-2"]
    assert [(segment.start_ms, segment.end_ms) for segment in result.segments] == [
        (0, 1000),
        (1500, 2000),
    ]


def test_speaker_change_inside_one_phrase_splits_the_segment() -> None:
    result = transcript(
        phrase(("uno", 0, 400), ("dos", 400, 800), ("tres", 800, 1200)),
        turns=[Turn(0, 400, "a"), Turn(400, 1200, "b")],
    )

    assert [segment.speaker_id for segment in result.segments] == ["speaker-1", "speaker-2"]
    assert [segment.text for segment in result.segments] == ["uno", "dos tres"]
    assert len(result.speakers) == 2


def test_silent_participant_does_not_add_a_speaker() -> None:
    result = transcript(phrase(("hola", 0, 500)), turns=[Turn(0, 500, "voice-a")])

    assert len(result.speakers) == 1
    assert all(speaker.participant_id is None for speaker in result.speakers)


def test_names_and_roles_do_not_identify_voices() -> None:
    result = transcript(phrase(("hola", 0, 500)), turns=[Turn(0, 500, "ana")])

    assert result.speakers[0].speaker_id == "speaker-1"
    assert result.speakers[0].participant_id is None


def test_simultaneous_voices_assign_text_to_the_dominant_voice() -> None:
    result = transcript(
        phrase(("hola", 100, 900)),
        turns=[Turn(0, 1000, "dominant"), Turn(100, 500, "brief")],
    )

    assert len(result.speakers) == 1
    assert result.speakers[0].speaker_id == "speaker-1"
    assert result.segments[0].speaker_id == "speaker-1"


def test_nearest_turn_within_one_second_is_used_when_there_is_no_overlap() -> None:
    result = transcript(
        phrase(("temprano", 0, 100)),
        phrase(("hola", 1000, 1100)),
        turns=[Turn(0, 500, "a"), Turn(1500, 2000, "b")],
    )

    assert [segment.speaker_id for segment in result.segments] == ["speaker-1", "speaker-2"]
    assert result.segments[1].start_ms == 1000


def test_far_word_inherits_the_previous_voice_of_its_phrase() -> None:
    result = transcript(
        phrase(("uno", 0, 100), ("dos", 5000, 5100)),
        turns=[Turn(0, 100, "a")],
    )

    assert len(result.segments) == 1
    assert result.segments[0].speaker_id == "speaker-1"
    assert result.segments[0].text == "uno dos"


def test_words_without_turns_become_one_voice() -> None:
    result = transcript(phrase(("uno", 0, 100), ("dos", 200, 300)), turns=[])

    assert len(result.speakers) == 1
    assert len(result.segments) == 1
    assert result.segments[0].text == "uno dos"


def test_no_audio_has_an_empty_transcript() -> None:
    result = transcript(turns=[])

    assert result == Transcript(speakers=[], segments=[])


def test_segments_are_numbered_in_temporal_order_and_intervals_are_valid() -> None:
    result = transcript(
        phrase(("tarde", 1000, 1100)),
        phrase(("temprano", 0, 100)),
        turns=[Turn(0, 1100, "a")],
    )

    assert [segment.segment_id for segment in result.segments] == ["segment-1", "segment-2"]
    assert [segment.start_ms for segment in result.segments] == [0, 1000]
    assert all(segment.end_ms > segment.start_ms for segment in result.segments)
