# app/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

class Tender(Base):
    __tablename__ = "tender"

    id = Column(Integer, primary_key=True, index=True)
    reference_code = Column(String, unique=True, index=True)
    request_name = Column(String)
    phase = Column(String)
    state = Column(String)
    procedure_type = Column(String)
    base_total_price = Column(Float)
    detail_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    total_lotes = Column(Integer)

# backend/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class TenderBase(BaseModel):
    reference_code: str
    request_name: str
    phase: str
    state: str
    procedure_type: str
    base_total_price: float
    detail_url: str
    total_lotes: int

class Tender(TenderBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PaginationResponse(BaseModel):
    page: int
    limit: int
    total: int

class TenderList(BaseModel):
    data: List[Tender]
    pagination: PaginationResponse

