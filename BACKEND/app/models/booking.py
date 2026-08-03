from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from app.core.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)

    pickup_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime, nullable=False)

    total_amount = Column(Float, nullable=False)
    status = Column(String(30), default="pending")

    created_at = Column(DateTime, default=datetime.utcnow)
