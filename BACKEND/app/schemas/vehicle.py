from pydantic import BaseModel, ConfigDict


class VehicleCreate(BaseModel):
    category_id: int
    brand: str
    model: str
    registration_number: str
    year: int | None = None
    color: str | None = None
    fuel_type: str | None = None
    transmission: str | None = None
    price_per_day: float
    image_url: str | None = None
    location: str | None = None


class VehicleUpdate(BaseModel):
    category_id: int | None = None
    brand: str | None = None
    model: str | None = None
    price_per_day: float | None = None
    image_url: str | None = None
    status: str | None = None
    location: str | None = None


class VehicleResponse(VehicleCreate):
    id: int
    status: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
