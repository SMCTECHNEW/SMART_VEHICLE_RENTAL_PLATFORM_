"""Test model imports and basic functionality"""
import pytest
from app.models import User, Vehicle, Booking, Review, Payment, Driver, Coupon


def test_user_model():
    """Test User model creation"""
    user = User(
        full_name="Test User",
        email="test@example.com",
        hashed_password="hashed123",
        role="user"
    )
    assert user.full_name == "Test User"
    assert user.email == "test@example.com"
    assert user.role == "user"


def test_vehicle_model():
    """Test Vehicle model creation"""
    vehicle = Vehicle(
        brand="Toyota",
        model="Camry",
        registration_number="ABC123",
        price_per_day=100.0,
        status="available"
    )
    assert vehicle.brand == "Toyota"
    assert vehicle.price_per_day == 100.0


def test_booking_model():
    """Test Booking model creation"""
    booking = Booking(
        user_id=1,
        vehicle_id=1,
        pickup_date="2024-01-01",
        return_date="2024-01-05",
        total_amount=400.0,
        status="pending"
    )
    assert booking.user_id == 1
    assert booking.total_amount == 400.0


def test_review_model():
    """Test Review model creation"""
    review = Review(
        user_id=1,
        vehicle_id=1,
        rating=5,
        comment="Great vehicle!"
    )
    assert review.rating == 5
    assert review.comment == "Great vehicle!"


def test_payment_model():
    """Test Payment model creation"""
    payment = Payment(
        booking_id=1,
        amount=400.0,
        payment_method="razorpay",
        status="pending"
    )
    assert payment.amount == 400.0
    assert payment.payment_method == "razorpay"


def test_driver_model():
    """Test Driver model creation"""
    driver = Driver(
        name="John Driver",
        phone="1234567890",
        license_number="DL123456",
        license_expiry="2025-12-31",
        is_active=True
    )
    assert driver.name == "John Driver"
    assert driver.is_active is True


def test_coupon_model():
    """Test Coupon model creation"""
    coupon = Coupon(
        code="SAVE10",
        discount_percentage=10.0,
        max_discount=50.0,
        is_active=True
    )
    assert coupon.code == "SAVE10"
    assert coupon.discount_percentage == 10.0


def test_no_duplicate_tables():
    """Verify no duplicate table definitions exist"""
    from app.core.database import Base
    
    tables = list(Base.metadata.tables.keys())
    unique_tables = set(tables)
    
    assert len(tables) == len(unique_tables), f"Duplicate tables found: {tables}"
    print(f"All tables unique: {sorted(tables)}")
