from datetime import datetime
from sqlalchemy import Column, DateTime, Float, Integer, String, Boolean, Date
from sqlalchemy.orm import relationship
from app.core.database import Base


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False)
    discount_percentage = Column(Float, nullable=False)
    max_discount = Column(Float, nullable=True)
    min_booking_amount = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    usage_limit = Column(Integer, nullable=True)
    used_count = Column(Integer, default=0)
    valid_until = Column(Date, nullable=True)
    for_new_users_only = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
