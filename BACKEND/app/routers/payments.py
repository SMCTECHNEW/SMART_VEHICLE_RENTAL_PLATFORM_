from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services.payment_service import create_payment

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/", response_model=PaymentResponse)
def make_payment(data: PaymentCreate, db: Session = Depends(get_db)):
    return create_payment(db, data)


@router.get("/", response_model=list[PaymentResponse])
def get_payments(db: Session = Depends(get_db)):
    return db.query(Payment).all()
