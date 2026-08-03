#!/bin/bash

echo "Starting Smart Vehicle Rental Platform..."

# Check if .env exists, if not create from example
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env with your database credentials before running."
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run database migrations (create tables)
echo "Setting up database..."
python -c "
from app.core.database import engine, Base
from app.models.models import User, Vehicle, Booking, Review, Coupon
Base.metadata.create_all(bind=engine)
print('Database tables created successfully!')
"

# Seed sample data
echo "Seeding sample data..."
python -c "
import sys
sys.path.insert(0, '.')
from app.main import app
from fastapi.testclient import TestClient
client = TestClient(app)
response = client.post('/api/admin/seed-data')
print(response.json())
"

# Start the server
echo "Starting FastAPI server on http://0.0.0.0:8000..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
