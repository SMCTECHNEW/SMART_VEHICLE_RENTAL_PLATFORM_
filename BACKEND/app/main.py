from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api import auth, vehicles, bookings, reviews, coupons, chatbot, admin

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(vehicles.router, prefix="/api")
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
