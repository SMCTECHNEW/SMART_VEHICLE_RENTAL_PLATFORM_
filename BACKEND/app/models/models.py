from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String)
    role = Column(String, default="user")
    is_new_user = Column(Boolean, default=True)
    loyalty_points = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    bookings = relationship("Booking", back_populates="user")
    reviews = relationship("Review", back_populates="user")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    vehicle_type = Column(String, default="car")
    price_per_day = Column(Float, nullable=False)
    seats = Column(Integer, default=4)
    transmission = Column(String, default="Manual")
    fuel_type = Column(String, default="Petrol")
    image_url = Column(String)
    description = Column(Text)
    is_available = Column(Boolean, default=True)
    has_driver_option = Column(Boolean, default=False)
    driver_charge_per_day = Column(Float, default=500.0)

    bookings = relationship("Booking", back_populates="vehicle")
    reviews = relationship("Review", back_populates="vehicle")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    total_days = Column(Integer, nullable=False)
    base_price = Column(Float, nullable=False)
    driver_required = Column(Boolean, default=False)
    driver_charge = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    final_amount = Column(Float, nullable=False)
    status = Column(String, default="pending")
    payment_id = Column(String)
    razorpay_order_id = Column(String)
    razorpay_signature = Column(String)
    coupon_code = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bookings")
    vehicle = relationship("Vehicle", back_populates="bookings")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    driver_rating = Column(Integer)
    driver_comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reviews")
    vehicle = relationship("Vehicle", back_populates="reviews")


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    discount_percentage = Column(Float, nullable=False)
    max_discount = Column(Float)
    min_booking_amount = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    usage_limit = Column(Integer)
    used_count = Column(Integer, default=0)
    valid_until = Column(DateTime)
    for_new_users_only = Column(Boolean, default=False)
