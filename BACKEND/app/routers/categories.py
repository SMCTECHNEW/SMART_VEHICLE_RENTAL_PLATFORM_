from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.vehicle_category import VehicleCategory
from app.schemas.vehicle_category import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/categories", tags=["Vehicle Categories"])


@router.post("/", response_model=CategoryResponse)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    category = VehicleCategory(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(VehicleCategory).filter(
        VehicleCategory.is_active == True
    ).all()


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(VehicleCategory).filter(
        VehicleCategory.id == category_id
    ).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category
