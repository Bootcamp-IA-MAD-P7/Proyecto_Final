"""Private storage of the class audio (ADR-0004): the AudioStorage interface and its disk version.

Files are named with opaque keys: the audio_id once committed, `.tmp-<random>` while a
reception is still validating it. Neither the keys nor the paths leave the service.
"""

from __future__ import annotations

import os
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol, runtime_checkable
from uuid import uuid4

TEMPORARY_PREFIX = ".tmp-"
_KEY = re.compile(r"^(\.tmp-)?[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")


class InvalidStorageKeyError(ValueError):
    """A key that is not an opaque name of this storage (for example, a path)."""


@dataclass(frozen=True)
class StoredFile:
    key: str
    modified_at: datetime
    temporary: bool
    """Left by a reception that never committed it: an orphan once it is old enough."""


@runtime_checkable
class AudioStorage(Protocol):
    def write_temporary(self, chunks: Iterable[bytes]) -> str:
        """Write the chunks to a new temporary file and return its key.

        If reading the chunks raises, the partial file is removed and the error propagates.
        """
        ...

    def path(self, key: str) -> Path:
        """Local path of a file, for tools such as ffprobe. Never sent to a client or a log."""
        ...

    def commit(self, temporary_key: str, key: str) -> str:
        """Move a temporary file to its final opaque key and return that key."""
        ...

    def delete(self, key: str) -> None:
        """Remove a file. A missing file is not an error, so a failed delete can be retried."""
        ...

    def list(self) -> list[StoredFile]:
        """Every file of the storage, committed or temporary."""
        ...


class DiskAudioStorage:
    """AudioStorage in a private directory (AUDIO_STORAGE_DIR), created on first use."""

    def __init__(self, directory: str | os.PathLike[str], chunk_size: int = 1024 * 1024) -> None:
        self._directory = Path(directory)
        self.chunk_size = chunk_size

    def write_temporary(self, chunks: Iterable[bytes]) -> str:
        self._directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        key = f"{TEMPORARY_PREFIX}{uuid4().hex}"
        target = self.path(key)
        try:
            with open(target, "xb") as file:
                for chunk in chunks:
                    file.write(chunk)
        except BaseException:
            target.unlink(missing_ok=True)
            raise
        return key

    def path(self, key: str) -> Path:
        if not _KEY.fullmatch(key):
            raise InvalidStorageKeyError("Not an opaque key of the audio storage")
        return self._directory / key

    def commit(self, temporary_key: str, key: str) -> str:
        if not temporary_key.startswith(TEMPORARY_PREFIX) or key.startswith(TEMPORARY_PREFIX):
            raise InvalidStorageKeyError("Only a temporary file can be committed, to a final key")
        target = self.path(key)
        if target.exists():
            raise FileExistsError("The key is already used")
        os.replace(self.path(temporary_key), target)
        return key

    def delete(self, key: str) -> None:
        self.path(key).unlink(missing_ok=True)

    def list(self) -> list[StoredFile]:
        if not self._directory.is_dir():
            return []
        files = []
        for entry in os.scandir(self._directory):
            if not entry.is_file(follow_symlinks=False) or not _KEY.fullmatch(entry.name):
                continue
            modified_at = datetime.fromtimestamp(entry.stat().st_mtime, UTC)
            files.append(
                StoredFile(entry.name, modified_at, entry.name.startswith(TEMPORARY_PREFIX))
            )
        return sorted(files, key=lambda stored: stored.key)
