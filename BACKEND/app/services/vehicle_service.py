from sqlalchemy.orm import Session

from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate


def create_vehicle(
    db: Session,
    data: VehicleCreate
):

    vehicle = Vehicle(
        category_id=data.category_id,
        brand=data.brand,
        model=data.model,
        registration_number=data.registration_number,
        year=data.year,
        color=data.color,
        fuel_type=data.fuel_type,
        transmission=data.transmission,
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



def get_vehicle(
    db: Session,
    vehicle_id: int
):

    return db.query(
        Vehicle
    ).filter(
        Vehicle.id == vehicle_id
    ).first()



def get_all_vehicles(
    db: Session
):

    return db.query(
        Vehicle
    ).filter(
        Vehicle.is_active == True
    ).all()