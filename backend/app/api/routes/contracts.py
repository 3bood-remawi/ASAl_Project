from datetime import datetime, timezone
from math import ceil
from typing import Any
from uuid import UUID

from azure.cosmos import exceptions
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)

from app.api.deps import get_current_user
from app.core.dependencies import current_organization_id
from app.data_access.contracts import (
    get_contract_by_id,
    get_contracts_page_with_versions,
    get_current_version_for_contract,
    get_current_version_job,
    get_distinct_contract_types,
    get_distinct_statuses,
    get_paginated_text_chunks,
    get_user_by_id,
    get_version_by_hash,
)
from app.schemas.ask import AskRequest, AskResponse
from app.schemas.contracts import (
    AppliedFilters,
    ContractDetailResponse,
    ContractListItem,
    ContractListResponse,
    ContractTextChunkResponse,
    ContractTextResponse,
    ContractVersionResponse,
    FilterValuesResponse,
)
from app.schemas.jobs import UploadStatus
from app.schemas.upload import DuplicateContract, UploadAccepted
from app.services.ask import ContractNotReadyError, ask_contract
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
    contracts, versions_by_contract, total_items = (
        get_contracts_page_with_versions(
            str(organization_id),
            offset,
            page_size,
            name,
            status,
            sort_by,
            sort_order,
            contract_type,
            language,
            uploaded_by,
            uploaded_after,
            uploaded_before,
        )
    )

    items = []
    for contract in contracts:
        current_version = versions_by_contract.get(contract["id"])
        items.append(
            ContractListItem(
                id=contract["id"],
                name=contract["name"],
                status=contract["status"],
                page_count=(
                    current_version["pageCount"]
                    if current_version
                    else None
                ),
                uploaded_at=(
                    current_version["uploadedAt"]
                    if current_version
                    else None
                ),
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


@router.post(
    "/",
    response_model=UploadAccepted,
    status_code=status.HTTP_201_CREATED,
)
def upload_contract(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    user: dict[str, Any] = Depends(get_current_user),
):
    try:
        file_hash, size = inspect_upload(file)
    except UploadRejected as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
        ) from None

    organization_id = user["organizationId"]
    existing = get_version_by_hash(organization_id, file_hash)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_duplicate_of(existing),
        )

    try:
        contract, version, job = store_upload(
            user,
            file,
            file_hash,
            size,
        )
    except UploadRejected as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
        ) from None
    except exceptions.CosmosBatchOperationError:
        existing = get_version_by_hash(organization_id, file_hash)
        if existing is None:
            raise

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_duplicate_of(existing),
        ) from None

    background.add_task(
        process_version,
        organization_id,
        version.id,
    )

    return UploadAccepted(
        contract_id=contract.id,
        version_id=version.id,
        job_id=job.id,
        status=contract.status.value,
        file_name=version.file_name,
        file_size_bytes=version.file_size_bytes,
    )


@router.get(
    "/{contract_id}/status",
    response_model=UploadStatus,
)
def contract_status(
    contract_id: UUID,
    organization_id: UUID = Depends(current_organization_id),
):
    organization = str(organization_id)

    if get_contract_by_id(organization, str(contract_id)) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )

    job = get_current_version_job(
        organization,
        str(contract_id),
    )
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This contract has no processing job yet",
        )

    return UploadStatus(
        job_id=job["id"],
        version_id=job["versionId"],
        stage=job["stage"],
        status=job["status"],
        error_message=job.get("errorMessage"),
        last_changed_at=datetime.fromtimestamp(
            job["_ts"],
            tz=timezone.utc,
        ),
    )


def _duplicate_of(version: dict[str, Any]) -> dict[str, Any]:
    return DuplicateContract(
        message="This file has already been uploaded",
        contract_id=version["contractId"],
        version_id=version["id"],
    ).model_dump(mode="json")


@router.post(
    "/{contract_id}/ask",
    response_model=AskResponse,
)
def ask(
    contract_id: str,
    payload: AskRequest,
    organization_id: UUID = Depends(current_organization_id),
):
    contract = get_contract_by_id(
        str(organization_id),
        contract_id,
    )
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )

    try:
        return ask_contract(
            str(organization_id),
            contract_id,
            payload.question,
        )
    except ContractNotReadyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This contract has not finished processing yet.",
        ) from None


@router.get(
    "/filter-values",
    response_model=FilterValuesResponse,
)
def get_filter_values(
    organization_id: UUID = Depends(current_organization_id),
):
    return FilterValuesResponse(
        statuses=get_distinct_statuses(str(organization_id)),
        contract_types=get_distinct_contract_types(
            str(organization_id)
        ),
    )


def _get_contract_and_current_version(
    organization_id: str,
    contract_id: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = get_contract_by_id(
        organization_id,
        contract_id,
    )
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )

    current_version = get_current_version_for_contract(
        organization_id,
        contract_id,
    )
    if current_version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Current contract version not found",
        )

    return contract, current_version


@router.get(
    "/{contract_id}",
    response_model=ContractDetailResponse,
)
def get_contract_detail(
    contract_id: UUID,
    organization_id: UUID = Depends(current_organization_id),
):
    organization_id_string = str(organization_id)
    contract, current_version = _get_contract_and_current_version(
        organization_id_string,
        str(contract_id),
    )

    uploader = get_user_by_id(
        organization_id_string,
        current_version["uploadedBy"],
    )
    uploaded_by = (
        uploader["fullName"]
        if uploader is not None
        else current_version["uploadedBy"]
    )

    return ContractDetailResponse(
        id=contract["id"],
        name=contract["name"],
        status=contract["status"],
        current_version=ContractVersionResponse(
            version_number=current_version["versionNumber"],
            uploaded_by=uploaded_by,
            uploaded_at=current_version["uploadedAt"],
            file_name=current_version["fileName"],
            file_size_bytes=current_version.get("fileSizeBytes"),
            page_count=current_version.get("pageCount"),
            processing_status=current_version["processingStatus"],
        ),
    )


@router.get(
    "/{contract_id}/text",
    response_model=ContractTextResponse,
)
def get_contract_text(
    contract_id: UUID,
    organization_id: UUID = Depends(current_organization_id),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    organization_id_string = str(organization_id)
    _, current_version = _get_contract_and_current_version(
        organization_id_string,
        str(contract_id),
    )

    total_items, chunks = get_paginated_text_chunks(
        organization_id_string,
        current_version["id"],
        page,
        page_size,
    )

    return ContractTextResponse(
        contract_id=contract_id,
        version_number=current_version["versionNumber"],
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=(
            ceil(total_items / page_size)
            if total_items
            else 0
        ),
        items=[
            ContractTextChunkResponse(
                page_number=chunk.get("pageNumber"),
                chunk_order=chunk["chunkOrder"],
                text=chunk["text"],
            )
            for chunk in chunks
        ],
    )