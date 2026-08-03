from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import ChatbotMessage
from app.models.models import Vehicle

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


@router.post("/")
def chat(message: ChatbotMessage, db: Session = Depends(get_db)):
    """AI Chatbot for vehicle rental assistance"""
    user_message = message.message.lower()
    
    responses = {
        "greeting": ["hello", "hi", "hey", "good morning", "good evening"],
        "vehicles": ["vehicle", "car", "bike", "suv", "available", "see vehicles"],
        "booking": ["book", "booking", "reserve", "rental"],
        "discount": ["discount", "offer", "deal", "save", "cheap"],
        "driver": ["driver", "chauffeur"],
        "payment": ["payment", "pay", "razorpay", "card"],
        "loyalty": ["loyalty", "points", "reward"],
        "help": ["help", "support", "assist"]
    }
    
    response = ""
    
    # Check for greetings
    if any(word in user_message for word in responses["greeting"]):
        response = "Hello! Welcome to Smart Vehicle Rental. How can I help you today? You can ask about available vehicles, bookings, discounts, or our driver services."
    
    # Check for vehicle queries
    elif any(word in user_message for word in responses["vehicles"]):
        vehicles = db.query(Vehicle).filter(Vehicle.is_available == True).limit(5).all()
        vehicle_list = "\n".join([f"- {v.brand} {v.model} ({v.vehicle_type}): ₹{v.price_per_day}/day" for v in vehicles])
        response = f"Here are some available vehicles:\n{vehicle_list}\n\nWould you like to book one?"
    
    # Check for booking queries
    elif any(word in user_message for word in responses["booking"]):
        response = "To book a vehicle, please select your preferred vehicle, choose pickup and drop-off dates, and decide if you need a driver. We offer advance booking with flexible cancellation!"
    
    # Check for discount queries
    elif any(word in user_message for word in responses["discount"]):
        response = "Great news! We offer:\n• 15% discount on bookings above 2 days\n• 20% discount for new users\n• Special deals through our Hidden Deal Finder!\nCheck out our coupons section for more savings."
    
    # Check for driver queries
    elif any(word in user_message for word in responses["driver"]):
        response = "Yes! We provide professional drivers with additional charges. Many of our vehicles have the driver option available. The driver charge is typically ₹500/day. You can rate your driver after the trip!"
    
    # Check for payment queries
    elif any(word in user_message for word in responses["payment"]):
        response = "We accept payments via Razorpay, which supports all major credit/debit cards, UPI, net banking, and wallets. Your payment is secure and processed instantly."
    
    # Check for loyalty queries
    elif any(word in user_message for word in responses["loyalty"]):
        response = "Our Loyalty Rewards program lets you earn points on every booking and review! Earn 50 points per review and redeem them for discounts on future bookings."
    
    # Help
    elif any(word in user_message for word in responses["help"]):
        response = "I'm here to help! You can ask me about:\n• Available vehicles and prices\n• How to book a vehicle\n• Discounts and offers\n• Driver services\n• Payment methods\n• Loyalty rewards\nWhat would you like to know?"
    
    else:
        response = "I'm not sure I understand. Could you please rephrase? You can ask me about vehicles, bookings, discounts, drivers, payments, or loyalty rewards."
    
    return {"response": response, "message_id": hash(user_message)}
