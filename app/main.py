from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, List
from . import models
from .database import engine, get_db
from .utils.email_utils import create_verification_token, send_verification_email, is_token_valid
import os
from dotenv import load_dotenv

# Initialize database
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Updated CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://junhuohz.com",   # Production frontend
        "https://www.junhuohz.com" # Production frontend www
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Pydantic models
class UserPreferences(BaseModel):
    keywords: List[str] = []
    max_budget: Optional[float] = None
    regions: List[str] = []

class UserCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    preferences: Optional[UserPreferences] = None

# Routes
@app.post("/api/users/register")
async def register_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Validate preferences if provided
    if user.preferences and len(user.preferences.keywords) > 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum 5 keyword preferences allowed"
        )

    # Check if user exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        if not db_user.is_verified:
            # Resend verification for unverified users
            token_data = create_verification_token()
            db_user.verification_token = token_data["token"]
            db_user.verification_token_expires = token_data["expires"]
            db.commit()
            
            background_tasks.add_task(
                send_verification_email,
                user.email,
                token_data["token"],
                user.name
            )
            return {"message": "Verification email resent"}
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create verification token
    token_data = create_verification_token()
    
    # Create new user
    db_user = models.User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        company=user.company,
        is_active=True,
        subscription_tier='free',
        is_verified=False,
        verification_token=token_data["token"],
        verification_token_expires=token_data["expires"],
        preferences=user.preferences.dict() if user.preferences else {}
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Send verification email
        background_tasks.add_task(
            send_verification_email,
            user.email,
            token_data["token"],
            user.name
        )
        
        return {"message": "Registration successful. Please check your email for verification."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/verify/{token}")
async def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=404, detail="Invalid verification token")
        
    if not is_token_valid(user.verification_token_expires):
        raise HTTPException(status_code=400, detail="Verification token has expired")
        
    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires = None
    
    db.commit()
    return {"message": "Email verified successfully"}