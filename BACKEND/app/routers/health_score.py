from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.vehicle_health_score import VehicleHealthScore
from app.schemas.vehicle_health_score import (
    HealthScoreCreate,
    HealthScoreResponse
)

router = APIRouter(prefix="/health-score", tags=["Vehicle Health Score"])


@router.post("/", response_model=HealthScoreResponse)
def create_health_score(
    data: HealthScoreCreate,
    db: Session = Depends(get_db)
):
    score = VehicleHealthScore(**data.model_dump())
    db.add(score)
    db.commit()
    db.refresh(score)
    return score


@router.get("/", response_model=list[HealthScoreResponse])
def get_health_scores(db: Session = Depends(get_db)):
    return db.query(VehicleHealthScore).all()
