from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from app.core.database import Base


class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)
    subject = Column(String(200), nullable=True)
    message = Column(Text, nullable=False)

    status = Column(String(30), default="unread")
    created_at = Column(DateTime, default=datetime.utcnow)
