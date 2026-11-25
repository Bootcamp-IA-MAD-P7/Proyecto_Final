"""Private audio storage on disk (app/storage)."""

import pytest

from app.storage import AudioStorage, DiskAudioStorage, InvalidStorageKeyError


@pytest.fixture
def storage(tmp_path) -> DiskAudioStorage:
    return DiskAudioStorage(tmp_path / "audio")


def test_implements_the_interface(storage):
    assert isinstance(storage, AudioStorage)


def test_temporary_file_is_committed_with_an_opaque_name(storage, tmp_path):
    temporary = storage.write_temporary([b"abc", b"def"])

    key = storage.commit(temporary, "audio-0001")

    assert key == "audio-0001"
    assert storage.path(key).read_bytes() == b"abcdef"
    assert [(f.key, f.temporary) for f in storage.list()] == [("audio-0001", False)]
    assert storage.path(key).parent == tmp_path / "audio"


def test_a_failed_write_leaves_no_file(storage):
    def chunks():
        yield b"partial"
        raise OSError("connection lost")

    with pytest.raises(OSError):
        storage.write_temporary(chunks())

    assert storage.list() == []


def test_temporary_files_are_listed_as_temporary(storage):
    temporary = storage.write_temporary([b"x"])

    assert [(f.key, f.temporary) for f in storage.list()] == [(temporary, True)]


def test_delete_is_idempotent(storage):
    key = storage.commit(storage.write_temporary([b"x"]), "audio-0001")

    storage.delete(key)
    storage.delete(key)

    assert storage.list() == []


def test_commit_never_overwrites(storage):
    storage.commit(storage.write_temporary([b"first"]), "audio-0001")

    with pytest.raises(FileExistsError):
        storage.commit(storage.write_temporary([b"second"]), "audio-0001")

    assert storage.path("audio-0001").read_bytes() == b"first"


@pytest.mark.parametrize("key", ["../outside", "a/b", "", ".hidden", "audio 1", "C:\\x"])
def test_keys_are_opaque_names_not_paths(storage, key):
    with pytest.raises(InvalidStorageKeyError):
        storage.path(key)


def test_list_of_a_missing_directory_is_empty(storage):
    assert storage.list() == []
