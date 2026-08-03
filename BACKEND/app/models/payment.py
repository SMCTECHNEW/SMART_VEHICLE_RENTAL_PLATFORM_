from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    
    # Razorpay specific fields
    razorpay_order_id = Column(String(150), nullable=True)
    razorpay_payment_id = Column(String(150), nullable=True)
    razorpay_signature = Column(String(255), nullable=True)

    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)  # razorpay, stripe, cash
    transaction_id = Column(String(150), nullable=True)

    status = Column(String(30), default="pending")  # pending, success, failed, refunded
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    booking = relationship("Booking", back_populates="payment")
