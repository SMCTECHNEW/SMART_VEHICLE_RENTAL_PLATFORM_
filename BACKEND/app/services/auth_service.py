from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password
from app.models.user import User


def create_user(db: Session, full_name, email, phone, password):
    user = User(
        full_name=full_name,
        email=email,
        phone=phone,
        hashed_password=hash_password(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email, password):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user
