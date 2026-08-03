from pydantic import BaseModel, ConfigDict


class AdminCreate(BaseModel):
    user_id: int
    department: str | None = None
    permissions: str | None = None


class AdminResponse(AdminCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
