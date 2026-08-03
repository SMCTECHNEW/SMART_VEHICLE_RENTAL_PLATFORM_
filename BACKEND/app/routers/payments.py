"""
Payments Router with Razorpay Integration
Handles payment order creation, verification, and webhook handling
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.models import User, Booking
from app.models.payment import Payment
from app.models.driver import Refund
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.core.deps import get_current_user, get_current_admin_user
from app.services.payment_service import (
    create_payment_order,
    verify_payment_signature,
    update_payment_status,
    process_refund,
    update_refund_status,
    get_payment_by_booking,
    get_refunds_by_booking
)
from app.services.notification_service import (
    send_payment_success_email,
    send_refund_email
)
import hmac
import hashlib
import json
from app.core.config import settings

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/create-order")
def create_payment(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a Razorpay payment order for a booking"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check ownership
    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    # Check if already paid
    existing_payment = get_payment_by_booking(db, booking_id)
    if existing_payment and existing_payment.status == 'completed':
        raise HTTPException(status_code=400, detail="Booking already paid")
    
    try:
        order_data = create_payment_order(
            db=db,
            booking_id=booking_id,
            amount=booking.total_amount
        )
        return order_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify")
def verify_payment(
    razorpay_payment_id: str,
    razorpay_order_id: str,
    razorpay_signature: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify Razorpay payment signature and update status"""
    # Verify signature
    is_valid = verify_payment_signature(
        razorpay_payment_id=razorpay_payment_id,
        razorpay_order_id=razorpay_order_id,
        razorpay_signature=razorpay_signature
    )
    
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid payment signature")
    
    # Find payment by order_id
    payment = db.query(Payment).filter(
        Payment.razorpay_order_id == razorpay_order_id
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found")
    
    # Check ownership
    booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    # Update payment status
    updated_payment = update_payment_status(
        db=db,
        payment_id=payment.id,
        razorpay_payment_id=razorpay_payment_id,
        razorpay_signature=razorpay_signature,
        status='completed'
    )
    
    # Send success email
    try:
        send_payment_success_email(
            user_email=booking.user.email,
            user_name=booking.user.full_name,
            booking_id=booking.id,
            amount=booking.total_amount,
            transaction_id=razorpay_payment_id
        )
    except Exception as e:
        pass
    
    return {
        "message": "Payment verified successfully",
        "payment": updated_payment
    }


@router.get("/my-payments", response_model=List[PaymentResponse])
def get_my_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all payments for current user's bookings"""
    # Get user's bookings
    user_bookings = db.query(Booking).filter(Booking.user_id == current_user.id).all()
    booking_ids = [b.id for b in user_bookings]
    
    # Get payments for those bookings
    payments = db.query(Payment).filter(Payment.booking_id.in_(booking_ids)).all()
    return payments


@router.get("/{booking_id}")
def get_booking_payment(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment details for a specific booking"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check ownership or admin
    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    payment = get_payment_by_booking(db, booking_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return payment


@router.get("/{booking_id}/refunds")
def get_booking_refunds(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all refunds for a booking"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check ownership or admin
    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    refunds = get_refunds_by_booking(db, booking_id)
    return refunds


# Admin endpoints
@router.get("/admin/all", response_model=List[PaymentResponse])
def get_all_payments(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all payments (Admin only)"""
    query = db.query(Payment)
    
    if status_filter:
        query = query.filter(Payment.status == status_filter)
    
    payments = query.order_by(Payment.created_at.desc()).all()
    return payments


@router.post("/webhook/razorpay")
async def razorpay_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Razorpay webhook events"""
    # Get the signature from headers
    signature = request.headers.get('X-Razorpay-Signature')
    
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")
    
    # Get the request body
    body = await request.body()
    
    # Verify webhook signature
    expected_signature = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
    
    # Parse the event
    event = json.loads(body.decode())
    event_type = event.get('event')
    payload = event.get('payload', {})
    
    if event_type == 'payment.captured':
        # Payment successful
        payment_data = payload.get('payment', {}).get('entity', {})
        order_id = payment_data.get('order_id')
        payment_id = payment_data.get('id')
        signature = payment_data.get('entity', {}).get('signature', '')
        
        # Find and update payment
        payment = db.query(Payment).filter(
            Payment.razorpay_order_id == order_id
        ).first()
        
        if payment:
            update_payment_status(
                db=db,
                payment_id=payment.id,
                razorpay_payment_id=payment_id,
                razorpay_signature=signature,
                status='completed'
            )
    
    elif event_type == 'refund.processed':
        # Refund processed
        refund_data = payload.get('refund', {}).get('entity', {})
        razorpay_refund_id = refund_data.get('id')
        payment_id = refund_data.get('payment_id')
        
        # Find refund record
        refund = db.query(Refund).filter(
            Refund.refund_transaction_id == razorpay_refund_id
        ).first()
        
        if refund:
            update_refund_status(
                db=db,
                refund_id=refund.id,
                status='completed'
            )
            
            # Send refund email
            booking = db.query(Booking).filter(Booking.id == refund.booking_id).first()
            if booking:
                try:
                    send_refund_email(
                        user_email=booking.user.email,
                        user_name=booking.user.full_name,
                        booking_id=booking.id,
                        refund_amount=refund.refund_amount,
                        refund_transaction_id=razorpay_refund_id,
                        status='completed'
                    )
                except Exception as e:
                    pass
    
    elif event_type == 'refund.failed':
        # Refund failed
        refund_data = payload.get('refund', {}).get('entity', {})
        razorpay_refund_id = refund_data.get('id')
        
        refund = db.query(Refund).filter(
            Refund.refund_transaction_id == razorpay_refund_id
        ).first()
        
        if refund:
            update_refund_status(
                db=db,
                refund_id=refund.id,
                status='failed'
            )
    
    return {"status": "success"}
