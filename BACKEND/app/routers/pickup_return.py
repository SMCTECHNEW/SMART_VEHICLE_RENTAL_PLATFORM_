from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.pickup_return import PickupReturn
from app.schemas.pickup_return import PickupReturnCreate, PickupReturnResponse

router = APIRouter(prefix="/pickup-return", tags=["Pickup & Return"])


@router.post("/", response_model=PickupReturnResponse)
def create_pickup_return(
    data: PickupReturnCreate,
    db: Session = Depends(get_db)
):
    record = PickupReturn(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/", response_model=list[PickupReturnResponse])
def get_pickup_returns(db: Session = Depends(get_db)):
    return db.query(PickupReturn).all()
