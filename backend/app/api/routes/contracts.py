from typing import Any
from uuid import UUID

from azure.cosmos import exceptions
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile, status

from app.api.deps import get_current_user
from app.core.dependencies import current_organization_id
from app.data_access.contracts import (
    get_contracts_page_with_versions,
    get_distinct_contract_types,
    get_distinct_statuses,
    get_version_by_hash,
)
from app.schemas.contracts import AppliedFilters, ContractListItem, ContractListResponse, FilterValuesResponse
from app.schemas.upload import DuplicateContract, UploadAccepted
from app.services.processing import process_version
from app.services.upload import UploadRejected, inspect_upload, store_upload

router = APIRouter()


@router.get("/", response_model=ContractListResponse)
def list_contracts(
    organization_id: UUID = Depends(current_organization_id),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    name: str | None = None,
    status: str | None = None,
    sort_by: str = "uploaded_date",
    sort_order: str = "desc",
    contract_type: str | None = None,
    language: str | None = None,
    uploaded_by: str | None = None,
    uploaded_after: str | None = None,
    uploaded_before: str | None = None,
):
    offset = (page - 1) * page_size
    contracts, versions_by_contract, total_items = get_contracts_page_with_versions(
        str(organization_id), offset, page_size, name, status, sort_by, sort_order,
        contract_type, language, uploaded_by, uploaded_after, uploaded_before,
    )
    items = []
    for contract in contracts:
        current_version = versions_by_contract.get(contract["id"])
        items.append(
            ContractListItem(
                id=contract["id"],
                name=contract["name"],
                status=contract["status"],
                page_count=current_version["pageCount"] if current_version else None,
                uploaded_at=current_version["uploadedAt"] if current_version else None,
            )
        )
    return ContractListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total_items=total_items,
        applied_filters=AppliedFilters(
            name=name,
            status=status,
            contract_type=contract_type,
            language=language,
            uploaded_by=uploaded_by,
            uploaded_after=uploaded_after,
            uploaded_before=uploaded_before,
            sort_by=sort_by,
            sort_order=sort_order,
        ),
    )

@router.post("/", response_model=UploadAccepted, status_code=status.HTTP_201_CREATED)
def upload_contract(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    user: dict[str, Any] = Depends(get_current_user),
):
    try:
        file_hash, size = inspect_upload(file)
    except UploadRejected as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from None

    organization_id = user["organizationId"]
    existing = get_version_by_hash(organization_id, file_hash)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=_duplicate_of(existing))

    try:
        contract, version, job = store_upload(user, file, file_hash, size)
    except UploadRejected as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from None
    except exceptions.CosmosBatchOperationError:
        # someone stored the same file while we were checking
        existing = get_version_by_hash(organization_id, file_hash)
        if existing is None:
            raise
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=_duplicate_of(existing)) from None

    # runs after this response is sent, the user is not kept waiting
    background.add_task(process_version, organization_id, version.id)

    return UploadAccepted(
        contract_id=contract.id,
        version_id=version.id,
        job_id=job.id,
        status=contract.status.value,
        file_name=version.file_name,
        file_size_bytes=version.file_size_bytes,
    )


def _duplicate_of(version: dict[str, Any]) -> dict[str, Any]:
    return DuplicateContract(
        message="This file has already been uploaded",
        contract_id=version["contractId"],
        version_id=version["id"],
    ).model_dump(mode="json")


@router.get("/filter-values", response_model=FilterValuesResponse)
def get_filter_values(organization_id: UUID = Depends(current_organization_id)):
    return FilterValuesResponse(
        statuses=get_distinct_statuses(str(organization_id)),
        contract_types=get_distinct_contract_types(str(organization_id)),
    )
