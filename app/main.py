# app/main.py (Move the existing main.py content here and update imports)
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

from app import models, schemas
from app.database import engine, get_db

# Load environment variables
load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="LicitaYa API")

# Configure CORS
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

@app.get("/")
async def root():
    return {"message": "LicitaYa API is running"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }

@app.get("/api/tenders", response_model=schemas.TenderList)
async def get_tenders(
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    phase: Optional[str] = None,
    state: Optional[str] = None,
    procedure_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = "created_at",
    sort_direction: Optional[str] = "desc",
    db: Session = Depends(get_db)
):
    try:
        # Calculate offset
        offset = (page - 1) * limit

        # Build query
        query = db.query(models.Tender)

        # Apply filters
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                models.Tender.request_name.ilike(search_filter) |
                models.Tender.reference_code.ilike(search_filter)
            )
        
        if phase:
            query = query.filter(models.Tender.phase == phase)
        
        if state:
            query = query.filter(models.Tender.state == state)
            
        if procedure_type:
            query = query.filter(models.Tender.procedure_type == procedure_type)
            
        if min_price is not None:
            query = query.filter(models.Tender.base_total_price >= min_price)
            
        if max_price is not None:
            query = query.filter(models.Tender.base_total_price <= max_price)

        # Get total count
        total = query.count()

        # Apply sorting
        if sort_by and hasattr(models.Tender, sort_by):
            order_col = getattr(models.Tender, sort_by)
            if sort_direction == "desc":
                order_col = order_col.desc()
            query = query.order_by(order_col)

        # Apply pagination
        tenders = query.offset(offset).limit(limit).all()

        return {
            "data": tenders,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch tenders: {str(e)}"
        )

@app.get("/api/tenders/{tender_id}", response_model=schemas.Tender)
async def get_tender(tender_id: int, db: Session = Depends(get_db)):
    tender = db.query(models.Tender).filter(models.Tender.id == tender_id).first()
    if tender is None:
        raise HTTPException(status_code=404, detail="Tender not found")
    return tender

    
@app.get("/api/health")
async def health_check():
    try:
        # Verify database connection
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": "production" if os.getenv("RENDER") else "development"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }