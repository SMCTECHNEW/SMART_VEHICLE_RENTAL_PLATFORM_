from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.models import Booking, Vehicle, User, Coupon
from app.schemas.schemas import BookingCreate, BookingResponse
from datetime import datetime, timedelta
import razorpay
from app.core.config import settings

router = APIRouter(prefix="/bookings", tags=["Bookings"])


def calculate_discount(base_price: float, total_days: int, user: User, coupon_code: str = None, db: Session = None):
    discount = 0.0
    
    # 15% discount for bookings above 2 days
    if total_days > 2:
        discount += base_price * 0.15
    
    # 20% discount for new users
    if user.is_new_user:
        discount += base_price * 0.20
        user.is_new_user = False  # Mark as not new anymore
    
    # Apply coupon if provided
    if coupon_code and db:
        coupon = db.query(Coupon).filter(Coupon.code == coupon_code).first()
        if coupon and coupon.is_active:
            if coupon.for_new_users_only and not user.is_new_user:
                pass  # Coupon not applicable
            else:
                coupon_discount = base_price * (coupon.discount_percentage / 100)
                if coupon.max_discount:
                    coupon_discount = min(coupon_discount, coupon.max_discount)
                discount += coupon_discount
    
    return discount


@router.post("/", response_model=BookingResponse)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db), user_id: int = 1):
    vehicle = db.query(Vehicle).filter(Vehicle.id == booking.vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    if not vehicle.is_available:
        raise HTTPException(status_code=400, detail="Vehicle not available")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate dates and pricing
    start_date = booking.start_date
    end_date = booking.end_date
    total_days = (end_date - start_date).days
    if total_days <= 0:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    
    base_price = vehicle.price_per_day * total_days
    driver_charge = 0.0
    
    if booking.driver_required and vehicle.has_driver_option:
        driver_charge = vehicle.driver_charge_per_day * total_days
    
    # Calculate discounts
    discount = calculate_discount(base_price, total_days, user, booking.coupon_code, db)
    final_amount = base_price + driver_charge - discount
    
    # Create Razorpay order
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    razorpay_order = client.order.create({
        "amount": int(final_amount * 100),  # Amount in paise
        "currency": "INR",
        "payment_capture": 1
    })
    
    db_booking = Booking(
        user_id=user_id,
        vehicle_id=booking.vehicle_id,
        start_date=start_date,
        end_date=end_date,
        total_days=total_days,
        base_price=base_price,
        driver_required=booking.driver_required,
        driver_charge=driver_charge,
        discount_amount=discount,
        final_amount=final_amount,
        status="pending",
        razorpay_order_id=razorpay_order.get("id"),
        coupon_code=booking.coupon_code
    )
    
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    
    return db_booking


@router.get("/", response_model=List[BookingResponse])
def get_user_bookings(user_id: int = 1, db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter(Booking.user_id == user_id).all()
    return bookings


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.put("/{booking_id}/confirm")
def confirm_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.status = "confirmed"
    db.commit()
    return {"message": "Booking confirmed"}


@router.delete("/{booking_id}")
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.status = "cancelled"
    db.commit()
    return {"message": "Booking cancelled"}


@router.get("/hidden-deal/{booking_id}")
def get_hidden_deal(booking_id: int, db: Session = Depends(get_db)):
    """Hidden Deal Finder - suggests cheaper similar vehicle"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    vehicle = db.query(Vehicle).filter(Vehicle.id == booking.vehicle_id).first()
    
    # Find similar but cheaper vehicles
    similar_vehicles = db.query(Vehicle).filter(
        Vehicle.vehicle_type == vehicle.vehicle_type,
        Vehicle.id != booking.vehicle_id,
        Vehicle.price_per_day < vehicle.price_per_day,
        Vehicle.is_available == True
    ).all()
    
    deals = []
    for sv in similar_vehicles:
        savings = (vehicle.price_per_day - sv.price_per_day) * booking.total_days
        deals.append({
            "vehicle_id": sv.id,
            "vehicle_name": f"{sv.brand} {sv.model}",
            "original_price": vehicle.price_per_day,
            "new_price": sv.price_per_day,
            "total_savings": savings,
            "savings_percentage": round((savings / (vehicle.price_per_day * booking.total_days)) * 100, 2)
        })
    
    return {"deals": deals, "current_booking": booking_id}
