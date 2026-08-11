from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import current_organization_id
from app.data_access.contracts import get_contracts

router = APIRouter()


@router.get("/")
def list_contracts(
    db: Session = Depends(get_db),
    organization_id: UUID = Depends(current_organization_id),
):
    return get_contracts(db, organization_id)
