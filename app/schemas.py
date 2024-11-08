# app/schemas.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

class TenderBase(BaseModel):
    """Base Tender schema with common attributes"""
    reference_code: str = Field(..., description="Unique reference code for the tender")
    request_name: str = Field(..., description="Name or title of the tender request")
    phase: str = Field(..., description="Current phase of the tender")
    state: str = Field(..., description="Current state of the tender")
    procedure_type: str = Field(..., description="Type of tender procedure")
    base_total_price: float = Field(..., description="Base total price for the tender")
    detail_url: str = Field(..., description="URL to the tender details")
    total_lotes: int = Field(..., description="Total number of lots in the tender")

class TenderCreate(TenderBase):
    """Schema for creating a new tender"""
    pass

class Tender(TenderBase):
    """Complete Tender schema including database fields"""
    id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
    )

class BuyerBase(BaseModel):
    """Base Buyer schema"""
    name: str
    profile_url: Optional[str] = None

class Buyer(BuyerBase):
    """Complete Buyer schema including database fields"""
    id: int
    tender_id: int

    model_config = ConfigDict(from_attributes=True)

class MipymesBase(BaseModel):
    """Base Mipymes schema"""
    dirigido_mipymes: bool = False
    dirigido_mipymes_mujeres: bool = False

class Mipymes(MipymesBase):
    """Complete Mipymes schema including database fields"""
    id: int
    tender_id: int

    model_config = ConfigDict(from_attributes=True)

class ItemBase(BaseModel):
    """Base Item schema"""
    referencia: str
    codigo_unspsc: str
    cuenta_presupuestaria: str
    descripcion: str
    cantidad: float
    unidad: str
    precio_unitario_estimado: float
    precio_total_estimado: float

class Item(ItemBase):
    """Complete Item schema including database fields"""
    id: int
    lote_id: int

    model_config = ConfigDict(from_attributes=True)

class LoteBase(BaseModel):
    """Base Lote schema"""
    lote_number: int
    name: str

class Lote(LoteBase):
    """Complete Lote schema including database fields"""
    id: int
    tender_id: int
    items: List[Item] = []

    model_config = ConfigDict(from_attributes=True)

class PaginationResponse(BaseModel):
    """Pagination metadata"""
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of items per page")
    total: int = Field(..., description="Total number of items")

class TenderList(BaseModel):
    """Response model for paginated tender list"""
    data: List[Tender]
    pagination: PaginationResponse

    model_config = ConfigDict(from_attributes=True)

class TenderDetail(Tender):
    """Detailed Tender schema including related data"""
    buyer: Optional[Buyer] = None
    mipymes: Optional[Mipymes] = None
    lotes: List[Lote] = []

    model_config = ConfigDict(from_attributes=True)

# Models are now self-referential through type hints
# No need for update_forward_refs() or model_rebuild()