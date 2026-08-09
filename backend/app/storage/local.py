import os
import shutil
from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

from app.storage.base import (
    DEFAULT_URL_TTL_SECONDS,
    InvalidStorageKeyError,
    ObjectAlreadyExistsError,
    ObjectNotFoundError,
    ObjectStorage,
)

# the API streams these back, they are not served off disk
DOWNLOAD_URL_PREFIX = "/api/files"


class LocalFileStorage(ObjectStorage):
    """Contract files on local disk, under one root directory."""

    def __init__(self, root: str | Path) -> None:
        self._root = Path(root).resolve()

    def save(self, key: str, source: BinaryIO) -> str:
        path = self._resolve(key)
        if path.exists():
            raise ObjectAlreadyExistsError(key)

        path.parent.mkdir(parents=True, exist_ok=True)
        # unique, so two saves never share a staging file
        staged = path.with_name(f"{path.name}.{uuid4().hex}.part")
        try:
            with staged.open("wb") as destination:
                shutil.copyfileobj(source, destination)
            try:
                os.link(staged, path)  # atomic, fails if the key was taken meanwhile
            except FileExistsError:
                raise ObjectAlreadyExistsError(key) from None
        finally:
            staged.unlink(missing_ok=True)
        return key

    def open(self, key: str) -> BinaryIO:
        try:
            return self._resolve(key).open("rb")
        except FileNotFoundError:
            raise ObjectNotFoundError(key) from None

    def exists(self, key: str) -> bool:
        return self._resolve(key).is_file()

    def url_for(self, key: str, expires_in: int = DEFAULT_URL_TTL_SECONDS) -> str:
        # nothing expires on disk, the arg keeps both backends the same
        return f"{DOWNLOAD_URL_PREFIX}/{key}"

    def _resolve(self, key: str) -> Path:
        # keys also come back from the db, so check the path again here
        path = (self._root / key).resolve()
        if not path.is_relative_to(self._root):
            raise InvalidStorageKeyError(key)
        return path
