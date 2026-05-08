"""
DEMAND-24 — Pydantic Schemas: Sku

DTOs para creación, lectura y actualización de SKUs.
Contrato entre Backend y Frontend (Regla VII).
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SkuCreate(BaseModel):
    """Schema para crear un nuevo SKU."""

    sku_code: str = Field(..., max_length=50, description="Codigo unico del SKU")
    description: Optional[str] = Field(None, description="Descripcion del producto")
    current_stock: Optional[int] = Field(0, ge=0, description="Stock actual en unidades")


class SkuRead(BaseModel):
    """Schema para leer un SKU desde la BD."""

    id: int
    sku_code: str
    description: Optional[str] = None
    current_stock: Optional[int] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SkuUpdate(BaseModel):
    """Schema para actualizar un SKU (campos opcionales)."""

    sku_code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    current_stock: Optional[int] = Field(None, ge=0)
