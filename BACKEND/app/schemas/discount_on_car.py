from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DiscountCreate(BaseModel):
    vehicle_id: int
    title: str
    percentage: float
    start_date: datetime | None = None
    end_date: datetime | None = None


class DiscountResponse(DiscountCreate):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
