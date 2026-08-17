from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.documents.enums import ContractStatus, ProcessingStatus


class ContractListItem(BaseModel):
    id: str
    name: str
    status: ContractStatus
    page_count: int | None
    uploaded_at: datetime | None


class AppliedFilters(BaseModel):
    name: str | None = None
    status: str | None = None
    contract_type: str | None = None
    language: str | None = None
    uploaded_by: str | None = None
    uploaded_after: str | None = None
    uploaded_before: str | None = None
    sort_by: str
    sort_order: str


class ContractListResponse(BaseModel):
    items: list[ContractListItem]
    page: int
    page_size: int
    total_items: int
    applied_filters: AppliedFilters


class FilterValuesResponse(BaseModel):
    statuses: list[str]
    contract_types: list[str]


class ContractVersionResponse(BaseModel):
    version_number: int
    uploaded_by: str
    uploaded_at: datetime
    file_name: str
    file_size_bytes: int | None
    page_count: int | None
    processing_status: ProcessingStatus


class ContractDetailResponse(BaseModel):
    id: UUID
    name: str
    status: ContractStatus
    current_version: ContractVersionResponse


class ContractTextChunkResponse(BaseModel):
    page_number: int | None
    chunk_order: int
    text: str


class ContractTextResponse(BaseModel):
    contract_id: UUID
    version_number: int
    page: int
    page_size: int
    total_items: int
    total_pages: int
    items: list[ContractTextChunkResponse]