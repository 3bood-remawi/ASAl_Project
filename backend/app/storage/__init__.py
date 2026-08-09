from functools import lru_cache

from app.core.config import settings
from app.storage.azure_blob import AzureBlobStorage
from app.storage.base import (
    InvalidStorageKeyError,
    ObjectAlreadyExistsError,
    ObjectNotFoundError,
    ObjectStorage,
    StorageError,
    StorageNotConfiguredError,
    build_key,
    safe_filename,
)
from app.storage.local import LocalFileStorage

__all__ = [
    "AzureBlobStorage",
    "InvalidStorageKeyError",
    "LocalFileStorage",
    "ObjectAlreadyExistsError",
    "ObjectNotFoundError",
    "ObjectStorage",
    "StorageError",
    "StorageNotConfiguredError",
    "build_key",
    "get_storage",
    "safe_filename",
]


@lru_cache
def get_storage() -> ObjectStorage:
    """The backend the app uses. Only place that picks one."""
    backend = settings.STORAGE_BACKEND.strip().lower()
    if backend == "local":
        return LocalFileStorage(settings.UPLOAD_DIR)
    if backend == "azure_blob":
        return AzureBlobStorage(settings.AZURE_STORAGE_CONNECTION_STRING, settings.AZURE_STORAGE_CONTAINER)
    raise StorageNotConfiguredError(
        f"Unknown STORAGE_BACKEND {settings.STORAGE_BACKEND!r}. Expected 'local' or 'azure_blob'."
    )
