"""
Drivers Management API
Admin can manage drivers, assign to bookings
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.models import User, Booking
from app.models.driver import Driver
from app.schemas.schemas import DriverCreate, DriverResponse
from app.core.deps import get_current_admin_user, get_current_user
from datetime import date

router = APIRouter(prefix="/drivers", tags=["Drivers"])


@router.post("/", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
def create_driver(
    driver: DriverCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new driver (Admin only)"""
    # Check if phone or license already exists
    existing = db.query(Driver).filter(
        (Driver.phone == driver.phone) | 
        (Driver.license_number == driver.license_number)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver with this phone or license number already exists"
        )
    
    db_driver = Driver(**driver.dict())
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    
    return db_driver


@router.get("/", response_model=List[DriverResponse])
def list_drivers(
    skip: int = 0,
    limit: int = 50,
    is_active: Optional[bool] = None,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all drivers with optional filters"""
    query = db.query(Driver)
    
    if is_active is not None:
        query = query.filter(Driver.is_active == is_active)
    
    if status_filter:
        query = query.filter(Driver.status == status_filter)
    
    drivers = query.offset(skip).limit(limit).all()
    return drivers


@router.get("/{driver_id}", response_model=DriverResponse)
def get_driver(
    driver_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get driver by ID"""
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


@router.put("/{driver_id}", response_model=DriverResponse)
def update_driver(
    driver_id: int,
    driver_update: DriverCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update driver information (Admin only)"""
    db_driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not db_driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    for key, value in driver_update.dict().items():
        setattr(db_driver, key, value)
    
    db.commit()
    db.refresh(db_driver)
    return db_driver


@router.delete("/{driver_id}")
def delete_driver(
    driver_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a driver (Admin only)"""
    db_driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not db_driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    db.delete(db_driver)
    db.commit()
    return {"message": "Driver deleted successfully"}


@router.patch("/{driver_id}/status")
def update_driver_status(
    driver_id: int,
    status_update: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update driver status (Admin only)"""
    valid_statuses = ["available", "busy", "on_leave"]
    if status_update not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    db_driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not db_driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    db_driver.status = status_update
    db.commit()
    db.refresh(db_driver)
    return {"message": f"Driver status updated to {status_update}"}


@router.patch("/{driver_id}/activate")
def activate_driver(
    driver_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Activate a driver (Admin only)"""
    db_driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not db_driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    db_driver.is_active = True
    db.commit()
    return {"message": "Driver activated successfully"}


@router.patch("/{driver_id}/deactivate")
def deactivate_driver(
    driver_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Deactivate a driver (Admin only)"""
    db_driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not db_driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    db_driver.is_active = False
    db.commit()
    return {"message": "Driver deactivated successfully"}


@router.get("/available/for-booking")
def get_available_drivers(
    db: Session = Depends(get_db)
):
    """Get list of available drivers for booking assignment"""
    drivers = db.query(Driver).filter(
        Driver.is_active == True,
        Driver.status == "available"
    ).all()
    return drivers
