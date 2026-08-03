"""
Bookings Router - Complete booking management with cancellation, payments, and history
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.models.models import User, Booking, Vehicle
from app.models.driver import Refund
from app.schemas.booking import BookingCreate, BookingResponse, BookingHistoryResponse
from app.schemas.schemas import DriverResponse
from app.core.deps import get_current_user, get_current_admin_user
from app.services.booking_service import BookingService
from app.services.payment_service import (
    create_payment_order,
    verify_payment_signature,
    update_payment_status,
    process_refund,
    get_payment_by_booking,
    get_refunds_by_booking
)
from app.services.notification_service import (
    send_booking_confirmation_email,
    send_booking_cancellation_email,
    send_payment_success_email,
    send_driver_assignment_email
)
from pydantic import BaseModel

router = APIRouter(prefix="/bookings", tags=["Bookings"])


class PaymentVerificationRequest(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str


class CancellationRequest(BaseModel):
    reason: str


class DriverAssignmentRequest(BaseModel):
    driver_id: int


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new booking with availability check"""
    try:
        booking = BookingService.create_booking(
            db=db,
            user_id=current_user.id,
            data=data
        )
        
        # Send confirmation email
        try:
            send_booking_confirmation_email(
                user_email=current_user.email,
                user_name=current_user.full_name,
                booking_id=booking.id,
                vehicle_name=f"{booking.vehicle.brand} {booking.vehicle.model}",
                pickup_date=booking.pickup_date.strftime("%Y-%m-%d %H:%M"),
                return_date=booking.return_date.strftime("%Y-%m-%d %H:%M"),
                total_amount=booking.total_amount
            )
        except Exception as e:
            pass  # Don't fail booking if email fails
        
        return booking
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history")
def get_booking_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complete booking history categorized by status"""
    history = BookingService.get_booking_history(db=db, user_id=current_user.id)
    return history


@router.get("/my-bookings", response_model=List[BookingResponse])
def my_bookings(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all bookings for current user with optional status filter"""
    bookings = BookingService.get_user_bookings(
        db=db,
        user_id=current_user.id,
        status=status_filter
    )
    return bookings


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get booking details by ID"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check ownership or admin
    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    return booking


@router.post("/{booking_id}/payment/create-order")
def create_booking_payment_order(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Razorpay payment order for a booking"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check ownership
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    # Check if already paid
    existing_payment = get_payment_by_booking(db, booking_id)
    if existing_payment and existing_payment.status == 'completed':
        raise HTTPException(status_code=400, detail="Booking already paid")
    
    # Re-check availability before payment
    availability = BookingService.check_availability(
        db=db,
        vehicle_id=booking.vehicle_id,
        pickup_date=booking.pickup_date,
        return_date=booking.return_date,
        exclude_booking_id=booking_id
    )
    
    if not availability["available"]:
        raise HTTPException(status_code=400, detail="Vehicle no longer available")
    
    try:
        order_data = create_payment_order(
            db=db,
            booking_id=booking_id,
            amount=booking.total_amount
        )
        return order_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{booking_id}/payment/verify")
def verify_booking_payment(
    booking_id: int,
    verification: PaymentVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify Razorpay payment signature and update booking status"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check ownership
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    # Get payment record
    payment = get_payment_by_booking(db, booking_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found")
    
    # Verify signature
    is_valid = verify_payment_signature(
        razorpay_payment_id=verification.razorpay_payment_id,
        razorpay_order_id=verification.razorpay_order_id,
        razorpay_signature=verification.razorpay_signature
    )
    
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid payment signature")
    
    # Update payment status
    updated_payment = update_payment_status(
        db=db,
        payment_id=payment.id,
        razorpay_payment_id=verification.razorpay_payment_id,
        razorpay_signature=verification.razorpay_signature,
        status='completed'
    )
    
    # Send payment success email
    try:
        send_payment_success_email(
            user_email=current_user.email,
            user_name=current_user.full_name,
            booking_id=booking_id,
            amount=booking.total_amount,
            transaction_id=verification.razorpay_payment_id
        )
    except Exception as e:
        pass
    
    return {
        "message": "Payment verified successfully",
        "payment": updated_payment,
        "booking_status": booking.status
    }


@router.post("/{booking_id}/cancel")
def cancel_booking(
    booking_id: int,
    cancellation: CancellationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a booking with refund processing"""
    try:
        result = BookingService.cancel_booking(
            db=db,
            booking_id=booking_id,
            user_id=current_user.id,
            cancellation_reason=cancellation.reason,
            is_admin=(current_user.role == "admin")
        )
        
        booking = result["booking"]
        refund_amount = result["refund_amount"]
        refund_percentage = result["refund_percentage"]
        
        # Process refund if applicable
        refund_info = None
        if refund_amount > 0:
            # Check if payment was completed
            payment = get_payment_by_booking(db, booking_id)
            if payment and payment.status == 'completed':
                try:
                    refund_info = process_refund(
                        db=db,
                        booking_id=booking_id,
                        refund_amount=refund_amount,
                        refund_reason=cancellation.reason
                    )
                except Exception as e:
                    # Log error but don't fail cancellation
                    pass
        
        # Send cancellation email
        try:
            send_booking_cancellation_email(
                user_email=current_user.email,
                user_name=current_user.full_name,
                booking_id=booking_id,
                vehicle_name=f"{booking.vehicle.brand} {booking.vehicle.model}",
                refund_amount=refund_amount,
                refund_status=booking.refund_status or "not_applicable"
            )
        except Exception as e:
            pass
        
        return {
            "message": "Booking cancelled successfully",
            "booking": booking,
            "refund_amount": refund_amount,
            "refund_percentage": refund_percentage,
            "refund_info": refund_info
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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


# Admin-only endpoints
@router.get("/admin/all", response_model=List[BookingResponse])
def all_bookings(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all bookings (Admin only)"""
    query = db.query(Booking)
    
    if status_filter:
        query = query.filter(Booking.status == status_filter)
    
    bookings = query.order_by(Booking.created_at.desc()).all()
    return bookings


@router.patch("/{booking_id}/assign-driver")
def assign_driver_to_booking(
    booking_id: int,
    driver_data: DriverAssignmentRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Assign a driver to a booking (Admin only)"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Verify driver exists and is active
    from app.models.driver import Driver
    driver = db.query(Driver).filter(
        Driver.id == driver_data.driver_id,
        Driver.is_active == True
    ).first()
    
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found or inactive")
    
    booking.driver_id = driver_data.driver_id
    db.commit()
    db.refresh(booking)
    
    # Send driver assignment email to user
    try:
        send_driver_assignment_email(
            user_email=booking.user.email,
            user_name=booking.user.full_name,
            booking_id=booking_id,
            driver_name=driver.name,
            driver_phone=driver.phone,
            driver_license=driver.license_number
        )
    except Exception as e:
        pass
    
    return {
        "message": "Driver assigned successfully",
        "booking": booking,
        "driver": driver
    }


@router.patch("/{booking_id}/status")
def update_booking_status(
    booking_id: int,
    new_status: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update booking status (Admin only)"""
    valid_statuses = ["pending", "confirmed", "active", "completed", "cancelled"]
    
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.status = new_status
    db.commit()
    db.refresh(booking)
    
    return {"message": f"Booking status updated to {new_status}", "booking": booking}
