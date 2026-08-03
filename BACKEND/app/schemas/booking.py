from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class BookingCreate(BaseModel):
    vehicle_id: int
    pickup_date: datetime
    return_date: datetime
    driver_required: bool = False


class BookingUpdate(BaseModel):
    status: Optional[str] = None
    driver_id: Optional[int] = None
    cancellation_reason: Optional[str] = None


class BookingResponse(BaseModel):
    id: int
    user_id: int
    vehicle_id: int
    driver_id: Optional[int] = None
    pickup_date: datetime
    return_date: datetime
    total_amount: float
    status: str
    cancellation_reason: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    refund_status: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class BookingHistoryResponse(BookingResponse):
    """Extended booking response with related data"""
    vehicle_brand: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_image: Optional[str] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    payment_status: Optional[str] = None
