"""
Payment Service with Razorpay Integration
Handles payment creation, verification, and refund processing
"""
import razorpay
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.payment import Payment
from app.models.booking import Booking
from app.models.driver import Refund
from app.core.config import settings


# Initialize Razorpay client
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


def create_payment_order(db: Session, booking_id: int, amount: float) -> Dict[str, Any]:
    """Create a Razorpay payment order"""
    try:
        # Create Razorpay order
        order_data = {
            'amount': int(amount * 100),  # Amount in paise
            'currency': 'INR',
            'receipt': f'booking_{booking_id}_{datetime.utcnow().timestamp()}',
            'payment_capture': 1
        }
        
        order = razorpay_client.order.create(data=order_data)
        
        # Create pending payment record
        payment = Payment(
            booking_id=booking_id,
            amount=amount,
            payment_method='razorpay',
            razorpay_order_id=order['id'],
            status='pending'
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        return {
            'order_id': order['id'],
            'amount': amount,
            'currency': 'INR',
            'payment_id': payment.id,
            'key_id': settings.RAZORPAY_KEY_ID
        }
        
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to create payment order: {str(e)}")


def verify_payment_signature(
    razorpay_payment_id: str,
    razorpay_order_id: str,
    razorpay_signature: str
) -> bool:
    """Verify Razorpay payment signature"""
    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_order_id': razorpay_order_id,
            'razorpay_signature': razorpay_signature
        })
        return True
    except Exception as e:
        return False


def update_payment_status(
    db: Session,
    payment_id: int,
    razorpay_payment_id: str,
    razorpay_signature: str,
    status: str = 'completed'
) -> Payment:
    """Update payment status after verification"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise ValueError("Payment not found")
    
    payment.razorpay_payment_id = razorpay_payment_id
    payment.razorpay_signature = razorpay_signature
    payment.status = status
    payment.paid_at = datetime.utcnow()
    payment.transaction_id = razorpay_payment_id
    
    # Update booking status if payment is successful
    if status == 'completed':
        booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
        if booking and booking.status == 'pending':
            booking.status = 'confirmed'
    
    db.commit()
    db.refresh(payment)
    return payment


def process_refund(
    db: Session,
    booking_id: int,
    refund_amount: float,
    refund_reason: str,
    speed: str = 'normal'
) -> Dict[str, Any]:
    """
    Process refund through Razorpay
    speed: 'normal' (5-7 days) or 'instant' (within 30 mins)
    """
    try:
        # Get the payment for this booking
        payment = db.query(Payment).filter(
            Payment.booking_id == booking_id,
            Payment.status == 'completed'
        ).first()
        
        if not payment or not payment.razorpay_payment_id:
            raise ValueError("No completed payment found for this booking")
        
        # Check if refund already exists
        existing_refund = db.query(Refund).filter(
            Refund.booking_id == booking_id,
            Refund.refund_status.in_(['pending', 'processing'])
        ).first()
        
        if existing_refund:
            raise ValueError("Refund already in progress")
        
        # Create refund in Razorpay
        razorpay_refund = razorpay_client.payment.refund(
            payment.razorpay_payment_id,
            {
                'amount': int(refund_amount * 100),
                'speed': speed,
                'notes': {
                    'reason': refund_reason,
                    'booking_id': str(booking_id)
                }
            }
        )
        
        # Create refund record in database
        refund = Refund(
            booking_id=booking_id,
            payment_id=payment.id,
            refund_amount=refund_amount,
            refund_reason=refund_reason,
            refund_status='processing',
            refund_transaction_id=razorpay_refund.get('id'),
            initiated_at=datetime.utcnow()
        )
        
        db.add(refund)
        
        # Update booking refund status
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if booking:
            booking.refund_status = 'processing'
        
        db.commit()
        db.refresh(refund)
        
        return {
            'refund_id': refund.id,
            'razorpay_refund_id': razorpay_refund.get('id'),
            'amount': refund_amount,
            'status': 'processing'
        }
        
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to process refund: {str(e)}")


def update_refund_status(
    db: Session,
    refund_id: int,
    status: str,
    razorpay_refund_id: Optional[str] = None
) -> Refund:
    """Update refund status (called via webhook or manual check)"""
    refund = db.query(Refund).filter(Refund.id == refund_id).first()
    
    if not refund:
        raise ValueError("Refund not found")
    
    refund.refund_status = status
    
    if status == 'completed':
        refund.completed_at = datetime.utcnow()
        
        # Update booking refund status
        booking = db.query(Booking).filter(Booking.id == refund.booking_id).first()
        if booking:
            booking.refund_status = 'completed'
            
        # Update payment status
        payment = db.query(Payment).filter(Payment.id == refund.payment_id).first()
        if payment:
            payment.status = 'refunded'
    
    elif status == 'failed':
        booking = db.query(Booking).filter(Booking.id == refund.booking_id).first()
        if booking:
            booking.refund_status = 'failed'
    
    db.commit()
    db.refresh(refund)
    return refund


def get_payment_by_booking(db: Session, booking_id: int) -> Optional[Payment]:
    """Get payment for a booking"""
    return db.query(Payment).filter(Payment.booking_id == booking_id).first()


def get_refunds_by_booking(db: Session, booking_id: int):
    """Get all refunds for a booking"""
    return db.query(Refund).filter(Refund.booking_id == booking_id).all()
