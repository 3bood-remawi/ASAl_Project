from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.contract import Contract

router = APIRouter()


@router.get("/")
def list_contracts(db: Session = Depends(get_db)):
    return db.query(Contract).all()
