from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List


class VehicleImageBase(BaseModel):
    image_url: str
    is_primary: bool = False
    display_order: int = 0


class VehicleImageCreate(VehicleImageBase):
    pass


class VehicleImageResponse(VehicleImageBase):
    id: int
    vehicle_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class VehicleCreate(BaseModel):
    category_id: int
    brand: str
    model: str
    registration_number: str
    year: Optional[int] = None
    color: Optional[str] = None
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    seats: Optional[int] = 4
    price_per_day: float
    image_url: Optional[str] = None
    location: Optional[str] = None


class VehicleUpdate(BaseModel):
    category_id: Optional[int] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    price_per_day: Optional[float] = None
    image_url: Optional[str] = None
    status: Optional[str] = None
    location: Optional[str] = None
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    seats: Optional[int] = None
    is_active: Optional[bool] = None


class VehicleResponse(VehicleCreate):
    id: int
    status: str
    is_active: bool
    rating: float = 0.0
    total_reviews: int = 0
    created_at: datetime
    updated_at: datetime
    images: List[VehicleImageResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class VehicleFilterParams(BaseModel):
    """Parameters for filtering, searching and sorting vehicles"""
    search: Optional[str] = None
    brand: Optional[str] = None
    vehicle_type: Optional[str] = None  # Car/Bike from category
    category_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    seats: Optional[int] = None
    min_rating: Optional[float] = None
    available_from: Optional[datetime] = None
    available_to: Optional[datetime] = None
    
    # Sorting
    sort_by: Optional[str] = None  # price, rating, newest, popular
    sort_order: Optional[str] = None  # asc, desc
    
    # Pagination
    page: int = 1
    page_size: int = 10
