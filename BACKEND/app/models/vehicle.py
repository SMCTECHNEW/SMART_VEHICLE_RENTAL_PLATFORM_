from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("vehicle_categories.id"), nullable=False)

    brand = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    registration_number = Column(String(50), unique=True, nullable=False)
    year = Column(Integer, nullable=True)
    color = Column(String(50), nullable=True)
    fuel_type = Column(String(50), nullable=True)
    transmission = Column(String(50), nullable=True)
    seats = Column(Integer, nullable=True, default=4)

    price_per_day = Column(Float, nullable=False)
    image_url = Column(String(500), nullable=True)

    status = Column(String(30), default="available")
    location = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)

    # Ratings
    rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    images = relationship("VehicleImage", back_populates="vehicle", cascade="all, delete-orphan", lazy="selectin")
    bookings = relationship("Booking", back_populates="vehicle", lazy="dynamic")
    reviews = relationship("Review", back_populates="vehicle", lazy="dynamic")
