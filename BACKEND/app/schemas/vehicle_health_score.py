from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class HealthScoreCreate(BaseModel):
    vehicle_id: int
    score: int = Field(..., ge=0, le=100)
    condition: str
    notes: str | None = None


class HealthScoreResponse(HealthScoreCreate):
    id: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
