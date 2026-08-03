from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.models import Vehicle, Booking
from app.schemas.schemas import VehicleCreate, VehicleResponse
from datetime import datetime

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.get("/", response_model=List[VehicleResponse])
def get_all_vehicles(db: Session = Depends(get_db)):
    vehicles = db.query(Vehicle).filter(Vehicle.is_available == True).all()
    return vehicles


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.post("/", response_model=VehicleResponse)
def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    db_vehicle = Vehicle(**vehicle.model_dump())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(vehicle_id: int, vehicle: VehicleCreate, db: Session = Depends(get_db)):
    db_vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    for key, value in vehicle.model_dump().items():
        setattr(db_vehicle, key, value)
    
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


@router.delete("/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    db_vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    db.delete(db_vehicle)
    db.commit()
    return {"message": "Vehicle deleted successfully"}


@router.get("/type/{vehicle_type}", response_model=List[VehicleResponse])
def get_vehicles_by_type(vehicle_type: str, db: Session = Depends(get_db)):
    vehicles = db.query(Vehicle).filter(
        Vehicle.vehicle_type == vehicle_type,
        Vehicle.is_available == True
    ).all()
    return vehicles


@router.get("/{vehicle_id}/similar", response_model=List[VehicleResponse])
def get_similar_vehicles(vehicle_id: int, db: Session = Depends(get_db)):
    """Get similar vehicles for the Hidden Deal Finder feature"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Find similar vehicles of same type but cheaper
    similar = db.query(Vehicle).filter(
        Vehicle.vehicle_type == vehicle.vehicle_type,
        Vehicle.id != vehicle_id,
        Vehicle.price_per_day < vehicle.price_per_day,
        Vehicle.is_available == True
    ).limit(3).all()
    
    return similar
