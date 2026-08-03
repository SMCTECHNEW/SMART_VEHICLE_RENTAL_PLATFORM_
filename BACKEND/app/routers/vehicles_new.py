from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.booking import Booking
from app.models.driver import VehicleImage
from app.schemas.vehicle import (
    VehicleCreate, VehicleResponse, VehicleUpdate, 
    VehicleFilterParams, VehicleImageResponse, VehicleImageCreate
)
from app.services.vehicle_service import (
    create_vehicle, get_vehicle, get_all_vehicles,
    check_vehicle_availability, search_filter_sort_vehicles,
    update_vehicle_rating, get_available_vehicles
)
from app.services.storage_service import storage_service
from app.services.booking_service import BookingService


router = APIRouter(prefix="/vehicles", tags=["Vehicles"])
security = HTTPBearer()


# =====================================================
# PUBLIC VEHICLE ENDPOINTS
# =====================================================

@router.get("/", response_model=List[VehicleResponse])
def list_vehicles(
    search: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    fuel_type: Optional[str] = Query(None),
    transmission: Optional[str] = Query(None),
    seats: Optional[int] = Query(None),
    min_rating: Optional[float] = Query(None),
    sort_by: Optional[str] = Query(None),
    sort_order: Optional[str] = Query("asc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all vehicles with filtering, searching, sorting and pagination.
    All filters are optional and work through backend database queries.
    """
    params = VehicleFilterParams(
        search=search,
        brand=brand,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        fuel_type=fuel_type,
        transmission=transmission,
        seats=seats,
        min_rating=min_rating,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size
    )
    
    vehicles, total_count = search_filter_sort_vehicles(db, params)
    
    # Return vehicles with pagination info in headers (could be enhanced)
    return vehicles


@router.get("/available")
def get_available_vehicles_endpoint(
    pickup_date: datetime = Query(...),
    return_date: datetime = Query(...),
    db: Session = Depends(get_db)
):
    """Get vehicles available for specific dates"""
    if return_date <= pickup_date:
        raise HTTPException(status_code=400, detail="Return date must be after pickup date")
    
    vehicles = get_available_vehicles(db, pickup_date, return_date)
    return {
        "available_vehicles": vehicles,
        "count": len(vehicles),
        "pickup_date": pickup_date,
        "return_date": return_date
    }


@router.get("/check-availability/{vehicle_id}")
def check_availability_endpoint(
    vehicle_id: int,
    pickup_date: datetime = Query(...),
    return_date: datetime = Query(...),
    db: Session = Depends(get_db)
):
    """Check if a specific vehicle is available for given dates"""
    if return_date <= pickup_date:
        raise HTTPException(status_code=400, detail="Return date must be after pickup date")
    
    availability = check_vehicle_availability(
        db=db,
        vehicle_id=vehicle_id,
        pickup_date=pickup_date,
        return_date=return_date
    )
    
    return availability


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def vehicle_details(vehicle_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific vehicle including images and reviews"""
    vehicle = get_vehicle(db, vehicle_id)
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    return vehicle


# =====================================================
# ADMIN-ONLY VEHICLE ENDPOINTS
# =====================================================

@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def add_vehicle(
    data: VehicleCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin only: Add a new vehicle"""
    # Check for duplicate registration number
    existing = db.query(Vehicle).filter(
        Vehicle.registration_number == data.registration_number
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Registration number already exists"
        )
    
    return create_vehicle(db, data)


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: int,
    data: VehicleUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin only: Update vehicle information"""
    vehicle = get_vehicle(db, vehicle_id)
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(vehicle, key, value)
    
    db.commit()
    db.refresh(vehicle)
    
    return vehicle


@router.delete("/{vehicle_id}")
def delete_vehicle(
    vehicle_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin only: Soft delete a vehicle"""
    vehicle = get_vehicle(db, vehicle_id)
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    vehicle.is_active = False
    db.commit()
    
    return {"message": "Vehicle deleted successfully"}


# =====================================================
# VEHICLE IMAGE UPLOAD ENDPOINTS (Admin Only)
# =====================================================

@router.post("/{vehicle_id}/images", response_model=VehicleImageResponse)
async def upload_vehicle_image(
    vehicle_id: int,
    file: UploadFile = File(..., description="Vehicle image file"),
    is_primary: bool = Form(False),
    display_order: int = Form(0),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Admin only: Upload a vehicle image.
    Supports multiple images per vehicle.
    One image can be marked as primary (displayed first).
    """
    # Verify vehicle exists
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Validate and upload file
    try:
        image_url = storage_service.upload_vehicle_image(file, vehicle_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")
    
    # If this is set as primary, unset other primary images
    if is_primary:
        db.query(VehicleImage).filter(
            VehicleImage.vehicle_id == vehicle_id,
            VehicleImage.is_primary == True
        ).update({"is_primary": False})
    
    # Create image record
    image_record = VehicleImage(
        vehicle_id=vehicle_id,
        image_url=image_url,
        is_primary=is_primary,
        display_order=display_order
    )
    
    db.add(image_record)
    db.commit()
    db.refresh(image_record)
    
    return image_record


@router.get("/{vehicle_id}/images", response_model=List[VehicleImageResponse])
def get_vehicle_images(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    """Get all images for a vehicle"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    return db.query(VehicleImage).filter(
        VehicleImage.vehicle_id == vehicle_id
    ).order_by(VehicleImage.display_order, VehicleImage.created_at).all()


@router.delete("/{vehicle_id}/images/{image_id}")
def delete_vehicle_image(
    vehicle_id: int,
    image_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Admin only: Delete a vehicle image.
    Also deletes the file from storage.
    """
    image = db.query(VehicleImage).filter(
        VehicleImage.id == image_id,
        VehicleImage.vehicle_id == vehicle_id
    ).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Delete file from storage
    storage_service.delete_vehicle_image(image.image_url)
    
    # Delete database record
    db.delete(image)
    db.commit()
    
    return {"message": "Image deleted successfully"}


@router.post("/{vehicle_id}/images/set-primary/{image_id}")
def set_primary_image(
    vehicle_id: int,
    image_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin only: Set a specific image as the primary image for a vehicle"""
    # Verify vehicle and image exist
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    image = db.query(VehicleImage).filter(
        VehicleImage.id == image_id,
        VehicleImage.vehicle_id == vehicle_id
    ).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Unset all other primary images
    db.query(VehicleImage).filter(
        VehicleImage.vehicle_id == vehicle_id,
        VehicleImage.is_primary == True
    ).update({"is_primary": False})
    
    # Set this image as primary
    image.is_primary = True
    db.commit()
    
    return {"message": "Primary image updated successfully"}
