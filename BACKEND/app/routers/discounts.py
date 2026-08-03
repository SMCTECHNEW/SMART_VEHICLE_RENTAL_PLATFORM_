from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.discount_on_car import DiscountOnCar
from app.schemas.discount_on_car import DiscountCreate, DiscountResponse

router = APIRouter(prefix="/discounts", tags=["Vehicle Discounts"])


@router.post("/", response_model=DiscountResponse)
def create_discount(
    data: DiscountCreate,
    db: Session = Depends(get_db)
):
    discount = DiscountOnCar(**data.model_dump())
    db.add(discount)
    db.commit()
    db.refresh(discount)
    return discount


@router.get("/", response_model=list[DiscountResponse])
def get_discounts(db: Session = Depends(get_db)):
    return db.query(DiscountOnCar).filter(
        DiscountOnCar.is_active == True
    ).all()
