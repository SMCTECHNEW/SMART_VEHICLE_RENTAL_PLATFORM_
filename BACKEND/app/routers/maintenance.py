from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.maintenance import Maintenance
from app.schemas.maintenance import MaintenanceCreate, MaintenanceResponse

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])


@router.post("/", response_model=MaintenanceResponse)
def create_maintenance(
    data: MaintenanceCreate,
    db: Session = Depends(get_db)
):
    maintenance = Maintenance(**data.model_dump())
    db.add(maintenance)
    db.commit()
    db.refresh(maintenance)
    return maintenance


@router.get("/", response_model=list[MaintenanceResponse])
def get_maintenance(db: Session = Depends(get_db)):
    return db.query(Maintenance).all()


@router.patch("/{maintenance_id}/complete")
def complete_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db)
):
    maintenance = db.query(Maintenance).filter(
        Maintenance.id == maintenance_id
    ).first()

    if not maintenance:
        return {"error": "Maintenance record not found"}

    from datetime import datetime

    maintenance.status = "completed"
    maintenance.completed_date = datetime.utcnow()

    db.commit()

    return {"message": "Maintenance completed successfully"}
