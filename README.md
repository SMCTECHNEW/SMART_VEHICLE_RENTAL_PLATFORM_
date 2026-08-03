# Smart Vehicle Rental Platform

A complete production-ready vehicle rental platform with AI-powered features, built with FastAPI backend and modern frontend.

## 🚀 Features

### Core Features
- **AI Chatbot** - 24/7 intelligent customer assistance
- **User Authentication** - JWT-based secure authentication
- **Multiple Vehicle Booking** - Book various vehicle types (Cars, SUVs, Bikes, Luxury)
- **Advance Booking** - Schedule bookings in advance
- **Driver Option** - Professional drivers available with additional charges

### Discount System
- **15% Discount** - On bookings above 2 days
- **20% Discount** - For new users on first booking
- **Coupon Management** - Admin can create and manage promotional coupons

### Payment Integration
- **Razorpay** - Secure payment gateway integration
- Multiple payment methods (Cards, UPI, Net Banking, Wallets)

### Loyalty Program
- Earn points on bookings and reviews
- Redeem points for discounts
- Tier-based membership system

### Hidden Deal Finder
- Automatically suggests cheaper similar vehicles before checkout
- Save money with smart recommendations

### Reviews & Ratings
- Rate vehicles after booking
- Driver ratings and reviews
- Average rating display

### Dashboards
- **User Dashboard** - Manage bookings, profile, loyalty rewards
- **Admin Dashboard** - Complete vehicle, booking, and user management

## 🛠️ Tech Stack

### Backend
- **Python FastAPI** - Modern async web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM for database operations
- **JWT** - JSON Web Tokens for authentication
- **Razorpay SDK** - Payment processing
- **Passlib** - Password hashing
- **Pydantic** - Data validation

### Frontend
- **HTML5/CSS3** - Semantic markup and styling
- **JavaScript (ES6+)** - Interactive functionality
- **Bootstrap 5** - Responsive UI framework
- **Font Awesome** - Icon library
- **Razorpay Checkout** - Payment integration

## 📁 Project Structure

```
/workspace
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── vehicles.py    # Vehicle CRUD operations
│   │   │   ├── bookings.py    # Booking management
│   │   │   ├── reviews.py     # Review system
│   │   │   ├── coupons.py     # Coupon management
│   │   │   ├── chatbot.py     # AI chatbot
│   │   │   └── admin.py       # Admin dashboard APIs
│   │   ├── core/
│   │   │   ├── config.py      # Configuration settings
│   │   │   └── database.py    # Database connection
│   │   ├── models/
│   │   │   └── models.py      # SQLAlchemy models
│   │   ├── schemas/
│   │   │   └── schemas.py     # Pydantic schemas
│   │   ├── utils/
│   │   │   ├── security.py    # Password hashing
│   │   │   └── jwt.py         # JWT utilities
│   │   └── main.py            # FastAPI application
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/
    ├── index.html             # Main landing page
    ├── dashboard.html         # User dashboard
    ├── css/
    │   └── style.css          # Custom styles (Orange theme)
    └── js/
        └── app.js             # Frontend JavaScript
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Node.js (optional, for development)

### Installation

1. **Clone the repository**
```bash
cd /workspace
```

2. **Set up PostgreSQL database**
```sql
CREATE DATABASE vehicle_rental;
```

3. **Configure environment variables**
```bash
cd backend
cp .env.example .env
# Edit .env with your database credentials and Razorpay keys
```

4. **Install dependencies**
```bash
cd backend
pip install -r requirements.txt
```

5. **Run the backend server**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Seed the database** (Optional)
```bash
curl -X POST http://localhost:8000/api/admin/seed-data
```

7. **Open the frontend**
```bash
# Open frontend/index.html in a browser
# Or serve it with a simple HTTP server
python -m http.server 3000 --directory frontend
```

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user

### Vehicles
- `GET /api/vehicles/` - List all vehicles
- `GET /api/vehicles/{id}` - Get vehicle details
- `GET /api/vehicles/type/{type}` - Filter by type
- `GET /api/vehicles/{id}/similar` - Get similar vehicles (Hidden Deal Finder)

### Bookings
- `POST /api/bookings/` - Create booking
- `GET /api/bookings/` - Get user bookings
- `GET /api/bookings/{id}` - Get booking details
- `PUT /api/bookings/{id}/confirm` - Confirm booking
- `DELETE /api/bookings/{id}` - Cancel booking
- `GET /api/bookings/hidden-deal/{id}` - Get hidden deals

### Reviews
- `POST /api/reviews/` - Create review
- `GET /api/reviews/vehicle/{id}` - Get vehicle reviews
- `GET /api/reviews/average/{id}` - Get average rating

### Coupons
- `GET /api/coupons/` - List active coupons
- `GET /api/coupons/validate/{code}` - Validate coupon

### Chatbot
- `POST /api/chatbot/` - Send message to AI chatbot

### Admin
- `GET /api/admin/dashboard` - Dashboard statistics
- `GET /api/admin/users` - All users
- `GET /api/admin/bookings` - All bookings
- `GET /api/admin/vehicles` - All vehicles
- `POST /api/admin/seed-data` - Seed database

## 🎨 Theme Colors

- **Primary Orange**: #FF7A00
- **Secondary Orange**: #e56d00
- **White**: #FFFFFF
- **Dark**: #1a1a1a

## 🔐 Security Features

- Password hashing with bcrypt
- JWT token authentication
- CORS protection
- SQL injection prevention (via SQLAlchemy ORM)
- Input validation with Pydantic

## 📝 License

MIT License

---

Built with ❤️ using FastAPI and Bootstrap
