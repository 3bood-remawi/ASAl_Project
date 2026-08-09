from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import BinaryIO

from app.storage.base import (
    DEFAULT_URL_TTL_SECONDS,
    ObjectAlreadyExistsError,
    ObjectNotFoundError,
    ObjectStorage,
    StorageNotConfiguredError,
)

_sdk = None


def _load_sdk():
    # not in requirements yet, so only import it if this backend is picked
    global _sdk
    if _sdk is None:
        try:
            from azure.core import exceptions
            from azure.storage import blob
        except ImportError as exc:
            raise StorageNotConfiguredError(
                "azure-storage-blob is not installed. Add it to requirements.txt to use this backend."
            ) from exc
        _sdk = (blob, exceptions)
    return _sdk


class AzureBlobStorage(ObjectStorage):
    """Contract files in an Azure Blob container.

    Not run against a real account yet, there is no subscription. The container needs an
    immutability policy on it for NFR-1.
    """

    def __init__(self, connection_string: str, container: str) -> None:
        if not connection_string:
            raise StorageNotConfiguredError(
                "AZURE_STORAGE_CONNECTION_STRING is empty. Set it, or run with STORAGE_BACKEND=local."
            )
        self._connection_string = connection_string
        self._container = container
        self._service = None

    def save(self, key: str, source: BinaryIO) -> str:
        _, exceptions = _load_sdk()
        try:
            self._blob(key).upload_blob(source, overwrite=False)
        except exceptions.ResourceExistsError as exc:
            raise ObjectAlreadyExistsError(key) from exc
        return key

    def open(self, key: str) -> BinaryIO:
        _, exceptions = _load_sdk()
        # pdf parsing seeks, a download stream only goes forward
        buffer = BytesIO()
        try:
            self._blob(key).download_blob().readinto(buffer)
        except exceptions.ResourceNotFoundError as exc:
            raise ObjectNotFoundError(key) from exc
        buffer.seek(0)
        return buffer

    def exists(self, key: str) -> bool:
        return self._blob(key).exists()

    def url_for(self, key: str, expires_in: int = DEFAULT_URL_TTL_SECONDS) -> str:
        blob, _ = _load_sdk()
        client = self._blob(key)
        account_key = getattr(self._service.credential, "account_key", None)
        if not account_key:
            # managed identity needs a user delegation SAS instead
            raise StorageNotConfiguredError("Cannot sign a download URL without an account key.")
        token = blob.generate_blob_sas(
            account_name=client.account_name,
            container_name=client.container_name,
            blob_name=client.blob_name,
            account_key=account_key,
            permission=blob.BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(seconds=expires_in),
        )
        return f"{client.url}?{token}"

    def _blob(self, key: str):
        blob, _ = _load_sdk()
        if self._service is None:
            self._service = blob.BlobServiceClient.from_connection_string(self._connection_string)
        return self._service.get_container_client(self._container).get_blob_client(key)
