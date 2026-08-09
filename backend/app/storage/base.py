import re
from abc import ABC, abstractmethod
from typing import BinaryIO
from uuid import UUID

# filesystems cap one path segment at 255 bytes
MAX_FILENAME_LENGTH = 120

DEFAULT_URL_TTL_SECONDS = 3600

_UNSAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]+")


class StorageError(Exception):
    """Base for storage failures."""


class StorageNotConfiguredError(StorageError):
    """Backend is missing settings it needs."""


class ObjectNotFoundError(StorageError):
    """Nothing stored under that key."""


class ObjectAlreadyExistsError(StorageError):
    """Key is taken, and originals are never overwritten."""


class InvalidStorageKeyError(StorageError):
    """Key resolves outside the storage root."""


def safe_filename(filename: str) -> str:
    """Turn a user-supplied filename into a safe key segment."""
    # comes from a browser, could be ../../etc/passwd or a windows path
    name = filename.replace("\\", "/").rsplit("/", 1)[-1]
    name = _UNSAFE_CHARS.sub("_", name).lstrip(".")
    if not name:
        return "upload"
    if len(name) <= MAX_FILENAME_LENGTH:
        return name

    # keep the extension when trimming
    stem, dot, suffix = name.rpartition(".")
    if dot and len(suffix) <= 10:
        return f"{stem[: MAX_FILENAME_LENGTH - len(suffix) - 1]}.{suffix}"
    return name[:MAX_FILENAME_LENGTH]


def build_key(
    organization_id: UUID | str,
    contract_id: UUID | str,
    version_id: UUID | str,
    filename: str,
) -> str:
    """Key layout: organisation / contract / version / file."""
    return f"{organization_id}/{contract_id}/{version_id}/{safe_filename(filename)}"


class ObjectStorage(ABC):
    """Stores and retrieves contract files. Callers work in keys, not paths.

    No delete and no overwrite on purpose. NFR-1 says the upload is immutable.
    """

    @abstractmethod
    def save(self, key: str, source: BinaryIO) -> str:
        """Store source under key and return the key."""

    @abstractmethod
    def open(self, key: str) -> BinaryIO:
        """Open for reading. Caller closes it."""

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Whether anything is stored under key."""

    @abstractmethod
    def url_for(self, key: str, expires_in: int = DEFAULT_URL_TTL_SECONDS) -> str:
        """URL the browser can fetch the file from."""
