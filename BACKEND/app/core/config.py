from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/vehicle_rental"
    RAZORPAY_KEY_ID: str = "rzp_test_your_key_id"
    RAZORPAY_KEY_SECRET: str = "your_key_secret"

    class Config:
        env_file = ".env"


settings = Settings()
