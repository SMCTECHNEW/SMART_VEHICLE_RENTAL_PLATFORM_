from datetime import datetime
from sqlalchemy.orm import Session
from app.models.payment import Payment


def create_payment(db: Session, data):
    payment = Payment(
        booking_id=data.booking_id,
        amount=data.amount,
        payment_method=data.payment_method,
        transaction_id=data.transaction_id,
        status="completed",
        paid_at=datetime.utcnow()
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment
