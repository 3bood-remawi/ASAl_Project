from uuid import UUID

from sqlalchemy.orm import Session

from app.models.contract import Contract


def get_contracts(
    db: Session,
    organization_id: UUID,
) -> list[Contract]:
    return (
        db.query(Contract)
        .filter(Contract.organization_id == organization_id)
        .all()
    )


def get_contract_by_id(
    db: Session,
    organization_id: UUID,
    contract_id: UUID,
) -> Contract | None:
    return (
        db.query(Contract)
        .filter(
            Contract.organization_id == organization_id,
            Contract.id == contract_id,
        )
        .one_or_none()
    )
