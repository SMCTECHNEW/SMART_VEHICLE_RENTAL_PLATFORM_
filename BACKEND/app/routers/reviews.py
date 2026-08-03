from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewResponse
from app.routers.users import get_current_user
from app.models.user import User

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewResponse)
def create_review(
    data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    review = Review(
        user_id=current_user.id,
        **data.model_dump()
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


@router.get("/vehicle/{vehicle_id}", response_model=list[ReviewResponse])
def get_vehicle_reviews(vehicle_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter(
        Review.vehicle_id == vehicle_id
    ).all()
