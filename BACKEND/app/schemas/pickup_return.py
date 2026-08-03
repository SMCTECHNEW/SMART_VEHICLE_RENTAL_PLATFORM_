from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PickupReturnCreate(BaseModel):
    booking_id: int
    pickup_location: str | None = None
    return_location: str | None = None
    pickup_time: datetime | None = None
    return_time: datetime | None = None
    pickup_notes: str | None = None
    return_notes: str | None = None


class PickupReturnResponse(PickupReturnCreate):
    id: int
    status: str

    model_config = ConfigDict(from_attributes=True)
