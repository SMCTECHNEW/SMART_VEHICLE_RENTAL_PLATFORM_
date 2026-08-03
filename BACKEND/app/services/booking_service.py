from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, text

from app.models.booking import Booking
from app.models.vehicle import Vehicle
from app.models.user import User
from app.models.driver import Driver
from app.schemas.booking import BookingCreate


class BookingService:
    
    @staticmethod
    def check_availability(
        db: Session,
        vehicle_id: int,
        pickup_date: datetime,
        return_date: datetime,
        exclude_booking_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Check if vehicle is available for the given dates.
        Returns dict with 'available' boolean and 'message'.
        """
        # Validate dates
        if return_date <= pickup_date:
            return {
                "available": False,
                "message": "Return date must be after pickup date"
            }
        
        # Query for overlapping bookings (pending, confirmed, or active)
        query = db.query(Booking).filter(
            Booking.vehicle_id == vehicle_id,
            Booking.status.in_(["pending", "confirmed", "active"]),
            Booking.pickup_date < return_date,
            Booking.return_date > pickup_date
        )
        
        if exclude_booking_id:
            query = query.filter(Booking.id != exclude_booking_id)
        
        overlapping = query.first()
        
        if overlapping:
            return {
                "available": False,
                "message": "Vehicle is not available for the selected dates",
                "conflicting_booking_id": overlapping.id
            }
        
        return {"available": True, "message": "Vehicle is available"}
    
    @staticmethod
    def calculate_total_amount(
        db: Session,
        vehicle_id: int,
        pickup_date: datetime,
        return_date: datetime,
        driver_required: bool = False
    ) -> float:
        """Calculate total booking amount including driver charges if applicable"""
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle:
            raise ValueError("Vehicle not found")
        
        # Calculate days (minimum 1 day)
        delta = return_date - pickup_date
        days = max(1, delta.total_seconds() / 86400)
        
        # Round up partial days
        if delta.total_seconds() % 86400 > 0:
            days = int(days) + 1
        
        total = days * vehicle.price_per_day
        
        # Add driver charges if required (e.g., $20 per day)
        if driver_required:
            total += days * 20.0
        
        return total
    
    @staticmethod
    def create_booking(
        db: Session,
        user_id: int,
        data: BookingCreate
    ) -> Booking:
        """
        Create a new booking with availability check and double booking prevention.
        Uses database transaction for atomicity.
        """
        # Verify vehicle exists and is active
        vehicle = db.query(Vehicle).filter(
            Vehicle.id == data.vehicle_id,
            Vehicle.is_active == True
        ).first()
        
        if not vehicle:
            raise ValueError("Vehicle not found or inactive")
        
        # First availability check
        availability = BookingService.check_availability(
            db=db,
            vehicle_id=data.vehicle_id,
            pickup_date=data.pickup_date,
            return_date=data.return_date
        )
        
        if not availability["available"]:
            raise ValueError(availability["message"])
        
        # Calculate total amount
        total_amount = BookingService.calculate_total_amount(
            db=db,
            vehicle_id=data.vehicle_id,
            pickup_date=data.pickup_date,
            return_date=data.return_date,
            driver_required=data.driver_required
        )
        
        # Create booking within transaction
        try:
            # Use SELECT FOR UPDATE to prevent concurrent bookings
            # This locks the vehicle row during the transaction
            locked_vehicle = db.query(Vehicle).filter(
                Vehicle.id == data.vehicle_id
            ).with_for_update().first()
            
            if not locked_vehicle:
                raise ValueError("Vehicle not found")
            
            # Double-check availability after locking
            availability = BookingService.check_availability(
                db=db,
                vehicle_id=data.vehicle_id,
                pickup_date=data.pickup_date,
                return_date=data.return_date
            )
            
            if not availability["available"]:
                raise ValueError("Vehicle was just booked by another user. Please select different dates.")
            
            # Create the booking
            booking = Booking(
                user_id=user_id,
                vehicle_id=data.vehicle_id,
                pickup_date=data.pickup_date,
                return_date=data.return_date,
                total_amount=total_amount,
                status="pending"  # Pending until payment is confirmed
            )
            
            db.add(booking)
            db.flush()  # Get the booking ID
            
            # Assign driver if required
            if data.driver_required:
                available_driver = db.query(Driver).filter(
                    Driver.is_active == True,
                    Driver.status == "available"
                ).first()
                
                if available_driver:
                    booking.driver_id = available_driver.id
            
            db.commit()
            db.refresh(booking)
            
            # Load relationships for response
            booking_with_relations = db.query(Booking).filter(
                Booking.id == booking.id
            ).options(
                joinedload(Booking.vehicle),
                joinedload(Booking.user),
                joinedload(Booking.driver)
            ).first()
            
            return booking_with_relations
            
        except Exception as e:
            db.rollback()
            raise e
    
    @staticmethod
    def cancel_booking(
        db: Session,
        booking_id: int,
        user_id: int,
        cancellation_reason: str,
        is_admin: bool = False
    ) -> Booking:
        """
        Cancel a booking with refund logic.
        Only the booking owner or admin can cancel.
        """
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        
        if not booking:
            raise ValueError("Booking not found")
        
        # Check ownership (unless admin)
        if not is_admin and booking.user_id != user_id:
            raise ValueError("Unauthorized: You can only cancel your own bookings")
        
        # Check if already cancelled
        if booking.status == "cancelled":
            raise ValueError("Booking is already cancelled")
        
        # Check if booking is in the past
        if booking.pickup_date < datetime.utcnow():
            raise ValueError("Cannot cancel a booking that has already started")
        
        # Determine refund eligibility based on cancellation policy
        hours_until_pickup = (booking.pickup_date - datetime.utcnow()).total_seconds() / 3600
        
        refund_percentage = 0.0
        if hours_until_pickup >= 48:
            refund_percentage = 1.0  # 100% refund
        elif hours_until_pickup >= 24:
            refund_percentage = 0.75  # 75% refund
        elif hours_until_pickup >= 12:
            refund_percentage = 0.50  # 50% refund
        else:
            refund_percentage = 0.0  # No refund
        
        refund_amount = booking.total_amount * refund_percentage
        
        # Update booking status
        booking.status = "cancelled"
        booking.cancellation_reason = cancellation_reason
        booking.cancelled_at = datetime.utcnow()
        
        if refund_percentage > 0:
            booking.refund_status = "pending"
        
        db.commit()
        db.refresh(booking)
        
        # Return booking with refund info
        return {
            "booking": booking,
            "refund_amount": refund_amount,
            "refund_percentage": refund_percentage * 100
        }
    
    @staticmethod
    def get_user_bookings(
        db: Session,
        user_id: int,
        status: Optional[str] = None,
        include_past: bool = True
    ):
        """Get all bookings for a user with optional filtering"""
        query = db.query(Booking).filter(
            Booking.user_id == user_id
        ).options(
            joinedload(Booking.vehicle),
            joinedload(Booking.driver),
            joinedload(Booking.payment)
        ).order_by(Booking.created_at.desc())
        
        if status:
            query = query.filter(Booking.status == status)
        
        if not include_past:
            # Only upcoming and active bookings
            query = query.filter(
                Booking.return_date >= datetime.utcnow(),
                Booking.status.in_(["pending", "confirmed", "active"])
            )
        
        return query.all()
    
    @staticmethod
    def get_booking_history(
        db: Session,
        user_id: int
    ):
        """Get complete booking history categorized by status"""
        now = datetime.utcnow()
        
        bookings = db.query(Booking).filter(
            Booking.user_id == user_id
        ).options(
            joinedload(Booking.vehicle),
            joinedload(Booking.driver),
            joinedload(Booking.payment)
        ).order_by(Booking.created_at.desc()).all()
        
        history = {
            "upcoming": [],
            "active": [],
            "completed": [],
            "cancelled": [],
            "pending": []
        }
        
        for booking in bookings:
            booking_data = {
                "id": booking.id,
                "user_id": booking.user_id,
                "vehicle_id": booking.vehicle_id,
                "driver_id": booking.driver_id,
                "pickup_date": booking.pickup_date,
                "return_date": booking.return_date,
                "total_amount": booking.total_amount,
                "status": booking.status,
                "cancellation_reason": booking.cancellation_reason,
                "cancelled_at": booking.cancelled_at,
                "refund_status": booking.refund_status,
                "created_at": booking.created_at,
                "updated_at": booking.updated_at,
                "vehicle_brand": booking.vehicle.brand if booking.vehicle else None,
                "vehicle_model": booking.vehicle.model if booking.vehicle else None,
                "vehicle_image": booking.vehicle.image_url if booking.vehicle else None,
                "driver_name": booking.driver.name if booking.driver else None,
                "driver_phone": booking.driver.phone if booking.driver else None,
                "payment_status": booking.payment.status if booking.payment else None
            }
            
            if booking.status == "pending":
                history["pending"].append(booking_data)
            elif booking.status == "cancelled":
                history["cancelled"].append(booking_data)
            elif booking.status == "completed":
                history["completed"].append(booking_data)
            elif booking.status == "active":
                history["active"].append(booking_data)
            elif booking.status == "confirmed":
                if booking.return_date > now:
                    history["upcoming"].append(booking_data)
                else:
                    history["completed"].append(booking_data)
        
        return history