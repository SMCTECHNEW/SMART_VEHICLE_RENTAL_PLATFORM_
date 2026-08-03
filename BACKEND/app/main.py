from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.core.database import engine, Base
from app.api import auth, vehicles, bookings, reviews, coupons, chatbot, admin
from app.routers import vehicles_new as vehicles_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Vehicle Rental Platform",
    description="AI-powered vehicle rental platform with advanced booking features",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for vehicle images
uploads_path = Path("BACKEND/uploads")
uploads_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(vehicles_router.router, prefix="/api")  # New enhanced vehicles router
app.include_router(bookings.router, prefix="/api")
app.include_router(reviews.router, prefix="/api")
app.include_router(coupons.router, prefix="/api")
app.include_router(chatbot.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Smart Vehicle Rental Platform API",
        "docs": "/docs",
        "features": [
            "AI Chatbot Assistance",
            "Multiple Vehicle Booking",
            "15% discount on bookings above 2 days",
            "20% discount for new users",
            "Driver option with additional charges",
            "Advance booking",
            "Razorpay payment integration",
            "Driver ratings and reviews",
            "Loyalty rewards program",
            "Hidden Deal Finder",
            "Admin dashboard",
            "User dashboard"
        ]
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
