from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.models import User, Vehicle, Booking, Review, Coupon
from app.schemas.schemas import UserResponse, VehicleResponse, BookingResponse, ReviewResponse, CouponResponse
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get admin dashboard statistics"""
    total_users = db.query(User).count()
    total_vehicles = db.query(Vehicle).count()
    total_bookings = db.query(Booking).count()
    active_bookings = db.query(Booking).filter(Booking.status == "active").count()
    total_revenue = db.query(Booking).filter(Booking.status == "completed").all()
    revenue = sum(b.final_amount for b in total_revenue)
    
    return {
        "total_users": total_users,
        "total_vehicles": total_vehicles,
        "total_bookings": total_bookings,
        "active_bookings": active_bookings,
        "total_revenue": round(revenue, 2),
        "new_users_this_month": db.query(User).filter(
            User.created_at >= datetime.utcnow().replace(day=1)
        ).count()
    }


@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@router.get("/bookings", response_model=List[BookingResponse])
def get_all_bookings(db: Session = Depends(get_db)):
    bookings = db.query(Booking).order_by(Booking.created_at.desc()).all()
    return bookings


@router.get("/vehicles", response_model=List[VehicleResponse])
def get_all_vehicles_admin(db: Session = Depends(get_db)):
    vehicles = db.query(Vehicle).all()
    return vehicles


@router.put("/vehicles/{vehicle_id}/availability")
def toggle_vehicle_availability(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    vehicle.is_available = not vehicle.is_available
    db.commit()
    
    return {"message": f"Vehicle availability set to {vehicle.is_available}"}


@router.get("/reviews", response_model=List[ReviewResponse])
def get_all_reviews(db: Session = Depends(get_db)):
    reviews = db.query(Review).order_by(Review.created_at.desc()).all()
    return reviews


@router.get("/coupons", response_model=List[CouponResponse])
def get_all_coupons_admin(db: Session = Depends(get_db)):
    coupons = db.query(Coupon).all()
    return coupons


@router.post("/seed-data")
def seed_database(db: Session = Depends(get_db)):
    """Seed the database with sample data"""
    
    # Check if data already exists
    if db.query(Vehicle).count() > 0:
        return {"message": "Database already seeded"}
    
    # Sample vehicles
    vehicles_data = [
        {"name": "Swift Dzire", "brand": "Maruti", "model": "Dzire", "vehicle_type": "car", "price_per_day": 1500.0, "seats": 4, "transmission": "Manual", "fuel_type": "Petrol", "has_driver_option": True, "driver_charge_per_day": 500.0},
        {"name": "Creta", "brand": "Hyundai", "model": "Creta", "vehicle_type": "suv", "price_per_day": 2500.0, "seats": 5, "transmission": "Automatic", "fuel_type": "Diesel", "has_driver_option": True, "driver_charge_per_day": 600.0},
        {"name": "City", "brand": "Honda", "model": "City", "vehicle_type": "car", "price_per_day": 1800.0, "seats": 4, "transmission": "Automatic", "fuel_type": "Petrol", "has_driver_option": True, "driver_charge_per_day": 500.0},
        {"name": "Innova Crysta", "brand": "Toyota", "model": "Innova", "vehicle_type": "suv", "price_per_day": 3500.0, "seats": 7, "transmission": "Manual", "fuel_type": "Diesel", "has_driver_option": True, "driver_charge_per_day": 700.0},
        {"name": "Splendor Plus", "brand": "Hero", "model": "Splendor", "vehicle_type": "bike", "price_per_day": 500.0, "seats": 2, "transmission": "Manual", "fuel_type": "Petrol", "has_driver_option": False},
        {"name": "Mercedes C-Class", "brand": "Mercedes", "model": "C-Class", "vehicle_type": "luxury", "price_per_day": 8000.0, "seats": 4, "transmission": "Automatic", "fuel_type": "Petrol", "has_driver_option": True, "driver_charge_per_day": 1000.0},
        {"name": "Fortuner", "brand": "Toyota", "model": "Fortuner", "vehicle_type": "suv", "price_per_day": 4000.0, "seats": 7, "transmission": "Automatic", "fuel_type": "Diesel", "has_driver_option": True, "driver_charge_per_day": 800.0},
        {"name": "i20", "brand": "Hyundai", "model": "i20", "vehicle_type": "car", "price_per_day": 1200.0, "seats": 4, "transmission": "Manual", "fuel_type": "Petrol", "has_driver_option": True, "driver_charge_per_day": 450.0},
    ]
    
    for v_data in vehicles_data:
        vehicle = Vehicle(**v_data)
        db.add(vehicle)
    
    # Sample coupons
    coupons_data = [
        {"code": "WELCOME20", "discount_percentage": 20.0, "max_discount": 500.0, "for_new_users_only": True, "usage_limit": 100},
        {"code": "LONGTRIP15", "discount_percentage": 15.0, "min_booking_amount": 3000.0, "usage_limit": 500},
        {"code": "SAVE100", "discount_percentage": 10.0, "max_discount": 100.0, "is_active": True},
    ]
    
    for c_data in coupons_data:
        coupon = Coupon(**c_data)
        db.add(coupon)
    
    db.commit()
    
    return {"message": "Database seeded successfully", "vehicles": len(vehicles_data), "coupons": len(coupons_data)}
