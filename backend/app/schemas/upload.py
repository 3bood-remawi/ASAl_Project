from uuid import UUID

from pydantic import BaseModel


class UploadAccepted(BaseModel):
    contract_id: UUID
    version_id: UUID
    job_id: UUID
    status: str
    file_name: str
    file_size_bytes: int


class DuplicateContract(BaseModel):
    message: str
    contract_id: UUID
    version_id: UUID
