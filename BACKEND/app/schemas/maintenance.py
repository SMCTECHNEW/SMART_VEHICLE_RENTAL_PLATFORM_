from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MaintenanceCreate(BaseModel):
    vehicle_id: int
    title: str
    description: str | None = None
    cost: float = 0
    scheduled_date: datetime | None = None


class MaintenanceResponse(MaintenanceCreate):
    id: int
    status: str
    completed_date: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
