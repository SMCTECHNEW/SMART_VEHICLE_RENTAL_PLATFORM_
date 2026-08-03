from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.admin import Admin
from app.schemas.admin import AdminCreate, AdminResponse

router = APIRouter(prefix="/admins", tags=["Admins"])


@router.post("/", response_model=AdminResponse)
def create_admin(data: AdminCreate, db: Session = Depends(get_db)):
    admin = Admin(**data.model_dump())
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@router.get("/", response_model=list[AdminResponse])
def get_admins(db: Session = Depends(get_db)):
    return db.query(Admin).all()
