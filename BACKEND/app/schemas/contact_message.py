from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class ContactMessageCreate(BaseModel):
    name: str
    email: EmailStr
    subject: str | None = None
    message: str


class ContactMessageResponse(ContactMessageCreate):
    id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
