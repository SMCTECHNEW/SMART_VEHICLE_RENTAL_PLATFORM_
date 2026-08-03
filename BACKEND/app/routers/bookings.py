from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.booking import Booking
from app.schemas.booking import BookingCreate, BookingResponse
from app.routers.users import get_current_user
from app.models.user import User
from app.services.booking_service import create_booking

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/", response_model=BookingResponse)
def create_new_booking(
    data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if data.return_date <= data.pickup_date:
        raise HTTPException(
            status_code=400,
            detail="Return date must be after pickup date"
        )

    booking = create_booking(db, current_user.id, data)

    if not booking:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    return booking


@router.get("/my-bookings", response_model=list[BookingResponse])
def my_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Booking).filter(
        Booking.user_id == current_user.id
    ).all()


@router.get("/", response_model=list[BookingResponse])
def all_bookings(db: Session = Depends(get_db)):
    return db.query(Booking).all()


@router.patch("/{booking_id}/cancel")
def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.status = "cancelled"
    db.commit()

    return {"message": "Booking cancelled successfully"}
