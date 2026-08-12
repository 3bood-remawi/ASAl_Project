from datetime import datetime

from pydantic import BaseModel

from app.documents.enums import ContractStatus


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