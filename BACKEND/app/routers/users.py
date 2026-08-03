from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

security = HTTPBearer()


# =====================================================
# GET CURRENT USER
# =====================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    payload = decode_access_token(
        credentials.credentials
    )

    if not payload:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


    if "sub" not in payload:

        raise HTTPException(
            status_code=401,
            detail="Invalid token payload"
        )


    try:

        user_id = int(
            payload["sub"]
        )

    except (ValueError, TypeError):

        raise HTTPException(
            status_code=401,
            detail="Invalid user ID"
        )


    user = db.query(User).filter(
        User.id == user_id
    ).first()


    if not user:

        raise HTTPException(
            status_code=401,
            detail="User not found"
        )


    return user


# =====================================================
# GET MY PROFILE
# =====================================================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(
        get_current_user
    )
):

    return current_user


# =====================================================
# UPDATE MY PROFILE
# =====================================================

@router.put(
    "/me",
    response_model=UserResponse
)
def update_me(
    data: UserUpdate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):


    # UPDATE FULL NAME

    if data.full_name is not None:

        current_user.full_name = (
            data.full_name
        )


    # UPDATE PHONE

    if data.phone is not None:

        current_user.phone = (
            data.phone
        )


    db.commit()

    db.refresh(
        current_user
    )


    return current_user


# =====================================================
# GET ALL USERS
# =====================================================

@router.get(
    "/",
    response_model=list[UserResponse]
)
def get_users(
    db: Session = Depends(get_db)
):

    return db.query(
        User
    ).all()