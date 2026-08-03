# Import all models to ensure they are registered with SQLAlchemy
from app.models.models import User, Vehicle, Booking, Review, Payment, Driver, PasswordResetToken, Refund, VehicleImage, Admin, ContactMessage, Coupon, DiscountOnCar, Maintenance, PickupReturn, VehicleCategory, VehicleHealthScore

__all__ = [
    "User",
    "Vehicle",
    "Booking",
    "Driver",
    "PasswordResetToken",
    "Refund",
    "VehicleImage",
    "Review",
    "Payment",
    "Admin",
    "ContactMessage",
    "Coupon",
    "DiscountOnCar",
    "Maintenance",
    "PickupReturn",
    "VehicleCategory",
    "VehicleHealthScore"
]
