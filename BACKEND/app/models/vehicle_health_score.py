from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from app.core.database import Base


class VehicleHealthScore(Base):
    __tablename__ = "vehicle_health_scores"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)

    score = Column(Integer, nullable=False)
    condition = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)

    updated_at = Column(DateTime, default=datetime.utcnow)
