from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.contact_message import ContactMessage
from app.schemas.contact_message import (
    ContactMessageCreate,
    ContactMessageResponse
)

router = APIRouter(prefix="/contact", tags=["Contact"])


@router.post("/", response_model=ContactMessageResponse)
def send_message(
    data: ContactMessageCreate,
    db: Session = Depends(get_db)
):
    message = ContactMessage(**data.model_dump())
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.get("/", response_model=list[ContactMessageResponse])
def get_messages(db: Session = Depends(get_db)):
    return db.query(ContactMessage).all()
