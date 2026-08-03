from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, Float, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)  # Link to completed booking

    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    
    # Admin moderation
    is_approved = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    admin_remark = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="reviews")
    vehicle = relationship("Vehicle", back_populates="reviews")
    booking = relationship("Booking", back_populates="review", uselist=False)
