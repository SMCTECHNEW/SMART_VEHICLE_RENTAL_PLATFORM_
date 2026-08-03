from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.models import Coupon
from app.schemas.schemas import CouponCreate, CouponResponse
from datetime import datetime

router = APIRouter(prefix="/coupons", tags=["Coupons"])


@router.get("/", response_model=List[CouponResponse])
def get_all_coupons(db: Session = Depends(get_db)):
    coupons = db.query(Coupon).filter(Coupon.is_active == True).all()
    return coupons


@router.post("/", response_model=CouponResponse)
def create_coupon(coupon: CouponCreate, db: Session = Depends(get_db)):
    existing = db.query(Coupon).filter(Coupon.code == coupon.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Coupon code already exists")
    
    db_coupon = Coupon(**coupon.model_dump())
    db.add(db_coupon)
    db.commit()
    db.refresh(db_coupon)
    return db_coupon


@router.put("/{coupon_id}", response_model=CouponResponse)
def update_coupon(coupon_id: int, coupon: CouponCreate, db: Session = Depends(get_db)):
    db_coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not db_coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    
    for key, value in coupon.model_dump().items():
        setattr(db_coupon, key, value)
    
    db.commit()
    db.refresh(db_coupon)
    return db_coupon


@router.delete("/{coupon_id}")
def delete_coupon(coupon_id: int, db: Session = Depends(get_db)):
    db_coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not db_coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    db.delete(db_coupon)
    db.commit()
    return {"message": "Coupon deleted successfully"}


@router.get("/validate/{code}")
def validate_coupon(code: str, user_id: int = 1, db: Session = Depends(get_db)):
    coupon = db.query(Coupon).filter(Coupon.code == code).first()
    if not coupon:
        return {"valid": False, "message": "Coupon not found"}
    
    if not coupon.is_active:
        return {"valid": False, "message": "Coupon is inactive"}
    
    if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
        return {"valid": False, "message": "Coupon usage limit reached"}
    
    if coupon.valid_until and coupon.valid_until < datetime.utcnow():
        return {"valid": False, "message": "Coupon has expired"}
    
    # Check if for new users only
    if coupon.for_new_users_only:
        user = db.query(User).filter(User.id == user_id).first()
        if user and not user.is_new_user:
            return {"valid": False, "message": "Coupon only for new users"}
    
    return {
        "valid": True,
        "discount_percentage": coupon.discount_percentage,
        "max_discount": coupon.max_discount,
        "message": "Coupon is valid"
    }

# Import User here to avoid circular import
from app.models.models import User
