from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.vehicle import Vehicle


def create_booking(
    db: Session,
    user_id: int,
    data
):

    vehicle = db.query(
        Vehicle
    ).filter(
        Vehicle.id == data.vehicle_id,
        Vehicle.is_active == True
    ).first()


    if not vehicle:

        return None


    difference = (
        data.return_date -
        data.pickup_date
    )


    days = (
        difference.total_seconds()
        / 86400
    )


    if days < 1:

        days = 1


    total_amount = (
        days *
        vehicle.price_per_day
    )


    booking = Booking(

        user_id=user_id,

        vehicle_id=data.vehicle_id,

        pickup_date=data.pickup_date,

        return_date=data.return_date,

        total_amount=total_amount,

        status="confirmed"

    )


    db.add(
        booking
    )


    db.commit()


    db.refresh(
        booking
    )


    return booking