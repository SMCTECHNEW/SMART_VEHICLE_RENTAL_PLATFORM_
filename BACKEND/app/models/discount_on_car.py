from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from app.core.database import Base


class DiscountOnCar(Base):
    __tablename__ = "discounts_on_cars"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)

    title = Column(String(200), nullable=False)
    percentage = Column(Float, nullable=False)

    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)

    is_active = Column(Boolean, default=True)
