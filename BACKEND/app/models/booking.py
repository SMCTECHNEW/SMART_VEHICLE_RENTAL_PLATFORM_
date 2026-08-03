from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, Date, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)

    pickup_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime, nullable=False)

    total_amount = Column(Float, nullable=False)
    status = Column(String(30), default="pending")  # pending, confirmed, active, completed, cancelled
    
    # Cancellation fields
    cancellation_reason = Column(Text, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    refund_status = Column(String(30), default=None, nullable=True)  # pending, processing, completed, failed

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="bookings")
    vehicle = relationship("Vehicle", back_populates="bookings")
    driver = relationship("Driver", back_populates="bookings")
    payment = relationship("Payment", back_populates="booking", uselist=False)
    refunds = relationship("Refund", back_populates="booking", lazy="dynamic")
