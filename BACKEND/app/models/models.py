# This file is deprecated. All models have been moved to individual files.
# Import from app.models instead of app.models.models
# This file is kept for backward compatibility only.

from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.booking import Booking
from app.models.review import Review
from app.models.payment import Payment
from app.models.driver import Driver, PasswordResetToken, Refund, VehicleImage
from app.models.admin import Admin
from app.models.contact_message import ContactMessage
from app.models.coupon import Coupon
from app.models.discount_on_car import DiscountOnCar
from app.models.maintenance import Maintenance
from app.models.pickup_return import PickupReturn
from app.models.vehicle_category import VehicleCategory
from app.models.vehicle_health_score import VehicleHealthScore

__all__ = [
    "User",
    "Vehicle", 
    "Booking",
    "Review",
    "Payment",
    "Driver",
    "PasswordResetToken",
    "Refund",
    "VehicleImage",
    "Admin",
    "ContactMessage",
    "Coupon",
    "DiscountOnCar",
    "Maintenance",
    "PickupReturn",
    "VehicleCategory",
    "VehicleHealthScore"
]
