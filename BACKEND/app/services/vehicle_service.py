from datetime import datetime
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, select
from sqlalchemy.sql import text

from app.models.vehicle import Vehicle
from app.models.booking import Booking
from app.models.vehicle_category import VehicleCategory
from app.schemas.vehicle import VehicleCreate, VehicleFilterParams


def create_vehicle(db: Session, data: VehicleCreate):
    vehicle = Vehicle(
        category_id=data.category_id,
        brand=data.brand,
        model=data.model,
        registration_number=data.registration_number,
        year=data.year,
        color=data.color,
        fuel_type=data.fuel_type,
        transmission=data.transmission,
        seats=data.seats,
        price_per_day=data.price_per_day,
        image_url=data.image_url,
        location=data.location,
        status="available",
        is_active=True
    )

    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    return vehicle


def get_vehicle(db: Session, vehicle_id: int):
    return db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.is_active == True
    ).options(joinedload(Vehicle.images)).first()


def get_all_vehicles(db: Session):
    return db.query(Vehicle).filter(
        Vehicle.is_active == True
    ).options(joinedload(Vehicle.images)).all()


def check_vehicle_availability(
    db: Session,
    vehicle_id: int,
    pickup_date: datetime,
    return_date: datetime,
    exclude_booking_id: Optional[int] = None
) -> bool:
    """
    Check if a vehicle is available for the given date range.
    Returns True if available, False if already booked.
    
    A vehicle is unavailable if there's an overlapping booking that is:
    - pending, confirmed, or active (not cancelled or completed)
    """
    # Query for overlapping bookings
    query = db.query(Booking).filter(
        Booking.vehicle_id == vehicle_id,
        Booking.status.in_(["pending", "confirmed", "active"]),
        or_(
            # Existing booking starts before new booking ends AND ends after new booking starts
            and_(
                Booking.pickup_date < return_date,
                Booking.return_date > pickup_date
            )
        )
    )
    
    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)
    
    overlapping_bookings = query.count()
    
    return overlapping_bookings == 0


def get_available_vehicles(
    db: Session,
    pickup_date: datetime,
    return_date: datetime
) -> List[Vehicle]:
    """
    Get all vehicles that are available for the given date range.
    Uses subquery to exclude vehicles with overlapping bookings.
    """
    # Subquery to find vehicles with overlapping bookings
    overlapping_subquery = db.query(Booking.vehicle_id).filter(
        Booking.status.in_(["pending", "confirmed", "active"]),
        Booking.pickup_date < return_date,
        Booking.return_date > pickup_date
    ).subquery()
    
    # Get vehicles not in the overlapping list
    vehicles = db.query(Vehicle).filter(
        Vehicle.is_active == True,
        ~Vehicle.id.in_(overlapping_subquery)
    ).options(joinedload(Vehicle.images)).all()
    
    return vehicles


def search_filter_sort_vehicles(
    db: Session,
    params: VehicleFilterParams
) -> Tuple[List[Vehicle], int]:
    """
    Search, filter, and sort vehicles with pagination.
    Returns (vehicles, total_count)
    """
    query = db.query(Vehicle).filter(Vehicle.is_active == True)
    
    # Search by vehicle name/brand/model
    if params.search:
        search_term = f"%{params.search}%"
        query = query.filter(
            or_(
                Vehicle.brand.ilike(search_term),
                Vehicle.model.ilike(search_term),
                Vehicle.registration_number.ilike(search_term)
            )
        )
    
    # Filter by brand
    if params.brand:
        query = query.filter(Vehicle.brand.ilike(f"%{params.brand}%"))
    
    # Filter by category
    if params.category_id:
        query = query.filter(Vehicle.category_id == params.category_id)
    
    # Filter by vehicle type (through category join)
    if params.vehicle_type:
        category_subquery = db.query(VehicleCategory.id).filter(
            VehicleCategory.name.ilike(f"%{params.vehicle_type}%")
        ).subquery()
        query = query.filter(Vehicle.category_id.in_(category_subquery))
    
    # Price range filter
    if params.min_price is not None:
        query = query.filter(Vehicle.price_per_day >= params.min_price)
    if params.max_price is not None:
        query = query.filter(Vehicle.price_per_day <= params.max_price)
    
    # Fuel type filter
    if params.fuel_type:
        query = query.filter(Vehicle.fuel_type.ilike(f"%{params.fuel_type}%"))
    
    # Transmission filter
    if params.transmission:
        query = query.filter(Vehicle.transmission.ilike(f"%{params.transmission}%"))
    
    # Seats filter
    if params.seats:
        query = query.filter(Vehicle.seats >= params.seats)
    
    # Rating filter
    if params.min_rating is not None:
        query = query.filter(Vehicle.rating >= params.min_rating)
    
    # Availability filter (if dates provided)
    if params.available_from and params.available_to:
        overlapping_subquery = db.query(Booking.vehicle_id).filter(
            Booking.status.in_(["pending", "confirmed", "active"]),
            Booking.pickup_date < params.available_to,
            Booking.return_date > params.available_from
        ).subquery()
        query = query.filter(~Vehicle.id.in_(overlapping_subquery))
    
    # Sorting
    if params.sort_by:
        sort_order = params.sort_order or "asc"
        
        if params.sort_by == "price":
            if sort_order == "asc":
                query = query.order_by(Vehicle.price_per_day.asc())
            else:
                query = query.order_by(Vehicle.price_per_day.desc())
        elif params.sort_by == "rating":
            if sort_order == "asc":
                query = query.order_by(Vehicle.rating.asc())
            else:
                query = query.order_by(Vehicle.rating.desc())
        elif params.sort_by == "newest":
            query = query.order_by(Vehicle.created_at.desc())
        elif params.sort_by == "popular":
            # Sort by total_reviews or rating as proxy for popularity
            query = query.order_by(Vehicle.total_reviews.desc(), Vehicle.rating.desc())
        else:
            query = query.order_by(Vehicle.created_at.desc())
    else:
        # Default sort by newest
        query = query.order_by(Vehicle.created_at.desc())
    
    # Get total count before pagination
    total_count = query.count()
    
    # Pagination
    offset = (params.page - 1) * params.page_size
    query = query.offset(offset).limit(params.page_size)
    
    # Load images
    vehicles = query.options(joinedload(Vehicle.images)).all()
    
    return vehicles, total_count


def update_vehicle_rating(db: Session, vehicle_id: int):
    """Recalculate average rating for a vehicle based on its reviews"""
    from app.models.review import Review
    
    result = db.query(
        func.avg(Review.rating).label('avg_rating'),
        func.count(Review.id).label('total_reviews')
    ).filter(
        Review.vehicle_id == vehicle_id,
        Review.is_approved == True,
        Review.is_deleted == False
    ).first()
    
    if result and result[0] is not None:
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if vehicle:
            vehicle.rating = round(float(result[0]), 2)
            vehicle.total_reviews = result[1]
            db.commit()
            db.refresh(vehicle)
            return vehicle
    
    return None