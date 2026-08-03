from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from app.core.database import Base


class PickupReturn(Base):
    __tablename__ = "pickup_returns"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)

    pickup_location = Column(String(255), nullable=True)
    return_location = Column(String(255), nullable=True)

    pickup_time = Column(DateTime, nullable=True)
    return_time = Column(DateTime, nullable=True)

    pickup_notes = Column(Text, nullable=True)
    return_notes = Column(Text, nullable=True)

    status = Column(String(30), default="pending")
