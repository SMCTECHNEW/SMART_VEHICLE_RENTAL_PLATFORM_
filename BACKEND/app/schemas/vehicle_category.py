from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    name: str
    description: str | None = None


class CategoryResponse(CategoryCreate):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
