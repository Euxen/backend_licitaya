from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)  # This was missing
    company = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    subscription_tier = Column(String, default='free')
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, unique=True, nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)
    preferences = Column(JSONB, nullable=True, default=dict)