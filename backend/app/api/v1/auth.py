"""
Authentication routes
"""
from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
import random
import os

from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
)
from app.models.database import get_db
from app.models.user import User
from app.models.finance import UserProfile, UserProgress
from app.schemas.schemas import UserCreate, UserResponse, Token

router = APIRouter()

# In-memory OTP storage (user_id -> {otp: str, timestamp: datetime})
otp_storage = {}


class OTPVerifyRequest(BaseModel):
    email: str
    otp: str


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""

    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    db_user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=get_password_hash(user_data.password),
        age=user_data.age,
        occupation=user_data.occupation,
        monthly_income=user_data.monthly_income or 0.0,
        location=user_data.location,
        financial_knowledge=user_data.financial_knowledge or "beginner"
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create user profile and progress records
    user_profile = UserProfile(user_id=db_user.id)
    user_progress = UserProgress(user_id=db_user.id)
    db.add(user_profile)
    db.add(user_progress)
    db.commit()

    # Store OTP for verification
    otp_code = "123456" if os.getenv("OTP_DEVELOPER_MODE") == "true" else str(random.randint(100000, 999999))
    otp_storage[db_user.id] = {
        "otp": otp_code,
        "timestamp": datetime.utcnow(),
        "email": user_data.email
    }

    # In development mode, print OTP to console
    if os.getenv("OTP_DEVELOPER_MODE") == "true":
        print(f"📧 OTP for {user_data.email}: {otp_code}")

    return db_user


@router.post("/verify-otp", response_model=Token)
async def verify_otp(otp_request: OTPVerifyRequest, db: Session = Depends(get_db)):
    """Verify OTP and return access token"""

    # Find user by email
    user = db.query(User).filter(User.email == otp_request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # Check OTP
    if user.id not in otp_storage:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OTP expired or not found"
        )

    stored_otp = otp_storage[user.id]

    # Check if OTP matches and is not expired (10 minutes)
    if stored_otp["otp"] != otp_request.otp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP"
        )

    time_diff = (datetime.utcnow() - stored_otp["timestamp"]).total_seconds()
    if time_diff > 600:  # 10 minutes
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OTP expired"
        )

    # Clear OTP
    del otp_storage[user.id]

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login user"""
    
    # Find user
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
