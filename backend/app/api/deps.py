from typing import Any
from uuid import UUID

from fastapi import Depends, HTTPException, status

from app.core.dependencies import current_organization_id
from app.data_access.contracts import get_editor


# stand-in until auth lands, picks the Editor created by scripts/seed.py
def get_current_user(organization_id: UUID = Depends(current_organization_id)) -> dict[str, Any]:
    user = get_editor(str(organization_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No Editor in the database. Run scripts/seed.py first.",
        )
    return user
