from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.models import Review, Vehicle, User, Booking
from app.schemas.schemas import ReviewCreate, ReviewResponse

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewResponse)
def create_review(review: ReviewCreate, db: Session = Depends(get_db), user_id: int = 1):
    vehicle = db.query(Vehicle).filter(Vehicle.id == review.vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    db_review = Review(
        user_id=user_id,
        vehicle_id=review.vehicle_id,
        booking_id=review.booking_id,
        rating=review.rating,
        comment=review.comment,
        driver_rating=review.driver_rating,
        driver_comment=review.driver_comment
    )
    
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    # Add loyalty points for review
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.loyalty_points += 50  # 50 points per review
    
    db.commit()
    return db_review


@router.get("/vehicle/{vehicle_id}", response_model=List[ReviewResponse])
def get_vehicle_reviews(vehicle_id: int, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.vehicle_id == vehicle_id).all()
    return reviews


@router.get("/average/{vehicle_id}")
def get_average_rating(vehicle_id: int, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.vehicle_id == vehicle_id).all()
    if not reviews:
        return {"average_rating": 0, "total_reviews": 0}
    
    avg_rating = sum(r.rating for r in reviews) / len(reviews)
    avg_driver_rating = sum(r.driver_rating for r in reviews if r.driver_rating) / len([r for r in reviews if r.driver_rating]) if any(r.driver_rating for r in reviews) else 0
    
    return {
        "average_rating": round(avg_rating, 2),
        "average_driver_rating": round(avg_driver_rating, 2),
        "total_reviews": len(reviews)
    }
