from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BookingCreate(BaseModel):
    vehicle_id: int
    pickup_date: datetime
    return_date: datetime


class BookingResponse(BaseModel):
    id: int
    user_id: int
    vehicle_id: int
    pickup_date: datetime
    return_date: datetime
    total_amount: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
