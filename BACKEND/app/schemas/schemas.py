from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    role: str
    loyalty_points: int
    is_new_user: bool

    class Config:
        from_attributes = True


class VehicleBase(BaseModel):
    name: str
    brand: str
    model: str
    vehicle_type: str = "car"
    price_per_day: float
    seats: int = 4
    transmission: str = "Manual"
    fuel_type: str = "Petrol"
    image_url: Optional[str] = None
    description: Optional[str] = None
    has_driver_option: bool = False
    driver_charge_per_day: float = 500.0


class VehicleCreate(VehicleBase):
    pass


class VehicleResponse(VehicleBase):
    id: int
    is_available: bool

    class Config:
        from_attributes = True


class BookingBase(BaseModel):
    vehicle_id: int
    start_date: datetime
    end_date: datetime
    driver_required: bool = False
    coupon_code: Optional[str] = None


class BookingCreate(BookingBase):
    pass


class BookingResponse(BaseModel):
    id: int
    user_id: int
    vehicle_id: int
    start_date: datetime
    end_date: datetime
    total_days: int
    base_price: float
    driver_required: bool
    driver_charge: float
    discount_amount: float
    final_amount: float
    status: str
    coupon_code: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewBase(BaseModel):
    vehicle_id: int
    booking_id: Optional[int] = None
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    driver_rating: Optional[int] = Field(ge=1, le=5, default=None)
    driver_comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    pass


class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CouponBase(BaseModel):
    code: str
    discount_percentage: float
    max_discount: Optional[float] = None
    min_booking_amount: float = 0.0
    is_active: bool = True
    usage_limit: Optional[int] = None
    for_new_users_only: bool = False
    valid_until: Optional[datetime] = None


class CouponCreate(CouponBase):
    pass


class CouponResponse(CouponBase):
    id: int
    used_count: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class PaymentRequest(BaseModel):
    booking_id: int
    amount: float


class PaymentVerification(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str


class ChatbotMessage(BaseModel):
    message: str
    user_id: Optional[int] = None
