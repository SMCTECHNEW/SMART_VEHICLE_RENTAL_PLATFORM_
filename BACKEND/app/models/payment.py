from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from app.core.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)

    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)
    transaction_id = Column(String(150), nullable=True)

    status = Column(String(30), default="pending")
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
