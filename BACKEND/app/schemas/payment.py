from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PaymentCreate(BaseModel):
    booking_id: int
    amount: float
    payment_method: str
    transaction_id: str | None = None


class PaymentResponse(PaymentCreate):
    id: int
    status: str
    paid_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
